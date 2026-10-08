package ports

import "context"

// UnitOfWork coordinates chat persistence and the transaction boundary.
// Repositories must not commit; Commit/Rollback belong here.
// ListingRepository is external and is not exposed through UoW.
type UnitOfWork interface {
	Conversations() ConversationRepository
	ConversationStates() ConversationUserStateRepository
	Messages() MessageRepository
	UserBlocks() UserBlockRepository

	Commit(ctx context.Context) error
	Rollback(ctx context.Context) error
}

type UnitOfWorkFactory interface {
	New(ctx context.Context) (UnitOfWork, error)
}
