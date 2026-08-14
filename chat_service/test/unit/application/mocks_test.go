package application_test

import (
	"context"
	"sync"

	"github.com/HDAI654/Kologram/chat_service/internal/domain"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/event"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/port"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

// --- Conversation repository mock ---

type mockConversationRepo struct {
	mu sync.Mutex

	AddFn                  func(ctx context.Context, c *domain.Conversation) error
	GetByIDFn              func(ctx context.Context, id valueobject.ConversationID) (*domain.Conversation, error)
	UpdateFn               func(ctx context.Context, c *domain.Conversation) error
	FindByBuyerAndListingFn func(ctx context.Context, buyerID valueobject.UserID, listingID valueobject.ListingID) (*domain.Conversation, error)
	ListForUserFn          func(ctx context.Context, userID valueobject.UserID, limit, offset int) ([]*domain.Conversation, error)

	AddCalls    int
	UpdateCalls int
}

func (m *mockConversationRepo) Add(ctx context.Context, c *domain.Conversation) error {
	m.mu.Lock()
	m.AddCalls++
	m.mu.Unlock()
	if m.AddFn != nil {
		return m.AddFn(ctx, c)
	}
	return nil
}

func (m *mockConversationRepo) GetByID(ctx context.Context, id valueobject.ConversationID) (*domain.Conversation, error) {
	if m.GetByIDFn != nil {
		return m.GetByIDFn(ctx, id)
	}
	return nil, domain.ErrConversationNotFound
}

func (m *mockConversationRepo) Update(ctx context.Context, c *domain.Conversation) error {
	m.mu.Lock()
	m.UpdateCalls++
	m.mu.Unlock()
	if m.UpdateFn != nil {
		return m.UpdateFn(ctx, c)
	}
	return nil
}

func (m *mockConversationRepo) FindByBuyerAndListing(
	ctx context.Context,
	buyerID valueobject.UserID,
	listingID valueobject.ListingID,
) (*domain.Conversation, error) {
	if m.FindByBuyerAndListingFn != nil {
		return m.FindByBuyerAndListingFn(ctx, buyerID, listingID)
	}
	return nil, nil
}

func (m *mockConversationRepo) ListForUser(
	ctx context.Context,
	userID valueobject.UserID,
	limit, offset int,
) ([]*domain.Conversation, error) {
	if m.ListForUserFn != nil {
		return m.ListForUserFn(ctx, userID, limit, offset)
	}
	return nil, nil
}

// --- Unit of work mock ---

type mockUoW struct {
	repo     *mockConversationRepo
	committed bool
	rolledBack bool
}

func (u *mockUoW) Conversations() port.ConversationRepository { return u.repo }
func (u *mockUoW) Commit(context.Context) error {
	u.committed = true
	return nil
}
func (u *mockUoW) Rollback(context.Context) error {
	u.rolledBack = true
	return nil
}

type mockUoWFactory struct {
	uow *mockUoW
	err error
}

func (f *mockUoWFactory) New(context.Context) (port.UnitOfWork, error) {
	if f.err != nil {
		return nil, f.err
	}
	return f.uow, nil
}

// --- Event publisher mock ---

type mockEvents struct {
	mu     sync.Mutex
	events []event.DomainEvent
}

func (m *mockEvents) Publish(_ context.Context, evt event.DomainEvent) error {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.events = append(m.events, evt)
	return nil
}

func (m *mockEvents) Last() event.DomainEvent {
	m.mu.Lock()
	defer m.mu.Unlock()
	if len(m.events) == 0 {
		return nil
	}
	return m.events[len(m.events)-1]
}

// --- Realtime notifier mock ---

type mockRealtime struct {
	mu      sync.Mutex
	notified []string
}

func (m *mockRealtime) NotifyUser(_ context.Context, userID string, _ any) error {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.notified = append(m.notified, userID)
	return nil
}

// helpers

const (
	buyerID   = "550e8400-e29b-41d4-a716-446655440001"
	sellerID  = "550e8400-e29b-41d4-a716-446655440002"
	listingID = "550e8400-e29b-41d4-a716-446655440003"
)

func mustUser(raw string) valueobject.UserID {
	id, err := valueobject.NewUserID(raw)
	if err != nil {
		panic(err)
	}
	return id
}

func mustListing(raw string) valueobject.ListingID {
	id, err := valueobject.NewListingID(raw)
	if err != nil {
		panic(err)
	}
	return id
}

func openConversation() *domain.Conversation {
	c, err := domain.StartConversation(mustUser(buyerID), mustUser(sellerID), mustListing(listingID))
	if err != nil {
		panic(err)
	}
	return c
}

func newMocks() (*mockUoWFactory, *mockConversationRepo, *mockEvents, *mockRealtime) {
	repo := &mockConversationRepo{}
	uow := &mockUoW{repo: repo}
	factory := &mockUoWFactory{uow: uow}
	events := &mockEvents{}
	rt := &mockRealtime{}
	return factory, repo, events, rt
}
