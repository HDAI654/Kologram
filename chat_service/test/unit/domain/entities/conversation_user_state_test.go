package entities_test

import (
	"testing"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
)

func TestNewConversationUserState_InitialValues(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	now := time.Now().UTC()

	state := entities.NewConversationUserState(conv.ID, conv.BuyerID, now)

	if state.ConversationID.String() != conv.ID.String() {
		t.Fatalf("ConversationID mismatch")
	}
	if !state.UserID.Equals(conv.BuyerID) {
		t.Fatalf("UserID mismatch")
	}
	if state.LastReadMessageID.String() != "" {
		t.Fatalf("LastReadMessageID = %q, want empty", state.LastReadMessageID.String())
	}
	if state.UnreadCount != 0 {
		t.Fatalf("UnreadCount = %d, want 0", state.UnreadCount)
	}
	if state.IsArchived || state.IsHidden || state.IsPinned {
		t.Fatalf("flags should be false on new state")
	}
	if state.MutedUntil != nil {
		t.Fatalf("MutedUntil = %v, want nil", state.MutedUntil)
	}
	if !state.CreatedAt.Equal(now) || !state.UpdatedAt.Equal(now) {
		t.Fatalf("timestamps should equal now")
	}
}

func TestConversationUserState_MarkRead(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	state := newUserState(t, conv, conv.BuyerID)
	state.UnreadCount = 5

	msgID := mustMessageID(t, "3bb6a3ca-66dc-440e-8d11-d8cca7ad7792")
	now := time.Now().UTC().Add(time.Second)

	state.MarkRead(msgID, now)

	if state.LastReadMessageID.String() != msgID.String() {
		t.Fatalf("LastReadMessageID = %q, want %q", state.LastReadMessageID.String(), msgID.String())
	}
	if state.UnreadCount != 0 {
		t.Fatalf("UnreadCount = %d, want 0", state.UnreadCount)
	}
	if !state.UpdatedAt.Equal(now) {
		t.Fatalf("UpdatedAt = %v, want %v", state.UpdatedAt, now)
	}
}

func TestConversationUserState_RecordIncomingMessage(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	state := newUserState(t, conv, conv.SellerID)
	now1 := time.Now().UTC().Add(time.Second)
	now2 := now1.Add(time.Second)

	state.RecordIncomingMessage(now1)
	if state.UnreadCount != 1 {
		t.Fatalf("UnreadCount = %d, want 1", state.UnreadCount)
	}
	if !state.UpdatedAt.Equal(now1) {
		t.Fatalf("UpdatedAt = %v, want %v", state.UpdatedAt, now1)
	}

	state.RecordIncomingMessage(now2)
	if state.UnreadCount != 2 {
		t.Fatalf("UnreadCount = %d, want 2", state.UnreadCount)
	}
	if !state.UpdatedAt.Equal(now2) {
		t.Fatalf("UpdatedAt = %v, want %v", state.UpdatedAt, now2)
	}
}

func TestConversationUserState_ArchiveUnarchive(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	state := newUserState(t, conv, conv.BuyerID)
	now := time.Now().UTC().Add(time.Second)

	state.Archive(now)
	if !state.IsArchived {
		t.Fatalf("IsArchived = false after Archive")
	}
	if !state.UpdatedAt.Equal(now) {
		t.Fatalf("UpdatedAt not set on Archive")
	}

	// idempotent
	later := now.Add(time.Hour)
	state.Archive(later)
	if !state.UpdatedAt.Equal(now) {
		t.Fatalf("UpdatedAt changed on redundant Archive")
	}

	unarchiveAt := later.Add(time.Minute)
	state.Unarchive(unarchiveAt)
	if state.IsArchived {
		t.Fatalf("IsArchived = true after Unarchive")
	}
	if !state.UpdatedAt.Equal(unarchiveAt) {
		t.Fatalf("UpdatedAt not set on Unarchive")
	}

	// idempotent unarchive
	state.Unarchive(unarchiveAt.Add(time.Hour))
	if !state.UpdatedAt.Equal(unarchiveAt) {
		t.Fatalf("UpdatedAt changed on redundant Unarchive")
	}
}

