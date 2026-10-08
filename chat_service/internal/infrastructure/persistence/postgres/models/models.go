package models

import "time"

// Row types mirror schema.sql. They must not leave the infrastructure layer.

type ConversationRow struct {
	ID                 string
	BuyerID            string
	SellerID           string
	ListingID          string
	IsReadOnly         bool
	LastMessageID      *string
	LastMessagePreview string
	LastMessageAt      time.Time
	CreatedAt          time.Time
	UpdatedAt          time.Time
}

type ConversationUserStateRow struct {
	ConversationID     string
	UserID             string
	LastReadMessageID  *string
	UnreadCount        int
	IsArchived         bool
	IsHidden           bool
	IsPinned           bool
	MutedUntil         *time.Time
	UpdatedAt          time.Time
}

type MessageRow struct {
	ID                 string
	ConversationID     string
	SenderID           string
	Content            string
	SentAt             time.Time
	ClientMessageID    string
	DeletedForEveryone bool
	DeletedAt          *time.Time
}

type UserBlockRow struct {
	BlockerID string
	BlockedID string
	CreatedAt time.Time
}

// ConversationListRow is the join projection for ListForUser (not an aggregate).
type ConversationListRow struct {
	ConversationID     string
	BuyerID            string
	SellerID           string
	ListingID          string
	IsReadOnly         bool
	LastMessagePreview string
	LastMessageAt      time.Time
	CreatedAt          time.Time
	UpdatedAt          time.Time
	UnreadCount        int
	IsArchived         bool
	IsPinned           bool
	MutedUntil         *time.Time
}
