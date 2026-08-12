package domain

import (
	"time"

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
		return nil, ErrBuyerSellerSame
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

// Rehydrate rebuilds a conversation from persistence without domain validation of history.
func RehydrateConversation(
	id valueobject.ConversationID,
	buyerID valueobject.UserID,
	sellerID valueobject.UserID,
	listingID valueobject.ListingID,
	status valueobject.ConversationStatus,
	messages []Message,
	createdAt, updatedAt time.Time,
) *Conversation {
	return &Conversation{
		ID:        id,
		BuyerID:   buyerID,
		SellerID:  sellerID,
		ListingID: listingID,
		Status:    status,
		Messages:  messages,
		CreatedAt: createdAt,
		UpdatedAt: updatedAt,
	}
}

func (c *Conversation) IsParticipant(userID valueobject.UserID) bool {
	return c.BuyerID.Equals(userID) || c.SellerID.Equals(userID)
}

// AddMessage appends a message if the sender is a participant and conversation is open.
func (c *Conversation) AddMessage(senderID valueobject.UserID, content valueobject.MessageContent) (Message, error) {
	if !c.IsParticipant(senderID) {
		return Message{}, ErrNotParticipant
	}
	if !c.Status.AllowsMessages() {
		return Message{}, ErrConversationNotOpen
	}
	msg := NewMessage(c.ID, senderID, content)
	c.Messages = append(c.Messages, msg)
	c.UpdatedAt = time.Now().UTC()
	return msg, nil
}

// MarkMessagesRead marks unread messages from the other party as read for the given reader.
func (c *Conversation) MarkMessagesRead(readerID valueobject.UserID) error {
	if !c.IsParticipant(readerID) {
		return ErrNotParticipant
	}
	changed := false
	for i := range c.Messages {
		if !c.Messages[i].SenderID.Equals(readerID) && !c.Messages[i].IsRead {
			c.Messages[i].MarkRead()
			changed = true
		}
	}
	if changed {
		c.UpdatedAt = time.Now().UTC()
	}
	return nil
}

// TransitionStatus applies an allowed lifecycle transition.
func (c *Conversation) TransitionStatus(target valueobject.ConversationStatus, actorID valueobject.UserID) error {
	if !c.IsParticipant(actorID) {
		return ErrNotParticipant
	}
	if !c.Status.CanTransitionTo(target) {
		return ErrInvalidStatusTransition
	}
	c.Status = target
	c.UpdatedAt = time.Now().UTC()
	return nil
}
