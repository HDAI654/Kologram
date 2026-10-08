package entities

import (
	"time"

	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

// Conversation is the shared shell between two participants about a single
// listing. Per-user state (read cursor, unread, archive, hide, mute, pin)
// lives on ConversationUserState — nothing user-specific belongs here.
type Conversation struct {
	ID        valueobjects.ConversationID
	BuyerID   valueobjects.UserID
	SellerID  valueobjects.UserID
	ListingID valueobjects.ListingID

	// True when the market service reports the listing deleted.
	// New messages are rejected; history is preserved.
	IsReadOnly bool

	// Cached so the conversation list never joins the messages table.
	LastMessageID      valueobjects.MessageID
	LastMessagePreview string
	LastMessageAt      time.Time

	CreatedAt time.Time
	UpdatedAt time.Time
}

func StartConversation(
	buyerID valueobjects.UserID,
	sellerID valueobjects.UserID,
	listingID valueobjects.ListingID,
) (*Conversation, error) {
	if buyerID.Equals(sellerID) {
		return nil, domainerrors.ErrBuyerSellerSame
	}
	now := time.Now().UTC()
	return &Conversation{
		ID:        valueobjects.GenerateConversationID(),
		BuyerID:   buyerID,
		SellerID:  sellerID,
		ListingID: listingID,
		// Set at creation so the conversation sorts correctly in the
		// user's list before the first message arrives.
		LastMessageAt: now,
		CreatedAt:     now,
		UpdatedAt:     now,
	}, nil
}

func (c *Conversation) IsParticipant(userID valueobjects.UserID) bool {
	return c.BuyerID.Equals(userID) || c.SellerID.Equals(userID)
}

func (c *Conversation) ParticipantIDs() [2]valueobjects.UserID {
	return [2]valueobjects.UserID{c.BuyerID, c.SellerID}
}

// CounterpartID returns the other participant.
// The bool is false when the caller is not a participant.
func (c *Conversation) CounterpartID(userID valueobjects.UserID) (valueobjects.UserID, bool) {
	if userID.Equals(c.BuyerID) {
		return c.SellerID, true
	}
	if userID.Equals(c.SellerID) {
		return c.BuyerID, true
	}
	return valueobjects.UserID{}, false
}

// AddMessage validates sender and conversation state, then produces a Message.
// The caller persists it and updates both participants' ConversationUserState.
func (c *Conversation) AddMessage(
	senderID valueobjects.UserID,
	clientMessageID string,
	content valueobjects.MessageContent,
) (Message, error) {
	if !c.IsParticipant(senderID) {
		return Message{}, domainerrors.ErrNotParticipant
	}
	if c.IsReadOnly {
		return Message{}, domainerrors.ErrConversationNotOpen
	}
	return NewMessage(c.ID, senderID, clientMessageID, content)
}

func (c *Conversation) RecordLastMessage(msg Message) {
	c.LastMessageID = msg.ID
	c.LastMessagePreview = msg.Content.String()
	c.LastMessageAt = msg.SentAt
	c.UpdatedAt = msg.SentAt
}

// ClearLastMessagePreview clears cached preview after the last visible message
// is soft-deleted. LastMessageAt is left unchanged so list sort stays stable.
func (c *Conversation) ClearLastMessagePreview(now time.Time) {
	c.LastMessageID = valueobjects.MessageID{}
	c.LastMessagePreview = ""
	c.UpdatedAt = now
}

// MarkListingUnavailable freezes the conversation after the listing is deleted.
// Idempotent.
func (c *Conversation) MarkListingUnavailable(now time.Time) {
	if c.IsReadOnly {
		return
	}
	c.IsReadOnly = true
	c.UpdatedAt = now
}
