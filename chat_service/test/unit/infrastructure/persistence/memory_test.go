package persistence_test

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/persistence/memory"
)

func TestMemory_ConversationAndMessageFlow(t *testing.T) {
	t.Parallel()

	store := memory.NewStore()
	factory := memory.NewUnitOfWorkFactory(store)
	uow, err := factory.New(context.Background())
	if err != nil {
		t.Fatalf("New uow: %v", err)
	}

	buyer, _ := valueobjects.NewUserID("0d47ddfe-a4ca-446a-839e-d3bbcba824c6")
	seller, _ := valueobjects.NewUserID("bdf038e5-8b16-4825-a895-ce7d0648e845")
	listing, _ := valueobjects.NewListingID("431f7a61-1a30-4c3a-b2d4-5282ca2799b5")

	conv, err := entities.StartConversation(buyer, seller, listing)
	if err != nil {
		t.Fatalf("StartConversation: %v", err)
	}
	if err := uow.Conversations().Add(context.Background(), conv); err != nil {
		t.Fatalf("Add conversation: %v", err)
	}

	now := time.Now().UTC()
	for _, uid := range conv.ParticipantIDs() {
		st := entities.NewConversationUserState(conv.ID, uid, now)
		if err := uow.ConversationStates().Add(context.Background(), st); err != nil {
			t.Fatalf("Add state: %v", err)
		}
	}

	content, _ := valueobjects.NewMessageContent("hello")
	msg, err := entities.NewMessage(conv.ID, buyer, "11111111-1111-4111-8111-111111111111", content)
	if err != nil {
		t.Fatalf("NewMessage: %v", err)
	}
	if err := uow.Messages().Add(context.Background(), &msg); err != nil {
		t.Fatalf("Add message: %v", err)
	}
	conv.RecordLastMessage(msg)
	if err := uow.Conversations().Update(context.Background(), conv); err != nil {
		t.Fatalf("Update conversation: %v", err)
	}
	if err := uow.Commit(context.Background()); err != nil {
		t.Fatalf("Commit: %v", err)
	}

	found, err := uow.Conversations().FindByBuyerAndListing(context.Background(), buyer, listing)
	if err != nil || found == nil {
		t.Fatalf("FindByBuyerAndListing: %v %v", found, err)
	}
	if found.LastMessagePreview != "hello" {
		t.Fatalf("preview = %q", found.LastMessagePreview)
	}

	list, err := uow.Messages().ListMessages(context.Background(), conv.ID, nil, ports.DirectionOlder, 10)
	if err != nil {
		t.Fatalf("ListMessages: %v", err)
	}
	if len(list) != 1 {
		t.Fatalf("list len = %d, want 1", len(list))
	}

	if err := msg.DeleteForEveryone(buyer); err != nil {
		t.Fatalf("DeleteForEveryone: %v", err)
	}
	if err := uow.Messages().Update(context.Background(), &msg); err != nil {
		t.Fatalf("Update message: %v", err)
	}
	visible, err := uow.Messages().FindLatestVisible(context.Background(), conv.ID)
	if err != nil {
		t.Fatalf("FindLatestVisible: %v", err)
	}
	if visible != nil {
		t.Fatalf("expected no visible messages after soft-delete")
	}
}

func TestMemory_GetConversationNotFound(t *testing.T) {
	t.Parallel()

	store := memory.NewStore()
	repo := memory.NewConversationRepository(store)
	id, _ := valueobjects.NewConversationID("0d47ddfe-a4ca-446a-839e-d3bbcba824c6")
	_, err := repo.GetByID(context.Background(), id)
	var nf *domainerrors.NotFoundError
	if !errors.As(err, &nf) {
		t.Fatalf("err = %v, want NotFoundError", err)
	}
}

func TestMemory_BlockEitherWay(t *testing.T) {
	t.Parallel()

	store := memory.NewStore()
	repo := memory.NewUserBlockRepository(store)
	a, _ := valueobjects.NewUserID("0d47ddfe-a4ca-446a-839e-d3bbcba824c6")
	b, _ := valueobjects.NewUserID("bdf038e5-8b16-4825-a895-ce7d0648e845")

	block, err := entities.NewUserBlock(a, b)
	if err != nil {
		t.Fatalf("NewUserBlock: %v", err)
	}
	if err := repo.Add(context.Background(), block); err != nil {
		t.Fatalf("Add: %v", err)
	}
	blocked, err := repo.IsBlockedEitherWay(context.Background(), b, a)
	if err != nil || !blocked {
		t.Fatalf("IsBlockedEitherWay = %v, %v", blocked, err)
	}
}
