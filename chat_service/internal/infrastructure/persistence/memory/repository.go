package memory

import (
	"context"
	"log/slog"
	"sort"
	"sync"

	"github.com/HDAI654/Kologram/chat_service/internal/domain"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/port"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

// ConversationRepository is an in-memory adapter for tests and local dev.
type ConversationRepository struct {
	mu            sync.RWMutex
	conversations map[string]*domain.Conversation
}

func NewConversationRepository() *ConversationRepository {
	return &ConversationRepository{
		conversations: make(map[string]*domain.Conversation),
	}
}

func (r *ConversationRepository) Add(_ context.Context, conversation *domain.Conversation) error {
	slog.Info("adding conversation", "id", conversation.ID.String())
	r.mu.Lock()
	defer r.mu.Unlock()
	clone := cloneConversation(conversation)
	r.conversations[conversation.ID.String()] = clone
	slog.Info("conversation added", "id", conversation.ID.String())
	return nil
}

func (r *ConversationRepository) GetByID(_ context.Context, id valueobject.ConversationID) (*domain.Conversation, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	c, ok := r.conversations[id.String()]
	if !ok {
		slog.Debug("conversation not found", "id", id.String())
		return nil, domain.ErrConversationNotFound
	}
	return cloneConversation(c), nil
}

func (r *ConversationRepository) Update(_ context.Context, conversation *domain.Conversation) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if _, ok := r.conversations[conversation.ID.String()]; !ok {
		return domain.ErrConversationNotFound
	}
	r.conversations[conversation.ID.String()] = cloneConversation(conversation)
	return nil
}

func (r *ConversationRepository) FindByBuyerAndListing(
	_ context.Context,
	buyerID valueobject.UserID,
	listingID valueobject.ListingID,
) (*domain.Conversation, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	for _, c := range r.conversations {
		if c.BuyerID.Equals(buyerID) && c.ListingID.String() == listingID.String() {
			return cloneConversation(c), nil
		}
	}
	return nil, nil
}

func (r *ConversationRepository) ListForUser(
	_ context.Context,
	userID valueobject.UserID,
	limit, offset int,
) ([]*domain.Conversation, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	items := make([]*domain.Conversation, 0)
	for _, c := range r.conversations {
		if c.IsParticipant(userID) {
			items = append(items, cloneConversation(c))
		}
	}
	sort.Slice(items, func(i, j int) bool {
		return items[i].UpdatedAt.After(items[j].UpdatedAt)
	})
	if offset >= len(items) {
		return []*domain.Conversation{}, nil
	}
	end := offset + limit
	if end > len(items) {
		end = len(items)
	}
	return items[offset:end], nil
}

func cloneConversation(c *domain.Conversation) *domain.Conversation {
	msgs := make([]domain.Message, len(c.Messages))
	copy(msgs, c.Messages)
	return domain.RehydrateConversation(
		c.ID, c.BuyerID, c.SellerID, c.ListingID, c.Status, msgs, c.CreatedAt, c.UpdatedAt,
	)
}

// UnitOfWork wraps the shared in-memory repository.
type UnitOfWork struct {
	repo *ConversationRepository
}

func (u *UnitOfWork) Conversations() port.ConversationRepository { return u.repo }
func (u *UnitOfWork) Commit(context.Context) error               { return nil }
func (u *UnitOfWork) Rollback(context.Context) error             { return nil }

type UnitOfWorkFactory struct {
	repo *ConversationRepository
}

func NewUnitOfWorkFactory(repo *ConversationRepository) *UnitOfWorkFactory {
	return &UnitOfWorkFactory{repo: repo}
}

func (f *UnitOfWorkFactory) New(context.Context) (port.UnitOfWork, error) {
	return &UnitOfWork{repo: f.repo}, nil
}
