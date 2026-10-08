package application_test

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/application"
	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
)

// ---------------------------------------------------------------------------
// Archive
// ---------------------------------------------------------------------------

func TestArchiveConversation_ArchiveAndUnarchive(t *testing.T) {
	t.Parallel()

	convs, states, _, _, uow, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)
	h := application.NewArchiveConversationHandler(factory)

	res, err := h.Handle(context.Background(), application.ArchiveConversationCommand{
		ConversationID: conv.ID.String(),
		UserID:         BuyerIDRaw,
		Archive:        true,
	})
	if err != nil {
		t.Fatalf("archive: %v", err)
	}
	if !res.IsArchived {
		t.Fatalf("IsArchived = false after archive")
	}
	if !uow.Committed {
		t.Fatalf("expected commit")
	}

	uow.Committed = false
	res, err = h.Handle(context.Background(), application.ArchiveConversationCommand{
		ConversationID: conv.ID.String(),
		UserID:         BuyerIDRaw,
		Archive:        false,
	})
	if err != nil {
		t.Fatalf("unarchive: %v", err)
	}
	if res.IsArchived {
		t.Fatalf("IsArchived = true after unarchive")
	}
}

func TestArchiveConversation_RejectsNonParticipant(t *testing.T) {
	t.Parallel()

	convs, states, _, _, _, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)
	h := application.NewArchiveConversationHandler(factory)

	_, err := h.Handle(context.Background(), application.ArchiveConversationCommand{
		ConversationID: conv.ID.String(),
		UserID:         ThirdIDRaw,
		Archive:        true,
	})
	if !errors.Is(err, domainerrors.ErrNotParticipant) {
		t.Fatalf("err = %v, want ErrNotParticipant", err)
	}
}

func TestArchiveConversation_NotFound(t *testing.T) {
	t.Parallel()

	_, _, _, _, _, factory := NewFakeUowBundle()
	h := application.NewArchiveConversationHandler(factory)
	_, err := h.Handle(context.Background(), application.ArchiveConversationCommand{
		ConversationID: "0d47ddfe-a4ca-446a-839e-d3bbcba824c6",
		UserID:         BuyerIDRaw,
		Archive:        true,
	})
	var nf *domainerrors.NotFoundError
	if !errors.As(err, &nf) {
		t.Fatalf("err = %v, want NotFoundError", err)
	}
}

// ---------------------------------------------------------------------------
// Hide
// ---------------------------------------------------------------------------

func TestHideConversation_HideAndUnhide(t *testing.T) {
	t.Parallel()

	convs, states, _, _, _, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)
	h := application.NewHideConversationHandler(factory)

	res, err := h.Handle(context.Background(), application.HideConversationCommand{
		ConversationID: conv.ID.String(),
		UserID:         BuyerIDRaw,
		Hide:           true,
	})
	if err != nil {
		t.Fatalf("hide: %v", err)
	}
	if !res.IsHidden {
		t.Fatalf("IsHidden = false after hide")
	}

	res, err = h.Handle(context.Background(), application.HideConversationCommand{
		ConversationID: conv.ID.String(),
		UserID:         BuyerIDRaw,
		Hide:           false,
	})
	if err != nil {
		t.Fatalf("unhide: %v", err)
	}
	if res.IsHidden {
		t.Fatalf("IsHidden = true after unhide")
	}
}

func TestHideConversation_RejectsNonParticipant(t *testing.T) {
	t.Parallel()

	convs, states, _, _, _, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)
	h := application.NewHideConversationHandler(factory)

	_, err := h.Handle(context.Background(), application.HideConversationCommand{
		ConversationID: conv.ID.String(),
		UserID:         ThirdIDRaw,
		Hide:           true,
	})
	if !errors.Is(err, domainerrors.ErrNotParticipant) {
		t.Fatalf("err = %v, want ErrNotParticipant", err)
	}
}

// ---------------------------------------------------------------------------
// Pin
// ---------------------------------------------------------------------------

func TestPinConversation_PinAndUnpin(t *testing.T) {
	t.Parallel()

	convs, states, _, _, _, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)
	h := application.NewPinConversationHandler(factory)

	res, err := h.Handle(context.Background(), application.PinConversationCommand{
		ConversationID: conv.ID.String(),
		UserID:         BuyerIDRaw,
		Pin:            true,
	})
	if err != nil {
		t.Fatalf("pin: %v", err)
	}
	if !res.IsPinned {
		t.Fatalf("IsPinned = false after pin")
	}

	res, err = h.Handle(context.Background(), application.PinConversationCommand{
		ConversationID: conv.ID.String(),
		UserID:         BuyerIDRaw,
		Pin:            false,
	})
	if err != nil {
		t.Fatalf("unpin: %v", err)
	}
	if res.IsPinned {
		t.Fatalf("IsPinned = true after unpin")
	}
}

