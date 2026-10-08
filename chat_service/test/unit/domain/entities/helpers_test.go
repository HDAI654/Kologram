package entities_test

import (
	"testing"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

var (
	FixedBuyerID, _      = valueobjects.NewUserID("0d47ddfe-a4ca-446a-839e-d3bbcba824c6")
	FixedSellerID, _     = valueobjects.NewUserID("bdf038e5-8b16-4825-a895-ce7d0648e845")
	FixedThirdPartyID, _ = valueobjects.NewUserID("a9a8c7c2-c7e5-41d5-be23-11357cd9f32a")
	FixedListingID, _    = valueobjects.NewListingID("431f7a61-1a30-4c3a-b2d4-5282ca2799b5")
)

// Valid UUID v4 client message ids for tests.
const (
	ClientMsgID1 = "11111111-1111-4111-8111-111111111111"
	ClientMsgID2 = "22222222-2222-4222-8222-222222222222"
	ClientMsgID3 = "33333333-3333-4333-8333-333333333333"
)

func mustContent(t *testing.T, raw string) valueobjects.MessageContent {
	t.Helper()
	c, err := valueobjects.NewMessageContent(raw)
	if err != nil {
		t.Fatalf("NewMessageContent(%q): %v", raw, err)
	}
	return c
}

func mustMessageID(t *testing.T, raw string) valueobjects.MessageID {
	t.Helper()
	id, err := valueobjects.NewMessageID(raw)
	if err != nil {
		t.Fatalf("NewMessageID(%q): %v", raw, err)
	}
	return id
}

func newConversation(t *testing.T) *entities.Conversation {
	t.Helper()
	conv, err := entities.StartConversation(FixedBuyerID, FixedSellerID, FixedListingID)
	if err != nil {
		t.Fatalf("StartConversation: %v", err)
	}
	return conv
}

func mustMessage(
	t *testing.T,
	conversationID valueobjects.ConversationID,
	senderID valueobjects.UserID,
	clientMessageID string,
	content string,
) entities.Message {
	t.Helper()
	msg, err := entities.NewMessage(conversationID, senderID, clientMessageID, mustContent(t, content))
	if err != nil {
		t.Fatalf("NewMessage: %v", err)
	}
	return msg
}

func newUserState(t *testing.T, conv *entities.Conversation, userID valueobjects.UserID) *entities.ConversationUserState {
	t.Helper()
	now := time.Now().UTC()
	return entities.NewConversationUserState(conv.ID, userID, now)
}
