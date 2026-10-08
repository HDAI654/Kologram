package memory

import (
	"context"
	"sort"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

type MessageRepository struct {
	store *Store
}

func NewMessageRepository(store *Store) *MessageRepository {
	return &MessageRepository{store: store}
}

func (r *MessageRepository) Add(ctx context.Context, message *entities.Message) error {
	r.store.mu.Lock()
	defer r.store.mu.Unlock()
	id := message.ID.String()
	r.store.Messages[id] = cloneMessage(message)
	r.store.MessagesByClient[clientKey(message.SenderID.String(), message.ConversationID.String(), message.ClientMessageID)] = id
	cid := message.ConversationID.String()
	r.store.MessagesByConversation[cid] = append(r.store.MessagesByConversation[cid], id)
	return nil
}

func (r *MessageRepository) Update(ctx context.Context, message *entities.Message) error {
	r.store.mu.Lock()
	defer r.store.mu.Unlock()
	id := message.ID.String()
	if _, ok := r.store.Messages[id]; !ok {
		return &domainerrors.NotFoundError{
			Field:   "message_id",
			Message: "message " + id + " not found",
		}
	}
	r.store.Messages[id] = cloneMessage(message)
	return nil
}

func (r *MessageRepository) GetByID(ctx context.Context, id valueobjects.MessageID) (*entities.Message, error) {
	r.store.mu.RLock()
	defer r.store.mu.RUnlock()
	m, ok := r.store.Messages[id.String()]
	if !ok {
		return nil, &domainerrors.NotFoundError{
			Field:   "message_id",
			Message: "message " + id.String() + " not found",
		}
	}
	return cloneMessage(m), nil
}

func (r *MessageRepository) FindByClientMessageID(
	ctx context.Context,
	senderID valueobjects.UserID,
	conversationID valueobjects.ConversationID,
	clientMessageID string,
) (*entities.Message, error) {
	r.store.mu.RLock()
	defer r.store.mu.RUnlock()
	id, ok := r.store.MessagesByClient[clientKey(senderID.String(), conversationID.String(), clientMessageID)]
	if !ok {
		return nil, nil
	}
	return cloneMessage(r.store.Messages[id]), nil
}

func (r *MessageRepository) FindLatestVisible(
	ctx context.Context,
	conversationID valueobjects.ConversationID,
) (*entities.Message, error) {
	r.store.mu.RLock()
	defer r.store.mu.RUnlock()
	var latest *entities.Message
	for _, id := range r.store.MessagesByConversation[conversationID.String()] {
		m := r.store.Messages[id]
		if m == nil || m.DeletedForEveryone {
			continue
		}
		if latest == nil || m.SentAt.After(latest.SentAt) ||
			(m.SentAt.Equal(latest.SentAt) && m.ID.String() > latest.ID.String()) {
			latest = m
		}
	}
	return cloneMessage(latest), nil
}

func (r *MessageRepository) ListMessages(
	ctx context.Context,
	conversationID valueobjects.ConversationID,
	cursor *ports.MessageCursor,
	direction ports.Direction,
	limit int,
) ([]*entities.Message, error) {
	r.store.mu.RLock()
	defer r.store.mu.RUnlock()

	if direction == ports.DirectionNewer && cursor == nil {
		return nil, &domainerrors.ValidationError{
			Field:   "cursor",
			Message: "cursor is required for direction newer",
		}
	}

	all := make([]*entities.Message, 0)
	for _, id := range r.store.MessagesByConversation[conversationID.String()] {
		m := r.store.Messages[id]
		if m == nil || m.DeletedForEveryone {
			continue
		}
		all = append(all, cloneMessage(m))
	}

	sort.Slice(all, func(i, j int) bool {
		if !all[i].SentAt.Equal(all[j].SentAt) {
			return all[i].SentAt.After(all[j].SentAt)
		}
		return all[i].ID.String() > all[j].ID.String()
	})

	filtered := make([]*entities.Message, 0, len(all))
	for _, m := range all {
		if cursor == nil {
			filtered = append(filtered, m)
			continue
		}
		switch direction {
		case ports.DirectionNewer:
			if m.SentAt.After(cursor.SentAt) ||
				(m.SentAt.Equal(cursor.SentAt) && m.ID.String() > cursor.ID.String()) {
				filtered = append(filtered, m)
			}
		default:
			if m.SentAt.Before(cursor.SentAt) ||
				(m.SentAt.Equal(cursor.SentAt) && m.ID.String() < cursor.ID.String()) {
				filtered = append(filtered, m)
			}
		}
	}

	if direction == ports.DirectionNewer {
		sort.Slice(filtered, func(i, j int) bool {
			if !filtered[i].SentAt.Equal(filtered[j].SentAt) {
				return filtered[i].SentAt.Before(filtered[j].SentAt)
			}
			return filtered[i].ID.String() < filtered[j].ID.String()
		})
	}

	if limit > 0 && len(filtered) > limit {
		filtered = filtered[:limit]
	}
	return filtered, nil
}
