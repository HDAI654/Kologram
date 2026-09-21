package domain

import (
	"time"

	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

// Conversation is the aggregate root for buyer–seller messaging about a listing.
type Conversation struct {
	ID        valueobject.ConversationID
	BuyerID   valueobject.UserID
	SellerID  valueobject.UserID
	ListingID valueobject.ListingID
	Status    valueobject.ConversationStatus
	Messages  []Message
	CreatedAt time.Time
	UpdatedAt time.Time
}

// StartConversation creates a new OPEN conversation between buyer and seller.
func StartConversation(
	buyerID valueobject.UserID,
	sellerID valueobject.UserID,
	listingID valueobject.ListingID,
) (*Conversation, error) {
	if buyerID.Equals(sellerID) {
		return nil, domainerrors.ErrBuyerSellerSame
	}
	now := time.Now().UTC()
	return &Conversation{
		ID:        valueobject.GenerateConversationID(),
		BuyerID:   buyerID,
		SellerID:  sellerID,
		ListingID: listingID,
		Status:    valueobject.StatusOpen,
		Messages:  nil,
		CreatedAt: now,
		UpdatedAt: now,
	}, nil
}

func (c *Conversation) IsParticipant(userID valueobject.UserID) bool {
	return c.BuyerID.Equals(userID) || c.SellerID.Equals(userID)
}

// AddMessage appends a message if the sender is a participant and conversation is open.
func (c *Conversation) AddMessage(senderID valueobject.UserID, content valueobject.MessageContent) (Message, error) {
	if !c.IsParticipant(senderID) {
		return Message{}, domainerrors.ErrNotParticipant
	}
	if !c.Status.AllowsMessages() {
		return Message{}, domainerrors.ErrConversationNotOpen
	}
	msg := NewMessage(c.ID, senderID, content)
	c.Messages = append(c.Messages, msg)
	c.UpdatedAt = time.Now().UTC()
	return msg, nil
}

// TransitionStatus applies an allowed lifecycle transition.
func (c *Conversation) TransitionStatus(target valueobject.ConversationStatus, actorID valueobject.UserID) error {
	if !c.IsParticipant(actorID) {
		return domainerrors.ErrNotParticipant
	}
	if !c.Status.CanTransitionTo(target) {
		return domainerrors.ErrInvalidStatusTransition
	}
	c.Status = target
	c.UpdatedAt = time.Now().UTC()
	return nil
}
