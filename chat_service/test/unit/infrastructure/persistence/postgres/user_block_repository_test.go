package postgres_test

import (
	"context"
	"database/sql"
	"testing"

	"github.com/DATA-DOG/go-sqlmock"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/persistence/postgres"
)

func TestUserBlockRepository_Add(t *testing.T) {
	t.Parallel()

	db, mock, err := sqlmock.New(sqlmock.QueryMatcherOption(sqlmock.QueryMatcherRegexp))
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()

	buyer, seller, _ := mustParticipantIDs(t)
	block, err := entities.NewUserBlock(buyer, seller)
	if err != nil {
		t.Fatal(err)
	}

	mock.ExpectExec(`(?s)INSERT INTO user_blocks`).
		WithArgs(buyer.String(), seller.String(), sqlmock.AnyArg()).
		WillReturnResult(sqlmock.NewResult(0, 1))

	repo := postgres.NewUserBlockRepository(db)
	if err := repo.Add(context.Background(), block); err != nil {
		t.Fatalf("Add: %v", err)
	}
}

func TestUserBlockRepository_IsBlockedEitherWay_True(t *testing.T) {
	t.Parallel()

	db, mock, err := sqlmock.New(sqlmock.QueryMatcherOption(sqlmock.QueryMatcherRegexp))
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()

	buyer, seller, _ := mustParticipantIDs(t)
	mock.ExpectQuery(`(?s)FROM user_blocks`).
		WithArgs(buyer.String(), seller.String()).
		WillReturnRows(sqlmock.NewRows([]string{"x"}).AddRow(1))

	repo := postgres.NewUserBlockRepository(db)
	ok, err := repo.IsBlockedEitherWay(context.Background(), buyer, seller)
	if err != nil || !ok {
		t.Fatalf("ok=%v err=%v", ok, err)
	}
}

func TestUserBlockRepository_IsBlockedEitherWay_False(t *testing.T) {
	t.Parallel()

	db, mock, err := sqlmock.New(sqlmock.QueryMatcherOption(sqlmock.QueryMatcherRegexp))
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()

	buyer, seller, _ := mustParticipantIDs(t)
	mock.ExpectQuery(`(?s)FROM user_blocks`).
		WithArgs(buyer.String(), seller.String()).
		WillReturnError(sql.ErrNoRows)

	repo := postgres.NewUserBlockRepository(db)
	ok, err := repo.IsBlockedEitherWay(context.Background(), buyer, seller)
	if err != nil || ok {
		t.Fatalf("ok=%v err=%v", ok, err)
	}
}

func TestUserBlockRepository_Remove(t *testing.T) {
	t.Parallel()

	db, mock, err := sqlmock.New(sqlmock.QueryMatcherOption(sqlmock.QueryMatcherRegexp))
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()

	buyer, seller, _ := mustParticipantIDs(t)
	mock.ExpectExec(`(?s)DELETE FROM user_blocks`).
		WithArgs(buyer.String(), seller.String()).
		WillReturnResult(sqlmock.NewResult(0, 1))

	repo := postgres.NewUserBlockRepository(db)
	if err := repo.Remove(context.Background(), buyer, seller); err != nil {
		t.Fatalf("Remove: %v", err)
	}
}
