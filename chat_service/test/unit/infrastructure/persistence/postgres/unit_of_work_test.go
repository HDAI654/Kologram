package postgres_test

import (
	"context"
	"testing"

	"github.com/DATA-DOG/go-sqlmock"
	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/persistence/postgres"
)

func TestUnitOfWorkFactory_Commit(t *testing.T) {
	t.Parallel()

	db, mock, err := sqlmock.New()
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()

	mock.ExpectBegin()
	mock.ExpectCommit()

	factory := postgres.NewUnitOfWorkFactory(db)
	uow, err := factory.New(context.Background())
	if err != nil {
		t.Fatalf("New: %v", err)
	}
	if uow.Conversations() == nil || uow.Messages() == nil ||
		uow.ConversationStates() == nil || uow.UserBlocks() == nil {
		t.Fatalf("repos not wired")
	}
	if err := uow.Commit(context.Background()); err != nil {
		t.Fatalf("Commit: %v", err)
	}
	if err := mock.ExpectationsWereMet(); err != nil {
		t.Fatalf("unmet: %v", err)
	}
}

func TestUnitOfWorkFactory_Rollback(t *testing.T) {
	t.Parallel()

	db, mock, err := sqlmock.New()
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()

	mock.ExpectBegin()
	mock.ExpectRollback()

	factory := postgres.NewUnitOfWorkFactory(db)
	uow, err := factory.New(context.Background())
	if err != nil {
		t.Fatalf("New: %v", err)
	}
	if err := uow.Rollback(context.Background()); err != nil {
		t.Fatalf("Rollback: %v", err)
	}
	if err := mock.ExpectationsWereMet(); err != nil {
		t.Fatalf("unmet: %v", err)
	}
}
