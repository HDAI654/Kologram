package postgres

import (
	"context"
	"database/sql"
	"errors"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/persistence/postgres/models"
)

type ConversationUserStateRepository struct {
	db DBTX
}

func NewConversationUserStateRepository(db DBTX) *ConversationUserStateRepository {
	return &ConversationUserStateRepository{db: db}
}

func (r *ConversationUserStateRepository) Add(ctx context.Context, state *entities.ConversationUserState) error {
	row := stateToRow(state)
	_, err := r.db.ExecContext(ctx, `
		INSERT INTO conversation_user_states (
			conversation_id, user_id, last_read_message_id, unread_count,
			is_archived, is_hidden, is_pinned, muted_until, updated_at
		) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)`,
		row.ConversationID, row.UserID, row.LastReadMessageID, row.UnreadCount,
		row.IsArchived, row.IsHidden, row.IsPinned, row.MutedUntil, row.UpdatedAt,
	)
	return translateDBError("ConversationUserStateRepository.Add", err)
}

// Update persists state. LastReadMessageID is not allowed to move backward in time
// (compared via messages.sent_at). Other fields always update.
func (r *ConversationUserStateRepository) Update(ctx context.Context, state *entities.ConversationUserState) error {
	row := stateToRow(state)
	res, err := r.db.ExecContext(ctx, `
		UPDATE conversation_user_states cus SET
			last_read_message_id = CASE
				WHEN $3::uuid IS NULL THEN cus.last_read_message_id
				WHEN cus.last_read_message_id IS NULL THEN $3::uuid
				WHEN EXISTS (
					SELECT 1
					FROM messages new_msg
					LEFT JOIN messages old_msg ON old_msg.id = cus.last_read_message_id
					WHERE new_msg.id = $3::uuid
					  AND (old_msg.id IS NULL OR new_msg.sent_at >= old_msg.sent_at)
				) THEN $3::uuid
				ELSE cus.last_read_message_id
			END,
			unread_count = $4,
			is_archived = $5,
			is_hidden = $6,
			is_pinned = $7,
			muted_until = $8,
			updated_at = $9
		WHERE conversation_id = $1 AND user_id = $2`,
		row.ConversationID, row.UserID, row.LastReadMessageID, row.UnreadCount,
		row.IsArchived, row.IsHidden, row.IsPinned, row.MutedUntil, row.UpdatedAt,
	)
	if err != nil {
		return translateDBError("ConversationUserStateRepository.Update", err)
	}
	n, err := res.RowsAffected()
	if err != nil {
		return translateDBError("ConversationUserStateRepository.Update", err)
	}
	if n == 0 {
		return &domainerrors.NotFoundError{
			Field:   "conversation_user_state",
			Message: "state for user in conversation not found",
		}
	}
	return nil
}

func (r *ConversationUserStateRepository) Get(
	ctx context.Context,
	conversationID valueobjects.ConversationID,
	userID valueobjects.UserID,
) (*entities.ConversationUserState, error) {
	row, err := r.scanState(r.db.QueryRowContext(ctx, `
		SELECT conversation_id, user_id, last_read_message_id, unread_count,
		       is_archived, is_hidden, is_pinned, muted_until, updated_at
		FROM conversation_user_states
		WHERE conversation_id = $1 AND user_id = $2`,
		conversationID.String(), userID.String()))
	if errors.Is(err, sql.ErrNoRows) {
		return nil, &domainerrors.NotFoundError{
			Field:   "conversation_user_state",
			Message: "state for user in conversation not found",
		}
	}
	if err != nil {
		return nil, translateDBError("ConversationUserStateRepository.Get", err)
	}
	return stateFromRow(row)
}

func (r *ConversationUserStateRepository) ListForConversation(
	ctx context.Context,
	conversationID valueobjects.ConversationID,
) ([]*entities.ConversationUserState, error) {
	rows, err := r.db.QueryContext(ctx, `
		SELECT conversation_id, user_id, last_read_message_id, unread_count,
		       is_archived, is_hidden, is_pinned, muted_until, updated_at
		FROM conversation_user_states
		WHERE conversation_id = $1`, conversationID.String())
	if err != nil {
		return nil, translateDBError("ConversationUserStateRepository.ListForConversation", err)
	}
	defer rows.Close()

	out := make([]*entities.ConversationUserState, 0)
	for rows.Next() {
		row, err := r.scanStateRows(rows)
		if err != nil {
			return nil, translateDBError("ConversationUserStateRepository.ListForConversation", err)
		}
		s, err := stateFromRow(row)
		if err != nil {
			return nil, err
		}
		out = append(out, s)
	}
	if err := rows.Err(); err != nil {
		return nil, translateDBError("ConversationUserStateRepository.ListForConversation", err)
	}
	return out, nil
}

func (r *ConversationUserStateRepository) scanState(row *sql.Row) (models.ConversationUserStateRow, error) {
	var m models.ConversationUserStateRow
	err := row.Scan(
		&m.ConversationID, &m.UserID, &m.LastReadMessageID, &m.UnreadCount,
		&m.IsArchived, &m.IsHidden, &m.IsPinned, &m.MutedUntil, &m.UpdatedAt,
	)
	return m, err
}

func (r *ConversationUserStateRepository) scanStateRows(rows *sql.Rows) (models.ConversationUserStateRow, error) {
	var m models.ConversationUserStateRow
	err := rows.Scan(
		&m.ConversationID, &m.UserID, &m.LastReadMessageID, &m.UnreadCount,
		&m.IsArchived, &m.IsHidden, &m.IsPinned, &m.MutedUntil, &m.UpdatedAt,
	)
	return m, err
}
