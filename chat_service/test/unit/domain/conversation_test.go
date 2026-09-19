package domain_test

import (
	"errors"
	"testing"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

// ---------------------------------------------------------------------------
// StartConversation
// ---------------------------------------------------------------------------

func TestStartConversation_Success(t *testing.T) {
	t.Parallel()

	buyer := mustUserID(t, fixedBuyerID)
	seller := mustUserID(t, fixedSellerID)
	listing := mustListingID(t, fixedListingID)

	before := time.Now().UTC()
	conv, err := domain.StartConversation(buyer, seller, listing)
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
	if !conv.Status.Equals(valueobject.StatusOpen) {
		t.Fatalf("Status = %s, want OPEN", conv.Status.String())
	}
	if conv.Messages != nil {
		t.Fatalf("Messages = %v, want nil on fresh conversation", conv.Messages)
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

	same := mustUserID(t, fixedBuyerID)
	listing := mustListingID(t, fixedListingID)

	conv, err := domain.StartConversation(same, same, listing)

	if !errors.Is(err, domain.ErrBuyerSellerSame) {
		t.Fatalf("err = %v, want ErrBuyerSellerSame", err)
	}
	if conv != nil {
		t.Fatalf("conversation = %v, want nil on error", conv)
	}
}

func TestStartConversation_IDsAreUnique(t *testing.T) {
	t.Parallel()

	buyer := mustUserID(t, fixedBuyerID)
	seller := mustUserID(t, fixedSellerID)
	listing := mustListingID(t, fixedListingID)

	a, err := domain.StartConversation(buyer, seller, listing)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	b, err := domain.StartConversation(buyer, seller, listing)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if a.ID.String() == b.ID.String() {
		t.Fatalf("two calls returned same ConversationID: %s", a.ID.String())
	}
}

// ---------------------------------------------------------------------------
// RehydrateConversation
// ---------------------------------------------------------------------------

func TestRehydrateConversation_PreservesAllFields(t *testing.T) {
	t.Parallel()

	id := mustConversationID(t, fixedConversationID)
	buyer := mustUserID(t, fixedBuyerID)
	seller := mustUserID(t, fixedSellerID)
	listing := mustListingID(t, fixedListingID)
	status := valueobject.StatusClosed
	messages := []domain.Message{
		domain.NewMessage(id, buyer, mustContent(t, "first")),
		domain.NewMessage(id, seller, mustContent(t, "second")),
	}
	created := time.Date(2024, 1, 1, 12, 0, 0, 0, time.UTC)
	updated := time.Date(2024, 1, 2, 12, 0, 0, 0, time.UTC)

	conv := domain.RehydrateConversation(id, buyer, seller, listing, status, messages, created, updated)

	if conv.ID.String() != id.String() {
		t.Fatalf("ID not preserved")
	}
	if !conv.BuyerID.Equals(buyer) {
		t.Fatalf("BuyerID not preserved")
	}
	if !conv.SellerID.Equals(seller) {
		t.Fatalf("SellerID not preserved")
	}
	if conv.ListingID.String() != listing.String() {
		t.Fatalf("ListingID not preserved")
	}
	if !conv.Status.Equals(status) {
		t.Fatalf("Status not preserved")
	}
	if len(conv.Messages) != 2 {
		t.Fatalf("Messages len = %d, want 2", len(conv.Messages))
	}
	if !conv.CreatedAt.Equal(created) {
		t.Fatalf("CreatedAt not preserved")
	}
	if !conv.UpdatedAt.Equal(updated) {
		t.Fatalf("UpdatedAt not preserved")
	}
}

func TestRehydrateConversation_DoesNotValidateState(t *testing.T) {
	t.Parallel()

	// ARCHIVED with messages would be unreachable via the normal API but
	// must round-trip cleanly from storage.
	conv := rehydrate(t, valueobject.StatusArchived, []domain.Message{
		domain.NewMessage(
			mustConversationID(t, fixedConversationID),
			mustUserID(t, fixedBuyerID),
			mustContent(t, "historical"),
		),
	})

	if !conv.Status.Equals(valueobject.StatusArchived) {
		t.Fatalf("status not preserved through rehydration")
	}
	if len(conv.Messages) != 1 {
		t.Fatalf("messages not preserved through rehydration")
	}
}

func TestRehydrateConversation_EmptyMessagesIsAllowed(t *testing.T) {
	t.Parallel()

	conv := rehydrate(t, valueobject.StatusOpen, nil)

	if conv.Messages != nil {
		t.Fatalf("Messages = %v, want nil when passed nil", conv.Messages)
	}
}

// ---------------------------------------------------------------------------
// IsParticipant
// ---------------------------------------------------------------------------

func TestConversation_IsParticipant(t *testing.T) {
	t.Parallel()

	conv := rehydrate(t, valueobject.StatusOpen, nil)

	cases := []struct {
		name string
		id   valueobject.UserID
		want bool
	}{
		{"buyer is participant", mustUserID(t, fixedBuyerID), true},
		{"seller is participant", mustUserID(t, fixedSellerID), true},
		{"third party is not participant", mustUserID(t, fixedThirdPartyID), false},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()
			if got := conv.IsParticipant(tc.id); got != tc.want {
				t.Fatalf("IsParticipant(%s) = %v, want %v", tc.id.String(), got, tc.want)
			}
		})
	}
}

