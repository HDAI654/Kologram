package postgres

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log/slog"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/port"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

// ConversationRepository is the PostgreSQL adapter for ConversationRepository port.
type ConversationRepository struct {
	pool *pgxpool.Pool
}

func NewConversationRepository(pool *pgxpool.Pool) *ConversationRepository {
	return &ConversationRepository{pool: pool}
}

// Migrate creates the conversations table if it does not exist.
func Migrate(ctx context.Context, pool *pgxpool.Pool) error {
	_, err := pool.Exec(ctx, `
CREATE TABLE IF NOT EXISTS conversations (
  id            TEXT PRIMARY KEY,
  buyer_id      TEXT NOT NULL,
  seller_id     TEXT NOT NULL,
  listing_id    TEXT NOT NULL,
  status        TEXT NOT NULL,
  messages_json JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at    TIMESTAMPTZ NOT NULL,
  updated_at    TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_conv_buyer_listing ON conversations (buyer_id, listing_id);
CREATE INDEX IF NOT EXISTS idx_conv_buyer ON conversations (buyer_id);
CREATE INDEX IF NOT EXISTS idx_conv_seller ON conversations (seller_id);
`)
	return err
}

type messageDTO struct {
	ID             string `json:"id"`
	ConversationID string `json:"conversation_id"`
	SenderID       string `json:"sender_id"`
	Content        string `json:"content"`
	IsRead         bool   `json:"is_read"`
	SentAt         string `json:"sent_at"`
}

func marshalMessages(msgs []domain.Message) ([]byte, error) {
	dtos := make([]messageDTO, 0, len(msgs))
	for _, m := range msgs {
		dtos = append(dtos, messageDTO{
			ID:             m.ID.String(),
			ConversationID: m.ConversationID.String(),
			SenderID:       m.SenderID.String(),
			Content:        m.Content.String(),
			IsRead:         m.IsRead,
			SentAt:         m.SentAt.UTC().Format(time.RFC3339Nano),
		})
	}
	return json.Marshal(dtos)
}

func unmarshalMessages(raw []byte, conversationID valueobject.ConversationID) ([]domain.Message, error) {
	if len(raw) == 0 {
		return nil, nil
	}
	var dtos []messageDTO
	if err := json.Unmarshal(raw, &dtos); err != nil {
		return nil, err
	}
	out := make([]domain.Message, 0, len(dtos))
	for _, d := range dtos {
		mid, err := valueobject.NewMessageID(d.ID)
		if err != nil {
			return nil, err
		}
		sid, err := valueobject.NewUserID(d.SenderID)
		if err != nil {
			return nil, err
		}
		content, err := valueobject.NewMessageContent(d.Content)
		if err != nil {
			return nil, err
		}
		sentAt, err := time.Parse(time.RFC3339Nano, d.SentAt)
		if err != nil {
			sentAt, err = time.Parse(time.RFC3339, d.SentAt)
			if err != nil {
				return nil, err
			}
		}
		cid := conversationID
		if d.ConversationID != "" {
			cid, err = valueobject.NewConversationID(d.ConversationID)
			if err != nil {
				return nil, err
			}
		}
		out = append(out, domain.Message{
			ID:             mid,
			ConversationID: cid,
			SenderID:       sid,
			Content:        content,
			IsRead:         d.IsRead,
			SentAt:         sentAt.UTC(),
		})
	}
	return out, nil
}

func (r *ConversationRepository) Add(ctx context.Context, c *domain.Conversation) error {
	msgs, err := marshalMessages(c.Messages)
	if err != nil {
		return err
	}
	slog.Info("postgres add conversation", "id", c.ID.String())
	_, err = r.pool.Exec(ctx, `
INSERT INTO conversations (id, buyer_id, seller_id, listing_id, status, messages_json, created_at, updated_at)
VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7, $8)`,
		c.ID.String(),
		c.BuyerID.String(),
		c.SellerID.String(),
		c.ListingID.String(),
		c.Status.String(),
		msgs,
		c.CreatedAt.UTC(),
		c.UpdatedAt.UTC(),
	)
	return err
}

func (r *ConversationRepository) GetByID(ctx context.Context, id valueobject.ConversationID) (*domain.Conversation, error) {
	row := r.pool.QueryRow(ctx, `
SELECT id, buyer_id, seller_id, listing_id, status, messages_json, created_at, updated_at
FROM conversations WHERE id = $1`, id.String())
	return scanConversation(row)
}

