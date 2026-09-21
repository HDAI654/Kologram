package domain

import (
	"time"

	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

// Conversation is the aggregate root for buyer–seller messaging about a listing.
type Conversation struct {
	ID        valueobjects.ConversationID
	BuyerID   valueobjects.UserID
	SellerID  valueobjects.UserID
	ListingID valueobjects.ListingID
	Status    valueobjects.ConversationStatus
	Messages  []Message
	CreatedAt time.Time
	UpdatedAt time.Time
}

// StartConversation creates a new OPEN conversation between buyer and seller.
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
		Status:    valueobjects.StatusOpen,
		Messages:  nil,
		CreatedAt: now,
		UpdatedAt: now,
	}, nil
}

func (c *Conversation) IsParticipant(userID valueobjects.UserID) bool {
	return c.BuyerID.Equals(userID) || c.SellerID.Equals(userID)
}

// AddMessage appends a message if the sender is a participant and conversation is open.
func (c *Conversation) AddMessage(senderID valueobjects.UserID, content valueobjects.MessageContent) (Message, error) {
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
func (c *Conversation) TransitionStatus(target valueobjects.ConversationStatus, actorID valueobjects.UserID) error {
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
