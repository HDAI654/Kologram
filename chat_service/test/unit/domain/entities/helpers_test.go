package entities_test

import (
	"testing"

	domain "github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

// Fixed IDs
var (
	FixedBuyerID, _      = valueobjects.NewUserID("0d47ddfe-a4ca-446a-839e-d3bbcba824c6")
	FixedSellerID, _     = valueobjects.NewUserID("bdf038e5-8b16-4825-a895-ce7d0648e845")
	FixedThirdPartyID, _ = valueobjects.NewUserID("a9a8c7c2-c7e5-41d5-be23-11357cd9f32a")
	FixedListingID, _    = valueobjects.NewListingID("431f7a61-1a30-4c3a-b2d4-5282ca2799b5")
)

func mustContent(t *testing.T, raw string) valueobjects.MessageContent {
	t.Helper()
	c, err := valueobjects.NewMessageContent(raw)
	if err != nil {
		t.Fatalf("NewMessageContent(%q): %v", raw, err)
	}
	return c
}

// newOpenConversation returns a freshly started OPEN conversation between the
// fixed buyer and seller.
func newOpenConversation(t *testing.T) *domain.Conversation {
	t.Helper()
	conv, err := domain.StartConversation(
		FixedBuyerID,
		FixedSellerID,
		FixedListingID,
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
	actor := FixedBuyerID
	if err := conv.TransitionStatus(target, actor); err != nil {
		t.Fatalf("TransitionStatus(%s): %v", target.String(), err)
	}
	return conv
}
