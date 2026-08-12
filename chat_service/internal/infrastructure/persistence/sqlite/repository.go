//go:build sqlite

package sqlite

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/port"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"

	_ "modernc.org/sqlite"
)

type ConversationRepository struct {
	db *sql.DB
}

func NewConversationRepository(db *sql.DB) *ConversationRepository {
	return &ConversationRepository{db: db}
}

func Migrate(db *sql.DB) error {
	_, err := db.Exec(`
CREATE TABLE IF NOT EXISTS conversations (
  id TEXT PRIMARY KEY,
  buyer_id TEXT NOT NULL,
  seller_id TEXT NOT NULL,
  listing_id TEXT NOT NULL,
  status TEXT NOT NULL,
  messages_json TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_conv_buyer_listing ON conversations(buyer_id, listing_id);
CREATE INDEX IF NOT EXISTS idx_conv_buyer ON conversations(buyer_id);
CREATE INDEX IF NOT EXISTS idx_conv_seller ON conversations(seller_id);
`)
	return err
}

type messageDTO struct {
	ID       string `json:"id"`
	SenderID string `json:"sender_id"`
	Content  string `json:"content"`
	IsRead   bool   `json:"is_read"`
	SentAt   string `json:"sent_at"`
}

func (r *ConversationRepository) Add(ctx context.Context, c *domain.Conversation) error {
	msgs, err := marshalMessages(c.Messages)
	if err != nil {
		return err
	}
	_, err = r.db.ExecContext(ctx, `
INSERT INTO conversations (id, buyer_id, seller_id, listing_id, status, messages_json, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
		c.ID.String(), c.BuyerID.String(), c.SellerID.String(), c.ListingID.String(),
		c.Status.String(), msgs, c.CreatedAt.Format(time.RFC3339Nano), c.UpdatedAt.Format(time.RFC3339Nano),
	)
	return err
}

func (r *ConversationRepository) GetByID(ctx context.Context, id valueobject.ConversationID) (*domain.Conversation, error) {
	row := r.db.QueryRowContext(ctx, `
SELECT id, buyer_id, seller_id, listing_id, status, messages_json, created_at, updated_at
FROM conversations WHERE id = ?`, id.String())
	return scanConversation(row)
}

func (r *ConversationRepository) Update(ctx context.Context, c *domain.Conversation) error {
	msgs, err := marshalMessages(c.Messages)
	if err != nil {
		return err
	}
	res, err := r.db.ExecContext(ctx, `
UPDATE conversations SET status = ?, messages_json = ?, updated_at = ? WHERE id = ?`,
		c.Status.String(), msgs, c.UpdatedAt.Format(time.RFC3339Nano), c.ID.String(),
	)
	if err != nil {
		return err
	}
	n, err := res.RowsAffected()
	if err != nil {
		return err
	}
	if n == 0 {
		return domain.ErrConversationNotFound
	}
	return nil
}

func (r *ConversationRepository) FindByBuyerAndListing(
	ctx context.Context,
	buyerID valueobject.UserID,
	listingID valueobject.ListingID,
) (*domain.Conversation, error) {
	row := r.db.QueryRowContext(ctx, `
SELECT id, buyer_id, seller_id, listing_id, status, messages_json, created_at, updated_at
FROM conversations WHERE buyer_id = ? AND listing_id = ? LIMIT 1`,
		buyerID.String(), listingID.String())
	c, err := scanConversation(row)
	if err == domain.ErrConversationNotFound {
		return nil, nil
	}
	return c, err
}

func (r *ConversationRepository) ListForUser(
	ctx context.Context,
	userID valueobject.UserID,
	limit, offset int,
) ([]*domain.Conversation, error) {
	rows, err := r.db.QueryContext(ctx, `
SELECT id, buyer_id, seller_id, listing_id, status, messages_json, created_at, updated_at
FROM conversations
WHERE buyer_id = ? OR seller_id = ?
ORDER BY updated_at DESC
LIMIT ? OFFSET ?`, userID.String(), userID.String(), limit, offset)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var result []*domain.Conversation
	for rows.Next() {
		c, err := scanConversationRows(rows)
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
		id, buyer, seller, listing, status, msgsJSON, createdAt, updatedAt string
	)
	if err := row.Scan(&id, &buyer, &seller, &listing, &status, &msgsJSON, &createdAt, &updatedAt); err != nil {
		if err == sql.ErrNoRows {
			return nil, domain.ErrConversationNotFound
		}
		return nil, err
	}
	return hydrate(id, buyer, seller, listing, status, msgsJSON, createdAt, updatedAt)
}

func scanConversationRows(rows *sql.Rows) (*domain.Conversation, error) {
	var (
		id, buyer, seller, listing, status, msgsJSON, createdAt, updatedAt string
	)
	if err := rows.Scan(&id, &buyer, &seller, &listing, &status, &msgsJSON, &createdAt, &updatedAt); err != nil {
		return nil, err
	}
	return hydrate(id, buyer, seller, listing, status, msgsJSON, createdAt, updatedAt)
}

func hydrate(
	id, buyer, seller, listing, status, msgsJSON, createdAt, updatedAt string,
) (*domain.Conversation, error) {
	cid, err := valueobject.NewConversationID(id)
	if err != nil {
		return nil, err
	}
	buyerID, err := valueobject.NewUserID(buyer)
	if err != nil {
		return nil, err
	}
	sellerID, err := valueobject.NewUserID(seller)
	if err != nil {
		return nil, err
	}
	listingID, err := valueobject.NewListingID(listing)
	if err != nil {
		return nil, err
	}
	st, err := valueobject.NewConversationStatus(status)
	if err != nil {
		return nil, err
	}
	messages, err := unmarshalMessages(cid, msgsJSON)
	if err != nil {
		return nil, err
	}
	ca, err := time.Parse(time.RFC3339Nano, createdAt)
	if err != nil {
		return nil, err
	}
	ua, err := time.Parse(time.RFC3339Nano, updatedAt)
	if err != nil {
		return nil, err
	}
	return domain.RehydrateConversation(cid, buyerID, sellerID, listingID, st, messages, ca, ua), nil
}

func marshalMessages(messages []domain.Message) (string, error) {
	dtos := make([]messageDTO, 0, len(messages))
	for _, m := range messages {
		dtos = append(dtos, messageDTO{
			ID:       m.ID.String(),
			SenderID: m.SenderID.String(),
			Content:  m.Content.String(),
			IsRead:   m.IsRead,
			SentAt:   m.SentAt.Format(time.RFC3339Nano),
		})
	}
	b, err := json.Marshal(dtos)
	if err != nil {
		return "", err
	}
	return string(b), nil
}

func unmarshalMessages(conversationID valueobject.ConversationID, raw string) ([]domain.Message, error) {
	var dtos []messageDTO
	if err := json.Unmarshal([]byte(raw), &dtos); err != nil {
		return nil, fmt.Errorf("messages json: %w", err)
	}
	messages := make([]domain.Message, 0, len(dtos))
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
			return nil, err
		}
		messages = append(messages, domain.Message{
			ID:             mid,
			ConversationID: conversationID,
			SenderID:       sid,
			Content:        content,
			IsRead:         d.IsRead,
			SentAt:         sentAt,
		})
	}
	return messages, nil
}

// UnitOfWork provides transactional boundaries on SQLite.
type UnitOfWork struct {
	tx   *sql.Tx
	repo *txConversationRepository
}

func (u *UnitOfWork) Conversations() port.ConversationRepository { return u.repo }

func (u *UnitOfWork) Commit(context.Context) error {
	return u.tx.Commit()
}

func (u *UnitOfWork) Rollback(context.Context) error {
	return u.tx.Rollback()
}

type UnitOfWorkFactory struct {
	db *sql.DB
}

func NewUnitOfWorkFactory(db *sql.DB) *UnitOfWorkFactory {
	return &UnitOfWorkFactory{db: db}
}

func (f *UnitOfWorkFactory) New(ctx context.Context) (port.UnitOfWork, error) {
	tx, err := f.db.BeginTx(ctx, nil)
	if err != nil {
		return nil, err
	}
	return &UnitOfWork{
		tx:   tx,
		repo: &txConversationRepository{tx: tx},
	}, nil
}

// txConversationRepository mirrors ConversationRepository against a transaction.
type txConversationRepository struct {
	tx *sql.Tx
}

func (r *txConversationRepository) Add(ctx context.Context, c *domain.Conversation) error {
	msgs, err := marshalMessages(c.Messages)
	if err != nil {
		return err
	}
	_, err = r.tx.ExecContext(ctx, `
INSERT INTO conversations (id, buyer_id, seller_id, listing_id, status, messages_json, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
		c.ID.String(), c.BuyerID.String(), c.SellerID.String(), c.ListingID.String(),
		c.Status.String(), msgs, c.CreatedAt.Format(time.RFC3339Nano), c.UpdatedAt.Format(time.RFC3339Nano),
	)
	return err
}

func (r *txConversationRepository) GetByID(ctx context.Context, id valueobject.ConversationID) (*domain.Conversation, error) {
	row := r.tx.QueryRowContext(ctx, `
SELECT id, buyer_id, seller_id, listing_id, status, messages_json, created_at, updated_at
FROM conversations WHERE id = ?`, id.String())
	return scanConversation(row)
}

func (r *txConversationRepository) Update(ctx context.Context, c *domain.Conversation) error {
	msgs, err := marshalMessages(c.Messages)
	if err != nil {
		return err
	}
	res, err := r.tx.ExecContext(ctx, `
UPDATE conversations SET status = ?, messages_json = ?, updated_at = ? WHERE id = ?`,
		c.Status.String(), msgs, c.UpdatedAt.Format(time.RFC3339Nano), c.ID.String(),
	)
	if err != nil {
		return err
	}
	n, err := res.RowsAffected()
	if err != nil {
		return err
	}
	if n == 0 {
		return domain.ErrConversationNotFound
	}
	return nil
}

func (r *txConversationRepository) FindByBuyerAndListing(
	ctx context.Context,
	buyerID valueobject.UserID,
	listingID valueobject.ListingID,
) (*domain.Conversation, error) {
	row := r.tx.QueryRowContext(ctx, `
SELECT id, buyer_id, seller_id, listing_id, status, messages_json, created_at, updated_at
FROM conversations WHERE buyer_id = ? AND listing_id = ? LIMIT 1`,
		buyerID.String(), listingID.String())
	c, err := scanConversation(row)
	if err == domain.ErrConversationNotFound {
		return nil, nil
	}
	return c, err
}

func (r *txConversationRepository) ListForUser(
	ctx context.Context,
	userID valueobject.UserID,
	limit, offset int,
) ([]*domain.Conversation, error) {
	rows, err := r.tx.QueryContext(ctx, `
SELECT id, buyer_id, seller_id, listing_id, status, messages_json, created_at, updated_at
FROM conversations
WHERE buyer_id = ? OR seller_id = ?
ORDER BY updated_at DESC
LIMIT ? OFFSET ?`, userID.String(), userID.String(), limit, offset)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var result []*domain.Conversation
	for rows.Next() {
		c, err := scanConversationRows(rows)
		if err != nil {
			return nil, err
		}
		result = append(result, c)
	}
	return result, rows.Err()
}