// ---------------------------------------------------------------------------
// AddMessage
// ---------------------------------------------------------------------------

func TestConversation_AddMessage_Success(t *testing.T) {

	conv := rehydrate(t, valueobject.StatusOpen, nil)
	buyer := mustUserID(t, fixedBuyerID)
	content := mustContent(t, "hello seller")

	before := time.Now().UTC()
	msg, err := conv.AddMessage(buyer, content)
	after := time.Now().UTC()
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if len(conv.Messages) != 1 {
		t.Fatalf("Messages len = %d, want 1", len(conv.Messages))
	}
	stored := conv.Messages[0]
	if stored.ID.String() != msg.ID.String() {
		t.Fatalf("returned message ID does not match stored message")
	}
	if stored.Content.String() != content.String() {
		t.Fatalf("content not preserved on stored message")
	}
	if !stored.SenderID.Equals(buyer) {
		t.Fatalf("sender not preserved on stored message")
	}
	if stored.IsRead {
		t.Fatalf("newly added message should be unread")
	}
	if stored.SentAt.Before(before) || stored.SentAt.After(after) {
		t.Fatalf("SentAt = %v, want within [%v, %v]", stored.SentAt, before, after)
	}
	if !conv.UpdatedAt.After(before) && !conv.UpdatedAt.Equal(before) {
		// UpdatedAt must be at least as recent as before the call.
		t.Fatalf("UpdatedAt = %v, want >= %v", conv.UpdatedAt, before)
	}
}

func TestConversation_AddMessage_SellerCanSend(t *testing.T) {
	t.Parallel()

	conv := rehydrate(t, valueobject.StatusOpen, nil)
	seller := mustUserID(t, fixedSellerID)

	msg, err := conv.AddMessage(seller, mustContent(t, "hello buyer"))
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !msg.SenderID.Equals(seller) {
		t.Fatalf("sender mismatch")
	}
}

func TestConversation_AddMessage_AppendsInOrder(t *testing.T) {
	t.Parallel()

	conv := rehydrate(t, valueobject.StatusOpen, nil)
	buyer := mustUserID(t, fixedBuyerID)
	seller := mustUserID(t, fixedSellerID)

	first, _ := conv.AddMessage(buyer, mustContent(t, "1"))
	second, _ := conv.AddMessage(seller, mustContent(t, "2"))
	third, _ := conv.AddMessage(buyer, mustContent(t, "3"))

	want := []string{first.ID.String(), second.ID.String(), third.ID.String()}
	for i, w := range want {
		if conv.Messages[i].ID.String() != w {
			t.Fatalf("Messages[%d].ID = %s, want %s", i, conv.Messages[i].ID.String(), w)
		}
	}
}

func TestConversation_AddMessage_RejectsNonParticipant(t *testing.T) {
	t.Parallel()

	conv := rehydrate(t, valueobject.StatusOpen, nil)
	third := mustUserID(t, fixedThirdPartyID)

	msg, err := conv.AddMessage(third, mustContent(t, "hi"))

	if !errors.Is(err, domain.ErrNotParticipant) {
		t.Fatalf("err = %v, want ErrNotParticipant", err)
	}
	if msg != (domain.Message{}) {
		t.Fatalf("returned message should be zero value on error")
	}
	if len(conv.Messages) != 0 {
		t.Fatalf("Messages len = %d, want 0", len(conv.Messages))
	}
}

func TestConversation_AddMessage_RejectsWhenNotOpen(t *testing.T) {
	t.Parallel()

	for _, status := range []valueobject.ConversationStatus{
		valueobject.StatusClosed,
		valueobject.StatusArchived,
	} {
		t.Run(status.String(), func(t *testing.T) {
			t.Parallel()
			conv := rehydrate(t, status, nil)
			buyer := mustUserID(t, fixedBuyerID)

			msg, err := conv.AddMessage(buyer, mustContent(t, "hi"))

			if !errors.Is(err, domain.ErrConversationNotOpen) {
				t.Fatalf("err = %v, want ErrConversationNotOpen", err)
			}
			if msg != (domain.Message{}) {
				t.Fatalf("returned message should be zero value on error")
			}
			if len(conv.Messages) != 0 {
				t.Fatalf("Messages len = %d, want 0", len(conv.Messages))
			}
		})
	}
}

