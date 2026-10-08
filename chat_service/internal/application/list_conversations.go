package application

import (
	"context"
	"time"

	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

type ListConversationsQuery struct {
	UserID string
	// Filter: "active" (default) | "archived"
	Filter string
	// Cursor fields; all empty = first page.
	CursorIsPinned      *bool
	CursorLastMessageAt string // RFC3339
	CursorID            string
	Limit               int
}

type ConversationListEntry struct {
	ConversationID     string
	BuyerID            string
	SellerID           string
	ListingID          string
	IsReadOnly         bool
	LastMessagePreview string
	LastMessageAt      string
	UnreadCount        int
	IsArchived         bool
	IsPinned           bool
	IsMuted            bool
}

type ListConversationsResult struct {
	Items   []ConversationListEntry
	HasMore bool
}

type ListConversationsHandler struct {
	conversations ports.ConversationRepository
}

func NewListConversationsHandler(conversations ports.ConversationRepository) *ListConversationsHandler {
	return &ListConversationsHandler{conversations: conversations}
}

func (h *ListConversationsHandler) Handle(
	ctx context.Context,
	query ListConversationsQuery,
) (ListConversationsResult, error) {
	userID, err := valueobjects.NewUserID(query.UserID)
	if err != nil {
		return ListConversationsResult{}, err
	}

	limit := query.Limit
	if limit <= 0 || limit > 100 {
		limit = 50
	}

	var filter ports.ConversationListFilter
	switch query.Filter {
	case "", "active":
		filter = ports.ListFilterActive
	case "archived":
		filter = ports.ListFilterArchived
	default:
		return ListConversationsResult{}, &domainerrors.ValidationError{
			Field:   "filter",
			Message: "must be active or archived",
		}
	}

	var cursor *ports.ConversationListCursor
	if query.CursorID != "" {
		id, err := valueobjects.NewConversationID(query.CursorID)
		if err != nil {
			return ListConversationsResult{}, err
		}
		lastAt, err := time.Parse(time.RFC3339, query.CursorLastMessageAt)
		if err != nil {
			return ListConversationsResult{}, &domainerrors.ValidationError{
				Field:   "cursor_last_message_at",
				Message: "must be RFC3339",
			}
		}
		pinned := false
		if query.CursorIsPinned != nil {
			pinned = *query.CursorIsPinned
		}
		cursor = &ports.ConversationListCursor{
			IsPinned:      pinned,
			LastMessageAt: lastAt.UTC(),
			ID:            id,
		}
	}

	items, err := h.conversations.ListForUser(ctx, userID, filter, cursor, limit+1)
	if err != nil {
		return ListConversationsResult{}, err
	}

	hasMore := len(items) > limit
	if hasMore {
		items = items[:limit]
	}

	out := make([]ConversationListEntry, 0, len(items))
	for _, it := range items {
		out = append(out, ConversationListEntry{
			ConversationID:     it.ConversationID.String(),
			BuyerID:            it.BuyerID.String(),
			SellerID:           it.SellerID.String(),
			ListingID:          it.ListingID.String(),
			IsReadOnly:         it.IsReadOnly,
			LastMessagePreview: it.LastMessagePreview,
			LastMessageAt:      it.LastMessageAt.Format(time.RFC3339),
			UnreadCount:        it.UnreadCount,
			IsArchived:         it.IsArchived,
			IsPinned:           it.IsPinned,
			IsMuted:            it.IsMuted,
		})
	}

	return ListConversationsResult{Items: out, HasMore: hasMore}, nil
}
