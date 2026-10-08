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

func TestDeleteMessageForEveryone_Success_RefreshesPreview(t *testing.T) {
	t.Parallel()

	convs, states, msgs, _, uow, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)

	olderContent, _ := valueobjects.NewMessageContent("older")
	older, _ := entities.NewMessage(conv.ID, mustUserID(t, BuyerIDRaw), ClientMsg1, olderContent)
	older.SentAt = time.Now().UTC().Add(-time.Minute)
	_ = msgs.Add(context.Background(), &older)

	newerContent, _ := valueobjects.NewMessageContent("newer")
	newer, _ := entities.NewMessage(conv.ID, mustUserID(t, BuyerIDRaw), ClientMsg2, newerContent)
	_ = msgs.Add(context.Background(), &newer)

	conv.RecordLastMessage(newer)
	_ = convs.Update(context.Background(), conv)

	realtime := NewFakeRealtimeNotifier()
	h := application.NewDeleteMessageForEveryoneHandler(factory, realtime, nil)

	result, err := h.Handle(context.Background(), application.DeleteMessageForEveryoneCommand{
		MessageID: newer.ID.String(),
		ActorID:   BuyerIDRaw,
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !result.DeletedForEveryone {
		t.Fatalf("DeletedForEveryone = false")
	}
	if !uow.Committed {
		t.Fatalf("expected commit")
	}

	stored, _ := msgs.GetByID(context.Background(), newer.ID)
	if !stored.DeletedForEveryone {
		t.Fatalf("message not soft-deleted")
	}
	if stored.Content.String() != "newer" {
		t.Fatalf("content must be retained for admin; got %q", stored.Content.String())
	}

	updatedConv, _ := convs.GetByID(context.Background(), conv.ID)
	if !updatedConv.LastMessageID.Equals(older.ID) {
		t.Fatalf("LastMessageID = %q, want older %q", updatedConv.LastMessageID.String(), older.ID.String())
	}
	if updatedConv.LastMessagePreview != "older" {
		t.Fatalf("preview = %q, want older", updatedConv.LastMessagePreview)
	}

	if realtime.Count() != 1 {
		t.Fatalf("realtime = %d, want 1", realtime.Count())
	}
	if realtime.Calls[0].UserID != SellerIDRaw {
		t.Fatalf("notify counterpart = %q, want seller", realtime.Calls[0].UserID)
	}
}

func TestDeleteMessageForEveryone_ClearsPreviewWhenNoVisibleLeft(t *testing.T) {
	t.Parallel()

	convs, states, msgs, _, _, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)

	content, _ := valueobjects.NewMessageContent("only one")
	msg, _ := entities.NewMessage(conv.ID, mustUserID(t, BuyerIDRaw), ClientMsg1, content)
	_ = msgs.Add(context.Background(), &msg)
	conv.RecordLastMessage(msg)
	_ = convs.Update(context.Background(), conv)

	h := application.NewDeleteMessageForEveryoneHandler(factory, NewFakeRealtimeNotifier(), nil)
	_, err := h.Handle(context.Background(), application.DeleteMessageForEveryoneCommand{
		MessageID: msg.ID.String(),
		ActorID:   BuyerIDRaw,
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	updatedConv, _ := convs.GetByID(context.Background(), conv.ID)
	if !updatedConv.LastMessageID.IsZero() {
		t.Fatalf("LastMessageID should be cleared")
	}
	if updatedConv.LastMessagePreview != "" {
		t.Fatalf("preview should be cleared")
	}
}

func TestDeleteMessageForEveryone_DoesNotTouchPreviewWhenNotLast(t *testing.T) {
	t.Parallel()

	convs, states, msgs, _, _, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)

	olderContent, _ := valueobjects.NewMessageContent("older")
	older, _ := entities.NewMessage(conv.ID, mustUserID(t, BuyerIDRaw), ClientMsg1, olderContent)
	older.SentAt = time.Now().UTC().Add(-time.Minute)
	_ = msgs.Add(context.Background(), &older)

	newerContent, _ := valueobjects.NewMessageContent("newer")
	newer, _ := entities.NewMessage(conv.ID, mustUserID(t, BuyerIDRaw), ClientMsg2, newerContent)
	_ = msgs.Add(context.Background(), &newer)

	conv.RecordLastMessage(newer)
	_ = convs.Update(context.Background(), conv)

	h := application.NewDeleteMessageForEveryoneHandler(factory, NewFakeRealtimeNotifier(), nil)
	_, err := h.Handle(context.Background(), application.DeleteMessageForEveryoneCommand{
		MessageID: older.ID.String(),
		ActorID:   BuyerIDRaw,
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	updatedConv, _ := convs.GetByID(context.Background(), conv.ID)
	if !updatedConv.LastMessageID.Equals(newer.ID) {
		t.Fatalf("LastMessageID must stay on newer message")
	}
	if updatedConv.LastMessagePreview != "newer" {
		t.Fatalf("preview must stay newer")
	}
}

func TestDeleteMessageForEveryone_RejectsNonAuthor(t *testing.T) {
	t.Parallel()

	convs, states, msgs, _, _, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)

	content, _ := valueobjects.NewMessageContent("mine")
	msg, _ := entities.NewMessage(conv.ID, mustUserID(t, BuyerIDRaw), ClientMsg1, content)
	_ = msgs.Add(context.Background(), &msg)
	conv.RecordLastMessage(msg)
	_ = convs.Update(context.Background(), conv)

	h := application.NewDeleteMessageForEveryoneHandler(factory, NewFakeRealtimeNotifier(), nil)
	_, err := h.Handle(context.Background(), application.DeleteMessageForEveryoneCommand{
		MessageID: msg.ID.String(),
		ActorID:   SellerIDRaw, // participant but not author
	})
	if !errors.Is(err, domainerrors.ErrNotMessageAuthor) {
		t.Fatalf("err = %v, want ErrNotMessageAuthor", err)
	}
}

func TestDeleteMessageForEveryone_MessageNotFound(t *testing.T) {
	t.Parallel()

	_, _, _, _, _, factory := NewFakeUowBundle()
	h := application.NewDeleteMessageForEveryoneHandler(factory, NewFakeRealtimeNotifier(), nil)
	_, err := h.Handle(context.Background(), application.DeleteMessageForEveryoneCommand{
		MessageID: "11111111-1111-4111-8111-111111111111",
		ActorID:   BuyerIDRaw,
	})
	var nf *domainerrors.NotFoundError
	if !errors.As(err, &nf) {
		t.Fatalf("err = %v, want NotFoundError", err)
	}
}

func TestDeleteMessageForEveryone_RejectsNonParticipant(t *testing.T) {
	t.Parallel()

	convs, states, msgs, _, _, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)
	content, _ := valueobjects.NewMessageContent("mine")
	msg, _ := entities.NewMessage(conv.ID, mustUserID(t, BuyerIDRaw), ClientMsg1, content)
	_ = msgs.Add(context.Background(), &msg)

	h := application.NewDeleteMessageForEveryoneHandler(factory, NewFakeRealtimeNotifier(), nil)
	_, err := h.Handle(context.Background(), application.DeleteMessageForEveryoneCommand{
		MessageID: msg.ID.String(),
		ActorID:   ThirdIDRaw,
	})
	if !errors.Is(err, domainerrors.ErrNotParticipant) {
		t.Fatalf("err = %v, want ErrNotParticipant", err)
	}
}

func TestDeleteMessageForEveryone_WindowExpired(t *testing.T) {
	t.Parallel()

	convs, states, msgs, _, _, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)
	content, _ := valueobjects.NewMessageContent("old")
	msg, _ := entities.NewMessage(conv.ID, mustUserID(t, BuyerIDRaw), ClientMsg1, content)
	msg.SentAt = time.Now().UTC().Add(-(entities.DeleteForEveryoneWindow + time.Hour))
	_ = msgs.Add(context.Background(), &msg)
	conv.RecordLastMessage(msg)
	_ = convs.Update(context.Background(), conv)

	h := application.NewDeleteMessageForEveryoneHandler(factory, NewFakeRealtimeNotifier(), nil)
	_, err := h.Handle(context.Background(), application.DeleteMessageForEveryoneCommand{
		MessageID: msg.ID.String(),
		ActorID:   BuyerIDRaw,
	})
	if !errors.Is(err, domainerrors.ErrDeleteWindowExpired) {
		t.Fatalf("err = %v, want ErrDeleteWindowExpired", err)
	}
}

