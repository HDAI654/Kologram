package application_test

import (
	"context"
	"sync"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/events"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

// ---------------------------------------------------------------------------
// ListingRepository
// ---------------------------------------------------------------------------

type FakeListingRepository struct {
	ByID map[string]*entities.Listing
	Err  error
}

func NewFakeListingRepository() *FakeListingRepository {
	return &FakeListingRepository{ByID: make(map[string]*entities.Listing)}
}

func (f *FakeListingRepository) GetByID(ctx context.Context, listingID valueobjects.ListingID) (*entities.Listing, error) {
	if f.Err != nil {
		return nil, f.Err
	}
	return f.ByID[listingID.String()], nil
}

// ---------------------------------------------------------------------------
// ConversationRepository
// ---------------------------------------------------------------------------

type FakeConversationRepository struct {
	mu sync.Mutex

	ByID              map[string]*entities.Conversation
	ByBuyerAndListing map[string]*entities.Conversation // key: buyerID|listingID
	ByListingID       map[string][]*entities.Conversation
	ListItems         []ports.ConversationListItem

	AddErr    error
	UpdateErr error
	GetErr    error
	FindErr   error
	ListErr   error
}

func NewFakeConversationRepository() *FakeConversationRepository {
	return &FakeConversationRepository{
		ByID:              make(map[string]*entities.Conversation),
		ByBuyerAndListing: make(map[string]*entities.Conversation),
		ByListingID:       make(map[string][]*entities.Conversation),
	}
}

func buyerListingKey(buyerID, listingID string) string {
	return buyerID + "|" + listingID
}

func (f *FakeConversationRepository) Add(ctx context.Context, conversation *entities.Conversation) error {
	f.mu.Lock()
	defer f.mu.Unlock()
	if f.AddErr != nil {
		return f.AddErr
	}
	cp := *conversation
	f.ByID[conversation.ID.String()] = &cp
	f.ByBuyerAndListing[buyerListingKey(conversation.BuyerID.String(), conversation.ListingID.String())] = &cp
	f.ByListingID[conversation.ListingID.String()] = append(
		f.ByListingID[conversation.ListingID.String()], &cp,
	)
	return nil
}

func (f *FakeConversationRepository) Update(ctx context.Context, conversation *entities.Conversation) error {
	f.mu.Lock()
	defer f.mu.Unlock()
	if f.UpdateErr != nil {
		return f.UpdateErr
	}
	cp := *conversation
	f.ByID[conversation.ID.String()] = &cp
	f.ByBuyerAndListing[buyerListingKey(conversation.BuyerID.String(), conversation.ListingID.String())] = &cp
	return nil
}

func (f *FakeConversationRepository) GetByID(ctx context.Context, id valueobjects.ConversationID) (*entities.Conversation, error) {
	f.mu.Lock()
	defer f.mu.Unlock()
	if f.GetErr != nil {
		return nil, f.GetErr
	}
	c, ok := f.ByID[id.String()]
	if !ok {
		return nil, nil
	}
	cp := *c
	return &cp, nil
}

func (f *FakeConversationRepository) FindByBuyerAndListing(
	ctx context.Context,
	buyerID valueobjects.UserID,
	listingID valueobjects.ListingID,
) (*entities.Conversation, error) {
	f.mu.Lock()
	defer f.mu.Unlock()
	if f.FindErr != nil {
		return nil, f.FindErr
	}
	c, ok := f.ByBuyerAndListing[buyerListingKey(buyerID.String(), listingID.String())]
	if !ok {
		return nil, nil
	}
	cp := *c
	return &cp, nil
}

func (f *FakeConversationRepository) ListForUser(
	ctx context.Context,
	userID valueobjects.UserID,
	filter ports.ConversationListFilter,
	cursor *ports.ConversationListCursor,
	limit int,
) ([]ports.ConversationListItem, error) {
	if f.ListErr != nil {
		return nil, f.ListErr
	}
	if limit <= 0 || limit > len(f.ListItems) {
		return append([]ports.ConversationListItem(nil), f.ListItems...), nil
	}
	return append([]ports.ConversationListItem(nil), f.ListItems[:limit]...), nil
}

func (f *FakeConversationRepository) ListByListingID(
	ctx context.Context,
	listingID valueobjects.ListingID,
) ([]*entities.Conversation, error) {
	f.mu.Lock()
	defer f.mu.Unlock()
	if f.ListErr != nil {
		return nil, f.ListErr
	}
	src := f.ByListingID[listingID.String()]
	out := make([]*entities.Conversation, 0, len(src))
	for _, c := range src {
		cp := *c
		out = append(out, &cp)
	}
	return out, nil
}

// ---------------------------------------------------------------------------
// ConversationUserStateRepository
// ---------------------------------------------------------------------------

type FakeConversationUserStateRepository struct {
	mu sync.Mutex

	// key: conversationID|userID
	ByKey map[string]*entities.ConversationUserState

	AddErr    error
	UpdateErr error
	GetErr    error
	ListErr   error
}

func NewFakeConversationUserStateRepository() *FakeConversationUserStateRepository {
	return &FakeConversationUserStateRepository{
		ByKey: make(map[string]*entities.ConversationUserState),
	}
}

func stateKey(conversationID, userID string) string {
	return conversationID + "|" + userID
}

func (f *FakeConversationUserStateRepository) Add(ctx context.Context, state *entities.ConversationUserState) error {
	f.mu.Lock()
	defer f.mu.Unlock()
	if f.AddErr != nil {
		return f.AddErr
	}
	cp := *state
	f.ByKey[stateKey(state.ConversationID.String(), state.UserID.String())] = &cp
	return nil
}

func (f *FakeConversationUserStateRepository) Update(ctx context.Context, state *entities.ConversationUserState) error {
	f.mu.Lock()
	defer f.mu.Unlock()
	if f.UpdateErr != nil {
		return f.UpdateErr
	}
	cp := *state
	f.ByKey[stateKey(state.ConversationID.String(), state.UserID.String())] = &cp
	return nil
}

func (f *FakeConversationUserStateRepository) Get(
	ctx context.Context,
	conversationID valueobjects.ConversationID,
	userID valueobjects.UserID,
) (*entities.ConversationUserState, error) {
	f.mu.Lock()
	defer f.mu.Unlock()
	if f.GetErr != nil {
		return nil, f.GetErr
	}
	s, ok := f.ByKey[stateKey(conversationID.String(), userID.String())]
	if !ok {
		return nil, nil
	}
	cp := *s
	return &cp, nil
}

func (f *FakeConversationUserStateRepository) ListForConversation(
	ctx context.Context,
	conversationID valueobjects.ConversationID,
) ([]*entities.ConversationUserState, error) {
	f.mu.Lock()
	defer f.mu.Unlock()
	if f.ListErr != nil {
		return nil, f.ListErr
	}
	prefix := conversationID.String() + "|"
	out := make([]*entities.ConversationUserState, 0)
	for k, s := range f.ByKey {
		if len(k) >= len(prefix) && k[:len(prefix)] == prefix {
			cp := *s
			out = append(out, &cp)
		}
	}
	return out, nil
}

// ---------------------------------------------------------------------------
// MessageRepository
// ---------------------------------------------------------------------------

type FakeMessageRepository struct {
	mu sync.Mutex

	ByID           map[string]*entities.Message
	ByClientKey    map[string]*entities.Message // sender|conversation|clientMessageID
	ByConversation map[string][]*entities.Message

	AddErr    error
	UpdateErr error
	GetErr    error
	FindErr   error
	ListErr   error
}

func NewFakeMessageRepository() *FakeMessageRepository {
	return &FakeMessageRepository{
		ByID:           make(map[string]*entities.Message),
		ByClientKey:    make(map[string]*entities.Message),
		ByConversation: make(map[string][]*entities.Message),
	}
}

func clientKey(senderID, conversationID, clientMessageID string) string {
	return senderID + "|" + conversationID + "|" + clientMessageID
}

func (f *FakeMessageRepository) Add(ctx context.Context, message *entities.Message) error {
	f.mu.Lock()
	defer f.mu.Unlock()
	if f.AddErr != nil {
		return f.AddErr
	}
	cp := *message
	f.ByID[message.ID.String()] = &cp
	f.ByClientKey[clientKey(message.SenderID.String(), message.ConversationID.String(), message.ClientMessageID)] = &cp
	f.ByConversation[message.ConversationID.String()] = append(
		f.ByConversation[message.ConversationID.String()], &cp,
	)
	return nil
}

func (f *FakeMessageRepository) Update(ctx context.Context, message *entities.Message) error {
	f.mu.Lock()
	defer f.mu.Unlock()
	if f.UpdateErr != nil {
		return f.UpdateErr
	}
	cp := *message
	f.ByID[message.ID.String()] = &cp
	f.ByClientKey[clientKey(message.SenderID.String(), message.ConversationID.String(), message.ClientMessageID)] = &cp
	cid := message.ConversationID.String()
	for i, m := range f.ByConversation[cid] {
		if m.ID.String() == message.ID.String() {
			f.ByConversation[cid][i] = &cp
			break
		}
	}
	return nil
}

func (f *FakeMessageRepository) GetByID(ctx context.Context, id valueobjects.MessageID) (*entities.Message, error) {
	f.mu.Lock()
	defer f.mu.Unlock()
	if f.GetErr != nil {
		return nil, f.GetErr
	}
	m, ok := f.ByID[id.String()]
	if !ok {
		return nil, nil
	}
	cp := *m
	return &cp, nil
}

func (f *FakeMessageRepository) FindByClientMessageID(
	ctx context.Context,
	senderID valueobjects.UserID,
	conversationID valueobjects.ConversationID,
	clientMessageID string,
) (*entities.Message, error) {
	f.mu.Lock()
	defer f.mu.Unlock()
	if f.FindErr != nil {
		return nil, f.FindErr
	}
	m, ok := f.ByClientKey[clientKey(senderID.String(), conversationID.String(), clientMessageID)]
	if !ok {
		return nil, nil
	}
	cp := *m
	return &cp, nil
}

func (f *FakeMessageRepository) FindLatestVisible(
	ctx context.Context,
	conversationID valueobjects.ConversationID,
) (*entities.Message, error) {
	f.mu.Lock()
	defer f.mu.Unlock()
	if f.FindErr != nil {
		return nil, f.FindErr
	}
	msgs := f.ByConversation[conversationID.String()]
	var latest *entities.Message
	for _, m := range msgs {
		if m.DeletedForEveryone {
			continue
		}
		if latest == nil || m.SentAt.After(latest.SentAt) {
			cp := *m
			latest = &cp
		}
	}
	return latest, nil
}

func (f *FakeMessageRepository) ListMessages(
	ctx context.Context,
	conversationID valueobjects.ConversationID,
	cursor *ports.MessageCursor,
	direction ports.Direction,
	limit int,
) ([]*entities.Message, error) {
	f.mu.Lock()
	defer f.mu.Unlock()
	if f.ListErr != nil {
		return nil, f.ListErr
	}
	src := f.ByConversation[conversationID.String()]
	out := make([]*entities.Message, 0, len(src))
	for _, m := range src {
		if m.DeletedForEveryone {
			continue
		}
		cp := *m
		out = append(out, &cp)
	}
	if limit > 0 && len(out) > limit {
		out = out[:limit]
	}
	return out, nil
}

// ---------------------------------------------------------------------------
// UserBlockRepository
// ---------------------------------------------------------------------------

type FakeUserBlockRepository struct {
	mu sync.Mutex

	// key: blockerID|blockedID
	Blocks map[string]struct{}

	AddErr     error
	RemoveErr  error
	ExistsErr  error
	EitherErr  error
	EitherWay  bool // global override when set via ForceEitherWay
	UseForce   bool
}

func NewFakeUserBlockRepository() *FakeUserBlockRepository {
	return &FakeUserBlockRepository{Blocks: make(map[string]struct{})}
}

func blockKey(a, b string) string { return a + "|" + b }

func (f *FakeUserBlockRepository) Add(ctx context.Context, block *entities.UserBlock) error {
	f.mu.Lock()
	defer f.mu.Unlock()
	if f.AddErr != nil {
		return f.AddErr
	}
	f.Blocks[blockKey(block.BlockerID.String(), block.BlockedID.String())] = struct{}{}
	return nil
}

func (f *FakeUserBlockRepository) Remove(
	ctx context.Context,
	blockerID valueobjects.UserID,
	blockedID valueobjects.UserID,
) error {
	f.mu.Lock()
	defer f.mu.Unlock()
	if f.RemoveErr != nil {
		return f.RemoveErr
	}
	delete(f.Blocks, blockKey(blockerID.String(), blockedID.String()))
	return nil
}

func (f *FakeUserBlockRepository) Exists(
	ctx context.Context,
	blockerID valueobjects.UserID,
	blockedID valueobjects.UserID,
) (bool, error) {
	f.mu.Lock()
	defer f.mu.Unlock()
	if f.ExistsErr != nil {
		return false, f.ExistsErr
	}
	_, ok := f.Blocks[blockKey(blockerID.String(), blockedID.String())]
	return ok, nil
}

func (f *FakeUserBlockRepository) IsBlockedEitherWay(
	ctx context.Context,
	userA valueobjects.UserID,
	userB valueobjects.UserID,
) (bool, error) {
	f.mu.Lock()
	defer f.mu.Unlock()
	if f.EitherErr != nil {
		return false, f.EitherErr
	}
	if f.UseForce {
		return f.EitherWay, nil
	}
	_, ab := f.Blocks[blockKey(userA.String(), userB.String())]
	_, ba := f.Blocks[blockKey(userB.String(), userA.String())]
	return ab || ba, nil
}

func (f *FakeUserBlockRepository) ForceEitherWay(blocked bool) {
	f.UseForce = true
	f.EitherWay = blocked
}

// ---------------------------------------------------------------------------
// UnitOfWork
// ---------------------------------------------------------------------------

type FakeUnitOfWork struct {
	ConversationsRepo ports.ConversationRepository
	StatesRepo        ports.ConversationUserStateRepository
	MessagesRepo      ports.MessageRepository
	BlocksRepo        ports.UserBlockRepository

	CommitErr   error
	RollbackErr error
	Committed   bool
	RolledBack  bool
}

func (u *FakeUnitOfWork) Conversations() ports.ConversationRepository {
	return u.ConversationsRepo
}
func (u *FakeUnitOfWork) ConversationStates() ports.ConversationUserStateRepository {
	return u.StatesRepo
}
func (u *FakeUnitOfWork) Messages() ports.MessageRepository { return u.MessagesRepo }
func (u *FakeUnitOfWork) UserBlocks() ports.UserBlockRepository {
	return u.BlocksRepo
}

func (u *FakeUnitOfWork) Commit(ctx context.Context) error {
	if u.CommitErr != nil {
		return u.CommitErr
	}
	u.Committed = true
	return nil
}

func (u *FakeUnitOfWork) Rollback(ctx context.Context) error {
	u.RolledBack = true
	return u.RollbackErr
}

type FakeUnitOfWorkFactory struct {
	Uow *FakeUnitOfWork
	Err error
}

func (f *FakeUnitOfWorkFactory) New(ctx context.Context) (ports.UnitOfWork, error) {
	if f.Err != nil {
		return nil, f.Err
	}
	return f.Uow, nil
}

func NewFakeUowBundle() (
	*FakeConversationRepository,
	*FakeConversationUserStateRepository,
	*FakeMessageRepository,
	*FakeUserBlockRepository,
	*FakeUnitOfWork,
	*FakeUnitOfWorkFactory,
) {
	convs := NewFakeConversationRepository()
	states := NewFakeConversationUserStateRepository()
	msgs := NewFakeMessageRepository()
	blocks := NewFakeUserBlockRepository()
	uow := &FakeUnitOfWork{
		ConversationsRepo: convs,
		StatesRepo:        states,
		MessagesRepo:      msgs,
		BlocksRepo:        blocks,
	}
	factory := &FakeUnitOfWorkFactory{Uow: uow}
	return convs, states, msgs, blocks, uow, factory
}

// ---------------------------------------------------------------------------
// EventPublisher / RealtimeNotifier
// ---------------------------------------------------------------------------

type FakeEventPublisher struct {
	mu     sync.Mutex
	Events []events.DomainEvent
	Err    error
}

func NewFakeEventPublisher() *FakeEventPublisher {
	return &FakeEventPublisher{}
}

func (f *FakeEventPublisher) Publish(ctx context.Context, evt events.DomainEvent) error {
	f.mu.Lock()
	defer f.mu.Unlock()
	if f.Err != nil {
		return f.Err
	}
	f.Events = append(f.Events, evt)
	return nil
}

func (f *FakeEventPublisher) Count() int {
	f.mu.Lock()
	defer f.mu.Unlock()
	return len(f.Events)
}

type FakeRealtimeNotifier struct {
	mu      sync.Mutex
	Calls   []RealtimeCall
	Err     error
}

type RealtimeCall struct {
	UserID  string
	Payload any
}

func NewFakeRealtimeNotifier() *FakeRealtimeNotifier {
	return &FakeRealtimeNotifier{}
}

func (f *FakeRealtimeNotifier) NotifyUser(ctx context.Context, userID string, payload any) error {
	f.mu.Lock()
	defer f.mu.Unlock()
	if f.Err != nil {
		return f.Err
	}
	f.Calls = append(f.Calls, RealtimeCall{UserID: userID, Payload: payload})
	return nil
}

func (f *FakeRealtimeNotifier) Count() int {
	f.mu.Lock()
	defer f.mu.Unlock()
	return len(f.Calls)
}
