package domain

import "errors"

var (
	ErrConversationNotFound      = errors.New("conversation not found")
	ErrMessageNotFound           = errors.New("message not found")
	ErrNotParticipant            = errors.New("user is not a participant of this conversation")
	ErrConversationNotOpen       = errors.New("conversation is not open for messages")
	ErrInvalidStatusTransition   = errors.New("invalid conversation status transition")
	ErrBuyerSellerSame           = errors.New("buyer and seller must be different users")
	ErrConversationAlreadyExists = errors.New("conversation already exists for buyer and listing")
)
