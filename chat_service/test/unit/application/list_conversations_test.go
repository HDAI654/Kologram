package application_test

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/application"
	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

func sampleListItem(id string, pinned bool) ports.ConversationListItem {
	cid, _ := valueobjects.NewConversationID(id)
	buyer, _ := valueobjects.NewUserID(BuyerIDRaw)
	seller, _ := valueobjects.NewUserID(SellerIDRaw)
	listing, _ := valueobjects.NewListingID(ListingIDRaw)
	return ports.ConversationListItem{
		ConversationID:     cid,
		BuyerID:            buyer,
		SellerID:           seller,
		ListingID:          listing,
		LastMessagePreview: "hi",
		LastMessageAt:      time.Now().UTC(),
		IsPinned:           pinned,
	}
}

func TestListConversations_Success_HasMore(t *testing.T) {
	t.Parallel()

	convs := NewFakeConversationRepository()
	convs.ListItems = []ports.ConversationListItem{
		sampleListItem("11111111-1111-4111-8111-111111111111", true),
		sampleListItem("22222222-2222-4222-8222-222222222222", false),
		sampleListItem("33333333-3333-4333-8333-333333333333", false),
	}

	h := application.NewListConversationsHandler(convs)
	result, err := h.Handle(context.Background(), application.ListConversationsQuery{
		UserID: BuyerIDRaw,
		Filter: "active",
		Limit:  2,
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(result.Items) != 2 {
		t.Fatalf("items = %d, want 2", len(result.Items))
	}
	if !result.HasMore {
		t.Fatalf("HasMore = false, want true")
	}
	if result.Items[0].ConversationID != "11111111-1111-4111-8111-111111111111" {
		t.Fatalf("unexpected first item")
	}
}

func TestListConversations_DefaultFilterActive(t *testing.T) {
	t.Parallel()

	convs := NewFakeConversationRepository()
	convs.ListItems = []ports.ConversationListItem{
		sampleListItem("11111111-1111-4111-8111-111111111111", false),
	}
	h := application.NewListConversationsHandler(convs)
	result, err := h.Handle(context.Background(), application.ListConversationsQuery{
		UserID: BuyerIDRaw,
		// Filter empty → active
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(result.Items) != 1 {
		t.Fatalf("items = %d, want 1", len(result.Items))
	}
}

func TestListConversations_InvalidFilter(t *testing.T) {
	t.Parallel()

	h := application.NewListConversationsHandler(NewFakeConversationRepository())
	_, err := h.Handle(context.Background(), application.ListConversationsQuery{
		UserID: BuyerIDRaw,
		Filter: "spam",
	})
	var ve *domainerrors.ValidationError
	if !errors.As(err, &ve) || ve.Field != "filter" {
		t.Fatalf("err = %v, want ValidationError field filter", err)
	}
}

func TestListConversations_InvalidUserID(t *testing.T) {
	t.Parallel()

	h := application.NewListConversationsHandler(NewFakeConversationRepository())
	_, err := h.Handle(context.Background(), application.ListConversationsQuery{
		UserID: "bad",
	})
	if !errors.Is(err, domainerrors.ErrInvalidArgument) {
		t.Fatalf("err = %v, want ErrInvalidArgument", err)
	}
}

func TestListConversations_InvalidCursorTime(t *testing.T) {
	t.Parallel()

	h := application.NewListConversationsHandler(NewFakeConversationRepository())
	_, err := h.Handle(context.Background(), application.ListConversationsQuery{
		UserID:              BuyerIDRaw,
		CursorID:            "11111111-1111-4111-8111-111111111111",
		CursorLastMessageAt: "nope",
	})
	var ve *domainerrors.ValidationError
	if !errors.As(err, &ve) || ve.Field != "cursor_last_message_at" {
		t.Fatalf("err = %v, want ValidationError field cursor_last_message_at", err)
	}
}

func TestListConversations_RepoError(t *testing.T) {
	t.Parallel()

	convs := NewFakeConversationRepository()
	convs.ListErr = errors.New("db down")
	h := application.NewListConversationsHandler(convs)
	_, err := h.Handle(context.Background(), application.ListConversationsQuery{
		UserID: BuyerIDRaw,
	})
	if err == nil || err.Error() != "db down" {
		t.Fatalf("err = %v, want db down", err)
	}
}
