package entities_test

import (
	"errors"
	"testing"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

// ---------------------------------------------------------------------------
// StartConversation
// ---------------------------------------------------------------------------

func TestStartConversation_PopulatesAllFields(t *testing.T) {
	t.Parallel()

	buyer := FixedBuyerID
	seller := FixedSellerID
	listing := FixedListingID

	before := time.Now().UTC()
	conv, err := entities.StartConversation(buyer, seller, listing)
	after := time.Now().UTC()
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if conv == nil {
		t.Fatalf("conversation is nil")
	}
	if conv.ID.String() == "" {
		t.Fatalf("ConversationID is empty")
	}
	if !conv.BuyerID.Equals(buyer) {
		t.Fatalf("BuyerID mismatch")
	}
	if !conv.SellerID.Equals(seller) {
		t.Fatalf("SellerID mismatch")
	}
	if conv.ListingID.String() != listing.String() {
		t.Fatalf("ListingID mismatch")
	}
	if !conv.Status.Equals(valueobjects.StatusOpen) {
		t.Fatalf("Status = %s, want OPEN", conv.Status.String())
	}
	if conv.CreatedAt.Before(before) || conv.CreatedAt.After(after) {
		t.Fatalf("CreatedAt = %v, want within [%v, %v]", conv.CreatedAt, before, after)
	}
	if !conv.CreatedAt.Equal(conv.UpdatedAt) {
		t.Fatalf("CreatedAt != UpdatedAt on fresh conversation")
	}
}

func TestStartConversation_LeavesPreviewEmpty(t *testing.T) {
	t.Parallel()

	conv, err := entities.StartConversation(FixedBuyerID, FixedSellerID, FixedListingID)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if conv.LastMessagePreview != "" {
		t.Fatalf("LastMessagePreview = %q, want empty on fresh conversation", conv.LastMessagePreview)
	}
	if !conv.LastMessageAt.IsZero() {
		t.Fatalf("LastMessageAt = %v, want zero on fresh conversation", conv.LastMessageAt)
	}
}

func TestStartConversation_RejectsSameBuyerAndSeller(t *testing.T) {
	t.Parallel()

	same := FixedBuyerID
	listing := FixedListingID

	conv, err := entities.StartConversation(same, same, listing)

	if !errors.Is(err, domainerrors.ErrBuyerSellerSame) {
		t.Fatalf("err = %v, want ErrBuyerSellerSame", err)
	}
	if !errors.Is(err, domainerrors.ErrInvalidArgument) {
		t.Fatalf("err = %v, want category ErrInvalidArgument", err)
	}
	if conv != nil {
		t.Fatalf("conversation = %v, want nil", conv)
	}
}

func TestStartConversation_GeneratesUniqueIDs(t *testing.T) {
	t.Parallel()

	a, err := entities.StartConversation(FixedBuyerID, FixedSellerID, FixedListingID)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	b, err := entities.StartConversation(FixedBuyerID, FixedSellerID, FixedListingID)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if a.ID.String() == b.ID.String() {
		t.Fatalf("two calls returned same ConversationID: %s", a.ID.String())
	}
}

// ---------------------------------------------------------------------------
// IsParticipant
// ---------------------------------------------------------------------------

func TestConversation_IsParticipant(t *testing.T) {
	t.Parallel()

	conv := newOpenConversation(t)

	cases := []struct {
		name string
		id   valueobjects.UserID
		want bool
	}{
		{"buyer is participant", conv.BuyerID, true},
		{"seller is participant", conv.SellerID, true},
		{"third party is not", FixedThirdPartyID, false},
	}

	for _, tc := range cases {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()
			if got := conv.IsParticipant(tc.id); got != tc.want {
				t.Fatalf("IsParticipant = %v, want %v", got, tc.want)
			}
		})
	}
}

// ---------------------------------------------------------------------------
// RecordLastMessage
// ---------------------------------------------------------------------------

func TestConversation_RecordLastMessage_SetsPreviewAndTimestamp(t *testing.T) {
	t.Parallel()

	conv := newOpenConversation(t)
	content := mustContent(t, "hello there")

	before := time.Now().UTC()
	conv.RecordLastMessage(content)
	after := time.Now().UTC()

	if conv.LastMessagePreview != "hello there" {
		t.Fatalf("LastMessagePreview = %q, want %q", conv.LastMessagePreview, "hello there")
	}
	if conv.LastMessageAt.Before(before) || conv.LastMessageAt.After(after) {
		t.Fatalf("LastMessageAt = %v, want within [%v, %v]", conv.LastMessageAt, before, after)
	}
}

func TestConversation_RecordLastMessage_AdvancesUpdatedAt(t *testing.T) {
	t.Parallel()

	conv := newOpenConversation(t)
	original := conv.UpdatedAt
	time.Sleep(time.Millisecond)

	conv.RecordLastMessage(mustContent(t, "hi"))

	if !conv.UpdatedAt.After(original) {
		t.Fatalf("UpdatedAt not advanced: before=%v after=%v", original, conv.UpdatedAt)
	}
	if !conv.UpdatedAt.Equal(conv.LastMessageAt) {
		t.Fatalf("UpdatedAt != LastMessageAt after RecordLastMessage")
	}
}

func TestConversation_RecordLastMessage_OverwritesPreviousPreview(t *testing.T) {
	t.Parallel()

	conv := newOpenConversation(t)

	conv.RecordLastMessage(mustContent(t, "first"))
	firstAt := conv.LastMessageAt
	time.Sleep(time.Millisecond)

	conv.RecordLastMessage(mustContent(t, "second"))

	if conv.LastMessagePreview != "second" {
		t.Fatalf("LastMessagePreview = %q, want %q", conv.LastMessagePreview, "second")
	}
	if !conv.LastMessageAt.After(firstAt) {
		t.Fatalf("LastMessageAt not advanced: first=%v, second=%v", firstAt, conv.LastMessageAt)
	}
}

