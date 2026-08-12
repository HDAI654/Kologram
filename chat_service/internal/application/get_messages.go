package application

import (
	"context"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/port"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

type GetMessagesQuery struct {
	ConversationID string
	RequesterID    string
}

type MessageItem struct {
	MessageID string `json:"message_id"`
	SenderID  string `json:"sender_id"`
	Content   string `json:"content"`
	IsRead    bool   `json:"is_read"`
	SentAt    string `json:"sent_at"`
}

type GetMessagesResult struct {
	ConversationID string        `json:"conversation_id"`
	Status         string        `json:"status"`
	Messages       []MessageItem `json:"messages"`
}

type GetMessagesHandler struct {
	uowFactory port.UnitOfWorkFactory
}

func NewGetMessagesHandler(uowFactory port.UnitOfWorkFactory) *GetMessagesHandler {
	return &GetMessagesHandler{uowFactory: uowFactory}
}

func (h *GetMessagesHandler) Handle(
	ctx context.Context,
	query GetMessagesQuery,
) (GetMessagesResult, error) {
	conversationID, err := valueobject.NewConversationID(query.ConversationID)
	if err != nil {
		return GetMessagesResult{}, err
	}
	requesterID, err := valueobject.NewUserID(query.RequesterID)
	if err != nil {
		return GetMessagesResult{}, err
	}

	uow, err := h.uowFactory.New(ctx)
	if err != nil {
		return GetMessagesResult{}, err
	}
	defer func() { _ = uow.Rollback(ctx) }()

	conversation, err := uow.Conversations().GetByID(ctx, conversationID)
	if err != nil {
		return GetMessagesResult{}, err
	}
	if !conversation.IsParticipant(requesterID) {
		return GetMessagesResult{}, domain.ErrNotParticipant
	}

	messages := make([]MessageItem, 0, len(conversation.Messages))
	for _, m := range conversation.Messages {
		messages = append(messages, MessageItem{
			MessageID: m.ID.String(),
			SenderID:  m.SenderID.String(),
			Content:   m.Content.String(),
			IsRead:    m.IsRead,
			SentAt:    m.SentAt.Format(time.RFC3339),
		})
	}

	return GetMessagesResult{
		ConversationID: conversation.ID.String(),
		Status:         conversation.Status.String(),
		Messages:       messages,
	}, nil
}
