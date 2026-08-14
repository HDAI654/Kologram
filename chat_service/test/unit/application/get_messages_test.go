package application_test

import (
	"context"
	"testing"

	"github.com/HDAI654/Kologram/chat_service/internal/application"
	"github.com/HDAI654/Kologram/chat_service/internal/domain"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

func TestGetMessages_Success(t *testing.T) {
	factory, repo, _, _ := newMocks()
	conv := openConversation()
	content, _ := valueobject.NewMessageContent("hello")
	_, _ = conv.AddMessage(mustUser(buyerID), content)
	repo.GetByIDFn = func(ctx context.Context, id valueobject.ConversationID) (*domain.Conversation, error) {
		return conv, nil
	}
	handler := application.NewGetMessagesHandler(factory)

	result, err := handler.Handle(context.Background(), application.GetMessagesQuery{
		ConversationID: conv.ID.String(),
		RequesterID:    buyerID,
	})
	if err != nil {
		t.Fatal(err)
	}
	if len(result.Messages) != 1 {
		t.Fatalf("messages=%d", len(result.Messages))
	}
	if result.Messages[0].Content != "hello" {
		t.Fatal(result.Messages[0].Content)
	}
}

func TestGetMessages_NotParticipant(t *testing.T) {
	factory, repo, _, _ := newMocks()
	conv := openConversation()
	repo.GetByIDFn = func(ctx context.Context, id valueobject.ConversationID) (*domain.Conversation, error) {
		return conv, nil
	}
	handler := application.NewGetMessagesHandler(factory)

	_, err := handler.Handle(context.Background(), application.GetMessagesQuery{
		ConversationID: conv.ID.String(),
		RequesterID:    "550e8400-e29b-41d4-a716-446655440099",
	})
	if err != domain.ErrNotParticipant {
		t.Fatalf("got %v", err)
	}
}
