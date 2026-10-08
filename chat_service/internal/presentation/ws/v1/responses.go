package v1

import "github.com/HDAI654/Kologram/chat_service/internal/application"

// toPayload maps application results to snake_case wire objects (Presentation boundary).
func toPayload(v any) any {
	switch r := v.(type) {
	case application.StartConversationResult:
		return map[string]any{
			"conversation_id": r.ConversationID,
			"created":         r.Created,
			"is_read_only":    r.IsReadOnly,
		}
	case application.SendMessageResult:
		return map[string]any{
			"message_id":      r.MessageID,
			"conversation_id": r.ConversationID,
			"sent_at":         r.SentAt,
			"idempotent_hit":  r.IdempotentHit,
		}
	case application.ListMessagesResult:
		items := make([]map[string]any, 0, len(r.Items))
		for _, it := range r.Items {
			items = append(items, map[string]any{
				"message_id":        it.MessageID,
				"sender_id":         it.SenderID,
				"content":           it.Content,
				"client_message_id": it.ClientMessageID,
				"sent_at":           it.SentAt,
			})
		}
		return map[string]any{"messages": items, "has_more": r.HasMore}
	case application.ListConversationsResult:
		items := make([]map[string]any, 0, len(r.Items))
		for _, it := range r.Items {
			items = append(items, map[string]any{
				"conversation_id":      it.ConversationID,
				"buyer_id":             it.BuyerID,
				"seller_id":            it.SellerID,
				"listing_id":           it.ListingID,
				"is_read_only":         it.IsReadOnly,
				"last_message_preview": it.LastMessagePreview,
				"last_message_at":      it.LastMessageAt,
				"unread_count":         it.UnreadCount,
				"is_archived":          it.IsArchived,
				"is_pinned":            it.IsPinned,
				"is_muted":             it.IsMuted,
			})
		}
		return map[string]any{"items": items, "has_more": r.HasMore}
	case application.GetConversationResult:
		return map[string]any{
			"conversation_id":      r.ConversationID,
			"buyer_id":             r.BuyerID,
			"seller_id":            r.SellerID,
			"listing_id":           r.ListingID,
			"is_read_only":         r.IsReadOnly,
			"last_message_preview": r.LastMessagePreview,
			"last_message_at":      r.LastMessageAt,
			"unread_count":         r.UnreadCount,
			"is_archived":          r.IsArchived,
			"is_hidden":            r.IsHidden,
			"is_pinned":            r.IsPinned,
			"is_muted":             r.IsMuted,
		}
	case application.MarkConversationReadResult:
		return map[string]any{"conversation_id": r.ConversationID, "unread_count": r.UnreadCount}
	case application.DeleteMessageForEveryoneResult:
		return map[string]any{
			"message_id":           r.MessageID,
			"conversation_id":      r.ConversationID,
			"deleted_for_everyone": r.DeletedForEveryone,
		}
	case application.ArchiveConversationResult:
		return map[string]any{"conversation_id": r.ConversationID, "is_archived": r.IsArchived}
	case application.HideConversationResult:
		return map[string]any{"conversation_id": r.ConversationID, "is_hidden": r.IsHidden}
	case application.PinConversationResult:
		return map[string]any{"conversation_id": r.ConversationID, "is_pinned": r.IsPinned}
	case application.MuteConversationResult:
		m := map[string]any{"conversation_id": r.ConversationID, "is_muted": r.IsMuted}
		if r.MutedUntil != nil {
			m["muted_until"] = *r.MutedUntil
		}
		return m
	case application.BlockUserResult:
		return map[string]any{"blocker_id": r.BlockerID, "blocked_id": r.BlockedID}
	case application.UnblockUserResult:
		return map[string]any{"blocker_id": r.BlockerID, "blocked_id": r.BlockedID}
	case application.MarkListingUnavailableResult:
		return map[string]any{
			"listing_id":            r.ListingID,
			"conversations_frozen":  r.ConversationsFrozen,
		}
	default:
		return v
	}
}
