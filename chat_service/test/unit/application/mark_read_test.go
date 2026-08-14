package application_test

import (
	"context"
	"testing"

	"github.com/HDAI654/Kologram/chat_service/internal/application"
	"github.com/HDAI654/Kologram/chat_service/internal/domain"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/event"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

func TestMarkRead_Success(t *testing.T) {
	factory, repo, events, rt := newMocks()
	conv := openConversation()
	content, _ := valueobject.NewMessageContent("hello")
	_, _ = conv.AddMessage(mustUser(buyerID), content)
	repo.GetByIDFn = func(ctx context.Context, id valueobject.ConversationID) (*domain.Conversation, error) {
		return conv, nil
	}
	handler := application.NewMarkReadHandler(factory, events, rt)

	result, err := handler.Handle(context.Background(), application.MarkReadCommand{
		ConversationID: conv.ID.String(),
		ReaderID:       sellerID,
	})
	if err != nil {
		t.Fatal(err)
	}
	if result.ConversationID != conv.ID.String() {
		t.Fatal("id mismatch")
	}
	if repo.UpdateCalls != 1 {
		t.Fatal("expected update")
	}
	if _, ok := events.Last().(event.MessagesRead); !ok {
		t.Fatalf("expected MessagesRead, got %T", events.Last())
	}
	if len(rt.notified) < 2 {
		t.Fatalf("expected notify both participants, got %v", rt.notified)
	}
}

func TestMarkRead_NotParticipant(t *testing.T) {
	factory, repo, events, rt := newMocks()
	conv := openConversation()
	repo.GetByIDFn = func(ctx context.Context, id valueobject.ConversationID) (*domain.Conversation, error) {
		return conv, nil
	}
	handler := application.NewMarkReadHandler(factory, events, rt)

	_, err := handler.Handle(context.Background(), application.MarkReadCommand{
		ConversationID: conv.ID.String(),
		ReaderID:       "550e8400-e29b-41d4-a716-446655440099",
	})
	if err != domain.ErrNotParticipant {
		t.Fatalf("got %v", err)
	}
}
