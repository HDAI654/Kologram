package postgres_test

import (
	"context"
	"database/sql"
	"errors"
	"testing"
	"time"

	"github.com/DATA-DOG/go-sqlmock"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/persistence/postgres"
)

func mustParticipantIDs(t *testing.T) (valueobjects.UserID, valueobjects.UserID, valueobjects.ListingID) {
	t.Helper()
	b, err := valueobjects.NewUserID("0d47ddfe-a4ca-446a-839e-d3bbcba824c6")
	if err != nil {
		t.Fatal(err)
	}
	s, err := valueobjects.NewUserID("bdf038e5-8b16-4825-a895-ce7d0648e845")
	if err != nil {
		t.Fatal(err)
	}
	l, err := valueobjects.NewListingID("431f7a61-1a30-4c3a-b2d4-5282ca2799b5")
	if err != nil {
		t.Fatal(err)
	}
	return b, s, l
}

func TestConversationRepository_Add_ExecutesInsert(t *testing.T) {
	t.Parallel()

	db, mock, err := sqlmock.New(sqlmock.QueryMatcherOption(sqlmock.QueryMatcherRegexp))
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()

	buyer, seller, listing := mustParticipantIDs(t)
	conv, err := entities.StartConversation(buyer, seller, listing)
	if err != nil {
		t.Fatal(err)
	}

	mock.ExpectExec(`(?s)INSERT INTO conversations`).
		WithArgs(
			conv.ID.String(), buyer.String(), seller.String(), listing.String(), false,
			nil, "", sqlmock.AnyArg(), sqlmock.AnyArg(), sqlmock.AnyArg(),
		).
		WillReturnResult(sqlmock.NewResult(0, 1))

	repo := postgres.NewConversationRepository(db)
	if err := repo.Add(context.Background(), conv); err != nil {
		t.Fatalf("Add: %v", err)
	}
	if err := mock.ExpectationsWereMet(); err != nil {
		t.Fatalf("unmet: %v", err)
	}
}

func TestConversationRepository_GetByID_NotFound(t *testing.T) {
	t.Parallel()

	db, mock, err := sqlmock.New(sqlmock.QueryMatcherOption(sqlmock.QueryMatcherRegexp))
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()

	id, _ := valueobjects.NewConversationID("0d47ddfe-a4ca-446a-839e-d3bbcba824c6")
	mock.ExpectQuery(`(?s)SELECT id, buyer_id`).
		WithArgs(id.String()).
		WillReturnError(sql.ErrNoRows)

	repo := postgres.NewConversationRepository(db)
	_, err = repo.GetByID(context.Background(), id)
	var nf *domainerrors.NotFoundError
	if !errors.As(err, &nf) {
		t.Fatalf("err = %v, want NotFoundError", err)
	}
}

func TestConversationRepository_FindByBuyerAndListing_None(t *testing.T) {
	t.Parallel()

	db, mock, err := sqlmock.New(sqlmock.QueryMatcherOption(sqlmock.QueryMatcherRegexp))
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()

	buyer, _, listing := mustParticipantIDs(t)
	mock.ExpectQuery(`(?s)SELECT id, buyer_id`).
		WithArgs(buyer.String(), listing.String()).
		WillReturnError(sql.ErrNoRows)

	repo := postgres.NewConversationRepository(db)
	got, err := repo.FindByBuyerAndListing(context.Background(), buyer, listing)
	if err != nil {
		t.Fatalf("err = %v", err)
	}
	if got != nil {
		t.Fatalf("want nil conversation")
	}
}

