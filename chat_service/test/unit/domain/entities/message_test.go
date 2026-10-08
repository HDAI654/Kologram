package entities_test

import (
	"errors"
	"testing"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
)

func TestNewMessage_PopulatesAllFields(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	content := mustContent(t, "hello world")

	before := time.Now().UTC()
	msg, err := entities.NewMessage(conv.ID, conv.BuyerID, ClientMsgID1, content)
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
	if msg.Content.String() != content.String() {
		t.Fatalf("Content = %q, want %q", msg.Content.String(), content.String())
	}
	if msg.ClientMessageID != ClientMsgID1 {
		t.Fatalf("ClientMessageID = %q, want %q", msg.ClientMessageID, ClientMsgID1)
	}
	if msg.DeletedForEveryone {
		t.Fatalf("DeletedForEveryone = true, want false")
	}
	if msg.DeletedAt != nil {
		t.Fatalf("DeletedAt = %v, want nil", msg.DeletedAt)
	}
	if msg.SentAt.Before(before) || msg.SentAt.After(after) {
		t.Fatalf("SentAt = %v, want within [%v, %v]", msg.SentAt, before, after)
	}
}

func TestNewMessage_GeneratesUniqueIDs(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	content := mustContent(t, "hello world")

	a, err := entities.NewMessage(conv.ID, conv.BuyerID, ClientMsgID1, content)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	b, err := entities.NewMessage(conv.ID, conv.BuyerID, ClientMsgID2, content)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if a.ID.String() == b.ID.String() {
		t.Fatalf("two calls returned same MessageID: %s", a.ID.String())
	}
}

func TestNewMessage_RejectsEmptyClientMessageID(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)

	msg, err := entities.NewMessage(conv.ID, conv.BuyerID, "", mustContent(t, "hello"))
	if err == nil {
		t.Fatalf("expected error")
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
	if msg.ID.String() != "" {
		t.Fatalf("message should be zero value on error")
	}
}

func TestNewMessage_RejectsNonUUIDv4ClientMessageID(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)

	cases := []string{
		"not-a-uuid",
		"client-msg-1",
		"a8098c1a-f86e-11da-bd1a-00112444be1e", // v1
	}

	for _, raw := range cases {
		raw := raw
		t.Run(raw, func(t *testing.T) {
			t.Parallel()
			_, err := entities.NewMessage(conv.ID, conv.BuyerID, raw, mustContent(t, "hello"))
			if err == nil {
				t.Fatalf("expected error for %q", raw)
			}
			if !errors.Is(err, domainerrors.ErrInvalidArgument) {
				t.Fatalf("err = %v, want ErrInvalidArgument", err)
			}
			var ve *domainerrors.ValidationError
			if !errors.As(err, &ve) || ve.Field != "client_message_id" {
				t.Fatalf("err = %v, want ValidationError field client_message_id", err)
			}
		})
	}
}

// ---------------------------------------------------------------------------
// DeleteForEveryone (soft-delete)
// ---------------------------------------------------------------------------

func TestMessage_DeleteForEveryone_Success(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	msg := mustMessage(t, conv.ID, conv.BuyerID, ClientMsgID1, "retractable")
	originalContent := msg.Content.String()

	before := time.Now().UTC()
	if err := msg.DeleteForEveryone(conv.BuyerID); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	after := time.Now().UTC()

	if !msg.DeletedForEveryone {
		t.Fatalf("DeletedForEveryone = false, want true")
	}
	// Soft-delete retains content for admin/security.
	if msg.Content.String() != originalContent {
		t.Fatalf("Content = %q, want retained %q", msg.Content.String(), originalContent)
	}
	if msg.DeletedAt == nil {
		t.Fatalf("DeletedAt is nil")
	}
	if msg.DeletedAt.Before(before) || msg.DeletedAt.After(after) {
		t.Fatalf("DeletedAt = %v, want within [%v, %v]", *msg.DeletedAt, before, after)
	}
}

func TestMessage_DeleteForEveryone_RejectsNonAuthor(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	msg := mustMessage(t, conv.ID, conv.BuyerID, ClientMsgID1, "hello")
	originalContent := msg.Content.String()

	err := msg.DeleteForEveryone(conv.SellerID)

	if !errors.Is(err, domainerrors.ErrNotMessageAuthor) {
		t.Fatalf("err = %v, want ErrNotMessageAuthor", err)
	}
	if !errors.Is(err, domainerrors.ErrForbidden) {
		t.Fatalf("err = %v, want category ErrForbidden", err)
	}
	if msg.DeletedForEveryone {
		t.Fatalf("DeletedForEveryone changed despite rejection")
	}
	if msg.Content.String() != originalContent {
		t.Fatalf("Content changed despite rejection")
	}
	if msg.DeletedAt != nil {
		t.Fatalf("DeletedAt set despite rejection")
	}
}

func TestMessage_DeleteForEveryone_RejectsAfterWindow(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	msg := mustMessage(t, conv.ID, conv.BuyerID, ClientMsgID1, "old message")
	msg.SentAt = time.Now().UTC().Add(-(entities.DeleteForEveryoneWindow + time.Hour))

	err := msg.DeleteForEveryone(conv.BuyerID)

	if !errors.Is(err, domainerrors.ErrDeleteWindowExpired) {
		t.Fatalf("err = %v, want ErrDeleteWindowExpired", err)
	}
	if !errors.Is(err, domainerrors.ErrConflict) {
		t.Fatalf("err = %v, want category ErrConflict", err)
	}
	if msg.DeletedForEveryone {
		t.Fatalf("DeletedForEveryone changed despite rejection")
	}
}

func TestMessage_DeleteForEveryone_AllowsWithinWindow(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	msg := mustMessage(t, conv.ID, conv.BuyerID, ClientMsgID1, "recent")
	// Window is evaluated as now.Sub(SentAt) > DeleteForEveryoneWindow.
	msg.SentAt = time.Now().UTC().Add(-(entities.DeleteForEveryoneWindow - time.Hour))

	if err := msg.DeleteForEveryone(conv.BuyerID); err != nil {
		t.Fatalf("unexpected error within window: %v", err)
	}
	if !msg.DeletedForEveryone {
		t.Fatalf("DeletedForEveryone = false, want true")
	}
}

func TestMessage_DeleteForEveryone_IsIdempotent(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	msg := mustMessage(t, conv.ID, conv.BuyerID, ClientMsgID1, "hello")

	if err := msg.DeleteForEveryone(conv.BuyerID); err != nil {
		t.Fatalf("first call: %v", err)
	}
	firstDeletedAt := *msg.DeletedAt

	time.Sleep(time.Millisecond)

	if err := msg.DeleteForEveryone(conv.BuyerID); err != nil {
		t.Fatalf("second call: %v", err)
	}
	if !msg.DeletedAt.Equal(firstDeletedAt) {
		t.Fatalf("DeletedAt changed on second call: first=%v second=%v", firstDeletedAt, *msg.DeletedAt)
	}
}

func TestMessage_DeleteForEveryone_DoesNotShareState(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	a := mustMessage(t, conv.ID, conv.BuyerID, ClientMsgID1, "first")
	b := mustMessage(t, conv.ID, conv.BuyerID, ClientMsgID2, "second")

	if err := a.DeleteForEveryone(conv.BuyerID); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if b.DeletedForEveryone {
		t.Fatalf("DeleteForEveryone on one message affected another")
	}
	if b.Content.String() != "second" {
		t.Fatalf("Content of other message changed")
	}
}
