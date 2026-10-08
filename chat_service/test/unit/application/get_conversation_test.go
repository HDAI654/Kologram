package application_test

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/application"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
)

func TestGetConversation_Success(t *testing.T) {
	t.Parallel()

	convs := NewFakeConversationRepository()
	states := NewFakeConversationUserStateRepository()
	conv := existingConversation(t)
	_ = convs.Add(context.Background(), conv)

	now := time.Now().UTC()
	buyerState := entities.NewConversationUserState(conv.ID, mustUserID(t, BuyerIDRaw), now)
	buyerState.UnreadCount = 3
	buyerState.IsPinned = true
	_ = states.Add(context.Background(), buyerState)

	h := application.NewGetConversationHandler(convs, states)
	result, err := h.Handle(context.Background(), application.GetConversationQuery{
		ConversationID: conv.ID.String(),
		RequesterID:    BuyerIDRaw,
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result.ConversationID != conv.ID.String() {
		t.Fatalf("ConversationID mismatch")
	}
	if result.UnreadCount != 3 {
		t.Fatalf("UnreadCount = %d, want 3", result.UnreadCount)
	}
	if !result.IsPinned {
		t.Fatalf("IsPinned = false, want true")
	}
	if result.BuyerID != BuyerIDRaw || result.SellerID != SellerIDRaw {
		t.Fatalf("participants mismatch")
	}
}

func TestGetConversation_RejectsNonParticipant(t *testing.T) {
	t.Parallel()

	convs := NewFakeConversationRepository()
	states := NewFakeConversationUserStateRepository()
	conv := existingConversation(t)
	_ = convs.Add(context.Background(), conv)

	h := application.NewGetConversationHandler(convs, states)
	_, err := h.Handle(context.Background(), application.GetConversationQuery{
		ConversationID: conv.ID.String(),
		RequesterID:    ThirdIDRaw,
	})
	if !errors.Is(err, domainerrors.ErrNotParticipant) {
		t.Fatalf("err = %v, want ErrNotParticipant", err)
	}
}

func TestGetConversation_NotFound(t *testing.T) {
	t.Parallel()

	h := application.NewGetConversationHandler(NewFakeConversationRepository(), NewFakeConversationUserStateRepository())
	_, err := h.Handle(context.Background(), application.GetConversationQuery{
		ConversationID: "0d47ddfe-a4ca-446a-839e-d3bbcba824c6",
		RequesterID:    BuyerIDRaw,
	})
	var nf *domainerrors.NotFoundError
	if !errors.As(err, &nf) {
		t.Fatalf("err = %v, want NotFoundError", err)
	}
}

func TestGetConversation_StateMissing(t *testing.T) {
	t.Parallel()

	convs := NewFakeConversationRepository()
	states := NewFakeConversationUserStateRepository()
	conv := existingConversation(t)
	_ = convs.Add(context.Background(), conv)
	// no state row

	h := application.NewGetConversationHandler(convs, states)
	_, err := h.Handle(context.Background(), application.GetConversationQuery{
		ConversationID: conv.ID.String(),
		RequesterID:    BuyerIDRaw,
	})
	var nf *domainerrors.NotFoundError
	if !errors.As(err, &nf) || nf.Field != "conversation_user_state" {
		t.Fatalf("err = %v, want NotFoundError conversation_user_state", err)
	}
}

func TestGetConversation_InvalidIDs(t *testing.T) {
	t.Parallel()

	h := application.NewGetConversationHandler(NewFakeConversationRepository(), NewFakeConversationUserStateRepository())

	_, err := h.Handle(context.Background(), application.GetConversationQuery{
		ConversationID: "bad",
		RequesterID:    BuyerIDRaw,
	})
	if !errors.Is(err, domainerrors.ErrInvalidArgument) {
		t.Fatalf("err = %v, want ErrInvalidArgument", err)
	}

	_, err = h.Handle(context.Background(), application.GetConversationQuery{
		ConversationID: "0d47ddfe-a4ca-446a-839e-d3bbcba824c6",
		RequesterID:    "bad",
	})
	if !errors.Is(err, domainerrors.ErrInvalidArgument) {
		t.Fatalf("err = %v, want ErrInvalidArgument", err)
	}
}
