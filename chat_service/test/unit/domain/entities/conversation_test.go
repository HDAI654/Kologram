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
	if conv.IsReadOnly {
		t.Fatalf("IsReadOnly = true, want false on fresh conversation")
	}
	if conv.LastMessagePreview != "" {
		t.Fatalf("LastMessagePreview = %q, want empty", conv.LastMessagePreview)
	}
	if !conv.LastMessageID.IsZero() {
		t.Fatalf("LastMessageID = %q, want empty", conv.LastMessageID.String())
	}
	if conv.LastMessageAt.Before(before) || conv.LastMessageAt.After(after) {
		t.Fatalf("LastMessageAt = %v, want within [%v, %v]", conv.LastMessageAt, before, after)
	}
	if conv.CreatedAt.Before(before) || conv.CreatedAt.After(after) {
		t.Fatalf("CreatedAt = %v, want within [%v, %v]", conv.CreatedAt, before, after)
	}
	if !conv.CreatedAt.Equal(conv.UpdatedAt) {
		t.Fatalf("CreatedAt != UpdatedAt on fresh conversation")
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
// IsParticipant / ParticipantIDs / CounterpartID
// ---------------------------------------------------------------------------

func TestConversation_IsParticipant(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)

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

func TestConversation_ParticipantIDs(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	ids := conv.ParticipantIDs()

	if !ids[0].Equals(conv.BuyerID) {
		t.Fatalf("ParticipantIDs[0] = %s, want buyer %s", ids[0].String(), conv.BuyerID.String())
	}
	if !ids[1].Equals(conv.SellerID) {
		t.Fatalf("ParticipantIDs[1] = %s, want seller %s", ids[1].String(), conv.SellerID.String())
	}
}

func TestConversation_CounterpartID(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)

	t.Run("buyer sees seller", func(t *testing.T) {
		t.Parallel()
		got, ok := conv.CounterpartID(conv.BuyerID)
		if !ok {
			t.Fatalf("ok = false, want true")
		}
		if !got.Equals(conv.SellerID) {
			t.Fatalf("counterpart = %s, want seller %s", got.String(), conv.SellerID.String())
		}
	})

	t.Run("seller sees buyer", func(t *testing.T) {
		t.Parallel()
		got, ok := conv.CounterpartID(conv.SellerID)
		if !ok {
			t.Fatalf("ok = false, want true")
		}
		if !got.Equals(conv.BuyerID) {
			t.Fatalf("counterpart = %s, want buyer %s", got.String(), conv.BuyerID.String())
		}
	})

	t.Run("third party is not a participant", func(t *testing.T) {
		t.Parallel()
		got, ok := conv.CounterpartID(FixedThirdPartyID)
		if ok {
			t.Fatalf("ok = true, want false")
		}
		if got.String() != "" {
			t.Fatalf("counterpart = %q, want zero value", got.String())
		}
	})
}

// ---------------------------------------------------------------------------
// AddMessage
// ---------------------------------------------------------------------------

func TestConversation_AddMessage_Success(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	content := mustContent(t, "hello world")
	clientID := ClientMsgID1

	before := time.Now().UTC()
	msg, err := conv.AddMessage(conv.BuyerID, clientID, content)
	after := time.Now().UTC()
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if msg.ID.String() == "" {
		t.Fatalf("MessageID is empty")
	}
	if msg.ConversationID.String() != conv.ID.String() {
		t.Fatalf("ConversationID mismatch")
	}
	if !msg.SenderID.Equals(conv.BuyerID) {
		t.Fatalf("SenderID mismatch")
	}
	if msg.Content.String() != "hello world" {
		t.Fatalf("Content = %q, want %q", msg.Content.String(), "hello world")
	}
	if msg.ClientMessageID != clientID {
		t.Fatalf("ClientMessageID = %q, want %q", msg.ClientMessageID, clientID)
	}
	if msg.DeletedForEveryone {
		t.Fatalf("DeletedForEveryone = true, want false")
	}
	if msg.SentAt.Before(before) || msg.SentAt.After(after) {
		t.Fatalf("SentAt = %v, want within [%v, %v]", msg.SentAt, before, after)
	}
}

func TestConversation_AddMessage_SellerCanSend(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	msg, err := conv.AddMessage(conv.SellerID, ClientMsgID1, mustContent(t, "from seller"))
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !msg.SenderID.Equals(conv.SellerID) {
		t.Fatalf("SenderID mismatch")
	}
}

func TestConversation_AddMessage_RejectsNonParticipant(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)

	msg, err := conv.AddMessage(FixedThirdPartyID, ClientMsgID1, mustContent(t, "hello"))

	if !errors.Is(err, domainerrors.ErrNotParticipant) {
		t.Fatalf("err = %v, want ErrNotParticipant", err)
	}
	if !errors.Is(err, domainerrors.ErrForbidden) {
		t.Fatalf("err = %v, want category ErrForbidden", err)
	}
	if msg.ID.String() != "" {
		t.Fatalf("message should be zero value on error")
	}
}

func TestConversation_AddMessage_RejectsWhenReadOnly(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	conv.MarkListingUnavailable(time.Now().UTC())

	msg, err := conv.AddMessage(conv.BuyerID, ClientMsgID1, mustContent(t, "hello"))

	if !errors.Is(err, domainerrors.ErrConversationNotOpen) {
		t.Fatalf("err = %v, want ErrConversationNotOpen", err)
	}
	if !errors.Is(err, domainerrors.ErrConflict) {
		t.Fatalf("err = %v, want category ErrConflict", err)
	}
	if msg.ID.String() != "" {
		t.Fatalf("message should be zero value on error")
	}
}

