package ports

import (
	"context"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

// ConversationListFilter selects which rows ListForUser returns.
// Hidden conversations are always excluded; they reappear when the user
// unhides or when SendMessage unhides the receiver on a new message.
type ConversationListFilter int

const (
	// Active inbox: not archived, not hidden.
	ListFilterActive ConversationListFilter = iota
	// Archived tab: archived, not hidden.
	ListFilterArchived
)

type ConversationRepository interface {
	Add(ctx context.Context, conversation *entities.Conversation) error
	Update(ctx context.Context, conversation *entities.Conversation) error

	// Must return NotFoundError when no row exists.
	GetByID(ctx context.Context, id valueobjects.ConversationID) (*entities.Conversation, error)

	// Idempotency key for StartConversation: one thread per (buyer, listing).
	// Seller is implied by the listing. Returns (nil, nil) when none exists.
	FindByBuyerAndListing(
		ctx context.Context,
		buyerID valueobjects.UserID,
		listingID valueobjects.ListingID,
	) (*entities.Conversation, error)

	// Single read-model page: shared conversation fields + the caller's
	// ConversationUserState. Sort: (IsPinned DESC, LastMessageAt DESC, ID DESC).
	// No total count — callers use len(items) == limit as has-more.
	ListForUser(
		ctx context.Context,
		userID valueobjects.UserID,
		filter ConversationListFilter,
		cursor *ConversationListCursor,
		limit int,
	) ([]ConversationListItem, error)

	// Used by MarkListingUnavailable to freeze every thread on a listing.
	ListByListingID(
		ctx context.Context,
		listingID valueobjects.ListingID,
	) ([]*entities.Conversation, error)
}

// Sort key: (IsPinned DESC, LastMessageAt DESC, ID DESC).
type ConversationListCursor struct {
	IsPinned      bool
	LastMessageAt time.Time
	ID            valueobjects.ConversationID
}

// ConversationListItem is a read projection only — never pass to a write path.
type ConversationListItem struct {
	ConversationID     valueobjects.ConversationID
	BuyerID            valueobjects.UserID
	SellerID           valueobjects.UserID
	ListingID          valueobjects.ListingID
	IsReadOnly         bool
	LastMessagePreview string
	LastMessageAt      time.Time
	CreatedAt          time.Time
	UpdatedAt          time.Time

	UnreadCount int
	IsArchived  bool
	IsPinned    bool
	IsMuted     bool
}
