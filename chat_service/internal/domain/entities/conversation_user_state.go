package entities

import (
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

// ConversationUserState holds everything a single user sees about a single
// conversation. One row per (conversation, user). Actions that affect only
// one participant — archive, hide, mute, pin, read tracking — live here,
// never on the shared Conversation.
type ConversationUserState struct {
	ConversationID valueobjects.ConversationID
	UserID         valueobjects.UserID

	// Most recent message this user has seen. Zero value means nothing read yet.
	// Implementations must not regress this cursor.
	LastReadMessageID valueobjects.MessageID

	// Denormalized so the conversation list never issues per-conversation COUNT queries.
	UnreadCount int

	IsArchived bool
	IsHidden   bool
	IsPinned   bool

	// nil = not muted. A timestamp in the past means the mute has lapsed;
	// callers treat it as unmuted without requiring a write.
	MutedUntil *time.Time

	CreatedAt time.Time
	UpdatedAt time.Time
}

func NewConversationUserState(
	conversationID valueobjects.ConversationID,
	userID valueobjects.UserID,
	now time.Time,
) *ConversationUserState {
	return &ConversationUserState{
		ConversationID: conversationID,
		UserID:         userID,
		CreatedAt:      now,
		UpdatedAt:      now,
	}
}

// MarkRead advances the read cursor and resets the unread counter.
// The caller must confirm lastRead is not older than the current cursor.
func (s *ConversationUserState) MarkRead(lastRead valueobjects.MessageID, now time.Time) {
	s.LastReadMessageID = lastRead
	s.UnreadCount = 0
	s.UpdatedAt = now
}

// RecordIncomingMessage bumps the unread counter.
// The caller skips this for the sender's own state.
func (s *ConversationUserState) RecordIncomingMessage(now time.Time) {
	s.UnreadCount++
	s.UpdatedAt = now
}

func (s *ConversationUserState) Archive(now time.Time) {
	if s.IsArchived {
		return
	}
	s.IsArchived = true
	s.UpdatedAt = now
}

func (s *ConversationUserState) Unarchive(now time.Time) {
	if !s.IsArchived {
		return
	}
	s.IsArchived = false
	s.UpdatedAt = now
}

// Hide removes the conversation from this user's list only.
func (s *ConversationUserState) Hide(now time.Time) {
	if s.IsHidden {
		return
	}
	s.IsHidden = true
	s.UpdatedAt = now
}

func (s *ConversationUserState) Unhide(now time.Time) {
	if !s.IsHidden {
		return
	}
	s.IsHidden = false
	s.UpdatedAt = now
}

func (s *ConversationUserState) Pin(now time.Time) {
	if s.IsPinned {
		return
	}
	s.IsPinned = true
	s.UpdatedAt = now
}

func (s *ConversationUserState) Unpin(now time.Time) {
	if !s.IsPinned {
		return
	}
	s.IsPinned = false
	s.UpdatedAt = now
}

func (s *ConversationUserState) Mute(until time.Time, now time.Time) {
	s.MutedUntil = &until
	s.UpdatedAt = now
}

func (s *ConversationUserState) Unmute(now time.Time) {
	if s.MutedUntil == nil {
		return
	}
	s.MutedUntil = nil
	s.UpdatedAt = now
}

// IsMuted reports whether the conversation is muted at now.
// A lapsed mute is treated as unmuted without a write.
func (s *ConversationUserState) IsMuted(now time.Time) bool {
	if s.MutedUntil == nil {
		return false
	}
	return now.Before(*s.MutedUntil)
}
