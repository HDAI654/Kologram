package postgres

import (
	"context"
	"database/sql"
	"errors"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
)

type unitOfWork struct {
	tx            *sql.Tx
	conversations *ConversationRepository
	states        *ConversationUserStateRepository
	messages      *MessageRepository
	blocks        *UserBlockRepository
}

func (u *unitOfWork) Conversations() ports.ConversationRepository { return u.conversations }
func (u *unitOfWork) ConversationStates() ports.ConversationUserStateRepository {
	return u.states
}
func (u *unitOfWork) Messages() ports.MessageRepository   { return u.messages }
func (u *unitOfWork) UserBlocks() ports.UserBlockRepository { return u.blocks }

func (u *unitOfWork) Commit(ctx context.Context) error {
	if err := u.tx.Commit(); err != nil {
		return translateDBError("UnitOfWork.Commit", err)
	}
	return nil
}

func (u *unitOfWork) Rollback(ctx context.Context) error {
	err := u.tx.Rollback()
	if err == nil || errors.Is(err, sql.ErrTxDone) {
		return nil
	}
	return translateDBError("UnitOfWork.Rollback", err)
}

// UnitOfWorkFactory opens a transaction per New call. Repositories share that tx.
type UnitOfWorkFactory struct {
	db *sql.DB
}

func NewUnitOfWorkFactory(db *sql.DB) *UnitOfWorkFactory {
	return &UnitOfWorkFactory{db: db}
}

func (f *UnitOfWorkFactory) New(ctx context.Context) (ports.UnitOfWork, error) {
	tx, err := f.db.BeginTx(ctx, nil)
	if err != nil {
		return nil, translateDBError("UnitOfWorkFactory.New", err)
	}
	return &unitOfWork{
		tx:            tx,
		conversations: NewConversationRepository(tx),
		states:        NewConversationUserStateRepository(tx),
		messages:      NewMessageRepository(tx),
		blocks:        NewUserBlockRepository(tx),
	}, nil
}

// Ensure interface compliance at compile time.
var _ ports.UnitOfWork = (*unitOfWork)(nil)
var _ ports.UnitOfWorkFactory = (*UnitOfWorkFactory)(nil)