func (r *ConversationRepository) Update(ctx context.Context, c *domain.Conversation) error {
	msgs, err := marshalMessages(c.Messages)
	if err != nil {
		return err
	}
	tag, err := r.pool.Exec(ctx, `
UPDATE conversations
SET status = $1, messages_json = $2::jsonb, updated_at = $3
WHERE id = $4`,
		c.Status.String(), msgs, c.UpdatedAt.UTC(), c.ID.String(),
	)
	if err != nil {
		return err
	}
	if tag.RowsAffected() == 0 {
		return domain.ErrConversationNotFound
	}
	return nil
}

func (r *ConversationRepository) FindByBuyerAndListing(
	ctx context.Context,
	buyerID valueobject.UserID,
	listingID valueobject.ListingID,
) (*domain.Conversation, error) {
	row := r.pool.QueryRow(ctx, `
SELECT id, buyer_id, seller_id, listing_id, status, messages_json, created_at, updated_at
FROM conversations
WHERE buyer_id = $1 AND listing_id = $2
LIMIT 1`, buyerID.String(), listingID.String())
	c, err := scanConversation(row)
	if errors.Is(err, domain.ErrConversationNotFound) {
		return nil, nil
	}
	return c, err
}

func (r *ConversationRepository) ListForUser(
	ctx context.Context,
	userID valueobject.UserID,
	limit, offset int,
) ([]*domain.Conversation, error) {
	if limit <= 0 {
		limit = 50
	}
	if offset < 0 {
		offset = 0
	}
	rows, err := r.pool.Query(ctx, `
SELECT id, buyer_id, seller_id, listing_id, status, messages_json, created_at, updated_at
FROM conversations
WHERE buyer_id = $1 OR seller_id = $1
ORDER BY updated_at DESC
LIMIT $2 OFFSET $3`, userID.String(), limit, offset)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	result := make([]*domain.Conversation, 0)
	for rows.Next() {
		c, err := scanConversationFromRows(rows)
		if err != nil {
			return nil, err
		}
		result = append(result, c)
	}
	return result, rows.Err()
}

type scannable interface {
	Scan(dest ...any) error
}

func scanConversation(row scannable) (*domain.Conversation, error) {
	var (
		id, buyerID, sellerID, listingID, status string
		messagesRaw                              []byte
		createdAt, updatedAt                     time.Time
	)
	err := row.Scan(&id, &buyerID, &sellerID, &listingID, &status, &messagesRaw, &createdAt, &updatedAt)
	if errors.Is(err, pgx.ErrNoRows) {
		return nil, domain.ErrConversationNotFound
	}
	if err != nil {
		return nil, err
	}
	return rehydrate(id, buyerID, sellerID, listingID, status, messagesRaw, createdAt, updatedAt)
}

func scanConversationFromRows(rows pgx.Rows) (*domain.Conversation, error) {
	var (
		id, buyerID, sellerID, listingID, status string
		messagesRaw                              []byte
		createdAt, updatedAt                     time.Time
	)
	if err := rows.Scan(&id, &buyerID, &sellerID, &listingID, &status, &messagesRaw, &createdAt, &updatedAt); err != nil {
		return nil, err
	}
	return rehydrate(id, buyerID, sellerID, listingID, status, messagesRaw, createdAt, updatedAt)
}

func rehydrate(
	id, buyerID, sellerID, listingID, status string,
	messagesRaw []byte,
	createdAt, updatedAt time.Time,
) (*domain.Conversation, error) {
	cid, err := valueobject.NewConversationID(id)
	if err != nil {
		return nil, err
	}
	bid, err := valueobject.NewUserID(buyerID)
	if err != nil {
		return nil, err
	}
	sid, err := valueobject.NewUserID(sellerID)
	if err != nil {
		return nil, err
	}
	lid, err := valueobject.NewListingID(listingID)
	if err != nil {
		return nil, err
	}
	st, err := valueobject.NewConversationStatus(status)
	if err != nil {
		return nil, err
	}
	msgs, err := unmarshalMessages(messagesRaw, cid)
	if err != nil {
		return nil, err
	}
	return domain.RehydrateConversation(cid, bid, sid, lid, st, msgs, createdAt.UTC(), updatedAt.UTC()), nil
}

// --- Unit of Work ---

type UnitOfWork struct {
	pool *pgxpool.Pool
	tx   pgx.Tx
	repo *txConversationRepository
}

func (u *UnitOfWork) Conversations() port.ConversationRepository { return u.repo }

func (u *UnitOfWork) Commit(ctx context.Context) error {
	if u.tx == nil {
		return nil
	}
	err := u.tx.Commit(ctx)
	u.tx = nil
	return err
}

