package application_test

import (
	"testing"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

const (
	BuyerIDRaw   = "0d47ddfe-a4ca-446a-839e-d3bbcba824c6"
	SellerIDRaw  = "bdf038e5-8b16-4825-a895-ce7d0648e845"
	ThirdIDRaw   = "a9a8c7c2-c7e5-41d5-be23-11357cd9f32a"
	ListingIDRaw = "431f7a61-1a30-4c3a-b2d4-5282ca2799b5"
	ClientMsg1   = "11111111-1111-4111-8111-111111111111"
	ClientMsg2   = "22222222-2222-4222-8222-222222222222"
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

func mustConversationID(t *testing.T, raw string) valueobjects.ConversationID {
	t.Helper()
	id, err := valueobjects.NewConversationID(raw)
	if err != nil {
		t.Fatalf("NewConversationID(%q): %v", raw, err)
	}
	return id
}

func messageableListing(t *testing.T) *entities.Listing {
	t.Helper()
	return &entities.Listing{
		ID:             mustListingID(t, ListingIDRaw),
		SellerID:       mustUserID(t, SellerIDRaw),
		MessageAllowed: true,
	}
}

func existingConversation(t *testing.T) *entities.Conversation {
	t.Helper()
	conv, err := entities.StartConversation(
		mustUserID(t, BuyerIDRaw),
		mustUserID(t, SellerIDRaw),
		mustListingID(t, ListingIDRaw),
	)
	if err != nil {
		t.Fatalf("StartConversation: %v", err)
	}
	return conv
}
