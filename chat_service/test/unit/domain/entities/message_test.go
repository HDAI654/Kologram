package entities_test

import (
	"testing"
	"time"

	domain "github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
)

func TestNewMessage_PopulatesAllFields(t *testing.T) {
	t.Parallel()

	conv := newOpenConversation(t)
	convID := conv.ID
	senderID := conv.BuyerID
	content := mustContent(t, "hello world")

	before := time.Now().UTC()
	msg := domain.NewMessage(convID, senderID, content)
	after := time.Now().UTC()

	if msg.ID.String() == "" {
		t.Fatalf("MessageID is empty")
	}
	if msg.ConversationID.String() != convID.String() {
		t.Fatalf("ConversationID = %q, want %q", msg.ConversationID.String(), convID.String())
	}
	if !msg.SenderID.Equals(senderID) {
		t.Fatalf("SenderID mismatch")
	}
	if msg.Content.String() != content.String() {
		t.Fatalf("Content = %q, want %q", msg.Content.String(), content.String())
	}
	if msg.IsRead {
		t.Fatalf("IsRead = true, want false on freshly created message")
	}
	if msg.SentAt.Before(before) || msg.SentAt.After(after) {
		t.Fatalf("SentAt = %v, want within [%v, %v]", msg.SentAt, before, after)
	}
}

func TestNewMessage_GeneratesUniqueIDs(t *testing.T) {
	t.Parallel()

	conv := newOpenConversation(t)
	convID := conv.ID
	senderID := conv.BuyerID
	content := mustContent(t, "hello world")

	a := domain.NewMessage(convID, senderID, content)
	b := domain.NewMessage(convID, senderID, content)

	if a.ID.String() == b.ID.String() {
		t.Fatalf("two calls returned same MessageID: %s", a.ID.String())
	}
}

func TestNewMessage_DoesNotShareMutableState(t *testing.T) {
	t.Parallel()

	conv := newOpenConversation(t)
	convID := conv.ID
	senderID := conv.BuyerID
	content := mustContent(t, "hello world")

	a := domain.NewMessage(convID, senderID, content)
	b := domain.NewMessage(convID, senderID, content)

	a.MarkRead()

	if b.IsRead {
		t.Fatalf("MarkRead on one message affected another")
	}
}

func TestMessage_MarkRead(t *testing.T) {
	t.Parallel()

	conv := newOpenConversation(t)
	convID := conv.ID
	senderID := conv.BuyerID
	content := mustContent(t, "hello world")

	msg := domain.NewMessage(
		convID,
		senderID,
		content,
	)

	if msg.IsRead {
		t.Fatalf("precondition failed: message starts unread")
	}

	msg.MarkRead()

	if !msg.IsRead {
		t.Fatalf("after MarkRead: IsRead = false, want true")
	}
}
