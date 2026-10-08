package e2e_test

import (
	"testing"
	"time"
)

func TestE2E_StartConversation_SuccessAndIdempotent(t *testing.T) {
	t.Parallel()
	h := newHarness(t)
	buyer := h.dial(t, buyerID, false)

	r1 := buyer.mustOK("1", "start_conversation", map[string]any{"listing_id": listingActive})
	p1 := payloadMap(r1)
	convID, _ := p1["conversation_id"].(string)
	if convID == "" {
		t.Fatalf("payload=%v", p1)
	}
	if p1["created"] != true {
		t.Fatalf("first start should create: %v", p1)
	}

	r2 := buyer.mustOK("2", "start_conversation", map[string]any{"listing_id": listingActive})
	p2 := payloadMap(r2)
	if p2["conversation_id"] != convID {
		t.Fatalf("idempotent id mismatch")
	}
	if p2["created"] == true {
		t.Fatalf("second start should not create")
	}
}

func TestE2E_StartConversation_SoldListing(t *testing.T) {
	t.Parallel()
	h := newHarness(t)
	h.dial(t, buyerID, false).mustErr("1", "start_conversation", map[string]any{"listing_id": listingSold}, "CONFLICT")
}

func TestE2E_StartConversation_MissingListing(t *testing.T) {
	t.Parallel()
	h := newHarness(t)
	h.dial(t, buyerID, false).mustErr("1", "start_conversation", map[string]any{"listing_id": listingMissing}, "NOT_FOUND")
}

func TestE2E_Messaging_FullJourney(t *testing.T) {
	t.Parallel()
	h := newHarness(t)
	buyer := h.dial(t, buyerID, false)
	seller := h.dial(t, sellerID, false)

	start := buyer.mustOK("s1", "start_conversation", map[string]any{"listing_id": listingActive})
	convID := payloadMap(start)["conversation_id"].(string)

	clientMsg := "11111111-1111-4111-8111-111111111111"
	send := buyer.mustOK("m1", "send_message", map[string]any{
		"conversation_id":   convID,
		"client_message_id": clientMsg,
		"content":           "hello seller",
	})
	msgID := payloadMap(send)["message_id"].(string)
	if msgID == "" {
		t.Fatalf("missing message_id")
	}

	push := seller.readPush(2 * time.Second)
	if push["type"] != "message_sent" {
		t.Fatalf("push=%v", push)
	}

	list := buyer.mustOK("l1", "list_messages", map[string]any{"conversation_id": convID, "limit": 20})
	items, _ := payloadMap(list)["messages"].([]any)
	if len(items) < 1 {
		t.Fatalf("list=%v", payloadMap(list))
	}

	get := buyer.mustOK("g1", "get_conversation", map[string]any{"conversation_id": convID})
	if payloadMap(get)["conversation_id"] != convID {
		t.Fatalf("get=%v", payloadMap(get))
	}

	buyer.mustOK("r1", "mark_conversation_read", map[string]any{
		"conversation_id":      convID,
		"last_read_message_id": msgID,
	})

	// idempotent send
	again := buyer.mustOK("m2", "send_message", map[string]any{
		"conversation_id": convID, "client_message_id": clientMsg, "content": "hello seller",
	})
	if payloadMap(again)["message_id"] != msgID {
		t.Fatalf("idempotent mismatch")
	}
}

func TestE2E_SendMessage_StrangerForbidden(t *testing.T) {
	t.Parallel()
	h := newHarness(t)
	buyer := h.dial(t, buyerID, false)
	stranger := h.dial(t, strangerID, false)
	start := buyer.mustOK("s1", "start_conversation", map[string]any{"listing_id": listingActive})
	convID := payloadMap(start)["conversation_id"].(string)
	stranger.mustErr("m1", "send_message", map[string]any{
		"conversation_id":   convID,
		"client_message_id": "33333333-3333-4333-8333-333333333333",
		"content":           "nope",
	}, "FORBIDDEN")
}

