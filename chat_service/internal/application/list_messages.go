package application

import (
	"context"
	"time"

	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

type ListMessagesQuery struct {
	ConversationID string
	RequesterID    string
	// CursorMessageID + CursorSentAt together form the page anchor; both empty = first page.
	CursorMessageID string
	CursorSentAt    string // RFC3339; required when CursorMessageID set
	Direction       string // "older" (default) | "newer"
	Limit           int
}

type MessageItem struct {
	MessageID       string
	SenderID        string
	Content         string
	ClientMessageID string
	SentAt          string
}

type ListMessagesResult struct {
	Items   []MessageItem
	HasMore bool
}

type ListMessagesHandler struct {
	conversations ports.ConversationRepository
	messages      ports.MessageRepository
}

func NewListMessagesHandler(
	conversations ports.ConversationRepository,
	messages ports.MessageRepository,
) *ListMessagesHandler {
	return &ListMessagesHandler{
		conversations: conversations,
		messages:      messages,
	}
}

func (h *ListMessagesHandler) Handle(
	ctx context.Context,
	query ListMessagesQuery,
) (ListMessagesResult, error) {
	conversationID, err := valueobjects.NewConversationID(query.ConversationID)
	if err != nil {
		return ListMessagesResult{}, err
	}
	requesterID, err := valueobjects.NewUserID(query.RequesterID)
	if err != nil {
		return ListMessagesResult{}, err
	}

	limit := query.Limit
	if limit <= 0 || limit > 100 {
		limit = 50
	}

	direction := ports.DirectionOlder
	switch query.Direction {
	case "", "older":
		direction = ports.DirectionOlder
	case "newer":
		direction = ports.DirectionNewer
	default:
		return ListMessagesResult{}, &domainerrors.ValidationError{
			Field:   "direction",
			Message: "must be older or newer",
		}
	}

	var cursor *ports.MessageCursor
	if query.CursorMessageID != "" {
		msgID, err := valueobjects.NewMessageID(query.CursorMessageID)
		if err != nil {
			return ListMessagesResult{}, err
		}
		sentAt, err := time.Parse(time.RFC3339, query.CursorSentAt)
		if err != nil {
			return ListMessagesResult{}, &domainerrors.ValidationError{
				Field:   "cursor_sent_at",
				Message: "must be RFC3339",
			}
		}
		cursor = &ports.MessageCursor{SentAt: sentAt.UTC(), ID: msgID}
	}

	conv, err := h.conversations.GetByID(ctx, conversationID)
	if err != nil {
		return ListMessagesResult{}, err
	}
	if conv == nil {
		return ListMessagesResult{}, &domainerrors.NotFoundError{
			Field:   "conversation_id",
			Message: "conversation " + conversationID.String() + " not found",
		}
	}
	if !conv.IsParticipant(requesterID) {
		return ListMessagesResult{}, domainerrors.ErrNotParticipant
	}

	messages, err := h.messages.ListMessages(ctx, conversationID, cursor, direction, limit+1)
	if err != nil {
		return ListMessagesResult{}, err
	}

	hasMore := len(messages) > limit
	if hasMore {
		messages = messages[:limit]
	}

	items := make([]MessageItem, 0, len(messages))
	for _, m := range messages {
		items = append(items, MessageItem{
			MessageID:       m.ID.String(),
			SenderID:        m.SenderID.String(),
			Content:         m.Content.String(),
			ClientMessageID: m.ClientMessageID,
			SentAt:          m.SentAt.Format(time.RFC3339),
		})
	}

	return ListMessagesResult{Items: items, HasMore: hasMore}, nil
}