func TestDeleteMessageForEveryone_CommitError_NoNotify(t *testing.T) {
	t.Parallel()

	convs, states, msgs, _, uow, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)
	content, _ := valueobjects.NewMessageContent("x")
	msg, _ := entities.NewMessage(conv.ID, mustUserID(t, BuyerIDRaw), ClientMsg1, content)
	_ = msgs.Add(context.Background(), &msg)
	conv.RecordLastMessage(msg)
	_ = convs.Update(context.Background(), conv)
	uow.CommitErr = errors.New("commit failed")

	realtime := NewFakeRealtimeNotifier()
	h := application.NewDeleteMessageForEveryoneHandler(factory, realtime, nil)
	_, err := h.Handle(context.Background(), application.DeleteMessageForEveryoneCommand{
		MessageID: msg.ID.String(),
		ActorID:   BuyerIDRaw,
	})
	if err == nil || err.Error() != "commit failed" {
		t.Fatalf("err = %v, want commit failed", err)
	}
	if realtime.Count() != 0 {
		t.Fatalf("must not notify after commit failure")
	}
}

func TestDeleteMessageForEveryone_InvalidIDs(t *testing.T) {
	t.Parallel()

	_, _, _, _, _, factory := NewFakeUowBundle()
	h := application.NewDeleteMessageForEveryoneHandler(factory, NewFakeRealtimeNotifier(), nil)

	_, err := h.Handle(context.Background(), application.DeleteMessageForEveryoneCommand{
		MessageID: "bad",
		ActorID:   BuyerIDRaw,
	})
	if !errors.Is(err, domainerrors.ErrInvalidArgument) {
		t.Fatalf("err = %v, want ErrInvalidArgument", err)
	}
}
