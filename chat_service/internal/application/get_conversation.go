package application

import (
	"context"
	"time"

	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

type GetConversationQuery struct {
	ConversationID string
	RequesterID    string
}

type GetConversationResult struct {
	ConversationID     string
	BuyerID            string
	SellerID           string
	ListingID          string
	IsReadOnly         bool
	LastMessagePreview string
	LastMessageAt      string
	UnreadCount        int
	IsArchived         bool
	IsHidden           bool
	IsPinned           bool
	IsMuted            bool
}

type GetConversationHandler struct {
	conversations ports.ConversationRepository
	states        ports.ConversationUserStateRepository
}

func NewGetConversationHandler(
	conversations ports.ConversationRepository,
	states ports.ConversationUserStateRepository,
) *GetConversationHandler {
	return &GetConversationHandler{
		conversations: conversations,
		states:        states,
	}
}

func (h *GetConversationHandler) Handle(
	ctx context.Context,
	query GetConversationQuery,
) (GetConversationResult, error) {
	conversationID, err := valueobjects.NewConversationID(query.ConversationID)
	if err != nil {
		return GetConversationResult{}, err
	}
	requesterID, err := valueobjects.NewUserID(query.RequesterID)
	if err != nil {
		return GetConversationResult{}, err
	}

	conv, err := h.conversations.GetByID(ctx, conversationID)
	if err != nil {
		return GetConversationResult{}, err
	}
	if conv == nil {
		return GetConversationResult{}, &domainerrors.NotFoundError{
			Field:   "conversation_id",
			Message: "conversation " + conversationID.String() + " not found",
		}
	}
	if !conv.IsParticipant(requesterID) {
		return GetConversationResult{}, domainerrors.ErrNotParticipant
	}

	state, err := h.states.Get(ctx, conversationID, requesterID)
	if err != nil {
		return GetConversationResult{}, err
	}
	if state == nil {
		return GetConversationResult{}, &domainerrors.NotFoundError{
			Field:   "conversation_user_state",
			Message: "state for user in conversation not found",
		}
	}

	now := time.Now().UTC()
	return GetConversationResult{
		ConversationID:     conv.ID.String(),
		BuyerID:            conv.BuyerID.String(),
		SellerID:           conv.SellerID.String(),
		ListingID:          conv.ListingID.String(),
		IsReadOnly:         conv.IsReadOnly,
		LastMessagePreview: conv.LastMessagePreview,
		LastMessageAt:      conv.LastMessageAt.Format(time.RFC3339),
		UnreadCount:        state.UnreadCount,
		IsArchived:         state.IsArchived,
		IsHidden:           state.IsHidden,
		IsPinned:           state.IsPinned,
		IsMuted:            state.IsMuted(now),
	}, nil
}