func TestConversation_AddMessage_RejectsEmptyClientMessageID(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)

	_, err := conv.AddMessage(conv.BuyerID, "", mustContent(t, "hello"))
	if err == nil {
		t.Fatalf("expected error for empty clientMessageID")
	}
	if !errors.Is(err, domainerrors.ErrInvalidArgument) {
		t.Fatalf("err = %v, want category ErrInvalidArgument", err)
	}
	var ve *domainerrors.ValidationError
	if !errors.As(err, &ve) {
		t.Fatalf("err = %v, want ValidationError", err)
	}
	if ve.Field != "client_message_id" {
		t.Fatalf("Field = %q, want client_message_id", ve.Field)
	}
}

// ---------------------------------------------------------------------------
// RecordLastMessage
// ---------------------------------------------------------------------------

func TestConversation_RecordLastMessage_SetsPreviewAndTimestamp(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	msg := mustMessage(t, conv.ID, conv.BuyerID, ClientMsgID1, "hello there")

	conv.RecordLastMessage(msg)

	if !conv.LastMessageID.Equals(msg.ID) {
		t.Fatalf("LastMessageID = %q, want %q", conv.LastMessageID.String(), msg.ID.String())
	}
	if conv.LastMessagePreview != "hello there" {
		t.Fatalf("LastMessagePreview = %q, want %q", conv.LastMessagePreview, "hello there")
	}
	if !conv.LastMessageAt.Equal(msg.SentAt) {
		t.Fatalf("LastMessageAt = %v, want %v", conv.LastMessageAt, msg.SentAt)
	}
	if !conv.UpdatedAt.Equal(msg.SentAt) {
		t.Fatalf("UpdatedAt = %v, want %v", conv.UpdatedAt, msg.SentAt)
	}
}

func TestConversation_RecordLastMessage_OverwritesPreviousPreview(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)

	first := mustMessage(t, conv.ID, conv.BuyerID, ClientMsgID1, "first")
	first.SentAt = time.Now().UTC().Add(-time.Second)
	conv.RecordLastMessage(first)

	second := mustMessage(t, conv.ID, conv.BuyerID, ClientMsgID2, "second")
	conv.RecordLastMessage(second)

	if !conv.LastMessageID.Equals(second.ID) {
		t.Fatalf("LastMessageID = %q, want %q", conv.LastMessageID.String(), second.ID.String())
	}
	if conv.LastMessagePreview != "second" {
		t.Fatalf("LastMessagePreview = %q, want %q", conv.LastMessagePreview, "second")
	}
	if !conv.LastMessageAt.Equal(second.SentAt) {
		t.Fatalf("LastMessageAt = %v, want %v", conv.LastMessageAt, second.SentAt)
	}
}

func TestConversation_RecordLastMessage_UsesTrimmedContent(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	msg := mustMessage(t, conv.ID, conv.BuyerID, ClientMsgID1, "  padded message  ")

	conv.RecordLastMessage(msg)

	if conv.LastMessagePreview != "padded message" {
		t.Fatalf("LastMessagePreview = %q, want %q", conv.LastMessagePreview, "padded message")
	}
}


func TestConversation_ClearLastMessagePreview(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	msg := mustMessage(t, conv.ID, conv.BuyerID, ClientMsgID1, "hello")
	conv.RecordLastMessage(msg)
	lastAt := conv.LastMessageAt

	now := time.Now().UTC().Add(time.Second)
	conv.ClearLastMessagePreview(now)

	if !conv.LastMessageID.IsZero() {
		t.Fatalf("LastMessageID = %q, want empty", conv.LastMessageID.String())
	}
	if conv.LastMessagePreview != "" {
		t.Fatalf("LastMessagePreview = %q, want empty", conv.LastMessagePreview)
	}
	if !conv.LastMessageAt.Equal(lastAt) {
		t.Fatalf("LastMessageAt changed; want stable sort key %v, got %v", lastAt, conv.LastMessageAt)
	}
	if !conv.UpdatedAt.Equal(now) {
		t.Fatalf("UpdatedAt = %v, want %v", conv.UpdatedAt, now)
	}
}

// ---------------------------------------------------------------------------
// MarkListingUnavailable
// ---------------------------------------------------------------------------

func TestConversation_MarkListingUnavailable_SetsReadOnly(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	originalUpdatedAt := conv.UpdatedAt
	now := time.Now().UTC().Add(time.Second)

	conv.MarkListingUnavailable(now)

	if !conv.IsReadOnly {
		t.Fatalf("IsReadOnly = false, want true")
	}
	if !conv.UpdatedAt.Equal(now) {
		t.Fatalf("UpdatedAt = %v, want %v", conv.UpdatedAt, now)
	}
	if conv.UpdatedAt.Equal(originalUpdatedAt) {
		t.Fatalf("UpdatedAt was not advanced")
	}
}

func TestConversation_MarkListingUnavailable_IsIdempotent(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	first := time.Now().UTC().Add(time.Second)
	conv.MarkListingUnavailable(first)

	second := first.Add(time.Hour)
	conv.MarkListingUnavailable(second)

	if !conv.IsReadOnly {
		t.Fatalf("IsReadOnly = false, want true")
	}
	if !conv.UpdatedAt.Equal(first) {
		t.Fatalf("UpdatedAt changed on second call: got %v, want %v", conv.UpdatedAt, first)
	}
}
