package memory

import (
	"context"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
)

// unitOfWork is a no-op transaction boundary over a shared in-memory Store.
// Suitable for tests; does not provide isolation between concurrent writers.
type unitOfWork struct {
	conversations *ConversationRepository
	states        *ConversationUserStateRepository
	messages      *MessageRepository
	blocks        *UserBlockRepository
	committed     bool
	rolledBack    bool
}

func (u *unitOfWork) Conversations() ports.ConversationRepository { return u.conversations }
func (u *unitOfWork) ConversationStates() ports.ConversationUserStateRepository {
	return u.states
}
func (u *unitOfWork) Messages() ports.MessageRepository    { return u.messages }
func (u *unitOfWork) UserBlocks() ports.UserBlockRepository { return u.blocks }

func (u *unitOfWork) Commit(ctx context.Context) error {
	u.committed = true
	return nil
}

func (u *unitOfWork) Rollback(ctx context.Context) error {
	u.rolledBack = true
	return nil
}

type UnitOfWorkFactory struct {
	store *Store
}

func NewUnitOfWorkFactory(store *Store) *UnitOfWorkFactory {
	return &UnitOfWorkFactory{store: store}
}

func (f *UnitOfWorkFactory) New(ctx context.Context) (ports.UnitOfWork, error) {
	return &unitOfWork{
		conversations: NewConversationRepository(f.store),
		states:        NewConversationUserStateRepository(f.store),
		messages:      NewMessageRepository(f.store),
		blocks:        NewUserBlockRepository(f.store),
	}, nil
}

var _ ports.UnitOfWork = (*unitOfWork)(nil)
var _ ports.UnitOfWorkFactory = (*UnitOfWorkFactory)(nil)
