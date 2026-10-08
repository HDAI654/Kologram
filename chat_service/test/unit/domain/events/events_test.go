package events_test

import (
	"testing"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/events"
)

func TestConversationStarted_Contract(t *testing.T) {
	t.Parallel()

	at := time.Date(2026, 1, 2, 3, 4, 5, 0, time.UTC)
	e := events.ConversationStarted{
		ConversationID: "c1",
		BuyerID:        "b1",
		SellerID:       "s1",
		ListingID:      "l1",
		At:             at,
	}

	if e.EventType() != "ConversationStarted" {
		t.Fatalf("EventType = %q", e.EventType())
	}
	if !e.OccurredAt().Equal(at) {
		t.Fatalf("OccurredAt = %v, want %v", e.OccurredAt(), at)
	}
}

func TestMessageSent_Contract(t *testing.T) {
	t.Parallel()

	at := time.Date(2026, 1, 2, 3, 4, 5, 0, time.UTC)
	e := events.MessageSent{
		ConversationID: "c1",
		MessageID:      "m1",
		SenderID:       "u1",
		RecipientID:    "u2",
		At:             at,
	}

	if e.EventType() != "MessageSent" {
		t.Fatalf("EventType = %q", e.EventType())
	}
	if !e.OccurredAt().Equal(at) {
		t.Fatalf("OccurredAt = %v, want %v", e.OccurredAt(), at)
	}
	if e.RecipientID != "u2" {
		t.Fatalf("RecipientID = %q, want u2", e.RecipientID)
	}
}
