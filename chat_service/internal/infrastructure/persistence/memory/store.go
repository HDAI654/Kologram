package memory

import (
	"sync"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
)

// Store is a process-local, mutex-guarded dataset shared by in-memory repositories.
type Store struct {
	mu sync.RWMutex

	Conversations map[string]*entities.Conversation
	// buyerID|listingID -> conversation id
	ByBuyerListing map[string]string
	// listingID -> conversation ids
	ByListing map[string][]string

	States map[string]*entities.ConversationUserState // conversationID|userID

	Messages           map[string]*entities.Message
	MessagesByClient   map[string]string   // sender|conv|client -> message id
	MessagesByConversation map[string][]string // ordered append; queries sort by SentAt

	Blocks map[string]struct{} // blocker|blocked
}

func NewStore() *Store {
	return &Store{
		Conversations:          make(map[string]*entities.Conversation),
		ByBuyerListing:         make(map[string]string),
		ByListing:              make(map[string][]string),
		States:                 make(map[string]*entities.ConversationUserState),
		Messages:               make(map[string]*entities.Message),
		MessagesByClient:       make(map[string]string),
		MessagesByConversation: make(map[string][]string),
		Blocks:                 make(map[string]struct{}),
	}
}

func buyerListingKey(buyerID, listingID string) string { return buyerID + "|" + listingID }
func stateKey(conversationID, userID string) string    { return conversationID + "|" + userID }
func clientKey(senderID, conversationID, clientID string) string {
	return senderID + "|" + conversationID + "|" + clientID
}
func blockKey(a, b string) string { return a + "|" + b }

func cloneConversation(c *entities.Conversation) *entities.Conversation {
	if c == nil {
		return nil
	}
	cp := *c
	return &cp
}

func cloneState(s *entities.ConversationUserState) *entities.ConversationUserState {
	if s == nil {
		return nil
	}
	cp := *s
	if s.MutedUntil != nil {
		t := *s.MutedUntil
		cp.MutedUntil = &t
	}
	return &cp
}

func cloneMessage(m *entities.Message) *entities.Message {
	if m == nil {
		return nil
	}
	cp := *m
	if m.DeletedAt != nil {
		t := *m.DeletedAt
		cp.DeletedAt = &t
	}
	return &cp
}

func cloneBlock(b *entities.UserBlock) *entities.UserBlock {
	if b == nil {
		return nil
	}
	cp := *b
	return &cp
}
