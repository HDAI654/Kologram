package v1

import "encoding/json"

// Client → server request envelope.
type Request struct {
	ID      string          `json:"id"`
	Type    string          `json:"type"`
	Payload json.RawMessage `json:"payload"`
}

// Server → client reply for a request (id echoes request id).
type Response struct {
	ID      string    `json:"id"`
	Type    string    `json:"type"`
	OK      bool      `json:"ok"`
	Payload any       `json:"payload,omitempty"`
	Error   *ErrorBody `json:"error,omitempty"`
}

// Server → client push (no request id).
type Event struct {
	Type    string `json:"type"`
	Payload any    `json:"payload"`
}

type ErrorBody struct {
	Code    string `json:"code"`
	Message string `json:"message"`
	Field   string `json:"field,omitempty"`
}

// Action type names (client request "type").
const (
	TypeStartConversation       = "start_conversation"
	TypeSendMessage             = "send_message"
	TypeListMessages            = "list_messages"
	TypeListConversations       = "list_conversations"
	TypeGetConversation         = "get_conversation"
	TypeMarkConversationRead    = "mark_conversation_read"
	TypeDeleteMessageForEveryone = "delete_message_for_everyone"
	TypeArchiveConversation     = "archive_conversation"
	TypeHideConversation        = "hide_conversation"
	TypePinConversation         = "pin_conversation"
	TypeMuteConversation        = "mute_conversation"
	TypeBlockUser               = "block_user"
	TypeUnblockUser             = "unblock_user"
	TypeMarkListingUnavailable  = "mark_listing_unavailable"
)

// Result type names (server reply "type") — request type + "_result".
const (
	TypeStartConversationResult       = "start_conversation_result"
	TypeSendMessageResult             = "send_message_result"
	TypeListMessagesResult            = "list_messages_result"
	TypeListConversationsResult       = "list_conversations_result"
	TypeGetConversationResult         = "get_conversation_result"
	TypeMarkConversationReadResult    = "mark_conversation_read_result"
	TypeDeleteMessageForEveryoneResult = "delete_message_for_everyone_result"
	TypeArchiveConversationResult     = "archive_conversation_result"
	TypeHideConversationResult        = "hide_conversation_result"
	TypePinConversationResult         = "pin_conversation_result"
	TypeMuteConversationResult        = "mute_conversation_result"
	TypeBlockUserResult               = "block_user_result"
	TypeUnblockUserResult             = "unblock_user_result"
	TypeMarkListingUnavailableResult  = "mark_listing_unavailable_result"
)

// Push event types (server → client, no request id).
const (
	EventMessageSent            = "message_sent"
	EventMessageDeletedForEveryone = "message_deleted_for_everyone"
)

// Stable error codes for clients.
const (
	CodeInvalidRequest   = "INVALID_REQUEST"
	CodeValidation       = "VALIDATION_ERROR"
	CodeNotFound         = "NOT_FOUND"
	CodeForbidden        = "FORBIDDEN"
	CodeConflict         = "CONFLICT"
	CodeInternal         = "INTERNAL_ERROR"
)
