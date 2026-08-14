package application_test

import (
	"context"
	"testing"

	"github.com/HDAI654/Kologram/chat_service/internal/application"
	"github.com/HDAI654/Kologram/chat_service/internal/domain"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/event"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

func TestStartConversation_Success(t *testing.T) {
	factory, repo, events, _ := newMocks()
	repo.FindByBuyerAndListingFn = func(ctx context.Context, buyerID valueobject.UserID, listingID valueobject.ListingID) (*domain.Conversation, error) {
		return nil, nil
	}
	handler := application.NewStartConversationHandler(factory, events)

	result, err := handler.Handle(context.Background(), application.StartConversationCommand{
		BuyerID: buyerID, SellerID: sellerID, ListingID: listingID,
	})
	if err != nil {
		t.Fatal(err)
	}
	if !result.Created {
		t.Fatal("expected created")
	}
	if result.Status != "OPEN" {
		t.Fatalf("status=%s", result.Status)
	}
	if repo.AddCalls != 1 {
		t.Fatalf("add calls=%d", repo.AddCalls)
	}
	if factory.uow.committed != true {
		t.Fatal("expected commit")
	}
	if _, ok := events.Last().(event.ConversationStarted); !ok {
		t.Fatalf("expected ConversationStarted, got %T", events.Last())
	}
}

func TestStartConversation_IdempotentExisting(t *testing.T) {
	factory, repo, events, _ := newMocks()
	existing := openConversation()
	repo.FindByBuyerAndListingFn = func(ctx context.Context, buyerID valueobject.UserID, listingID valueobject.ListingID) (*domain.Conversation, error) {
		return existing, nil
	}
	handler := application.NewStartConversationHandler(factory, events)

	result, err := handler.Handle(context.Background(), application.StartConversationCommand{
		BuyerID: buyerID, SellerID: sellerID, ListingID: listingID,
	})
	if err != nil {
		t.Fatal(err)
	}
	if result.Created {
		t.Fatal("should not create again")
	}
	if result.ConversationID != existing.ID.String() {
		t.Fatal("should return existing id")
	}
	if repo.AddCalls != 0 {
		t.Fatal("should not add")
	}
	if events.Last() != nil {
		t.Fatal("should not publish")
	}
}

func TestStartConversation_SameBuyerSeller(t *testing.T) {
	factory, repo, events, _ := newMocks()
	repo.FindByBuyerAndListingFn = func(ctx context.Context, buyerID valueobject.UserID, listingID valueobject.ListingID) (*domain.Conversation, error) {
		return nil, nil
	}
	handler := application.NewStartConversationHandler(factory, events)

	_, err := handler.Handle(context.Background(), application.StartConversationCommand{
		BuyerID: buyerID, SellerID: buyerID, ListingID: listingID,
	})
	if err != domain.ErrBuyerSellerSame {
		t.Fatalf("got %v", err)
	}
}

func TestStartConversation_InvalidUserID(t *testing.T) {
	factory, _, events, _ := newMocks()
	handler := application.NewStartConversationHandler(factory, events)
	_, err := handler.Handle(context.Background(), application.StartConversationCommand{
		BuyerID: "bad", SellerID: sellerID, ListingID: listingID,
	})
	if err == nil {
		t.Fatal("expected validation error")
	}
}
