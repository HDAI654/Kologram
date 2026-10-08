package messaging_test

import (
	"context"
	"testing"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/events"
	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/messaging"
	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/realtime"
)

func TestNoOpEventPublisher_Publish(t *testing.T) {
	t.Parallel()

	p := messaging.NewNoOpEventPublisher()
	err := p.Publish(context.Background(), events.MessageSent{
		ConversationID: "c",
		MessageID:      "m",
		SenderID:       "s",
		RecipientID:    "r",
		At:             time.Now().UTC(),
	})
	if err != nil {
		t.Fatalf("Publish: %v", err)
	}
}

func TestNoOpRealtime_NotifyUser(t *testing.T) {
	t.Parallel()

	n := realtime.NewNoOpNotifier()
	if err := n.NotifyUser(context.Background(), "user", map[string]any{"x": 1}); err != nil {
		t.Fatalf("NotifyUser: %v", err)
	}
}

func TestRabbitMQEventPublisher_NilChannel(t *testing.T) {
	t.Parallel()

	p := &messaging.RabbitMQEventPublisher{}
	err := p.Publish(context.Background(), events.ConversationStarted{
		ConversationID: "c",
		BuyerID:        "b",
		SellerID:       "s",
		ListingID:      "l",
		At:             time.Now().UTC(),
	})
	if err == nil {
		t.Fatalf("expected error on nil channel")
	}
}
