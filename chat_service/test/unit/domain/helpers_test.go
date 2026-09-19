package domain_test

import (
	"testing"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

const (
	fixedBuyerID        = "11111111-1111-4111-8111-111111111111"
	fixedSellerID       = "22222222-2222-4222-8222-222222222222"
	fixedThirdPartyID   = "33333333-3333-4333-8333-333333333333"
	fixedListingID      = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
	fixedConversationID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
)

func mustUserID(t *testing.T, raw string) valueobject.UserID {
	t.Helper()
	id, err := valueobject.NewUserID(raw)
	if err != nil {
		t.Fatalf("NewUserID(%q): %v", raw, err)
	}
	return id
}

func mustConversationID(t *testing.T, raw string) valueobject.ConversationID {
	t.Helper()
	id, err := valueobject.NewConversationID(raw)
	if err != nil {
		t.Fatalf("NewConversationID(%q): %v", raw, err)
	}
	return id
}

func mustListingID(t *testing.T, raw string) valueobject.ListingID {
	t.Helper()
	id, err := valueobject.NewListingID(raw)
	if err != nil {
		t.Fatalf("NewListingID(%q): %v", raw, err)
	}
	return id
}

func mustContent(t *testing.T, raw string) valueobject.MessageContent {
	t.Helper()
	c, err := valueobject.NewMessageContent(raw)
	if err != nil {
		t.Fatalf("NewMessageContent(%q): %v", raw, err)
	}
	return c
}

func mustStatus(t *testing.T, raw string) valueobject.ConversationStatus {
	t.Helper()
	s, err := valueobject.NewConversationStatus(raw)
	if err != nil {
		t.Fatalf("NewConversationStatus(%q): %v", raw, err)
	}
	return s
}

func rehydrate(t *testing.T, status valueobject.ConversationStatus, messages []domain.Message) *domain.Conversation {
	t.Helper()
	now := time.Now().UTC()
	return domain.RehydrateConversation(
		mustConversationID(t, fixedConversationID),
		mustUserID(t, fixedBuyerID),
		mustUserID(t, fixedSellerID),
		mustListingID(t, fixedListingID),
		status,
		messages,
		now,
		now,
	)
}