func TestConversationRepository_GetByID_MapsRow(t *testing.T) {
	t.Parallel()

	db, mock, err := sqlmock.New(sqlmock.QueryMatcherOption(sqlmock.QueryMatcherRegexp))
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()

	buyer, seller, listing := mustParticipantIDs(t)
	id, _ := valueobjects.NewConversationID("11111111-1111-4111-8111-111111111111")
	now := time.Now().UTC().Truncate(time.Second)
	msgID := "22222222-2222-4222-8222-222222222222"

	rows := sqlmock.NewRows([]string{
		"id", "buyer_id", "seller_id", "listing_id", "is_read_only",
		"last_message_id", "last_message_preview", "last_message_at",
		"created_at", "updated_at",
	}).AddRow(
		id.String(), buyer.String(), seller.String(), listing.String(), false,
		msgID, "hello", now, now, now,
	)
	mock.ExpectQuery(`(?s)SELECT id, buyer_id`).WithArgs(id.String()).WillReturnRows(rows)

	repo := postgres.NewConversationRepository(db)
	got, err := repo.GetByID(context.Background(), id)
	if err != nil {
		t.Fatalf("GetByID: %v", err)
	}
	if got.LastMessagePreview != "hello" {
		t.Fatalf("preview = %q", got.LastMessagePreview)
	}
	if got.LastMessageID.String() != msgID {
		t.Fatalf("LastMessageID = %q", got.LastMessageID.String())
	}
}

func TestConversationRepository_ListForUser_ActiveFilter(t *testing.T) {
	t.Parallel()

	db, mock, err := sqlmock.New(sqlmock.QueryMatcherOption(sqlmock.QueryMatcherRegexp))
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()

	buyer, seller, listing := mustParticipantIDs(t)
	cid, _ := valueobjects.NewConversationID("11111111-1111-4111-8111-111111111111")
	now := time.Now().UTC().Truncate(time.Second)

	rows := sqlmock.NewRows([]string{
		"id", "buyer_id", "seller_id", "listing_id", "is_read_only",
		"last_message_preview", "last_message_at", "created_at", "updated_at",
		"unread_count", "is_archived", "is_pinned", "muted_until",
	}).AddRow(
		cid.String(), buyer.String(), seller.String(), listing.String(), false,
		"hi", now, now, now, 2, false, true, nil,
	)

	mock.ExpectQuery(`(?s)FROM conversations c`).
		WithArgs(buyer.String(), false, 10).
		WillReturnRows(rows)

	repo := postgres.NewConversationRepository(db)
	items, err := repo.ListForUser(context.Background(), buyer, ports.ListFilterActive, nil, 10)
	if err != nil {
		t.Fatalf("ListForUser: %v", err)
	}
	if len(items) != 1 {
		t.Fatalf("len = %d", len(items))
	}
	if items[0].UnreadCount != 2 || !items[0].IsPinned {
		t.Fatalf("item = %+v", items[0])
	}
}

func TestConversationRepository_Update_NotFound(t *testing.T) {
	t.Parallel()

	db, mock, err := sqlmock.New(sqlmock.QueryMatcherOption(sqlmock.QueryMatcherRegexp))
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()

	buyer, seller, listing := mustParticipantIDs(t)
	conv, _ := entities.StartConversation(buyer, seller, listing)

	mock.ExpectExec(`(?s)UPDATE conversations SET`).
		WillReturnResult(sqlmock.NewResult(0, 0))

	repo := postgres.NewConversationRepository(db)
	err = repo.Update(context.Background(), conv)
	var nf *domainerrors.NotFoundError
	if !errors.As(err, &nf) {
		t.Fatalf("err = %v, want NotFoundError", err)
	}
}

func TestConversationRepository_Add_TranslatesDBError(t *testing.T) {
	t.Parallel()

	db, mock, err := sqlmock.New(sqlmock.QueryMatcherOption(sqlmock.QueryMatcherRegexp))
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()

	buyer, seller, listing := mustParticipantIDs(t)
	conv, _ := entities.StartConversation(buyer, seller, listing)

	mock.ExpectExec(`(?s)INSERT INTO conversations`).
		WillReturnError(errors.New("unique violation"))

	repo := postgres.NewConversationRepository(db)
	err = repo.Add(context.Background(), conv)
	var op *domainerrors.DatabaseOperationError
	if !errors.As(err, &op) {
		t.Fatalf("err = %v, want DatabaseOperationError", err)
	}
}
