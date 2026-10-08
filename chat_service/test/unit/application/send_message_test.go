package application_test

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/application"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/events"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

func seedOpenConversation(t *testing.T, convs *FakeConversationRepository, states *FakeConversationUserStateRepository) *entities.Conversation {
	t.Helper()
	conv := existingConversation(t)
	if err := convs.Add(context.Background(), conv); err != nil {
		t.Fatalf("seed conversation: %v", err)
	}
	now := time.Now().UTC()
	for _, uid := range conv.ParticipantIDs() {
		st := entities.NewConversationUserState(conv.ID, uid, now)
		if err := states.Add(context.Background(), st); err != nil {
			t.Fatalf("seed state: %v", err)
		}
	}
	return conv
}

func TestSendMessage_Success(t *testing.T) {
	t.Parallel()

	convs, states, msgs, _, uow, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)
	publisher := NewFakeEventPublisher()
	realtime := NewFakeRealtimeNotifier()

	h := application.NewSendMessageHandler(factory, publisher, realtime, nil)

	result, err := h.Handle(context.Background(), application.SendMessageCommand{
		ConversationID:  conv.ID.String(),
		SenderID:        BuyerIDRaw,
		ClientMessageID: ClientMsg1,
		Content:         "hello seller",
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result.IdempotentHit {
		t.Fatalf("IdempotentHit = true, want false")
	}
	if result.MessageID == "" {
		t.Fatalf("MessageID empty")
	}
	if result.ConversationID != conv.ID.String() {
		t.Fatalf("ConversationID mismatch")
	}
	if !uow.Committed {
		t.Fatalf("expected commit")
	}
	if _, ok := msgs.ByID[result.MessageID]; !ok {
		t.Fatalf("message not persisted")
	}

	updatedConv, _ := convs.GetByID(context.Background(), conv.ID)
	if updatedConv.LastMessagePreview != "hello seller" {
		t.Fatalf("preview = %q, want hello seller", updatedConv.LastMessagePreview)
	}
	if updatedConv.LastMessageID.String() != result.MessageID {
		t.Fatalf("LastMessageID = %q, want %q", updatedConv.LastMessageID.String(), result.MessageID)
	}

	sellerState, _ := states.Get(context.Background(), conv.ID, mustUserID(t, SellerIDRaw))
	if sellerState.UnreadCount != 1 {
		t.Fatalf("seller UnreadCount = %d, want 1", sellerState.UnreadCount)
	}
	buyerState, _ := states.Get(context.Background(), conv.ID, mustUserID(t, BuyerIDRaw))
	if buyerState.UnreadCount != 0 {
		t.Fatalf("buyer UnreadCount = %d, want 0", buyerState.UnreadCount)
	}

	if publisher.Count() != 1 {
		t.Fatalf("events = %d, want 1", publisher.Count())
	}
	evt, ok := publisher.Events[0].(events.MessageSent)
	if !ok {
		t.Fatalf("event type = %T, want MessageSent", publisher.Events[0])
	}
	if evt.MessageID != result.MessageID || evt.SenderID != BuyerIDRaw || evt.RecipientID != SellerIDRaw {
		t.Fatalf("event mismatch: %+v", evt)
	}

	if realtime.Count() != 1 {
		t.Fatalf("realtime calls = %d, want 1", realtime.Count())
	}
	if realtime.Calls[0].UserID != SellerIDRaw {
		t.Fatalf("notify user = %q, want seller", realtime.Calls[0].UserID)
	}
}

func TestSendMessage_IdempotentHit(t *testing.T) {
	t.Parallel()

	convs, states, msgs, _, uow, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)

	content, err := valueobjects.NewMessageContent("already sent")
	if err != nil {
		t.Fatalf("content: %v", err)
	}
	existing, err := entities.NewMessage(conv.ID, mustUserID(t, BuyerIDRaw), ClientMsg1, content)
	if err != nil {
		t.Fatalf("NewMessage: %v", err)
	}
	if err := msgs.Add(context.Background(), &existing); err != nil {
		t.Fatalf("seed message: %v", err)
	}

	publisher := NewFakeEventPublisher()
	realtime := NewFakeRealtimeNotifier()
	h := application.NewSendMessageHandler(factory, publisher, realtime, nil)

	result, err := h.Handle(context.Background(), application.SendMessageCommand{
		ConversationID:  conv.ID.String(),
		SenderID:        BuyerIDRaw,
		ClientMessageID: ClientMsg1,
		Content:         "already sent",
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !result.IdempotentHit {
		t.Fatalf("IdempotentHit = false, want true")
	}
	if result.MessageID != existing.ID.String() {
		t.Fatalf("MessageID = %q, want %q", result.MessageID, existing.ID.String())
	}
	if uow.Committed {
		t.Fatalf("must not commit on idempotent hit")
	}
	if publisher.Count() != 0 {
		t.Fatalf("must not publish on idempotent hit")
	}
	if realtime.Count() != 0 {
		t.Fatalf("must not notify on idempotent hit")
	}
}

func TestSendMessage_UnhidesRecipient(t *testing.T) {
	t.Parallel()

	convs, states, _, _, _, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)

	sellerState, _ := states.Get(context.Background(), conv.ID, mustUserID(t, SellerIDRaw))
	sellerState.Hide(time.Now().UTC())
	_ = states.Update(context.Background(), sellerState)

	h := application.NewSendMessageHandler(factory, NewFakeEventPublisher(), NewFakeRealtimeNotifier(), nil)

	_, err := h.Handle(context.Background(), application.SendMessageCommand{
		ConversationID:  conv.ID.String(),
		SenderID:        BuyerIDRaw,
		ClientMessageID: ClientMsg1,
		Content:         "bring back",
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	updated, _ := states.Get(context.Background(), conv.ID, mustUserID(t, SellerIDRaw))
	if updated.IsHidden {
		t.Fatalf("recipient still hidden after incoming message")
	}
}

func TestSendMessage_SkipsRealtimeWhenRecipientMuted(t *testing.T) {
	t.Parallel()

	convs, states, _, _, _, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)

	sellerState, _ := states.Get(context.Background(), conv.ID, mustUserID(t, SellerIDRaw))
	until := time.Now().UTC().Add(time.Hour)
	sellerState.Mute(until, time.Now().UTC())
	_ = states.Update(context.Background(), sellerState)

	publisher := NewFakeEventPublisher()
	realtime := NewFakeRealtimeNotifier()
	h := application.NewSendMessageHandler(factory, publisher, realtime, nil)

	_, err := h.Handle(context.Background(), application.SendMessageCommand{
		ConversationID:  conv.ID.String(),
		SenderID:        BuyerIDRaw,
		ClientMessageID: ClientMsg1,
		Content:         "muted path",
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if publisher.Count() != 1 {
		t.Fatalf("event still required for offline push; got %d", publisher.Count())
	}
	if realtime.Count() != 0 {
		t.Fatalf("realtime must be skipped when muted; got %d", realtime.Count())
	}
}

func TestSendMessage_RejectsInvalidIDsAndContent(t *testing.T) {
	t.Parallel()

	_, _, _, _, _, factory := NewFakeUowBundle()
	h := application.NewSendMessageHandler(factory, NewFakeEventPublisher(), NewFakeRealtimeNotifier(), nil)
	ctx := context.Background()

	cases := []struct {
		name string
		cmd  application.SendMessageCommand
	}{
		{"bad conversation", application.SendMessageCommand{ConversationID: "x", SenderID: BuyerIDRaw, ClientMessageID: ClientMsg1, Content: "hi"}},
		{"bad sender", application.SendMessageCommand{ConversationID: "0d47ddfe-a4ca-446a-839e-d3bbcba824c6", SenderID: "x", ClientMessageID: ClientMsg1, Content: "hi"}},
		{"empty client id", application.SendMessageCommand{ConversationID: "0d47ddfe-a4ca-446a-839e-d3bbcba824c6", SenderID: BuyerIDRaw, ClientMessageID: "", Content: "hi"}},
		{"non-uuid client id", application.SendMessageCommand{ConversationID: "0d47ddfe-a4ca-446a-839e-d3bbcba824c6", SenderID: BuyerIDRaw, ClientMessageID: "client-1", Content: "hi"}},
		{"empty content", application.SendMessageCommand{ConversationID: "0d47ddfe-a4ca-446a-839e-d3bbcba824c6", SenderID: BuyerIDRaw, ClientMessageID: ClientMsg1, Content: "   "}},
	}

	for _, tc := range cases {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()
			_, err := h.Handle(ctx, tc.cmd)
			if !errors.Is(err, domainerrors.ErrInvalidArgument) {
				t.Fatalf("err = %v, want ErrInvalidArgument", err)
			}
		})
	}
}

func TestSendMessage_ConversationNotFound(t *testing.T) {
	t.Parallel()

	_, _, _, _, _, factory := NewFakeUowBundle()
	h := application.NewSendMessageHandler(factory, NewFakeEventPublisher(), NewFakeRealtimeNotifier(), nil)

	_, err := h.Handle(context.Background(), application.SendMessageCommand{
		ConversationID:  "0d47ddfe-a4ca-446a-839e-d3bbcba824c6",
		SenderID:        BuyerIDRaw,
		ClientMessageID: ClientMsg1,
		Content:         "hello",
	})
	var nf *domainerrors.NotFoundError
	if !errors.As(err, &nf) {
		t.Fatalf("err = %v, want NotFoundError", err)
	}
}

func TestSendMessage_RejectsNonParticipant(t *testing.T) {
	t.Parallel()

	convs, states, _, _, _, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)
	h := application.NewSendMessageHandler(factory, NewFakeEventPublisher(), NewFakeRealtimeNotifier(), nil)

	_, err := h.Handle(context.Background(), application.SendMessageCommand{
		ConversationID:  conv.ID.String(),
		SenderID:        ThirdIDRaw,
		ClientMessageID: ClientMsg1,
		Content:         "intruder",
	})
	if !errors.Is(err, domainerrors.ErrNotParticipant) {
		t.Fatalf("err = %v, want ErrNotParticipant", err)
	}
}

func TestSendMessage_RejectsWhenBlocked(t *testing.T) {
	t.Parallel()

	convs, states, _, blocks, _, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)
	blocks.ForceEitherWay(true)
	publisher := NewFakeEventPublisher()
	h := application.NewSendMessageHandler(factory, publisher, NewFakeRealtimeNotifier(), nil)

	_, err := h.Handle(context.Background(), application.SendMessageCommand{
		ConversationID:  conv.ID.String(),
		SenderID:        BuyerIDRaw,
		ClientMessageID: ClientMsg1,
		Content:         "blocked",
	})
	if !errors.Is(err, domainerrors.ErrUsersBlocked) {
		t.Fatalf("err = %v, want ErrUsersBlocked", err)
	}
	if publisher.Count() != 0 {
		t.Fatalf("must not publish when blocked")
	}
}

