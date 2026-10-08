package application_test

import (
	"context"
	"errors"
	"testing"

	"github.com/HDAI654/Kologram/chat_service/internal/application"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
)

func TestMarkListingUnavailable_FreezesOpenConversations(t *testing.T) {
	t.Parallel()

	convs, _, _, _, uow, factory := NewFakeUowBundle()

	open := existingConversation(t)
	_ = convs.Add(context.Background(), open)

	already := existingConversation(t)
	already.IsReadOnly = true
	_ = convs.Add(context.Background(), already)

	// second open on same listing for another buyer
	otherBuyer := mustUserID(t, ThirdIDRaw)
	other, err := entities.StartConversation(otherBuyer, mustUserID(t, SellerIDRaw), mustListingID(t, ListingIDRaw))
	if err != nil {
		t.Fatalf("StartConversation: %v", err)
	}
	_ = convs.Add(context.Background(), other)

	h := application.NewMarkListingUnavailableHandler(factory, nil)
	result, err := h.Handle(context.Background(), application.MarkListingUnavailableCommand{
		ListingID: ListingIDRaw,
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result.ConversationsFrozen != 2 {
		t.Fatalf("ConversationsFrozen = %d, want 2 (skip already read-only)", result.ConversationsFrozen)
	}
	if !uow.Committed {
		t.Fatalf("expected commit")
	}

	for _, id := range []string{open.ID.String(), other.ID.String()} {
		c, _ := convs.GetByID(context.Background(), mustConversationID(t, id))
		if !c.IsReadOnly {
			t.Fatalf("conversation %s not frozen", id)
		}
	}
}

func TestMarkListingUnavailable_NoConversations(t *testing.T) {
	t.Parallel()

	_, _, _, _, uow, factory := NewFakeUowBundle()
	h := application.NewMarkListingUnavailableHandler(factory, nil)

	result, err := h.Handle(context.Background(), application.MarkListingUnavailableCommand{
		ListingID: ListingIDRaw,
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result.ConversationsFrozen != 0 {
		t.Fatalf("ConversationsFrozen = %d, want 0", result.ConversationsFrozen)
	}
	if !uow.Committed {
		t.Fatalf("expected commit")
	}
}

func TestMarkListingUnavailable_InvalidListingID(t *testing.T) {
	t.Parallel()

	_, _, _, _, _, factory := NewFakeUowBundle()
	h := application.NewMarkListingUnavailableHandler(factory, nil)

	_, err := h.Handle(context.Background(), application.MarkListingUnavailableCommand{
		ListingID: "bad",
	})
	if !errors.Is(err, domainerrors.ErrInvalidArgument) {
		t.Fatalf("err = %v, want ErrInvalidArgument", err)
	}
}

func TestMarkListingUnavailable_CommitError(t *testing.T) {
	t.Parallel()

	convs, _, _, _, uow, factory := NewFakeUowBundle()
	open := existingConversation(t)
	_ = convs.Add(context.Background(), open)
	uow.CommitErr = errors.New("commit failed")

	h := application.NewMarkListingUnavailableHandler(factory, nil)
	_, err := h.Handle(context.Background(), application.MarkListingUnavailableCommand{
		ListingID: ListingIDRaw,
	})
	if err == nil || err.Error() != "commit failed" {
		t.Fatalf("err = %v, want commit failed", err)
	}
}