func TestConversation_RecordLastMessage_UsesTrimmedContent(t *testing.T) {
	t.Parallel()

	conv := newOpenConversation(t)
	content := mustContent(t, "  padded message  ")

	conv.RecordLastMessage(content)

	if conv.LastMessagePreview != "padded message" {
		t.Fatalf("LastMessagePreview = %q, want %q", conv.LastMessagePreview, "padded message")
	}
}

// ---------------------------------------------------------------------------
// TransitionStatus
// ---------------------------------------------------------------------------

func TestConversation_TransitionStatus_Matrix(t *testing.T) {
	t.Parallel()

	type tc struct {
		name    string
		from    valueobjects.ConversationStatus
		to      valueobjects.ConversationStatus
		wantErr error
	}

	cases := []tc{
		{"open→closed", valueobjects.StatusOpen, valueobjects.StatusClosed, nil},
		{"open→archived", valueobjects.StatusOpen, valueobjects.StatusArchived, nil},
		{"open→open", valueobjects.StatusOpen, valueobjects.StatusOpen, domainerrors.ErrInvalidStatusTransition},

		{"closed→open", valueobjects.StatusClosed, valueobjects.StatusOpen, nil},
		{"closed→archived", valueobjects.StatusClosed, valueobjects.StatusArchived, nil},
		{"closed→closed", valueobjects.StatusClosed, valueobjects.StatusClosed, domainerrors.ErrInvalidStatusTransition},

		{"archived→open", valueobjects.StatusArchived, valueobjects.StatusOpen, domainerrors.ErrInvalidStatusTransition},
		{"archived→closed", valueobjects.StatusArchived, valueobjects.StatusClosed, domainerrors.ErrInvalidStatusTransition},
		{"archived→archived", valueobjects.StatusArchived, valueobjects.StatusArchived, domainerrors.ErrInvalidStatusTransition},
	}

	for _, c := range cases {
		c := c
		t.Run(c.name, func(t *testing.T) {
			t.Parallel()

			var conv *entities.Conversation
			if c.from.Equals(valueobjects.StatusOpen) {
				conv = newOpenConversation(t)
			} else {
				conv = newConversationInStatus(t, c.from)
			}
			actor := conv.BuyerID

			err := conv.TransitionStatus(c.to, actor)

			switch {
			case c.wantErr == nil && err != nil:
				t.Fatalf("err = %v, want nil", err)
			case c.wantErr != nil && !errors.Is(err, c.wantErr):
				t.Fatalf("err = %v, want %v", err, c.wantErr)
			}

			if c.wantErr == nil {
				if !conv.Status.Equals(c.to) {
					t.Fatalf("status = %s, want %s", conv.Status.String(), c.to.String())
				}
			} else {
				if !conv.Status.Equals(c.from) {
					t.Fatalf("status changed on rejected transition: got %s, want %s",
						conv.Status.String(), c.from.String())
				}
			}
		})
	}
}

func TestConversation_TransitionStatus_RejectsNonParticipant(t *testing.T) {
	t.Parallel()

	conv := newOpenConversation(t)
	third := FixedThirdPartyID

	err := conv.TransitionStatus(valueobjects.StatusClosed, third)

	if !errors.Is(err, domainerrors.ErrNotParticipant) {
		t.Fatalf("err = %v, want ErrNotParticipant", err)
	}
	if !errors.Is(err, domainerrors.ErrForbidden) {
		t.Fatalf("err = %v, want category ErrForbidden", err)
	}
	if !conv.Status.Equals(valueobjects.StatusOpen) {
		t.Fatalf("status changed despite rejection: %s", conv.Status.String())
	}
}

func TestConversation_TransitionStatus_AdvancesUpdatedAtOnSuccess(t *testing.T) {
	t.Parallel()

	conv := newOpenConversation(t)
	actor := conv.BuyerID

	original := conv.UpdatedAt
	time.Sleep(time.Millisecond)

	if err := conv.TransitionStatus(valueobjects.StatusClosed, actor); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if !conv.UpdatedAt.After(original) {
		t.Fatalf("UpdatedAt not advanced: before=%v after=%v", original, conv.UpdatedAt)
	}
}

func TestConversation_TransitionStatus_LeavesUpdatedAtOnFailure(t *testing.T) {
	t.Parallel()

	conv := newConversationInStatus(t, valueobjects.StatusArchived)
	actor := conv.BuyerID

	original := conv.UpdatedAt
	time.Sleep(time.Millisecond)

	if err := conv.TransitionStatus(valueobjects.StatusOpen, actor); err == nil {
		t.Fatalf("expected error")
	}

	if !conv.UpdatedAt.Equal(original) {
		t.Fatalf("UpdatedAt changed on rejected transition: before=%v after=%v", original, conv.UpdatedAt)
	}
}

func TestConversation_TransitionStatus_SellerCanTransition(t *testing.T) {
	t.Parallel()

	conv := newOpenConversation(t)

	if err := conv.TransitionStatus(valueobjects.StatusClosed, conv.SellerID); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !conv.Status.Equals(valueobjects.StatusClosed) {
		t.Fatalf("status = %s, want CLOSED", conv.Status.String())
	}
}

func TestConversation_TransitionStatus_BuyerCanTransition(t *testing.T) {
	t.Parallel()

	conv := newOpenConversation(t)

	if err := conv.TransitionStatus(valueobjects.StatusClosed, conv.BuyerID); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !conv.Status.Equals(valueobjects.StatusClosed) {
		t.Fatalf("status = %s, want CLOSED", conv.Status.String())
	}
}
