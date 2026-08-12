package valueobject

import (
	"fmt"
	"strings"
)

// ConversationStatus is the lifecycle state of a conversation.
type ConversationStatus struct {
	value string
}

var (
	StatusOpen     = ConversationStatus{value: "OPEN"}
	StatusClosed   = ConversationStatus{value: "CLOSED"}
	StatusArchived = ConversationStatus{value: "ARCHIVED"}
)

var allowedStatuses = map[string]ConversationStatus{
	"OPEN":     StatusOpen,
	"CLOSED":   StatusClosed,
	"ARCHIVED": StatusArchived,
}

// adminTransitions: from → allowed targets
var statusTransitions = map[string]map[string]struct{}{
	"OPEN":     {"CLOSED": {}, "ARCHIVED": {}},
	"CLOSED":   {"ARCHIVED": {}, "OPEN": {}},
	"ARCHIVED": {},
}

func NewConversationStatus(raw string) (ConversationStatus, error) {
	normalized := strings.ToUpper(strings.TrimSpace(raw))
	status, ok := allowedStatuses[normalized]
	if !ok {
		return ConversationStatus{}, fmt.Errorf("invalid conversation status: %s", raw)
	}
	return status, nil
}

func (s ConversationStatus) String() string { return s.value }

func (s ConversationStatus) Equals(other ConversationStatus) bool {
	return s.value == other.value
}

func (s ConversationStatus) CanTransitionTo(target ConversationStatus) bool {
	allowed, ok := statusTransitions[s.value]
	if !ok {
		return false
	}
	_, ok = allowed[target.value]
	return ok
}

func (s ConversationStatus) AllowsMessages() bool {
	return s.value == "OPEN"
}
