package application

import (
	"context"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/port"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

type ListConversationsQuery struct {
	UserID string
	Limit  int
	Offset int
}

type ConversationItem struct {
	ConversationID string `json:"conversation_id"`
	BuyerID        string `json:"buyer_id"`
	SellerID       string `json:"seller_id"`
	ListingID      string `json:"listing_id"`
	Status         string `json:"status"`
	LastMessage    string `json:"last_message"`
	UpdatedAt      string `json:"updated_at"`
}

type ListConversationsResult struct {
	Items []ConversationItem `json:"items"`
}

type ListConversationsHandler struct {
	uowFactory port.UnitOfWorkFactory
}

func NewListConversationsHandler(uowFactory port.UnitOfWorkFactory) *ListConversationsHandler {
	return &ListConversationsHandler{uowFactory: uowFactory}
}

func (h *ListConversationsHandler) Handle(
	ctx context.Context,
	query ListConversationsQuery,
) (ListConversationsResult, error) {
	userID, err := valueobject.NewUserID(query.UserID)
	if err != nil {
		return ListConversationsResult{}, err
	}
	limit := query.Limit
	if limit <= 0 || limit > 100 {
		limit = 50
	}
	offset := query.Offset
	if offset < 0 {
		offset = 0
	}

	uow, err := h.uowFactory.New(ctx)
	if err != nil {
		return ListConversationsResult{}, err
	}
	defer func() { _ = uow.Rollback(ctx) }()

	conversations, err := uow.Conversations().ListForUser(ctx, userID, limit, offset)
	if err != nil {
		return ListConversationsResult{}, err
	}

	items := make([]ConversationItem, 0, len(conversations))
	for _, c := range conversations {
		last := ""
		if n := len(c.Messages); n > 0 {
			last = c.Messages[n-1].Content.String()
		}
		items = append(items, ConversationItem{
			ConversationID: c.ID.String(),
			BuyerID:        c.BuyerID.String(),
			SellerID:       c.SellerID.String(),
			ListingID:      c.ListingID.String(),
			Status:         c.Status.String(),
			LastMessage:    last,
			UpdatedAt:      c.UpdatedAt.Format(time.RFC3339),
		})
	}
	return ListConversationsResult{Items: items}, nil
}
