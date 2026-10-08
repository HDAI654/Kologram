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

func TestMessageRepository_Add(t *testing.T) {
	t.Parallel()

	db, mock, err := sqlmock.New(sqlmock.QueryMatcherOption(sqlmock.QueryMatcherRegexp))
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()

	buyer, _, _ := mustParticipantIDs(t)
	cid, _ := valueobjects.NewConversationID("11111111-1111-4111-8111-111111111111")
	content, _ := valueobjects.NewMessageContent("hello")
	msg, err := entities.NewMessage(cid, buyer, "33333333-3333-4333-8333-333333333333", content)
	if err != nil {
		t.Fatal(err)
	}

	mock.ExpectExec(`(?s)INSERT INTO messages`).
		WithArgs(
			msg.ID.String(), cid.String(), buyer.String(), "hello", sqlmock.AnyArg(),
			msg.ClientMessageID, false, nil,
		).
		WillReturnResult(sqlmock.NewResult(0, 1))

	repo := postgres.NewMessageRepository(db)
	if err := repo.Add(context.Background(), &msg); err != nil {
		t.Fatalf("Add: %v", err)
	}
}

func TestMessageRepository_FindLatestVisible_None(t *testing.T) {
	t.Parallel()

	db, mock, err := sqlmock.New(sqlmock.QueryMatcherOption(sqlmock.QueryMatcherRegexp))
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()

	cid, _ := valueobjects.NewConversationID("11111111-1111-4111-8111-111111111111")
	mock.ExpectQuery(`(?s)deleted_for_everyone = FALSE`).
		WithArgs(cid.String()).
		WillReturnError(sql.ErrNoRows)

	repo := postgres.NewMessageRepository(db)
	got, err := repo.FindLatestVisible(context.Background(), cid)
	if err != nil {
		t.Fatalf("err = %v", err)
	}
	if got != nil {
		t.Fatalf("want nil")
	}
}

func TestMessageRepository_ListMessages_Older(t *testing.T) {
	t.Parallel()

	db, mock, err := sqlmock.New(sqlmock.QueryMatcherOption(sqlmock.QueryMatcherRegexp))
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()

	buyer, _, _ := mustParticipantIDs(t)
	cid, _ := valueobjects.NewConversationID("11111111-1111-4111-8111-111111111111")
	mid, _ := valueobjects.NewMessageID("22222222-2222-4222-8222-222222222222")
	now := time.Now().UTC().Truncate(time.Second)

	rows := sqlmock.NewRows([]string{
		"id", "conversation_id", "sender_id", "content", "sent_at",
		"client_message_id", "deleted_for_everyone", "deleted_at",
	}).AddRow(
		mid.String(), cid.String(), buyer.String(), "hi", now,
		"33333333-3333-4333-8333-333333333333", false, nil,
	)

	mock.ExpectQuery(`(?s)deleted_for_everyone = FALSE`).
		WithArgs(cid.String(), 50).
		WillReturnRows(rows)

	repo := postgres.NewMessageRepository(db)
	list, err := repo.ListMessages(context.Background(), cid, nil, ports.DirectionOlder, 50)
	if err != nil {
		t.Fatalf("ListMessages: %v", err)
	}
	if len(list) != 1 || list[0].Content.String() != "hi" {
		t.Fatalf("list = %+v", list)
	}
}

func TestMessageRepository_GetByID_NotFound(t *testing.T) {
	t.Parallel()

	db, mock, err := sqlmock.New(sqlmock.QueryMatcherOption(sqlmock.QueryMatcherRegexp))
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()

	mid, _ := valueobjects.NewMessageID("22222222-2222-4222-8222-222222222222")
	mock.ExpectQuery(`(?s)FROM messages WHERE id`).
		WithArgs(mid.String()).
		WillReturnError(sql.ErrNoRows)

	repo := postgres.NewMessageRepository(db)
	_, err = repo.GetByID(context.Background(), mid)
	var nf *domainerrors.NotFoundError
	if !errors.As(err, &nf) {
		t.Fatalf("err = %v, want NotFoundError", err)
	}
}

func TestMessageRepository_FindByClientMessageID_None(t *testing.T) {
	t.Parallel()

	db, mock, err := sqlmock.New(sqlmock.QueryMatcherOption(sqlmock.QueryMatcherRegexp))
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()

	buyer, _, _ := mustParticipantIDs(t)
	cid, _ := valueobjects.NewConversationID("11111111-1111-4111-8111-111111111111")
	client := "33333333-3333-4333-8333-333333333333"

	mock.ExpectQuery(`(?s)client_message_id`).
		WithArgs(buyer.String(), cid.String(), client).
		WillReturnError(sql.ErrNoRows)

	repo := postgres.NewMessageRepository(db)
	got, err := repo.FindByClientMessageID(context.Background(), buyer, cid, client)
	if err != nil || got != nil {
		t.Fatalf("got=%v err=%v", got, err)
	}
}

func TestMessageRepository_ListMessages_NewerRequiresCursor(t *testing.T) {
	t.Parallel()

	db, _, err := sqlmock.New()
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()

	cid, _ := valueobjects.NewConversationID("11111111-1111-4111-8111-111111111111")
	repo := postgres.NewMessageRepository(db)
	_, err = repo.ListMessages(context.Background(), cid, nil, ports.DirectionNewer, 10)
	var ve *domainerrors.ValidationError
	if !errors.As(err, &ve) {
		t.Fatalf("err = %v, want ValidationError", err)
	}
}