func TestConversation_AddMessage_ParticipantCheckPrecedesStatusCheck(t *testing.T) {
	t.Parallel()

	conv := rehydrate(t, valueobject.StatusClosed, nil)
	third := mustUserID(t, fixedThirdPartyID)

	_, err := conv.AddMessage(third, mustContent(t, "hi"))

	if !errors.Is(err, domain.ErrNotParticipant) {
		t.Fatalf("err = %v, want ErrNotParticipant", err)
	}
}

// ---------------------------------------------------------------------------
// MarkMessagesRead
// ---------------------------------------------------------------------------

func seedTwoWayConversation(t *testing.T) (*domain.Conversation, domain.Message, domain.Message) {
	t.Helper()
	conv := rehydrate(t, valueobject.StatusOpen, nil)
	buyer := mustUserID(t, fixedBuyerID)
	seller := mustUserID(t, fixedSellerID)

	buyerMsg, _ := conv.AddMessage(buyer, mustContent(t, "from buyer"))
	sellerMsg, _ := conv.AddMessage(seller, mustContent(t, "from seller"))
	return conv, buyerMsg, sellerMsg
}

func TestConversation_MarkMessagesRead_MarksOnlyOtherParty(t *testing.T) {
	t.Parallel()

	conv, _, _ := seedTwoWayConversation(t)
	buyer := mustUserID(t, fixedBuyerID)

	if err := conv.MarkMessagesRead(buyer); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	// Buyer's own message stays unread; seller's becomes read.
	if conv.Messages[0].IsRead {
		t.Fatalf("buyer's own message marked as read")
	}
	if !conv.Messages[1].IsRead {
		t.Fatalf("seller's message not marked as read")
	}
}

func TestConversation_MarkMessagesRead_RejectsNonParticipant(t *testing.T) {
	t.Parallel()

	conv, _, _ := seedTwoWayConversation(t)
	third := mustUserID(t, fixedThirdPartyID)

	err := conv.MarkMessagesRead(third)

	if !errors.Is(err, domain.ErrNotParticipant) {
		t.Fatalf("err = %v, want ErrNotParticipant", err)
	}
	// No messages should have changed.
	for i, m := range conv.Messages {
		if m.IsRead {
			t.Fatalf("Messages[%d] marked read despite rejection", i)
		}
	}
}

func TestConversation_MarkMessagesRead_NoUnreadLeavesUpdatedAtUntouched(t *testing.T) {
	t.Parallel()

	conv := rehydrate(t, valueobject.StatusOpen, nil)
	buyer := mustUserID(t, fixedBuyerID)
	_, _ = conv.AddMessage(buyer, mustContent(t, "only buyer message"))

	originalUpdatedAt := conv.UpdatedAt
	time.Sleep(time.Millisecond)

	if err := conv.MarkMessagesRead(buyer); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if !conv.UpdatedAt.Equal(originalUpdatedAt) {
		t.Fatalf("UpdatedAt changed despite no messages marked")
	}
	if conv.Messages[0].IsRead {
		t.Fatalf("own message was marked read")
	}
}

func TestConversation_MarkMessagesRead_AdvancesUpdatedAtWhenChanged(t *testing.T) {
	t.Parallel()

	conv, _, _ := seedTwoWayConversation(t)
	buyer := mustUserID(t, fixedBuyerID)

	originalUpdatedAt := conv.UpdatedAt
	time.Sleep(time.Millisecond)

	if err := conv.MarkMessagesRead(buyer); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if !conv.UpdatedAt.After(originalUpdatedAt) {
		t.Fatalf("UpdatedAt not advanced: before=%v after=%v", originalUpdatedAt, conv.UpdatedAt)
	}
}

func TestConversation_MarkMessagesRead_IsIdempotent(t *testing.T) {
	t.Parallel()

	conv, _, _ := seedTwoWayConversation(t)
	buyer := mustUserID(t, fixedBuyerID)

	if err := conv.MarkMessagesRead(buyer); err != nil {
		t.Fatalf("first call: %v", err)
	}
	afterFirst := conv.UpdatedAt

	time.Sleep(time.Millisecond)

	if err := conv.MarkMessagesRead(buyer); err != nil {
		t.Fatalf("second call: %v", err)
	}

	if !conv.UpdatedAt.Equal(afterFirst) {
		t.Fatalf("second call advanced UpdatedAt despite no new work")
	}
}