func (u *UnitOfWork) Rollback(ctx context.Context) error {
	if u.tx == nil {
		return nil
	}
	err := u.tx.Rollback(ctx)
	u.tx = nil
	// After Commit, defer Rollback must be a no-op.
	if err != nil && (errors.Is(err, pgx.ErrTxClosed) || err.Error() == "tx is closed") {
		return nil
	}
	return err
}

type UnitOfWorkFactory struct {
	pool *pgxpool.Pool
}

func NewUnitOfWorkFactory(pool *pgxpool.Pool) *UnitOfWorkFactory {
	return &UnitOfWorkFactory{pool: pool}
}

func (f *UnitOfWorkFactory) New(ctx context.Context) (port.UnitOfWork, error) {
	tx, err := f.pool.Begin(ctx)
	if err != nil {
		return nil, fmt.Errorf("begin tx: %w", err)
	}
	return &UnitOfWork{
		pool: f.pool,
		tx:   tx,
		repo: &txConversationRepository{tx: tx},
	}, nil
}

// tx-scoped repository (same queries, bound to transaction).
type txConversationRepository struct {
	tx pgx.Tx
}

func (r *txConversationRepository) Add(ctx context.Context, c *domain.Conversation) error {
	msgs, err := marshalMessages(c.Messages)
	if err != nil {
		return err
	}
	_, err = r.tx.Exec(ctx, `
INSERT INTO conversations (id, buyer_id, seller_id, listing_id, status, messages_json, created_at, updated_at)
VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7, $8)`,
		c.ID.String(), c.BuyerID.String(), c.SellerID.String(), c.ListingID.String(),
		c.Status.String(), msgs, c.CreatedAt.UTC(), c.UpdatedAt.UTC(),
	)
	return err
}

func (r *txConversationRepository) GetByID(ctx context.Context, id valueobject.ConversationID) (*domain.Conversation, error) {
	row := r.tx.QueryRow(ctx, `
SELECT id, buyer_id, seller_id, listing_id, status, messages_json, created_at, updated_at
FROM conversations WHERE id = $1`, id.String())
	return scanConversation(row)
}

func (r *txConversationRepository) Update(ctx context.Context, c *domain.Conversation) error {
	msgs, err := marshalMessages(c.Messages)
	if err != nil {
		return err
	}
	tag, err := r.tx.Exec(ctx, `
UPDATE conversations
SET status = $1, messages_json = $2::jsonb, updated_at = $3
WHERE id = $4`,
		c.Status.String(), msgs, c.UpdatedAt.UTC(), c.ID.String(),
	)
	if err != nil {
		return err
	}
	if tag.RowsAffected() == 0 {
		return domain.ErrConversationNotFound
	}
	return nil
}

func (r *txConversationRepository) FindByBuyerAndListing(
	ctx context.Context,
	buyerID valueobject.UserID,
	listingID valueobject.ListingID,
) (*domain.Conversation, error) {
	row := r.tx.QueryRow(ctx, `
SELECT id, buyer_id, seller_id, listing_id, status, messages_json, created_at, updated_at
FROM conversations WHERE buyer_id = $1 AND listing_id = $2 LIMIT 1`,
		buyerID.String(), listingID.String())
	c, err := scanConversation(row)
	if errors.Is(err, domain.ErrConversationNotFound) {
		return nil, nil
	}
	return c, err
}

func (r *txConversationRepository) ListForUser(
	ctx context.Context,
	userID valueobject.UserID,
	limit, offset int,
) ([]*domain.Conversation, error) {
	if limit <= 0 {
		limit = 50
	}
	if offset < 0 {
		offset = 0
	}
	rows, err := r.tx.Query(ctx, `
SELECT id, buyer_id, seller_id, listing_id, status, messages_json, created_at, updated_at
FROM conversations
WHERE buyer_id = $1 OR seller_id = $1
ORDER BY updated_at DESC
LIMIT $2 OFFSET $3`, userID.String(), limit, offset)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	result := make([]*domain.Conversation, 0)
	for rows.Next() {
		c, err := scanConversationFromRows(rows)
		if err != nil {
			return nil, err
		}
		result = append(result, c)
	}
	return result, rows.Err()
}

// OpenPool connects to PostgreSQL using DATABASE_URL.
func OpenPool(ctx context.Context, databaseURL string) (*pgxpool.Pool, error) {
	cfg, err := pgxpool.ParseConfig(databaseURL)
	if err != nil {
		return nil, fmt.Errorf("parse database url: %w", err)
	}
	pool, err := pgxpool.NewWithConfig(ctx, cfg)
	if err != nil {
		return nil, fmt.Errorf("connect postgres: %w", err)
	}
	if err := pool.Ping(ctx); err != nil {
		pool.Close()
		return nil, fmt.Errorf("ping postgres: %w", err)
	}
	return pool, nil
}
