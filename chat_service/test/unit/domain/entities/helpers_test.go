package entities_test

import (
	"testing"

	domain "github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

// Fixed v4 UUIDs — deterministic identity graph shared by every test.
const (
	fixedBuyerID      = "0d47ddfe-a4ca-446a-839e-d3bbcba824c6"
	fixedSellerID     = "bdf038e5-8b16-4825-a895-ce7d0648e845"
	fixedThirdPartyID = "a9a8c7c2-c7e5-41d5-be23-11357cd9f32a"
	fixedListingID    = "431f7a61-1a30-4c3a-b2d4-5282ca2799b5"
)

func mustUserID(t *testing.T, raw string) valueobjects.UserID {
	t.Helper()
	id, err := valueobjects.NewUserID(raw)
	if err != nil {
		t.Fatalf("NewUserID(%q): %v", raw, err)
	}
	return id
}

func mustListingID(t *testing.T, raw string) valueobjects.ListingID {
	t.Helper()
	id, err := valueobjects.NewListingID(raw)
	if err != nil {
		t.Fatalf("NewListingID(%q): %v", raw, err)
	}
	return id
}

func mustContent(t *testing.T, raw string) valueobjects.MessageContent {
	t.Helper()
	c, err := valueobjects.NewMessageContent(raw)
	if err != nil {
		t.Fatalf("NewMessageContent(%q): %v", raw, err)
	}
	return c
}

func mustStatus(t *testing.T, raw string) valueobjects.ConversationStatus {
	t.Helper()
	s, err := valueobjects.NewConversationStatus(raw)
	if err != nil {
		t.Fatalf("NewConversationStatus(%q): %v", raw, err)
	}
	return s
}

// newOpenConversation returns a freshly started OPEN conversation between the
// fixed buyer and seller.
func newOpenConversation(t *testing.T) *domain.Conversation {
	t.Helper()
	conv, err := domain.StartConversation(
		mustUserID(t, fixedBuyerID),
		mustUserID(t, fixedSellerID),
		mustListingID(t, fixedListingID),
	)
	if err != nil {
		t.Fatalf("StartConversation: %v", err)
	}
	return conv
}

// newConversationInStatus drives a fresh conversation into the requested
// status using only the aggregate's public transitions.
func newConversationInStatus(t *testing.T, target valueobjects.ConversationStatus) *domain.Conversation {
	t.Helper()
	conv := newOpenConversation(t)
	actor := mustUserID(t, fixedBuyerID)
	if err := conv.TransitionStatus(target, actor); err != nil {
		t.Fatalf("TransitionStatus(%s): %v", target.String(), err)
	}
	return conv
}
