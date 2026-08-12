package domain_test

import (
	"testing"

	"github.com/HDAI654/Kologram/chat_service/internal/domain"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

func TestNewMessage(t *testing.T) {
	cid := valueobject.GenerateConversationID()
	sid, _ := valueobject.NewUserID("550e8400-e29b-41d4-a716-446655440001")
	content, _ := valueobject.NewMessageContent("hello")
	msg := domain.NewMessage(cid, sid, content)
	if msg.IsRead {
		t.Fatal("new message should be unread")
	}
	msg.MarkRead()
	if !msg.IsRead {
		t.Fatal("expected read")
	}
	if msg.ConversationID.String() != cid.String() {
		t.Fatal("conversation id")
	}
}
