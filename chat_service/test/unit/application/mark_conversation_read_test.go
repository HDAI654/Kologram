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

func TestMarkConversationRead_Success(t *testing.T) {
	t.Parallel()

	convs, states, msgs, _, uow, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)

	content, _ := valueobjects.NewMessageContent("hello")
	msg, err := entities.NewMessage(conv.ID, mustUserID(t, SellerIDRaw), ClientMsg1, content)
	if err != nil {
		t.Fatalf("NewMessage: %v", err)
	}
	_ = msgs.Add(context.Background(), &msg)

	buyerState, _ := states.Get(context.Background(), conv.ID, mustUserID(t, BuyerIDRaw))
	buyerState.UnreadCount = 5
	_ = states.Update(context.Background(), buyerState)

	h := application.NewMarkConversationReadHandler(factory)
	result, err := h.Handle(context.Background(), application.MarkConversationReadCommand{
		ConversationID:    conv.ID.String(),
		UserID:            BuyerIDRaw,
		LastReadMessageID: msg.ID.String(),
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result.UnreadCount != 0 {
		t.Fatalf("UnreadCount = %d, want 0", result.UnreadCount)
	}
	if !uow.Committed {
		t.Fatalf("expected commit")
	}

	updated, _ := states.Get(context.Background(), conv.ID, mustUserID(t, BuyerIDRaw))
	if !updated.LastReadMessageID.Equals(msg.ID) {
		t.Fatalf("LastReadMessageID not updated")
	}
	if updated.UnreadCount != 0 {
		t.Fatalf("persisted UnreadCount = %d, want 0", updated.UnreadCount)
	}
}

func TestMarkConversationRead_MessageNotFound(t *testing.T) {
	t.Parallel()

	convs, states, _, _, _, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)

	h := application.NewMarkConversationReadHandler(factory)
	_, err := h.Handle(context.Background(), application.MarkConversationReadCommand{
		ConversationID:    conv.ID.String(),
		UserID:            BuyerIDRaw,
		LastReadMessageID: "11111111-1111-4111-8111-111111111111",
	})
	var nf *domainerrors.NotFoundError
	if !errors.As(err, &nf) || nf.Field != "message_id" {
		t.Fatalf("err = %v, want NotFoundError message_id", err)
	}
}

func TestMarkConversationRead_MessageWrongConversation(t *testing.T) {
	t.Parallel()

	convs, states, msgs, _, _, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)

	other, err := entities.StartConversation(
		mustUserID(t, BuyerIDRaw),
		mustUserID(t, SellerIDRaw),
		mustListingID(t, "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
	)
	if err != nil {
		t.Fatalf("other conv: %v", err)
	}
	content, _ := valueobjects.NewMessageContent("elsewhere")
	msg, _ := entities.NewMessage(other.ID, mustUserID(t, BuyerIDRaw), ClientMsg1, content)
	_ = msgs.Add(context.Background(), &msg)

	h := application.NewMarkConversationReadHandler(factory)
	_, err = h.Handle(context.Background(), application.MarkConversationReadCommand{
		ConversationID:    conv.ID.String(),
		UserID:            BuyerIDRaw,
		LastReadMessageID: msg.ID.String(),
	})
	var ve *domainerrors.ValidationError
	if !errors.As(err, &ve) || ve.Field != "last_read_message_id" {
		t.Fatalf("err = %v, want ValidationError last_read_message_id", err)
	}
}

func TestMarkConversationRead_RejectsNonParticipant(t *testing.T) {
	t.Parallel()

	convs, states, msgs, _, _, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)
	content, _ := valueobjects.NewMessageContent("hello")
	msg, _ := entities.NewMessage(conv.ID, mustUserID(t, BuyerIDRaw), ClientMsg1, content)
	_ = msgs.Add(context.Background(), &msg)

	h := application.NewMarkConversationReadHandler(factory)
	_, err := h.Handle(context.Background(), application.MarkConversationReadCommand{
		ConversationID:    conv.ID.String(),
		UserID:            ThirdIDRaw,
		LastReadMessageID: msg.ID.String(),
	})
	if !errors.Is(err, domainerrors.ErrNotParticipant) {
		t.Fatalf("err = %v, want ErrNotParticipant", err)
	}
}


func TestMarkConversationRead_SoftDeletedMessageNotFound(t *testing.T) {
	t.Parallel()

	convs, states, msgs, _, _, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)

	content, _ := valueobjects.NewMessageContent("gone")
	msg, err := entities.NewMessage(conv.ID, mustUserID(t, SellerIDRaw), ClientMsg1, content)
	if err != nil {
		t.Fatalf("NewMessage: %v", err)
	}
	if err := msg.DeleteForEveryone(mustUserID(t, SellerIDRaw)); err != nil {
		t.Fatalf("DeleteForEveryone: %v", err)
	}
	_ = msgs.Add(context.Background(), &msg)

	h := application.NewMarkConversationReadHandler(factory)
	_, err = h.Handle(context.Background(), application.MarkConversationReadCommand{
		ConversationID:    conv.ID.String(),
		UserID:            BuyerIDRaw,
		LastReadMessageID: msg.ID.String(),
	})
	var nf *domainerrors.NotFoundError
	if !errors.As(err, &nf) || nf.Field != "message_id" {
		t.Fatalf("err = %v, want NotFoundError message_id", err)
	}
}

func TestMarkConversationRead_InvalidIDs(t *testing.T) {
	t.Parallel()

	_, _, _, _, _, factory := NewFakeUowBundle()
	h := application.NewMarkConversationReadHandler(factory)

	_, err := h.Handle(context.Background(), application.MarkConversationReadCommand{
		ConversationID:    "bad",
		UserID:            BuyerIDRaw,
		LastReadMessageID: ClientMsg1,
	})
	if !errors.Is(err, domainerrors.ErrInvalidArgument) {
		t.Fatalf("err = %v, want ErrInvalidArgument", err)
	}
}

func TestMarkConversationRead_CommitError(t *testing.T) {
	t.Parallel()

	convs, states, msgs, _, uow, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)
	content, _ := valueobjects.NewMessageContent("hello")
	msg, _ := entities.NewMessage(conv.ID, mustUserID(t, SellerIDRaw), ClientMsg1, content)
	_ = msgs.Add(context.Background(), &msg)
	uow.CommitErr = errors.New("commit failed")

	h := application.NewMarkConversationReadHandler(factory)
	_, err := h.Handle(context.Background(), application.MarkConversationReadCommand{
		ConversationID:    conv.ID.String(),
		UserID:            BuyerIDRaw,
		LastReadMessageID: msg.ID.String(),
	})
	if err == nil || err.Error() != "commit failed" {
		t.Fatalf("err = %v, want commit failed", err)
	}
}

// ensure time import used if needed
var _ = time.Time{}
