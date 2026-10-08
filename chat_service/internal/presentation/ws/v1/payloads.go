package v1

// Request payloads (JSON). Actor identity is never taken from these fields;
// the connection's X-User-Id is used for user/sender/actor/blocker.

type StartConversationPayload struct {
	ListingID string `json:"listing_id"`
}

type SendMessagePayload struct {
	ConversationID  string `json:"conversation_id"`
	ClientMessageID string `json:"client_message_id"`
	Content         string `json:"content"`
}

type ListMessagesPayload struct {
	ConversationID  string `json:"conversation_id"`
	CursorMessageID string `json:"cursor_message_id,omitempty"`
	CursorSentAt    string `json:"cursor_sent_at,omitempty"`
	Direction       string `json:"direction,omitempty"`
	Limit           int    `json:"limit,omitempty"`
}

type ListConversationsPayload struct {
	Filter              string `json:"filter,omitempty"`
	CursorID            string `json:"cursor_id,omitempty"`
	CursorLastMessageAt string `json:"cursor_last_message_at,omitempty"`
	CursorIsPinned      *bool  `json:"cursor_is_pinned,omitempty"`
	Limit               int    `json:"limit,omitempty"`
}

type GetConversationPayload struct {
	ConversationID string `json:"conversation_id"`
}

type MarkConversationReadPayload struct {
	ConversationID    string `json:"conversation_id"`
	LastReadMessageID string `json:"last_read_message_id"`
}

type DeleteMessageForEveryonePayload struct {
	MessageID string `json:"message_id"`
}

type ArchiveConversationPayload struct {
	ConversationID string `json:"conversation_id"`
	Archive        bool   `json:"archive"`
}

type HideConversationPayload struct {
	ConversationID string `json:"conversation_id"`
	Hide           bool   `json:"hide"`
}

type PinConversationPayload struct {
	ConversationID string `json:"conversation_id"`
	Pin            bool   `json:"pin"`
}

type MuteConversationPayload struct {
	ConversationID string  `json:"conversation_id"`
	Mute           bool    `json:"mute"`
	Until          *string `json:"until,omitempty"` // RFC3339 when mute=true
}

type BlockUserPayload struct {
	BlockedID string `json:"blocked_id"`
}

type UnblockUserPayload struct {
	BlockedID string `json:"blocked_id"`
}

type MarkListingUnavailablePayload struct {
	ListingID string `json:"listing_id"`
}
