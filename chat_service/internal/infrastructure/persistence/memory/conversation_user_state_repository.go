package memory

import (
	"context"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

type ConversationUserStateRepository struct {
	store *Store
}

func NewConversationUserStateRepository(store *Store) *ConversationUserStateRepository {
	return &ConversationUserStateRepository{store: store}
}

func (r *ConversationUserStateRepository) Add(ctx context.Context, state *entities.ConversationUserState) error {
	r.store.mu.Lock()
	defer r.store.mu.Unlock()
	r.store.States[stateKey(state.ConversationID.String(), state.UserID.String())] = cloneState(state)
	return nil
}

func (r *ConversationUserStateRepository) Update(ctx context.Context, state *entities.ConversationUserState) error {
	r.store.mu.Lock()
	defer r.store.mu.Unlock()
	key := stateKey(state.ConversationID.String(), state.UserID.String())
	existing, ok := r.store.States[key]
	if !ok {
		return &domainerrors.NotFoundError{
			Field:   "conversation_user_state",
			Message: "state for user in conversation not found",
		}
	}
	next := cloneState(state)
	// Non-regression: keep existing last_read if incoming message is older by SentAt.
	if !state.LastReadMessageID.IsZero() && !existing.LastReadMessageID.IsZero() {
		newMsg := r.store.Messages[state.LastReadMessageID.String()]
		oldMsg := r.store.Messages[existing.LastReadMessageID.String()]
		if newMsg != nil && oldMsg != nil && newMsg.SentAt.Before(oldMsg.SentAt) {
			next.LastReadMessageID = existing.LastReadMessageID
		}
	}
	r.store.States[key] = next
	return nil
}

func (r *ConversationUserStateRepository) Get(
	ctx context.Context,
	conversationID valueobjects.ConversationID,
	userID valueobjects.UserID,
) (*entities.ConversationUserState, error) {
	r.store.mu.RLock()
	defer r.store.mu.RUnlock()
	s, ok := r.store.States[stateKey(conversationID.String(), userID.String())]
	if !ok {
		return nil, &domainerrors.NotFoundError{
			Field:   "conversation_user_state",
			Message: "state for user in conversation not found",
		}
	}
	return cloneState(s), nil
}

func (r *ConversationUserStateRepository) ListForConversation(
	ctx context.Context,
	conversationID valueobjects.ConversationID,
) ([]*entities.ConversationUserState, error) {
	r.store.mu.RLock()
	defer r.store.mu.RUnlock()
	prefix := conversationID.String() + "|"
	out := make([]*entities.ConversationUserState, 0)
	for k, s := range r.store.States {
		if len(k) >= len(prefix) && k[:len(prefix)] == prefix {
			out = append(out, cloneState(s))
		}
	}
	return out, nil
}
