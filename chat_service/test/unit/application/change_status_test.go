package application_test

import (
	"context"
	"testing"

	"github.com/HDAI654/Kologram/chat_service/internal/application"
	"github.com/HDAI654/Kologram/chat_service/internal/domain"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/event"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

func TestChangeStatus_Success(t *testing.T) {
	factory, repo, events, _ := newMocks()
	conv := openConversation()
	repo.GetByIDFn = func(ctx context.Context, id valueobject.ConversationID) (*domain.Conversation, error) {
		return conv, nil
	}
	handler := application.NewChangeStatusHandler(factory, events)

	result, err := handler.Handle(context.Background(), application.ChangeStatusCommand{
		ConversationID: conv.ID.String(),
		ActorID:        buyerID,
		NewStatus:      "CLOSED",
	})
	if err != nil {
		t.Fatal(err)
	}
	if result.Status != "CLOSED" {
		t.Fatalf("status=%s", result.Status)
	}
	if repo.UpdateCalls != 1 {
		t.Fatal("expected update")
	}
	if _, ok := events.Last().(event.ConversationStatusChanged); !ok {
		t.Fatalf("expected ConversationStatusChanged, got %T", events.Last())
	}
}

func TestChangeStatus_InvalidTransition(t *testing.T) {
	factory, repo, events, _ := newMocks()
	conv := openConversation()
	_ = conv.TransitionStatus(valueobject.StatusArchived, mustUser(buyerID))
	repo.GetByIDFn = func(ctx context.Context, id valueobject.ConversationID) (*domain.Conversation, error) {
		return conv, nil
	}
	handler := application.NewChangeStatusHandler(factory, events)

	_, err := handler.Handle(context.Background(), application.ChangeStatusCommand{
		ConversationID: conv.ID.String(),
		ActorID:        buyerID,
		NewStatus:      "OPEN",
	})
	if err != domain.ErrInvalidStatusTransition {
		t.Fatalf("got %v", err)
	}
}

func TestChangeStatus_NotParticipant(t *testing.T) {
	factory, repo, events, _ := newMocks()
	conv := openConversation()
	repo.GetByIDFn = func(ctx context.Context, id valueobject.ConversationID) (*domain.Conversation, error) {
		return conv, nil
	}
	handler := application.NewChangeStatusHandler(factory, events)

	_, err := handler.Handle(context.Background(), application.ChangeStatusCommand{
		ConversationID: conv.ID.String(),
		ActorID:        "550e8400-e29b-41d4-a716-446655440099",
		NewStatus:      "CLOSED",
	})
	if err != domain.ErrNotParticipant {
		t.Fatalf("got %v", err)
	}
}
