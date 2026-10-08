package application

import (
	"context"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

func loadConversationForParticipant(
	ctx context.Context,
	uow ports.UnitOfWork,
	conversationID valueobjects.ConversationID,
	userID valueobjects.UserID,
) (*entities.Conversation, error) {
	conv, err := uow.Conversations().GetByID(ctx, conversationID)
	if err != nil {
		return nil, err
	}
	if conv == nil {
		return nil, &domainerrors.NotFoundError{
			Field:   "conversation_id",
			Message: "conversation " + conversationID.String() + " not found",
		}
	}
	if !conv.IsParticipant(userID) {
		return nil, domainerrors.ErrNotParticipant
	}
	return conv, nil
}

func loadUserState(
	ctx context.Context,
	uow ports.UnitOfWork,
	conversationID valueobjects.ConversationID,
	userID valueobjects.UserID,
) (*entities.ConversationUserState, error) {
	state, err := uow.ConversationStates().Get(ctx, conversationID, userID)
	if err != nil {
		return nil, err
	}
	if state == nil {
		return nil, &domainerrors.NotFoundError{
			Field:   "conversation_user_state",
			Message: "state for user in conversation not found",
		}
	}
	return state, nil
}