func TestPinConversation_RejectsNonParticipant(t *testing.T) {
	t.Parallel()

	convs, states, _, _, _, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)
	h := application.NewPinConversationHandler(factory)

	_, err := h.Handle(context.Background(), application.PinConversationCommand{
		ConversationID: conv.ID.String(),
		UserID:         ThirdIDRaw,
		Pin:            true,
	})
	if !errors.Is(err, domainerrors.ErrNotParticipant) {
		t.Fatalf("err = %v, want ErrNotParticipant", err)
	}
}

func TestPinConversation_InvalidIDs(t *testing.T) {
	t.Parallel()

	_, _, _, _, _, factory := NewFakeUowBundle()
	h := application.NewPinConversationHandler(factory)

	_, err := h.Handle(context.Background(), application.PinConversationCommand{
		ConversationID: "bad",
		UserID:         BuyerIDRaw,
		Pin:            true,
	})
	if !errors.Is(err, domainerrors.ErrInvalidArgument) {
		t.Fatalf("err = %v, want ErrInvalidArgument", err)
	}
}

// ---------------------------------------------------------------------------
// Mute
// ---------------------------------------------------------------------------

func TestMuteConversation_MuteAndUnmute(t *testing.T) {
	t.Parallel()

	convs, states, _, _, uow, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)
	h := application.NewMuteConversationHandler(factory)

	until := time.Now().UTC().Add(2 * time.Hour)
	res, err := h.Handle(context.Background(), application.MuteConversationCommand{
		ConversationID: conv.ID.String(),
		UserID:         BuyerIDRaw,
		Mute:           true,
		Until:          &until,
	})
	if err != nil {
		t.Fatalf("mute: %v", err)
	}
	if !res.IsMuted {
		t.Fatalf("IsMuted = false after mute")
	}
	if res.MutedUntil == nil {
		t.Fatalf("MutedUntil is nil")
	}
	if !uow.Committed {
		t.Fatalf("expected commit")
	}

	uow.Committed = false
	res, err = h.Handle(context.Background(), application.MuteConversationCommand{
		ConversationID: conv.ID.String(),
		UserID:         BuyerIDRaw,
		Mute:           false,
	})
	if err != nil {
		t.Fatalf("unmute: %v", err)
	}
	if res.IsMuted {
		t.Fatalf("IsMuted = true after unmute")
	}
}

func TestMuteConversation_RejectsPastUntil(t *testing.T) {
	t.Parallel()

	convs, states, _, _, _, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)
	h := application.NewMuteConversationHandler(factory)

	past := time.Now().UTC().Add(-time.Minute)
	_, err := h.Handle(context.Background(), application.MuteConversationCommand{
		ConversationID: conv.ID.String(),
		UserID:         BuyerIDRaw,
		Mute:           true,
		Until:          &past,
	})
	var ve *domainerrors.ValidationError
	if !errors.As(err, &ve) || ve.Field != "muted_until" {
		t.Fatalf("err = %v, want ValidationError muted_until", err)
	}
}

func TestMuteConversation_RejectsNilUntil(t *testing.T) {
	t.Parallel()

	convs, states, _, _, _, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)
	h := application.NewMuteConversationHandler(factory)

	_, err := h.Handle(context.Background(), application.MuteConversationCommand{
		ConversationID: conv.ID.String(),
		UserID:         BuyerIDRaw,
		Mute:           true,
		Until:          nil,
	})
	var ve *domainerrors.ValidationError
	if !errors.As(err, &ve) || ve.Field != "muted_until" {
		t.Fatalf("err = %v, want ValidationError muted_until", err)
	}
}

func TestMuteConversation_RejectsNonParticipant(t *testing.T) {
	t.Parallel()

	convs, states, _, _, _, factory := NewFakeUowBundle()
	conv := seedOpenConversation(t, convs, states)
	h := application.NewMuteConversationHandler(factory)

	until := time.Now().UTC().Add(time.Hour)
	_, err := h.Handle(context.Background(), application.MuteConversationCommand{
		ConversationID: conv.ID.String(),
		UserID:         ThirdIDRaw,
		Mute:           true,
		Until:          &until,
	})
	if !errors.Is(err, domainerrors.ErrNotParticipant) {
		t.Fatalf("err = %v, want ErrNotParticipant", err)
	}
}

func TestMuteConversation_StateMissing(t *testing.T) {
	t.Parallel()

	convs, states, _, _, _, factory := NewFakeUowBundle()
	conv := existingConversation(t)
	_ = convs.Add(context.Background(), conv)
	// no state rows

	h := application.NewMuteConversationHandler(factory)
	until := time.Now().UTC().Add(time.Hour)
	_, err := h.Handle(context.Background(), application.MuteConversationCommand{
		ConversationID: conv.ID.String(),
		UserID:         BuyerIDRaw,
		Mute:           true,
		Until:          &until,
	})
	var nf *domainerrors.NotFoundError
	if !errors.As(err, &nf) || nf.Field != "conversation_user_state" {
		t.Fatalf("err = %v, want NotFoundError conversation_user_state", err)
	}
	_ = states
}
