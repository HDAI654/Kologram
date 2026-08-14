package application_test

import (
	"context"
	"testing"

	"github.com/HDAI654/Kologram/chat_service/internal/application"
	"github.com/HDAI654/Kologram/chat_service/internal/domain"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

func TestListConversations_Success(t *testing.T) {
	factory, repo, _, _ := newMocks()
	conv := openConversation()
	content, _ := valueobject.NewMessageContent("yo")
	_, _ = conv.AddMessage(mustUser(buyerID), content)
	repo.ListForUserFn = func(ctx context.Context, userID valueobject.UserID, limit, offset int) ([]*domain.Conversation, error) {
		return []*domain.Conversation{conv}, nil
	}
	handler := application.NewListConversationsHandler(factory)

	result, err := handler.Handle(context.Background(), application.ListConversationsQuery{
		UserID: buyerID, Limit: 10, Offset: 0,
	})
	if err != nil {
		t.Fatal(err)
	}
	if len(result.Items) != 1 {
		t.Fatalf("items=%d", len(result.Items))
	}
	if result.Items[0].LastMessage != "yo" {
		t.Fatal(result.Items[0].LastMessage)
	}
}

func TestListConversations_InvalidUser(t *testing.T) {
	factory, _, _, _ := newMocks()
	handler := application.NewListConversationsHandler(factory)
	_, err := handler.Handle(context.Background(), application.ListConversationsQuery{UserID: "nope"})
	if err == nil {
		t.Fatal("expected error")
	}
}
