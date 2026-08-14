package infrastructure_test

import (
	"context"
	"testing"

	"github.com/HDAI654/Kologram/chat_service/internal/domain"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/event"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/messaging"
	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/persistence/memory"
)

func mustUser(t *testing.T, raw string) valueobject.UserID {
	t.Helper()
	id, err := valueobject.NewUserID(raw)
	if err != nil {
		t.Fatal(err)
	}
	return id
}

func mustListing(t *testing.T, raw string) valueobject.ListingID {
	t.Helper()
	id, err := valueobject.NewListingID(raw)
	if err != nil {
		t.Fatal(err)
	}
	return id
}

func TestMemoryRepo_CRUD(t *testing.T) {
	ctx := context.Background()
	repo := memory.NewConversationRepository()
	buyer := mustUser(t, "550e8400-e29b-41d4-a716-446655440001")
	seller := mustUser(t, "550e8400-e29b-41d4-a716-446655440002")
	listing := mustListing(t, "550e8400-e29b-41d4-a716-446655440003")

	conv, err := domain.StartConversation(buyer, seller, listing)
	if err != nil {
		t.Fatal(err)
	}
	if err := repo.Add(ctx, conv); err != nil {
		t.Fatal(err)
	}

	loaded, err := repo.GetByID(ctx, conv.ID)
	if err != nil {
		t.Fatal(err)
	}
	if loaded.ID.String() != conv.ID.String() {
		t.Fatal("id mismatch")
	}

	content, _ := valueobject.NewMessageContent("hi")
	_, err = loaded.AddMessage(buyer, content)
	if err != nil {
		t.Fatal(err)
	}
	again, _ := repo.GetByID(ctx, conv.ID)
	if len(again.Messages) != 0 {
		t.Fatal("store should be unchanged without Update")
	}

	if err := repo.Update(ctx, loaded); err != nil {
		t.Fatal(err)
	}
	again, _ = repo.GetByID(ctx, conv.ID)
	if len(again.Messages) != 1 {
		t.Fatalf("messages=%d", len(again.Messages))
	}

	found, err := repo.FindByBuyerAndListing(ctx, buyer, listing)
	if err != nil {
		t.Fatal(err)
	}
	if found == nil || found.ID.String() != conv.ID.String() {
		t.Fatal("find by buyer+listing failed")
	}

	list, err := repo.ListForUser(ctx, buyer, 10, 0)
	if err != nil {
		t.Fatal(err)
	}
	if len(list) != 1 {
		t.Fatalf("list=%d", len(list))
	}

	_, err = repo.GetByID(ctx, valueobject.GenerateConversationID())
	if err != domain.ErrConversationNotFound {
		t.Fatalf("got %v", err)
	}
}

func TestMemoryUoWFactory(t *testing.T) {
	repo := memory.NewConversationRepository()
	factory := memory.NewUnitOfWorkFactory(repo)
	uow, err := factory.New(context.Background())
	if err != nil {
		t.Fatal(err)
	}
	if uow.Conversations() == nil {
		t.Fatal("nil repo")
	}
	if err := uow.Commit(context.Background()); err != nil {
		t.Fatal(err)
	}
	if err := uow.Rollback(context.Background()); err != nil {
		t.Fatal(err)
	}
}

func TestNoOpEventPublisher(t *testing.T) {
	pub := messaging.NewNoOpEventPublisher()
	err := pub.Publish(context.Background(), event.ConversationStarted{
		ConversationID: "x",
	})
	if err != nil {
		t.Fatal(err)
	}
}
