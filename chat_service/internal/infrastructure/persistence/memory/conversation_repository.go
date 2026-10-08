package memory

import (
	"context"
	"sort"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

type ConversationRepository struct {
	store *Store
}

func NewConversationRepository(store *Store) *ConversationRepository {
	return &ConversationRepository{store: store}
}

func (r *ConversationRepository) Add(ctx context.Context, conversation *entities.Conversation) error {
	r.store.mu.Lock()
	defer r.store.mu.Unlock()
	id := conversation.ID.String()
	r.store.Conversations[id] = cloneConversation(conversation)
	r.store.ByBuyerListing[buyerListingKey(conversation.BuyerID.String(), conversation.ListingID.String())] = id
	lid := conversation.ListingID.String()
	r.store.ByListing[lid] = append(r.store.ByListing[lid], id)
	return nil
}

func (r *ConversationRepository) Update(ctx context.Context, conversation *entities.Conversation) error {
	r.store.mu.Lock()
	defer r.store.mu.Unlock()
	id := conversation.ID.String()
	if _, ok := r.store.Conversations[id]; !ok {
		return &domainerrors.NotFoundError{
			Field:   "conversation_id",
			Message: "conversation " + id + " not found",
		}
	}
	r.store.Conversations[id] = cloneConversation(conversation)
	return nil
}

func (r *ConversationRepository) GetByID(ctx context.Context, id valueobjects.ConversationID) (*entities.Conversation, error) {
	r.store.mu.RLock()
	defer r.store.mu.RUnlock()
	c, ok := r.store.Conversations[id.String()]
	if !ok {
		return nil, &domainerrors.NotFoundError{
			Field:   "conversation_id",
			Message: "conversation " + id.String() + " not found",
		}
	}
	return cloneConversation(c), nil
}

func (r *ConversationRepository) FindByBuyerAndListing(
	ctx context.Context,
	buyerID valueobjects.UserID,
	listingID valueobjects.ListingID,
) (*entities.Conversation, error) {
	r.store.mu.RLock()
	defer r.store.mu.RUnlock()
	id, ok := r.store.ByBuyerListing[buyerListingKey(buyerID.String(), listingID.String())]
	if !ok {
		return nil, nil
	}
	return cloneConversation(r.store.Conversations[id]), nil
}

func (r *ConversationRepository) ListByListingID(
	ctx context.Context,
	listingID valueobjects.ListingID,
) ([]*entities.Conversation, error) {
	r.store.mu.RLock()
	defer r.store.mu.RUnlock()
	ids := r.store.ByListing[listingID.String()]
	out := make([]*entities.Conversation, 0, len(ids))
	for _, id := range ids {
		if c, ok := r.store.Conversations[id]; ok {
			out = append(out, cloneConversation(c))
		}
	}
	return out, nil
}

func (r *ConversationRepository) ListForUser(
	ctx context.Context,
	userID valueobjects.UserID,
	filter ports.ConversationListFilter,
	cursor *ports.ConversationListCursor,
	limit int,
) ([]ports.ConversationListItem, error) {
	r.store.mu.RLock()
	defer r.store.mu.RUnlock()

	wantArchived := filter == ports.ListFilterArchived
	now := time.Now().UTC()
	items := make([]ports.ConversationListItem, 0)

	for _, state := range r.store.States {
		if state.UserID.String() != userID.String() {
			continue
		}
		if state.IsHidden {
			continue
		}
		if state.IsArchived != wantArchived {
			continue
		}
		conv, ok := r.store.Conversations[state.ConversationID.String()]
		if !ok {
			continue
		}
		if cursor != nil {
			if !afterCursor(state.IsPinned, conv.LastMessageAt, conv.ID, cursor) {
				continue
			}
		}
		items = append(items, ports.ConversationListItem{
			ConversationID:     conv.ID,
			BuyerID:            conv.BuyerID,
			SellerID:           conv.SellerID,
			ListingID:          conv.ListingID,
			IsReadOnly:         conv.IsReadOnly,
			LastMessagePreview: conv.LastMessagePreview,
			LastMessageAt:      conv.LastMessageAt,
			CreatedAt:          conv.CreatedAt,
			UpdatedAt:          conv.UpdatedAt,
			UnreadCount:        state.UnreadCount,
			IsArchived:         state.IsArchived,
			IsPinned:           state.IsPinned,
			IsMuted:            state.IsMuted(now),
		})
	}

	sort.Slice(items, func(i, j int) bool {
		if items[i].IsPinned != items[j].IsPinned {
			return items[i].IsPinned
		}
		if !items[i].LastMessageAt.Equal(items[j].LastMessageAt) {
			return items[i].LastMessageAt.After(items[j].LastMessageAt)
		}
		return items[i].ConversationID.String() > items[j].ConversationID.String()
	})

	if limit > 0 && len(items) > limit {
		items = items[:limit]
	}
	return items, nil
}

// afterCursor reports whether the row is strictly after the cursor in DESC (pinned, time, id) order.
func afterCursor(
	isPinned bool,
	lastMessageAt time.Time,
	id valueobjects.ConversationID,
	cursor *ports.ConversationListCursor,
) bool {
	if isPinned != cursor.IsPinned {
		return !isPinned && cursor.IsPinned // unpinned after pinned when scanning further pages
	}
	if !lastMessageAt.Equal(cursor.LastMessageAt) {
		return lastMessageAt.Before(cursor.LastMessageAt)
	}
	return id.String() < cursor.ID.String()
}
