package application

import (
	"context"
	"log/slog"
	"time"

	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/events"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

type SendMessageCommand struct {
	ConversationID  string
	SenderID        string
	ClientMessageID string
	Content         string
}

type SendMessageResult struct {
	MessageID      string
	ConversationID string
	SentAt         string
	IdempotentHit  bool
}

type SendMessageHandler struct {
	uowFactory ports.UnitOfWorkFactory
	events     ports.EventPublisher
	realtime   ports.RealtimeNotifier
	log        *slog.Logger
}

func NewSendMessageHandler(
	uowFactory ports.UnitOfWorkFactory,
	events ports.EventPublisher,
	realtime ports.RealtimeNotifier,
	log *slog.Logger,
) *SendMessageHandler {
	return &SendMessageHandler{
		uowFactory: uowFactory,
		events:     events,
		realtime:   realtime,
		log:        loggerOrDefault(log),
	}
}

func (h *SendMessageHandler) Handle(
	ctx context.Context,
	cmd SendMessageCommand,
) (SendMessageResult, error) {
	conversationID, err := valueobjects.NewConversationID(cmd.ConversationID)
	if err != nil {
		return SendMessageResult{}, err
	}
	senderID, err := valueobjects.NewUserID(cmd.SenderID)
	if err != nil {
		return SendMessageResult{}, err
	}
	if err := valueobjects.ValidateClientMessageID(cmd.ClientMessageID); err != nil {
		return SendMessageResult{}, err
	}
	content, err := valueobjects.NewMessageContent(cmd.Content)
	if err != nil {
		return SendMessageResult{}, err
	}

	uow, err := h.uowFactory.New(ctx)
	if err != nil {
		return SendMessageResult{}, err
	}
	defer func() { _ = uow.Rollback(ctx) }()

	conv, err := loadConversationForParticipant(ctx, uow, conversationID, senderID)
	if err != nil {
		return SendMessageResult{}, err
	}

	counterpartID, ok := conv.CounterpartID(senderID)
	if !ok {
		return SendMessageResult{}, domainerrors.ErrNotParticipant
	}

	blocked, err := uow.UserBlocks().IsBlockedEitherWay(ctx, senderID, counterpartID)
	if err != nil {
		return SendMessageResult{}, err
	}
	if blocked {
		return SendMessageResult{}, domainerrors.ErrUsersBlocked
	}

	existing, err := uow.Messages().FindByClientMessageID(
		ctx, senderID, conversationID, cmd.ClientMessageID,
	)
	if err != nil {
		return SendMessageResult{}, err
	}
	if existing != nil {
		return SendMessageResult{
			MessageID:      existing.ID.String(),
			ConversationID: existing.ConversationID.String(),
			SentAt:         existing.SentAt.Format(time.RFC3339),
			IdempotentHit:  true,
		}, nil
	}

	msg, err := conv.AddMessage(senderID, cmd.ClientMessageID, content)
	if err != nil {
		return SendMessageResult{}, err
	}

	if err := uow.Messages().Add(ctx, &msg); err != nil {
		return SendMessageResult{}, err
	}

	conv.RecordLastMessage(msg)
	if err := uow.Conversations().Update(ctx, conv); err != nil {
		return SendMessageResult{}, err
	}

	states, err := uow.ConversationStates().ListForConversation(ctx, conversationID)
	if err != nil {
		return SendMessageResult{}, err
	}
	now := msg.SentAt
	var recipientMuted bool
	for _, state := range states {
		if state.UserID.Equals(senderID) {
			continue
		}
		state.RecordIncomingMessage(now)
		if state.IsHidden {
			state.Unhide(now)
		}
		recipientMuted = state.IsMuted(now)
		if err := uow.ConversationStates().Update(ctx, state); err != nil {
			return SendMessageResult{}, err
		}
	}

	if err := uow.Commit(ctx); err != nil {
		return SendMessageResult{}, err
	}

	// Best-effort post-commit side effects (not transactional with the write).
	if h.events != nil {
		_ = h.events.Publish(ctx, events.MessageSent{
			ConversationID: conversationID.String(),
			MessageID:      msg.ID.String(),
			SenderID:       senderID.String(),
			RecipientID:    counterpartID.String(),
			At:             msg.SentAt,
		})
	}

	if h.realtime != nil && !recipientMuted {
		_ = h.realtime.NotifyUser(ctx, counterpartID.String(), map[string]any{
			"type":            "message_sent",
			"conversation_id": conversationID.String(),
			"message_id":      msg.ID.String(),
			"sender_id":       senderID.String(),
		})
	}

	h.log.Info("message sent",
		"conversation_id", conversationID.String(),
		"message_id", msg.ID.String(),
		"sender_id", senderID.String(),
	)

	return SendMessageResult{
		MessageID:      msg.ID.String(),
		ConversationID: conversationID.String(),
		SentAt:         msg.SentAt.Format(time.RFC3339),
		IdempotentHit:  false,
	}, nil
}
