package application_test

import (
	"context"
	"testing"

	"github.com/HDAI654/Kologram/chat_service/internal/application"
	"github.com/HDAI654/Kologram/chat_service/internal/domain"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/event"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

func TestSendMessage_Success(t *testing.T) {
	factory, repo, events, rt := newMocks()
	conv := openConversation()
	repo.GetByIDFn = func(ctx context.Context, id valueobject.ConversationID) (*domain.Conversation, error) {
		return conv, nil
	}
	handler := application.NewSendMessageHandler(factory, events, rt)

	result, err := handler.Handle(context.Background(), application.SendMessageCommand{
		ConversationID: conv.ID.String(),
		SenderID:       buyerID,
		Content:        "Is this still available?",
	})
	if err != nil {
		t.Fatal(err)
	}
	if result.MessageID == "" {
		t.Fatal("expected message id")
	}
	if repo.UpdateCalls != 1 {
		t.Fatalf("update calls=%d", repo.UpdateCalls)
	}
	if !factory.uow.committed {
		t.Fatal("expected commit")
	}
	if _, ok := events.Last().(event.MessageSent); !ok {
		t.Fatalf("expected MessageSent, got %T", events.Last())
	}
	if len(rt.notified) < 2 {
		t.Fatalf("expected notify recipient and sender, got %v", rt.notified)
	}
	seen := map[string]bool{}
	for _, id := range rt.notified {
		seen[id] = true
	}
	if !seen[sellerID] || !seen[buyerID] {
		t.Fatalf("expected both parties notified, got %v", rt.notified)
	}
}

func TestSendMessage_NotParticipant(t *testing.T) {
	factory, repo, events, rt := newMocks()
	conv := openConversation()
	repo.GetByIDFn = func(ctx context.Context, id valueobject.ConversationID) (*domain.Conversation, error) {
		return conv, nil
	}
	handler := application.NewSendMessageHandler(factory, events, rt)

	stranger := "550e8400-e29b-41d4-a716-446655440099"
	_, err := handler.Handle(context.Background(), application.SendMessageCommand{
		ConversationID: conv.ID.String(),
		SenderID:       stranger,
		Content:        "hi",
	})
	if err != domain.ErrNotParticipant {
		t.Fatalf("got %v", err)
	}
}

func TestSendMessage_ConversationNotFound(t *testing.T) {
	factory, repo, events, rt := newMocks()
	repo.GetByIDFn = func(ctx context.Context, id valueobject.ConversationID) (*domain.Conversation, error) {
		return nil, domain.ErrConversationNotFound
	}
	handler := application.NewSendMessageHandler(factory, events, rt)

	_, err := handler.Handle(context.Background(), application.SendMessageCommand{
		ConversationID: valueobject.GenerateConversationID().String(),
		SenderID:       buyerID,
		Content:        "hi",
	})
	if err != domain.ErrConversationNotFound {
		t.Fatalf("got %v", err)
	}
}

func TestSendMessage_ClosedConversation(t *testing.T) {
	factory, repo, events, rt := newMocks()
	conv := openConversation()
	_ = conv.TransitionStatus(valueobject.StatusClosed, mustUser(buyerID))
	repo.GetByIDFn = func(ctx context.Context, id valueobject.ConversationID) (*domain.Conversation, error) {
		return conv, nil
	}
	handler := application.NewSendMessageHandler(factory, events, rt)

	_, err := handler.Handle(context.Background(), application.SendMessageCommand{
		ConversationID: conv.ID.String(),
		SenderID:       buyerID,
		Content:        "still here?",
	})
	if err != domain.ErrConversationNotOpen {
		t.Fatalf("got %v", err)
	}
}

func TestSendMessage_EmptyContent(t *testing.T) {
	factory, _, events, rt := newMocks()
	handler := application.NewSendMessageHandler(factory, events, rt)
	_, err := handler.Handle(context.Background(), application.SendMessageCommand{
		ConversationID: valueobject.GenerateConversationID().String(),
		SenderID:       buyerID,
		Content:        "   ",
	})
	if err == nil {
		t.Fatal("expected content validation error")
	}
}