func TestConversationUserState_HideUnhide(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	state := newUserState(t, conv, conv.BuyerID)
	now := time.Now().UTC().Add(time.Second)

	state.Hide(now)
	if !state.IsHidden {
		t.Fatalf("IsHidden = false after Hide")
	}

	later := now.Add(time.Hour)
	state.Hide(later)
	if !state.UpdatedAt.Equal(now) {
		t.Fatalf("UpdatedAt changed on redundant Hide")
	}

	unhideAt := later.Add(time.Minute)
	state.Unhide(unhideAt)
	if state.IsHidden {
		t.Fatalf("IsHidden = true after Unhide")
	}

	state.Unhide(unhideAt.Add(time.Hour))
	if !state.UpdatedAt.Equal(unhideAt) {
		t.Fatalf("UpdatedAt changed on redundant Unhide")
	}
}

func TestConversationUserState_PinUnpin(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	state := newUserState(t, conv, conv.BuyerID)
	now := time.Now().UTC().Add(time.Second)

	state.Pin(now)
	if !state.IsPinned {
		t.Fatalf("IsPinned = false after Pin")
	}

	later := now.Add(time.Hour)
	state.Pin(later)
	if !state.UpdatedAt.Equal(now) {
		t.Fatalf("UpdatedAt changed on redundant Pin")
	}

	unpinAt := later.Add(time.Minute)
	state.Unpin(unpinAt)
	if state.IsPinned {
		t.Fatalf("IsPinned = true after Unpin")
	}

	state.Unpin(unpinAt.Add(time.Hour))
	if !state.UpdatedAt.Equal(unpinAt) {
		t.Fatalf("UpdatedAt changed on redundant Unpin")
	}
}

func TestConversationUserState_MuteUnmute(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	state := newUserState(t, conv, conv.BuyerID)
	now := time.Now().UTC()
	until := now.Add(2 * time.Hour)

	state.Mute(until, now)
	if state.MutedUntil == nil || !state.MutedUntil.Equal(until) {
		t.Fatalf("MutedUntil = %v, want %v", state.MutedUntil, until)
	}
	if !state.UpdatedAt.Equal(now) {
		t.Fatalf("UpdatedAt not set on Mute")
	}

	unmuteAt := now.Add(time.Minute)
	state.Unmute(unmuteAt)
	if state.MutedUntil != nil {
		t.Fatalf("MutedUntil = %v, want nil after Unmute", state.MutedUntil)
	}
	if !state.UpdatedAt.Equal(unmuteAt) {
		t.Fatalf("UpdatedAt not set on Unmute")
	}

	// idempotent unmute
	state.Unmute(unmuteAt.Add(time.Hour))
	if !state.UpdatedAt.Equal(unmuteAt) {
		t.Fatalf("UpdatedAt changed on redundant Unmute")
	}
}

func TestConversationUserState_IsMuted(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	state := newUserState(t, conv, conv.BuyerID)
	now := time.Now().UTC()

	if state.IsMuted(now) {
		t.Fatalf("IsMuted = true when MutedUntil is nil")
	}

	until := now.Add(time.Hour)
	state.Mute(until, now)

	if !state.IsMuted(now) {
		t.Fatalf("IsMuted = false while mute is active")
	}
	if !state.IsMuted(until.Add(-time.Second)) {
		t.Fatalf("IsMuted = false just before expiry")
	}
	if state.IsMuted(until) {
		t.Fatalf("IsMuted = true at exact expiry (Before is exclusive)")
	}
	if state.IsMuted(until.Add(time.Second)) {
		t.Fatalf("IsMuted = true after mute lapsed")
	}
}

func TestConversationUserState_MarkReadAfterIncoming(t *testing.T) {
	t.Parallel()

	conv := newConversation(t)
	state := newUserState(t, conv, conv.SellerID)
	now := time.Now().UTC()

	state.RecordIncomingMessage(now)
	state.RecordIncomingMessage(now.Add(time.Second))
	if state.UnreadCount != 2 {
		t.Fatalf("precondition: UnreadCount = %d, want 2", state.UnreadCount)
	}

	msgID := mustMessageID(t, "3bb6a3ca-66dc-440e-8d11-d8cca7ad7792")
	readAt := now.Add(2 * time.Second)
	state.MarkRead(msgID, readAt)

	if state.UnreadCount != 0 {
		t.Fatalf("UnreadCount = %d after MarkRead, want 0", state.UnreadCount)
	}
	if state.LastReadMessageID.String() != msgID.String() {
		t.Fatalf("LastReadMessageID not set")
	}
}