func TestE2E_DeleteMessage_AuthorAndPush(t *testing.T) {
	t.Parallel()
	h := newHarness(t)
	buyer := h.dial(t, buyerID, false)
	seller := h.dial(t, sellerID, false)
	start := buyer.mustOK("s1", "start_conversation", map[string]any{"listing_id": listingActive})
	convID := payloadMap(start)["conversation_id"].(string)
	send := buyer.mustOK("m1", "send_message", map[string]any{
		"conversation_id": convID,
		"client_message_id": "44444444-4444-4444-8444-444444444444",
		"content": "bye",
	})
	_ = seller.readPush(2 * time.Second)
	msgID := payloadMap(send)["message_id"].(string)

	buyer.mustOK("d1", "delete_message_for_everyone", map[string]any{"message_id": msgID})
	push := seller.readPush(2 * time.Second)
	if push["type"] != "message_deleted" {
		t.Fatalf("push=%v", push)
	}

	list := buyer.mustOK("l1", "list_messages", map[string]any{"conversation_id": convID})
	items, _ := payloadMap(list)["messages"].([]any)
	if len(items) != 0 {
		t.Fatalf("soft-deleted should be hidden, got %v", items)
	}
}

func TestE2E_DeleteMessage_NotAuthorForbidden(t *testing.T) {
	t.Parallel()
	h := newHarness(t)
	buyer := h.dial(t, buyerID, false)
	seller := h.dial(t, sellerID, false)
	start := buyer.mustOK("s1", "start_conversation", map[string]any{"listing_id": listingActive})
	convID := payloadMap(start)["conversation_id"].(string)
	send := buyer.mustOK("m1", "send_message", map[string]any{
		"conversation_id": convID,
		"client_message_id": "55555555-5555-4555-8555-555555555555",
		"content": "mine",
	})
	_ = seller.readPush(2 * time.Second)
	msgID := payloadMap(send)["message_id"].(string)
	seller.mustErr("d1", "delete_message_for_everyone", map[string]any{"message_id": msgID}, "FORBIDDEN")
}


func TestE2E_GetConversation_StrangerForbidden(t *testing.T) {
	t.Parallel()
	h := newHarness(t)
	buyer := h.dial(t, buyerID, false)
	stranger := h.dial(t, strangerID, false)
	start := buyer.mustOK("s1", "start_conversation", map[string]any{"listing_id": listingActive})
	convID := payloadMap(start)["conversation_id"].(string)
	stranger.mustErr("g1", "get_conversation", map[string]any{"conversation_id": convID}, "FORBIDDEN")
}

func TestE2E_MarkRead_SoftDeletedNotFound(t *testing.T) {
	t.Parallel()
	h := newHarness(t)
	buyer := h.dial(t, buyerID, false)
	start := buyer.mustOK("s1", "start_conversation", map[string]any{"listing_id": listingActive})
	convID := payloadMap(start)["conversation_id"].(string)
	send := buyer.mustOK("m1", "send_message", map[string]any{
		"conversation_id": convID,
		"client_message_id": "99999999-9999-4999-8999-999999999999",
		"content": "temp",
	})
	msgID := payloadMap(send)["message_id"].(string)
	buyer.mustOK("d1", "delete_message_for_everyone", map[string]any{"message_id": msgID})
	buyer.mustErr("r1", "mark_conversation_read", map[string]any{
		"conversation_id": convID,
		"last_read_message_id": msgID,
	}, "NOT_FOUND")
}

func TestE2E_Mute_RequiresUntil(t *testing.T) {
	t.Parallel()
	h := newHarness(t)
	buyer := h.dial(t, buyerID, false)
	start := buyer.mustOK("s1", "start_conversation", map[string]any{"listing_id": listingActive})
	convID := payloadMap(start)["conversation_id"].(string)
	buyer.mustErr("mu1", "mute_conversation", map[string]any{
		"conversation_id": convID, "mute": true,
	}, "VALIDATION_ERROR")
}
