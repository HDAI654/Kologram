package postgres

import (
	"context"
	"database/sql"
	"errors"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/persistence/postgres/models"
)

type ConversationRepository struct {
	db DBTX
}

func NewConversationRepository(db DBTX) *ConversationRepository {
	return &ConversationRepository{db: db}
}

func (r *ConversationRepository) Add(ctx context.Context, conversation *entities.Conversation) error {
	row := conversationToRow(conversation)
	_, err := r.db.ExecContext(ctx, `
		INSERT INTO conversations (
			id, buyer_id, seller_id, listing_id, is_read_only,
			last_message_id, last_message_preview, last_message_at,
			created_at, updated_at
		) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)`,
		row.ID, row.BuyerID, row.SellerID, row.ListingID, row.IsReadOnly,
		row.LastMessageID, row.LastMessagePreview, row.LastMessageAt,
		row.CreatedAt, row.UpdatedAt,
	)
	return translateDBError("ConversationRepository.Add", err)
}

func (r *ConversationRepository) Update(ctx context.Context, conversation *entities.Conversation) error {
	row := conversationToRow(conversation)
	res, err := r.db.ExecContext(ctx, `
		UPDATE conversations SET
			is_read_only = $2,
			last_message_id = $3,
			last_message_preview = $4,
			last_message_at = $5,
			updated_at = $6
		WHERE id = $1`,
		row.ID, row.IsReadOnly, row.LastMessageID, row.LastMessagePreview,
		row.LastMessageAt, row.UpdatedAt,
	)
	if err != nil {
		return translateDBError("ConversationRepository.Update", err)
	}
	n, err := res.RowsAffected()
	if err != nil {
		return translateDBError("ConversationRepository.Update", err)
	}
	if n == 0 {
		return &domainerrors.NotFoundError{
			Field:   "conversation_id",
			Message: "conversation " + row.ID + " not found",
		}
	}
	return nil
}

func (r *ConversationRepository) GetByID(ctx context.Context, id valueobjects.ConversationID) (*entities.Conversation, error) {
	row, err := r.scanConversation(r.db.QueryRowContext(ctx, `
		SELECT id, buyer_id, seller_id, listing_id, is_read_only,
		       last_message_id, last_message_preview, last_message_at,
		       created_at, updated_at
		FROM conversations WHERE id = $1`, id.String()))
	if errors.Is(err, sql.ErrNoRows) {
		return nil, &domainerrors.NotFoundError{
			Field:   "conversation_id",
			Message: "conversation " + id.String() + " not found",
		}
	}
	if err != nil {
		return nil, translateDBError("ConversationRepository.GetByID", err)
	}
	return conversationFromRow(row)
}

func (r *ConversationRepository) FindByBuyerAndListing(
	ctx context.Context,
	buyerID valueobjects.UserID,
	listingID valueobjects.ListingID,
) (*entities.Conversation, error) {
	row, err := r.scanConversation(r.db.QueryRowContext(ctx, `
		SELECT id, buyer_id, seller_id, listing_id, is_read_only,
		       last_message_id, last_message_preview, last_message_at,
		       created_at, updated_at
		FROM conversations
		WHERE buyer_id = $1 AND listing_id = $2`,
		buyerID.String(), listingID.String()))
	if errors.Is(err, sql.ErrNoRows) {
		return nil, nil
	}
	if err != nil {
		return nil, translateDBError("ConversationRepository.FindByBuyerAndListing", err)
	}
	return conversationFromRow(row)
}