func TestConversation_MarkMessagesRead_EmptyConversation(t *testing.T) {
	t.Parallel()

	conv := rehydrate(t, valueobject.StatusOpen, nil)
	buyer := mustUserID(t, fixedBuyerID)

	if err := conv.MarkMessagesRead(buyer); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
}

// ---------------------------------------------------------------------------
// TransitionStatus
// ---------------------------------------------------------------------------

func TestConversation_TransitionStatus_Matrix(t *testing.T) {
	t.Parallel()

	type tc struct {
		name    string
		from    valueobject.ConversationStatus
		to      valueobject.ConversationStatus
		wantErr error
	}

	cases := []tc{
		// OPEN
		{"open→closed", valueobject.StatusOpen, valueobject.StatusClosed, nil},
		{"open→archived", valueobject.StatusOpen, valueobject.StatusArchived, nil},
		{"open→open", valueobject.StatusOpen, valueobject.StatusOpen, domain.ErrInvalidStatusTransition},

		// CLOSED
		{"closed→open", valueobject.StatusClosed, valueobject.StatusOpen, nil},
		{"closed→archived", valueobject.StatusClosed, valueobject.StatusArchived, nil},
		{"closed→closed", valueobject.StatusClosed, valueobject.StatusClosed, domain.ErrInvalidStatusTransition},

		// ARCHIVED (terminal)
		{"archived→open", valueobject.StatusArchived, valueobject.StatusOpen, domain.ErrInvalidStatusTransition},
		{"archived→closed", valueobject.StatusArchived, valueobject.StatusClosed, domain.ErrInvalidStatusTransition},
		{"archived→archived", valueobject.StatusArchived, valueobject.StatusArchived, domain.ErrInvalidStatusTransition},
	}

	for _, c := range cases {
		c := c
		t.Run(c.name, func(t *testing.T) {
			t.Parallel()
			conv := rehydrate(t, c.from, nil)
			actor := mustUserID(t, fixedBuyerID)

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
					t.Fatalf("status changed on rejected transition: %s", conv.Status.String())
				}
			}
		})
	}
}

func TestConversation_TransitionStatus_RejectsNonParticipant(t *testing.T) {
	t.Parallel()

	conv := rehydrate(t, valueobject.StatusOpen, nil)
	third := mustUserID(t, fixedThirdPartyID)

	err := conv.TransitionStatus(valueobject.StatusClosed, third)

	if !errors.Is(err, domain.ErrNotParticipant) {
		t.Fatalf("err = %v, want ErrNotParticipant", err)
	}
	if !conv.Status.Equals(valueobject.StatusOpen) {
		t.Fatalf("status changed despite rejection")
	}
}

// Participant check precedes transition validity check: a non-participant
// attempting an invalid transition must see ErrNotParticipant.
func TestConversation_TransitionStatus_ParticipantCheckPrecedesTransitionCheck(t *testing.T) {
	t.Parallel()

	conv := rehydrate(t, valueobject.StatusArchived, nil)
	third := mustUserID(t, fixedThirdPartyID)

	err := conv.TransitionStatus(valueobject.StatusOpen, third)

	if !errors.Is(err, domain.ErrNotParticipant) {
		t.Fatalf("err = %v, want ErrNotParticipant", err)
	}
}

func TestConversation_TransitionStatus_AdvancesUpdatedAtOnSuccess(t *testing.T) {
	t.Parallel()

	conv := rehydrate(t, valueobject.StatusOpen, nil)
	actor := mustUserID(t, fixedBuyerID)

	original := conv.UpdatedAt
	time.Sleep(time.Millisecond)

	if err := conv.TransitionStatus(valueobject.StatusClosed, actor); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if !conv.UpdatedAt.After(original) {
		t.Fatalf("UpdatedAt not advanced: before=%v after=%v", original, conv.UpdatedAt)
	}
}

func TestConversation_TransitionStatus_LeavesUpdatedAtOnFailure(t *testing.T) {
	t.Parallel()

	conv := rehydrate(t, valueobject.StatusArchived, nil)
	actor := mustUserID(t, fixedBuyerID)

	original := conv.UpdatedAt
	time.Sleep(time.Millisecond)

	if err := conv.TransitionStatus(valueobject.StatusOpen, actor); err == nil {
		t.Fatalf("expected error")
	}

	if !conv.UpdatedAt.Equal(original) {
		t.Fatalf("UpdatedAt changed on rejected transition")
	}
}
