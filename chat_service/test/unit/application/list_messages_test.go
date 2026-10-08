package application_test

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/application"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

func TestListMessages_Success_HasMore(t *testing.T) {
	t.Parallel()

	convs := NewFakeConversationRepository()
	msgs := NewFakeMessageRepository()
	conv := existingConversation(t)
	_ = convs.Add(context.Background(), conv)

	for i, clientID := range []string{ClientMsg1, ClientMsg2, "33333333-3333-4333-8333-333333333333"} {
		content, _ := valueobjects.NewMessageContent("msg")
		m, err := entities.NewMessage(conv.ID, mustUserID(t, BuyerIDRaw), clientID, content)
		if err != nil {
			t.Fatalf("NewMessage: %v", err)
		}
		m.SentAt = time.Now().UTC().Add(time.Duration(i) * time.Second)
		_ = msgs.Add(context.Background(), &m)
	}

	h := application.NewListMessagesHandler(convs, msgs)
	result, err := h.Handle(context.Background(), application.ListMessagesQuery{
		ConversationID: conv.ID.String(),
		RequesterID:    BuyerIDRaw,
		Limit:          2,
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(result.Items) != 2 {
		t.Fatalf("items = %d, want 2", len(result.Items))
	}
	if !result.HasMore {
		t.Fatalf("HasMore = false, want true")
	}
}

func TestListMessages_ExcludesSoftDeleted(t *testing.T) {
	t.Parallel()

	convs := NewFakeConversationRepository()
	msgs := NewFakeMessageRepository()
	conv := existingConversation(t)
	_ = convs.Add(context.Background(), conv)

	content, _ := valueobjects.NewMessageContent("visible")
	visible, _ := entities.NewMessage(conv.ID, mustUserID(t, BuyerIDRaw), ClientMsg1, content)
	_ = msgs.Add(context.Background(), &visible)

	deletedContent, _ := valueobjects.NewMessageContent("gone")
	deleted, _ := entities.NewMessage(conv.ID, mustUserID(t, BuyerIDRaw), ClientMsg2, deletedContent)
	_ = deleted.DeleteForEveryone(mustUserID(t, BuyerIDRaw))
	_ = msgs.Add(context.Background(), &deleted)

	h := application.NewListMessagesHandler(convs, msgs)
	result, err := h.Handle(context.Background(), application.ListMessagesQuery{
		ConversationID: conv.ID.String(),
		RequesterID:    BuyerIDRaw,
		Limit:          10,
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(result.Items) != 1 {
		t.Fatalf("items = %d, want 1 (soft-deleted excluded)", len(result.Items))
	}
	if result.Items[0].MessageID != visible.ID.String() {
		t.Fatalf("unexpected message returned")
	}
}

func TestListMessages_RejectsNonParticipant(t *testing.T) {
	t.Parallel()

	convs := NewFakeConversationRepository()
	msgs := NewFakeMessageRepository()
	conv := existingConversation(t)
	_ = convs.Add(context.Background(), conv)

	h := application.NewListMessagesHandler(convs, msgs)
	_, err := h.Handle(context.Background(), application.ListMessagesQuery{
		ConversationID: conv.ID.String(),
		RequesterID:    ThirdIDRaw,
	})
	if !errors.Is(err, domainerrors.ErrNotParticipant) {
		t.Fatalf("err = %v, want ErrNotParticipant", err)
	}
}

func TestListMessages_ConversationNotFound(t *testing.T) {
	t.Parallel()

	h := application.NewListMessagesHandler(NewFakeConversationRepository(), NewFakeMessageRepository())
	_, err := h.Handle(context.Background(), application.ListMessagesQuery{
		ConversationID: "0d47ddfe-a4ca-446a-839e-d3bbcba824c6",
		RequesterID:    BuyerIDRaw,
	})
	var nf *domainerrors.NotFoundError
	if !errors.As(err, &nf) {
		t.Fatalf("err = %v, want NotFoundError", err)
	}
}

func TestListMessages_InvalidDirection(t *testing.T) {
	t.Parallel()

	h := application.NewListMessagesHandler(NewFakeConversationRepository(), NewFakeMessageRepository())
	_, err := h.Handle(context.Background(), application.ListMessagesQuery{
		ConversationID: "0d47ddfe-a4ca-446a-839e-d3bbcba824c6",
		RequesterID:    BuyerIDRaw,
		Direction:      "sideways",
	})
	var ve *domainerrors.ValidationError
	if !errors.As(err, &ve) || ve.Field != "direction" {
		t.Fatalf("err = %v, want ValidationError field direction", err)
	}
}

func TestListMessages_InvalidCursorSentAt(t *testing.T) {
	t.Parallel()

	h := application.NewListMessagesHandler(NewFakeConversationRepository(), NewFakeMessageRepository())
	_, err := h.Handle(context.Background(), application.ListMessagesQuery{
		ConversationID:  "0d47ddfe-a4ca-446a-839e-d3bbcba824c6",
		RequesterID:     BuyerIDRaw,
		CursorMessageID: ClientMsg1,
		CursorSentAt:    "not-a-time",
	})
	var ve *domainerrors.ValidationError
	if !errors.As(err, &ve) || ve.Field != "cursor_sent_at" {
		t.Fatalf("err = %v, want ValidationError field cursor_sent_at", err)
	}
}

func TestListMessages_InvalidRequesterID(t *testing.T) {
	t.Parallel()

	h := application.NewListMessagesHandler(NewFakeConversationRepository(), NewFakeMessageRepository())
	_, err := h.Handle(context.Background(), application.ListMessagesQuery{
		ConversationID: "0d47ddfe-a4ca-446a-839e-d3bbcba824c6",
		RequesterID:    "bad",
	})
	if !errors.Is(err, domainerrors.ErrInvalidArgument) {
		t.Fatalf("err = %v, want ErrInvalidArgument", err)
	}
}
