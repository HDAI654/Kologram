package domain_test

import (
	"testing"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

func mustUser(t *testing.T, raw string) valueobject.UserID {
	t.Helper()
	id, err := valueobject.NewUserID(raw)
	if err != nil {
		t.Fatal(err)
	}
	return id
}

func mustListing(t *testing.T, raw string) valueobject.ListingID {
	t.Helper()
	id, err := valueobject.NewListingID(raw)
	if err != nil {
		t.Fatal(err)
	}
	return id
}

func mustContent(t *testing.T, raw string) valueobject.MessageContent {
	t.Helper()
	c, err := valueobject.NewMessageContent(raw)
	if err != nil {
		t.Fatal(err)
	}
	return c
}

func TestStartConversationAndMessage(t *testing.T) {
	buyer := mustUser(t, "550e8400-e29b-41d4-a716-446655440001")
	seller := mustUser(t, "550e8400-e29b-41d4-a716-446655440002")
	listing := mustListing(t, "550e8400-e29b-41d4-a716-446655440003")
	conv, err := domain.StartConversation(buyer, seller, listing)
	if err != nil {
		t.Fatal(err)
	}
	if conv.Status.String() != "OPEN" {
		t.Fatalf("expected OPEN")
	}
	msg, err := conv.AddMessage(buyer, mustContent(t, "Is this still available?"))
	if err != nil {
		t.Fatal(err)
	}
	if msg.Content.String() != "Is this still available?" {
		t.Fatal("content")
	}
}

func TestCannotMessageWhenClosed(t *testing.T) {
	buyer := mustUser(t, "550e8400-e29b-41d4-a716-446655440001")
	seller := mustUser(t, "550e8400-e29b-41d4-a716-446655440002")
	listing := mustListing(t, "550e8400-e29b-41d4-a716-446655440003")
	conv, _ := domain.StartConversation(buyer, seller, listing)
	_ = conv.TransitionStatus(valueobject.StatusClosed, buyer)
	_, err := conv.AddMessage(buyer, mustContent(t, "hello"))
	if err != domain.ErrConversationNotOpen {
		t.Fatalf("got %v", err)
	}
}

func TestNotParticipant(t *testing.T) {
	buyer := mustUser(t, "550e8400-e29b-41d4-a716-446655440001")
	seller := mustUser(t, "550e8400-e29b-41d4-a716-446655440002")
	outsider := mustUser(t, "550e8400-e29b-41d4-a716-446655440099")
	listing := mustListing(t, "550e8400-e29b-41d4-a716-446655440003")
	conv, _ := domain.StartConversation(buyer, seller, listing)
	_, err := conv.AddMessage(outsider, mustContent(t, "hi"))
	if err != domain.ErrNotParticipant {
		t.Fatalf("got %v", err)
	}
}

func TestBuyerSellerSameRejected(t *testing.T) {
	user := mustUser(t, "550e8400-e29b-41d4-a716-446655440001")
	listing := mustListing(t, "550e8400-e29b-41d4-a716-446655440003")
	_, err := domain.StartConversation(user, user, listing)
	if err != domain.ErrBuyerSellerSame {
		t.Fatalf("got %v", err)
	}
}

func TestMarkRead(t *testing.T) {
	buyer := mustUser(t, "550e8400-e29b-41d4-a716-446655440001")
	seller := mustUser(t, "550e8400-e29b-41d4-a716-446655440002")
	listing := mustListing(t, "550e8400-e29b-41d4-a716-446655440003")
	conv, _ := domain.StartConversation(buyer, seller, listing)
	_, _ = conv.AddMessage(buyer, mustContent(t, "hello seller"))
	if err := conv.MarkMessagesRead(seller); err != nil {
		t.Fatal(err)
	}
	if !conv.Messages[0].IsRead {
		t.Fatal("expected read")
	}
}

func TestStatusTransitions(t *testing.T) {
	buyer := mustUser(t, "550e8400-e29b-41d4-a716-446655440001")
	seller := mustUser(t, "550e8400-e29b-41d4-a716-446655440002")
	listing := mustListing(t, "550e8400-e29b-41d4-a716-446655440003")
	conv, _ := domain.StartConversation(buyer, seller, listing)
	if err := conv.TransitionStatus(valueobject.StatusClosed, buyer); err != nil {
		t.Fatal(err)
	}
	if err := conv.TransitionStatus(valueobject.StatusOpen, seller); err != nil {
		t.Fatal(err)
	}
	if err := conv.TransitionStatus(valueobject.StatusArchived, buyer); err != nil {
		t.Fatal(err)
	}
	if err := conv.TransitionStatus(valueobject.StatusOpen, buyer); err != domain.ErrInvalidStatusTransition {
		t.Fatalf("got %v", err)
	}
}

func TestRehydrate(t *testing.T) {
	buyer := mustUser(t, "550e8400-e29b-41d4-a716-446655440001")
	seller := mustUser(t, "550e8400-e29b-41d4-a716-446655440002")
	listing := mustListing(t, "550e8400-e29b-41d4-a716-446655440003")
	id := valueobject.GenerateConversationID()
	now := time.Now().UTC()
	c := domain.RehydrateConversation(id, buyer, seller, listing, valueobject.StatusClosed, nil, now, now)
	if c.Status.String() != "CLOSED" {
		t.Fatal(c.Status.String())
	}
}
