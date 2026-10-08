package e2e_test

import (
	"testing"
	"time"
)

func TestE2E_ConversationStateActions(t *testing.T) {
	t.Parallel()
	h := newHarness(t)
	buyer := h.dial(t, buyerID, false)
	start := buyer.mustOK("s1", "start_conversation", map[string]any{"listing_id": listingActive})
	convID := payloadMap(start)["conversation_id"].(string)

	buyer.mustOK("a1", "archive_conversation", map[string]any{"conversation_id": convID, "archive": true})
	buyer.mustOK("a2", "archive_conversation", map[string]any{"conversation_id": convID, "archive": false})
	buyer.mustOK("p1", "pin_conversation", map[string]any{"conversation_id": convID, "pin": true})
	buyer.mustOK("h1", "hide_conversation", map[string]any{"conversation_id": convID, "hide": true})
	buyer.mustOK("h2", "hide_conversation", map[string]any{"conversation_id": convID, "hide": false})
	until := time.Now().UTC().Add(time.Hour).Format(time.RFC3339)
	buyer.mustOK("mu1", "mute_conversation", map[string]any{
		"conversation_id": convID, "mute": true, "until": until,
	})
	buyer.mustOK("mu2", "mute_conversation", map[string]any{"conversation_id": convID, "mute": false})
}

func TestE2E_ListConversations_ActiveAndArchived(t *testing.T) {
	t.Parallel()
	h := newHarness(t)
	buyer := h.dial(t, buyerID, false)
	start := buyer.mustOK("s1", "start_conversation", map[string]any{"listing_id": listingActive})
	convID := payloadMap(start)["conversation_id"].(string)

	active := buyer.mustOK("l1", "list_conversations", map[string]any{"filter": "active"})
	activeItems, _ := payloadMap(active)["items"].([]any)
	if !containsConv(activeItems, convID) {
		t.Fatalf("active list missing conv: %v", activeItems)
	}

	buyer.mustOK("a1", "archive_conversation", map[string]any{"conversation_id": convID, "archive": true})
	archived := buyer.mustOK("l2", "list_conversations", map[string]any{"filter": "archived"})
	archItems, _ := payloadMap(archived)["items"].([]any)
	if !containsConv(archItems, convID) {
		t.Fatalf("archived list missing conv: %v", archItems)
	}
	active2 := buyer.mustOK("l3", "list_conversations", map[string]any{"filter": "active"})
	if containsConv(payloadMap(active2)["items"].([]any), convID) {
		t.Fatalf("archived conv still in active list")
	}
}

func containsConv(items []any, convID string) bool {
	for _, it := range items {
		m, _ := it.(map[string]any)
		if m != nil && m["conversation_id"] == convID {
			return true
		}
	}
	return false
}

func TestE2E_Block_PreventsSend(t *testing.T) {
	t.Parallel()
	h := newHarness(t)
	buyer := h.dial(t, buyerID, false)
	seller := h.dial(t, sellerID, false)

	start := buyer.mustOK("s1", "start_conversation", map[string]any{"listing_id": listingActive})
	convID := payloadMap(start)["conversation_id"].(string)

	buyer.mustOK("b1", "block_user", map[string]any{"blocked_id": sellerID})
	buyer.mustErr("m1", "send_message", map[string]any{
		"conversation_id": convID,
		"client_message_id": "66666666-6666-4666-8666-666666666666",
		"content": "blocked",
	}, "FORBIDDEN")

	buyer.mustOK("u1", "unblock_user", map[string]any{"blocked_id": sellerID})
	buyer.mustOK("m2", "send_message", map[string]any{
		"conversation_id": convID,
		"client_message_id": "77777777-7777-4777-8777-777777777777",
		"content": "unblocked",
	})
	_ = seller.readPush(2 * time.Second)
}

func TestE2E_BlockSelf_Validation(t *testing.T) {
	t.Parallel()
	h := newHarness(t)
	h.dial(t, buyerID, false).mustErr("b1", "block_user", map[string]any{"blocked_id": buyerID}, "VALIDATION_ERROR")
}

func TestE2E_MarkListingUnavailable_AdminOnly(t *testing.T) {
	t.Parallel()
	h := newHarness(t)
	buyer := h.dial(t, buyerID, false)
	admin := h.dial(t, sellerID, true)

	start := buyer.mustOK("s1", "start_conversation", map[string]any{"listing_id": listingActive})
	convID := payloadMap(start)["conversation_id"].(string)

	buyer.mustErr("x1", "mark_listing_unavailable", map[string]any{"listing_id": listingActive}, "FORBIDDEN")

	admin.mustOK("x2", "mark_listing_unavailable", map[string]any{"listing_id": listingActive})

	// conversation should be read-only for further messages
	buyer.mustErr("m1", "send_message", map[string]any{
		"conversation_id": convID,
		"client_message_id": "88888888-8888-4888-8888-888888888888",
		"content": "after freeze",
	}, "CONFLICT")
}

func TestE2E_InvalidPayload(t *testing.T) {
	t.Parallel()
	h := newHarness(t)
	c := h.dial(t, buyerID, false)
	c.mustErr("1", "start_conversation", nil, "INVALID_REQUEST")
}