func TestSendMessage_RejectsReadOnlyConversation(t *testing.T) {
	t.Parallel()

	convs, states, _, _, _, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)
	conv.IsReadOnly = true
	_ = convs.Update(context.Background(), conv)

	h := application.NewSendMessageHandler(factory, NewFakeEventPublisher(), NewFakeRealtimeNotifier(), nil)

	_, err := h.Handle(context.Background(), application.SendMessageCommand{
		ConversationID:  conv.ID.String(),
		SenderID:        BuyerIDRaw,
		ClientMessageID: ClientMsg1,
		Content:         "too late",
	})
	if !errors.Is(err, domainerrors.ErrConversationNotOpen) {
		t.Fatalf("err = %v, want ErrConversationNotOpen", err)
	}
}

func TestSendMessage_CommitError_DoesNotPublishOrNotify(t *testing.T) {
	t.Parallel()

	convs, states, _, _, uow, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)
	uow.CommitErr = errors.New("commit failed")
	publisher := NewFakeEventPublisher()
	realtime := NewFakeRealtimeNotifier()
	h := application.NewSendMessageHandler(factory, publisher, realtime, nil)

	_, err := h.Handle(context.Background(), application.SendMessageCommand{
		ConversationID:  conv.ID.String(),
		SenderID:        BuyerIDRaw,
		ClientMessageID: ClientMsg1,
		Content:         "hello",
	})
	if err == nil || err.Error() != "commit failed" {
		t.Fatalf("err = %v, want commit failed", err)
	}
	if publisher.Count() != 0 {
		t.Fatalf("must not publish after commit failure")
	}
	if realtime.Count() != 0 {
		t.Fatalf("must not notify after commit failure")
	}
}
