package postgres

import (
	"context"
	"database/sql"
	"errors"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/persistence/postgres/models"
)

type MessageRepository struct {
	db DBTX
}

func NewMessageRepository(db DBTX) *MessageRepository {
	return &MessageRepository{db: db}
}

func (r *MessageRepository) Add(ctx context.Context, message *entities.Message) error {
	row := messageToRow(message)
	_, err := r.db.ExecContext(ctx, `
		INSERT INTO messages (
			id, conversation_id, sender_id, content, sent_at,
			client_message_id, deleted_for_everyone, deleted_at
		) VALUES ($1,$2,$3,$4,$5,$6,$7,$8)`,
		row.ID, row.ConversationID, row.SenderID, row.Content, row.SentAt,
		row.ClientMessageID, row.DeletedForEveryone, row.DeletedAt,
	)
	return translateDBError("MessageRepository.Add", err)
}

func (r *MessageRepository) Update(ctx context.Context, message *entities.Message) error {
	row := messageToRow(message)
	res, err := r.db.ExecContext(ctx, `
		UPDATE messages SET
			content = $2,
			deleted_for_everyone = $3,
			deleted_at = $4
		WHERE id = $1`,
		row.ID, row.Content, row.DeletedForEveryone, row.DeletedAt,
	)
	if err != nil {
		return translateDBError("MessageRepository.Update", err)
	}
	n, err := res.RowsAffected()
	if err != nil {
		return translateDBError("MessageRepository.Update", err)
	}
	if n == 0 {
		return &domainerrors.NotFoundError{
			Field:   "message_id",
			Message: "message " + row.ID + " not found",
		}
	}
	return nil
}

func (r *MessageRepository) GetByID(ctx context.Context, id valueobjects.MessageID) (*entities.Message, error) {
	row, err := r.scanMessage(r.db.QueryRowContext(ctx, `
		SELECT id, conversation_id, sender_id, content, sent_at,
		       client_message_id, deleted_for_everyone, deleted_at
		FROM messages WHERE id = $1`, id.String()))
	if errors.Is(err, sql.ErrNoRows) {
		return nil, &domainerrors.NotFoundError{
			Field:   "message_id",
			Message: "message " + id.String() + " not found",
		}
	}
	if err != nil {
		return nil, translateDBError("MessageRepository.GetByID", err)
	}
	return messageFromRow(row)
}

func (r *MessageRepository) FindByClientMessageID(
	ctx context.Context,
	senderID valueobjects.UserID,
	conversationID valueobjects.ConversationID,
	clientMessageID string,
) (*entities.Message, error) {
	row, err := r.scanMessage(r.db.QueryRowContext(ctx, `
		SELECT id, conversation_id, sender_id, content, sent_at,
		       client_message_id, deleted_for_everyone, deleted_at
		FROM messages
		WHERE sender_id = $1 AND conversation_id = $2 AND client_message_id = $3`,
		senderID.String(), conversationID.String(), clientMessageID))
	if errors.Is(err, sql.ErrNoRows) {
		return nil, nil
	}
	if err != nil {
		return nil, translateDBError("MessageRepository.FindByClientMessageID", err)
	}
	return messageFromRow(row)
}

func (r *MessageRepository) FindLatestVisible(
	ctx context.Context,
	conversationID valueobjects.ConversationID,
) (*entities.Message, error) {
	row, err := r.scanMessage(r.db.QueryRowContext(ctx, `
		SELECT id, conversation_id, sender_id, content, sent_at,
		       client_message_id, deleted_for_everyone, deleted_at
		FROM messages
		WHERE conversation_id = $1 AND deleted_for_everyone = FALSE
		ORDER BY sent_at DESC, id DESC
		LIMIT 1`, conversationID.String()))
	if errors.Is(err, sql.ErrNoRows) {
		return nil, nil
	}
	if err != nil {
		return nil, translateDBError("MessageRepository.FindLatestVisible", err)
	}
	return messageFromRow(row)
}

func (r *MessageRepository) ListMessages(
	ctx context.Context,
	conversationID valueobjects.ConversationID,
	cursor *ports.MessageCursor,
	direction ports.Direction,
	limit int,
) ([]*entities.Message, error) {
	var (
		rows *sql.Rows
		err  error
	)

	switch direction {
	case ports.DirectionNewer:
		if cursor == nil {
			return nil, &domainerrors.ValidationError{
				Field:   "cursor",
				Message: "cursor is required for direction newer",
			}
		}
		rows, err = r.db.QueryContext(ctx, `
			SELECT id, conversation_id, sender_id, content, sent_at,
			       client_message_id, deleted_for_everyone, deleted_at
			FROM messages
			WHERE conversation_id = $1
			  AND deleted_for_everyone = FALSE
			  AND (sent_at > $2 OR (sent_at = $2 AND id > $3::uuid))
			ORDER BY sent_at ASC, id ASC
			LIMIT $4`,
			conversationID.String(), cursor.SentAt.UTC(), cursor.ID.String(), limit,
		)
	default: // DirectionOlder
		if cursor == nil {
			rows, err = r.db.QueryContext(ctx, `
				SELECT id, conversation_id, sender_id, content, sent_at,
				       client_message_id, deleted_for_everyone, deleted_at
				FROM messages
				WHERE conversation_id = $1 AND deleted_for_everyone = FALSE
				ORDER BY sent_at DESC, id DESC
				LIMIT $2`,
				conversationID.String(), limit,
			)
		} else {
			rows, err = r.db.QueryContext(ctx, `
				SELECT id, conversation_id, sender_id, content, sent_at,
				       client_message_id, deleted_for_everyone, deleted_at
				FROM messages
				WHERE conversation_id = $1
				  AND deleted_for_everyone = FALSE
				  AND (sent_at < $2 OR (sent_at = $2 AND id < $3::uuid))
				ORDER BY sent_at DESC, id DESC
				LIMIT $4`,
				conversationID.String(), cursor.SentAt.UTC(), cursor.ID.String(), limit,
			)
		}
	}
	if err != nil {
		return nil, translateDBError("MessageRepository.ListMessages", err)
	}
	defer rows.Close()

	out := make([]*entities.Message, 0)
	for rows.Next() {
		row, err := r.scanMessageRows(rows)
		if err != nil {
			return nil, translateDBError("MessageRepository.ListMessages", err)
		}
		m, err := messageFromRow(row)
		if err != nil {
			return nil, err
		}
		out = append(out, m)
	}
	if err := rows.Err(); err != nil {
		return nil, translateDBError("MessageRepository.ListMessages", err)
	}
	return out, nil
}

func (r *MessageRepository) scanMessage(row *sql.Row) (models.MessageRow, error) {
	var m models.MessageRow
	err := row.Scan(
		&m.ID, &m.ConversationID, &m.SenderID, &m.Content, &m.SentAt,
		&m.ClientMessageID, &m.DeletedForEveryone, &m.DeletedAt,
	)
	return m, err
}

func (r *MessageRepository) scanMessageRows(rows *sql.Rows) (models.MessageRow, error) {
	var m models.MessageRow
	err := rows.Scan(
		&m.ID, &m.ConversationID, &m.SenderID, &m.Content, &m.SentAt,
		&m.ClientMessageID, &m.DeletedForEveryone, &m.DeletedAt,
	)
	return m, err
}
