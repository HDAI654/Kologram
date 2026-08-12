package application

import (
	"context"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/event"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/port"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

type SendMessageCommand struct {
	ConversationID string
	SenderID       string
	Content        string
}

type SendMessageResult struct {
	MessageID      string `json:"message_id"`
	ConversationID string `json:"conversation_id"`
	SentAt         string `json:"sent_at"`
}

type SendMessageHandler struct {
	uowFactory port.UnitOfWorkFactory
	events     port.EventPublisher
	realtime   port.RealtimeNotifier
}

func NewSendMessageHandler(
	uowFactory port.UnitOfWorkFactory,
	events port.EventPublisher,
	realtime port.RealtimeNotifier,
) *SendMessageHandler {
	return &SendMessageHandler{
		uowFactory: uowFactory,
		events:     events,
		realtime:   realtime,
	}
}

func (h *SendMessageHandler) Handle(
	ctx context.Context,
	cmd SendMessageCommand,
) (SendMessageResult, error) {
	conversationID, err := valueobject.NewConversationID(cmd.ConversationID)
	if err != nil {
		return SendMessageResult{}, err
	}
	senderID, err := valueobject.NewUserID(cmd.SenderID)
	if err != nil {
		return SendMessageResult{}, err
	}
	content, err := valueobject.NewMessageContent(cmd.Content)
	if err != nil {
		return SendMessageResult{}, err
	}

	uow, err := h.uowFactory.New(ctx)
	if err != nil {
		return SendMessageResult{}, err
	}
	defer func() { _ = uow.Rollback(ctx) }()

	conversation, err := uow.Conversations().GetByID(ctx, conversationID)
	if err != nil {
		return SendMessageResult{}, err
	}

	msg, err := conversation.AddMessage(senderID, content)
	if err != nil {
		return SendMessageResult{}, err
	}

	if err := uow.Conversations().Update(ctx, conversation); err != nil {
		return SendMessageResult{}, err
	}
	if err := uow.Commit(ctx); err != nil {
		return SendMessageResult{}, err
	}

	payload := map[string]any{
		"type":            "message.sent",
		"conversation_id": conversation.ID.String(),
		"message_id":      msg.ID.String(),
		"sender_id":       msg.SenderID.String(),
		"content":         msg.Content.String(),
		"sent_at":         msg.SentAt.Format(time.RFC3339),
	}

	if h.realtime != nil {
		recipient := conversation.SellerID
		if senderID.Equals(conversation.SellerID) {
			recipient = conversation.BuyerID
		}
		_ = h.realtime.NotifyUser(ctx, recipient.String(), payload)
		_ = h.realtime.NotifyUser(ctx, senderID.String(), payload)
	}

	if h.events != nil {
		_ = h.events.Publish(ctx, event.MessageSent{
			ConversationID: conversation.ID.String(),
			MessageID:      msg.ID.String(),
			SenderID:       msg.SenderID.String(),
			Content:        msg.Content.String(),
			At:             msg.SentAt,
		})
	}

	return SendMessageResult{
		MessageID:      msg.ID.String(),
		ConversationID: conversation.ID.String(),
		SentAt:         msg.SentAt.Format(time.RFC3339),
	}, nil
}