func (r *ConversationRepository) ListByListingID(
	ctx context.Context,
	listingID valueobjects.ListingID,
) ([]*entities.Conversation, error) {
	rows, err := r.db.QueryContext(ctx, `
		SELECT id, buyer_id, seller_id, listing_id, is_read_only,
		       last_message_id, last_message_preview, last_message_at,
		       created_at, updated_at
		FROM conversations WHERE listing_id = $1`, listingID.String())
	if err != nil {
		return nil, translateDBError("ConversationRepository.ListByListingID", err)
	}
	defer rows.Close()

	out := make([]*entities.Conversation, 0)
	for rows.Next() {
		row, err := r.scanConversationRows(rows)
		if err != nil {
			return nil, translateDBError("ConversationRepository.ListByListingID", err)
		}
		c, err := conversationFromRow(row)
		if err != nil {
			return nil, err
		}
		out = append(out, c)
	}
	if err := rows.Err(); err != nil {
		return nil, translateDBError("ConversationRepository.ListByListingID", err)
	}
	return out, nil
}

func (r *ConversationRepository) ListForUser(
	ctx context.Context,
	userID valueobjects.UserID,
	filter ports.ConversationListFilter,
	cursor *ports.ConversationListCursor,
	limit int,
) ([]ports.ConversationListItem, error) {
	archived := filter == ports.ListFilterArchived

	args := []any{userID.String(), archived, limit}
	query := `
		SELECT c.id, c.buyer_id, c.seller_id, c.listing_id, c.is_read_only,
		       c.last_message_preview, c.last_message_at, c.created_at, c.updated_at,
		       s.unread_count, s.is_archived, s.is_pinned, s.muted_until
		FROM conversations c
		INNER JOIN conversation_user_states s
			ON s.conversation_id = c.id AND s.user_id = $1
		WHERE s.is_hidden = FALSE
		  AND s.is_archived = $2`

	if cursor != nil {
		args = append(args, cursor.IsPinned, cursor.LastMessageAt.UTC(), cursor.ID.String())
		query += `
		  AND (
		    s.is_pinned < $4
		    OR (s.is_pinned = $4 AND c.last_message_at < $5)
		    OR (s.is_pinned = $4 AND c.last_message_at = $5 AND c.id < $6::uuid)
		  )`
	}

	query += `
		ORDER BY s.is_pinned DESC, c.last_message_at DESC, c.id DESC
		LIMIT $3`

	rows, err := r.db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, translateDBError("ConversationRepository.ListForUser", err)
	}
	defer rows.Close()

	now := time.Now().UTC()
	out := make([]ports.ConversationListItem, 0)
	for rows.Next() {
		var row models.ConversationListRow
		if err := rows.Scan(
			&row.ConversationID, &row.BuyerID, &row.SellerID, &row.ListingID, &row.IsReadOnly,
			&row.LastMessagePreview, &row.LastMessageAt, &row.CreatedAt, &row.UpdatedAt,
			&row.UnreadCount, &row.IsArchived, &row.IsPinned, &row.MutedUntil,
		); err != nil {
			return nil, translateDBError("ConversationRepository.ListForUser", err)
		}
		item, err := conversationListItemFromRow(row, now)
		if err != nil {
			return nil, err
		}
		out = append(out, item)
	}
	if err := rows.Err(); err != nil {
		return nil, translateDBError("ConversationRepository.ListForUser", err)
	}
	return out, nil
}

func (r *ConversationRepository) scanConversation(row *sql.Row) (models.ConversationRow, error) {
	var m models.ConversationRow
	err := row.Scan(
		&m.ID, &m.BuyerID, &m.SellerID, &m.ListingID, &m.IsReadOnly,
		&m.LastMessageID, &m.LastMessagePreview, &m.LastMessageAt,
		&m.CreatedAt, &m.UpdatedAt,
	)
	return m, err
}

func (r *ConversationRepository) scanConversationRows(rows *sql.Rows) (models.ConversationRow, error) {
	var m models.ConversationRow
	err := rows.Scan(
		&m.ID, &m.BuyerID, &m.SellerID, &m.ListingID, &m.IsReadOnly,
		&m.LastMessageID, &m.LastMessagePreview, &m.LastMessageAt,
		&m.CreatedAt, &m.UpdatedAt,
	)
	return m, err
}
