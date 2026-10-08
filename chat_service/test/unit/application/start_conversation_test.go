package application_test

import (
	"context"
	"errors"
	"testing"

	"github.com/HDAI654/Kologram/chat_service/internal/application"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/events"
)

func TestStartConversation_CreatesNewConversation(t *testing.T) {
	t.Parallel()

	convs, states, _, blocks, uow, factory := NewFakeUowBundle()
	listings := NewFakeListingRepository()
	listings.ByID[ListingIDRaw] = messageableListing(t)
	publisher := NewFakeEventPublisher()

	h := application.NewStartConversationHandler(factory, listings, publisher, nil)

	result, err := h.Handle(context.Background(), application.StartConversationCommand{
		BuyerID:   BuyerIDRaw,
		ListingID: ListingIDRaw,
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !result.Created {
		t.Fatalf("Created = false, want true")
	}
	if result.ConversationID == "" {
		t.Fatalf("ConversationID is empty")
	}
	if result.IsReadOnly {
		t.Fatalf("IsReadOnly = true, want false")
	}
	if !uow.Committed {
		t.Fatalf("expected commit")
	}

	stored, ok := convs.ByID[result.ConversationID]
	if !ok {
		t.Fatalf("conversation not persisted")
	}
	if stored.BuyerID.String() != BuyerIDRaw || stored.SellerID.String() != SellerIDRaw {
		t.Fatalf("participants mismatch: buyer=%s seller=%s", stored.BuyerID, stored.SellerID)
	}

	if len(states.ByKey) != 2 {
		t.Fatalf("state rows = %d, want 2", len(states.ByKey))
	}

	if publisher.Count() != 1 {
		t.Fatalf("events = %d, want 1", publisher.Count())
	}
	evt, ok := publisher.Events[0].(events.ConversationStarted)
	if !ok {
		t.Fatalf("event type = %T, want ConversationStarted", publisher.Events[0])
	}
	if evt.ConversationID != result.ConversationID {
		t.Fatalf("event ConversationID = %q, want %q", evt.ConversationID, result.ConversationID)
	}
	if evt.BuyerID != BuyerIDRaw || evt.SellerID != SellerIDRaw || evt.ListingID != ListingIDRaw {
		t.Fatalf("event participants mismatch: %+v", evt)
	}

	_ = blocks
}

func TestStartConversation_ReturnsExistingWithoutEvent(t *testing.T) {
	t.Parallel()

	convs, states, _, _, uow, factory := NewFakeUowBundle()
	existing := existingConversation(t)
	_ = convs.Add(context.Background(), existing)

	listings := NewFakeListingRepository()
	listings.ByID[ListingIDRaw] = messageableListing(t)
	publisher := NewFakeEventPublisher()

	h := application.NewStartConversationHandler(factory, listings, publisher, nil)

	result, err := h.Handle(context.Background(), application.StartConversationCommand{
		BuyerID:   BuyerIDRaw,
		ListingID: ListingIDRaw,
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result.Created {
		t.Fatalf("Created = true, want false")
	}
	if result.ConversationID != existing.ID.String() {
		t.Fatalf("ConversationID = %q, want %q", result.ConversationID, existing.ID.String())
	}
	if uow.Committed {
		t.Fatalf("must not commit when returning existing")
	}
	if publisher.Count() != 0 {
		t.Fatalf("events = %d, want 0", publisher.Count())
	}
	if len(states.ByKey) != 0 {
		t.Fatalf("must not create new states for existing conversation")
	}
}

func TestStartConversation_RejectsInvalidBuyerID(t *testing.T) {
	t.Parallel()

	_, _, _, _, _, factory := NewFakeUowBundle()
	h := application.NewStartConversationHandler(factory, NewFakeListingRepository(), NewFakeEventPublisher(), nil)

	_, err := h.Handle(context.Background(), application.StartConversationCommand{
		BuyerID:   "not-a-uuid",
		ListingID: ListingIDRaw,
	})
	if !errors.Is(err, domainerrors.ErrInvalidArgument) {
		t.Fatalf("err = %v, want ErrInvalidArgument", err)
	}
}

func TestStartConversation_RejectsInvalidListingID(t *testing.T) {
	t.Parallel()

	_, _, _, _, _, factory := NewFakeUowBundle()
	h := application.NewStartConversationHandler(factory, NewFakeListingRepository(), NewFakeEventPublisher(), nil)

	_, err := h.Handle(context.Background(), application.StartConversationCommand{
		BuyerID:   BuyerIDRaw,
		ListingID: "bad",
	})
	if !errors.Is(err, domainerrors.ErrInvalidArgument) {
		t.Fatalf("err = %v, want ErrInvalidArgument", err)
	}
}

func TestStartConversation_ListingNotFound(t *testing.T) {
	t.Parallel()

	_, _, _, _, _, factory := NewFakeUowBundle()
	listings := NewFakeListingRepository() // empty
	h := application.NewStartConversationHandler(factory, listings, NewFakeEventPublisher(), nil)

	_, err := h.Handle(context.Background(), application.StartConversationCommand{
		BuyerID:   BuyerIDRaw,
		ListingID: ListingIDRaw,
	})
	var nf *domainerrors.NotFoundError
	if !errors.As(err, &nf) {
		t.Fatalf("err = %v, want NotFoundError", err)
	}
	if nf.Field != "listing_id" {
		t.Fatalf("Field = %q, want listing_id", nf.Field)
	}
}

func TestStartConversation_ListingRepoError(t *testing.T) {
	t.Parallel()

	_, _, _, _, _, factory := NewFakeUowBundle()
	listings := NewFakeListingRepository()
	listings.Err = errors.New("market down")
	h := application.NewStartConversationHandler(factory, listings, NewFakeEventPublisher(), nil)

	_, err := h.Handle(context.Background(), application.StartConversationCommand{
		BuyerID:   BuyerIDRaw,
		ListingID: ListingIDRaw,
	})
	if err == nil || err.Error() != "market down" {
		t.Fatalf("err = %v, want market down", err)
	}
}

func TestStartConversation_RejectsBuyerIsSeller(t *testing.T) {
	t.Parallel()

	_, _, _, _, _, factory := NewFakeUowBundle()
	listings := NewFakeListingRepository()
	listings.ByID[ListingIDRaw] = messageableListing(t)
	h := application.NewStartConversationHandler(factory, listings, NewFakeEventPublisher(), nil)

	_, err := h.Handle(context.Background(), application.StartConversationCommand{
		BuyerID:   SellerIDRaw, // same as listing seller
		ListingID: ListingIDRaw,
	})
	if !errors.Is(err, domainerrors.ErrBuyerSellerSame) {
		t.Fatalf("err = %v, want ErrBuyerSellerSame", err)
	}
}

func TestStartConversation_RejectsListingNotMessageable(t *testing.T) {
	t.Parallel()

	_, _, _, _, _, factory := NewFakeUowBundle()
	listings := NewFakeListingRepository()
	listing := messageableListing(t)
	listing.MessageAllowed = false
	listings.ByID[ListingIDRaw] = listing
	h := application.NewStartConversationHandler(factory, listings, NewFakeEventPublisher(), nil)

	_, err := h.Handle(context.Background(), application.StartConversationCommand{
		BuyerID:   BuyerIDRaw,
		ListingID: ListingIDRaw,
	})
	if !errors.Is(err, domainerrors.ErrListingNotMessageable) {
		t.Fatalf("err = %v, want ErrListingNotMessageable", err)
	}
}

func TestStartConversation_RejectsWhenUsersBlocked(t *testing.T) {
	t.Parallel()

	_, _, _, blocks, _, factory := NewFakeUowBundle()
	blocks.ForceEitherWay(true)
	listings := NewFakeListingRepository()
	listings.ByID[ListingIDRaw] = messageableListing(t)
	publisher := NewFakeEventPublisher()
	h := application.NewStartConversationHandler(factory, listings, publisher, nil)

	_, err := h.Handle(context.Background(), application.StartConversationCommand{
		BuyerID:   BuyerIDRaw,
		ListingID: ListingIDRaw,
	})
	if !errors.Is(err, domainerrors.ErrUsersBlocked) {
		t.Fatalf("err = %v, want ErrUsersBlocked", err)
	}
	if publisher.Count() != 0 {
		t.Fatalf("must not publish event on blocked failure")
	}
}

func TestStartConversation_UowFactoryError(t *testing.T) {
	t.Parallel()

	_, _, _, _, _, factory := NewFakeUowBundle()
	factory.Err = errors.New("uow failed")
	listings := NewFakeListingRepository()
	listings.ByID[ListingIDRaw] = messageableListing(t)
	h := application.NewStartConversationHandler(factory, listings, NewFakeEventPublisher(), nil)

	_, err := h.Handle(context.Background(), application.StartConversationCommand{
		BuyerID:   BuyerIDRaw,
		ListingID: ListingIDRaw,
	})
	if err == nil || err.Error() != "uow failed" {
		t.Fatalf("err = %v, want uow failed", err)
	}
}

func TestStartConversation_CommitError_DoesNotPublishEvent(t *testing.T) {
	t.Parallel()

	_, _, _, _, uow, factory := NewFakeUowBundle()
	uow.CommitErr = errors.New("commit failed")
	listings := NewFakeListingRepository()
	listings.ByID[ListingIDRaw] = messageableListing(t)
	publisher := NewFakeEventPublisher()
	h := application.NewStartConversationHandler(factory, listings, publisher, nil)

	_, err := h.Handle(context.Background(), application.StartConversationCommand{
		BuyerID:   BuyerIDRaw,
		ListingID: ListingIDRaw,
	})
	if err == nil || err.Error() != "commit failed" {
		t.Fatalf("err = %v, want commit failed", err)
	}
	if publisher.Count() != 0 {
		t.Fatalf("must not publish after failed commit")
	}
}

func TestStartConversation_ReturnsExistingReadOnlyFlag(t *testing.T) {
	t.Parallel()

	convs, _, _, _, _, factory := NewFakeUowBundle()
	existing := existingConversation(t)
	existing.IsReadOnly = true
	_ = convs.Add(context.Background(), existing)

	listings := NewFakeListingRepository()
	listings.ByID[ListingIDRaw] = messageableListing(t)
	h := application.NewStartConversationHandler(factory, listings, NewFakeEventPublisher(), nil)

	result, err := h.Handle(context.Background(), application.StartConversationCommand{
		BuyerID:   BuyerIDRaw,
		ListingID: ListingIDRaw,
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result.Created {
		t.Fatalf("Created = true, want false")
	}
	if !result.IsReadOnly {
		t.Fatalf("IsReadOnly = false, want true")
	}
}

// silence unused import guard for entities in case of future fixtures
var _ = entities.Conversation{}
