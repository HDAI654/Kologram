package domain_test

import (
	"testing"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

func TestNewMessage_FieldsArePopulated(t *testing.T) {
	t.Parallel()

	convID := mustConversationID(t, fixedConversationID)
	senderID := mustUserID(t, fixedBuyerID)
	content := mustContent(t, "hello world")

	before := time.Now().UTC()
	msg := domain.NewMessage(convID, senderID, content)
	after := time.Now().UTC()

	if msg.ID.String() == "" {
		t.Fatalf("MessageID is empty")
	}
	if got := msg.ConversationID.String(); got != convID.String() {
		t.Fatalf("ConversationID = %q, want %q", got, convID.String())
	}
	if got := msg.SenderID.String(); got != senderID.String() {
		t.Fatalf("SenderID = %q, want %q", got, senderID.String())
	}
	if got := msg.Content.String(); got != content.String() {
		t.Fatalf("Content = %q, want %q", got, content.String())
	}
	if msg.IsRead {
		t.Fatalf("IsRead = true, want false on freshly created message")
	}
	if msg.SentAt.Before(before) || msg.SentAt.After(after) {
		t.Fatalf("SentAt = %v, want within [%v, %v]", msg.SentAt, before, after)
	}
}

func TestNewMessage_IDIsUnique(t *testing.T) {
	t.Parallel()

	convID := mustConversationID(t, fixedConversationID)
	senderID := mustUserID(t, fixedBuyerID)
	content := mustContent(t, "hello")

	a := domain.NewMessage(convID, senderID, content)
	b := domain.NewMessage(convID, senderID, content)

	if a.ID.String() == b.ID.String() {
		t.Fatalf("two calls returned same MessageID: %s", a.ID.String())
	}
}

func TestMessage_MarkRead(t *testing.T) {
	t.Parallel()

	msg := domain.NewMessage(
		mustConversationID(t, fixedConversationID),
		mustUserID(t, fixedBuyerID),
		mustContent(t, "hello"),
	)

	if msg.IsRead {
		t.Fatalf("precondition failed: message starts unread")
	}

	msg.MarkRead()

	if !msg.IsRead {
		t.Fatalf("after MarkRead: IsRead = false, want true")
	}
}

func TestMessage_MarkRead_IsIdempotent(t *testing.T) {
	t.Parallel()

	msg := domain.NewMessage(
		mustConversationID(t, fixedConversationID),
		mustUserID(t, fixedBuyerID),
		mustContent(t, "hello"),
	)

	msg.MarkRead()
	msg.MarkRead()

	if !msg.IsRead {
		t.Fatalf("after two MarkRead calls: IsRead = false, want true")
	}
}

// Sanity check: MessageContent is comparable, so the Message struct itself is
// comparable. This guards future refactors that add slice/map fields.
func TestMessage_IsComparable(t *testing.T) {
	t.Parallel()

	convID := mustConversationID(t, fixedConversationID)
	senderID := mustUserID(t, fixedBuyerID)
	content := mustContent(t, "hello")

	msg := domain.NewMessage(convID, senderID, content)
	same := msg

	_ = msg == same
}

func TestNewMessage_DoesNotShareMutableState(t *testing.T) {
	t.Parallel()

	convID := mustConversationID(t, fixedConversationID)
	senderID := mustUserID(t, fixedBuyerID)
	content := valueobject.MessageContent{} // zero value; constructor is pure

	a := domain.NewMessage(convID, senderID, content)
	b := domain.NewMessage(convID, senderID, content)

	a.MarkRead()

	if b.IsRead {
		t.Fatalf("MarkRead on one message affected another")
	}
}
