package ports

import "context"

// UnitOfWork coordinates repository access and transactional boundaries.
type UnitOfWork interface {
	Conversations() ConversationRepository
	Commit(ctx context.Context) error
	Rollback(ctx context.Context) error
}

// UnitOfWorkFactory creates a new unit of work for a use case.
type UnitOfWorkFactory interface {
	New(ctx context.Context) (UnitOfWork, error)
}
