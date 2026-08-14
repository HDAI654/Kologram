package e2e_test

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/HDAI654/Kologram/chat_service/internal/application"
	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/messaging"
	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/persistence/memory"
	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/realtime"
	httpapi "github.com/HDAI654/Kologram/chat_service/internal/presentation/http"
)

const (
	buyerID   = "550e8400-e29b-41d4-a716-446655440001"
	sellerID  = "550e8400-e29b-41d4-a716-446655440002"
	listingID = "550e8400-e29b-41d4-a716-446655440003"
	stranger  = "550e8400-e29b-41d4-a716-446655440099"
)

func newTestServer(t *testing.T) *httptest.Server {
	t.Helper()
	repo := memory.NewConversationRepository()
	factory := memory.NewUnitOfWorkFactory(repo)
	events := messaging.NewNoOpEventPublisher()
	hub := realtime.NewHub()

	handlers := &httpapi.Handlers{
		Start:   application.NewStartConversationHandler(factory, events),
		Send:    application.NewSendMessageHandler(factory, events, hub),
		List:    application.NewListConversationsHandler(factory),
		Get:     application.NewGetMessagesHandler(factory),
		Read:    application.NewMarkReadHandler(factory, events, hub),
		Status:  application.NewChangeStatusHandler(factory, events),
		AppName: "ChatServiceTest",
	}
	router := httpapi.NewRouter(handlers, nil)
	return httptest.NewServer(router)
}

func postJSON(t *testing.T, client *http.Client, url string, body any) (int, map[string]any) {
	t.Helper()
	b, _ := json.Marshal(body)
	resp, err := client.Post(url, "application/json", bytes.NewReader(b))
	if err != nil {
		t.Fatal(err)
	}
	defer resp.Body.Close()
	data, _ := io.ReadAll(resp.Body)
	var out map[string]any
	_ = json.Unmarshal(data, &out)
	return resp.StatusCode, out
}

func getJSON(t *testing.T, client *http.Client, url string) (int, map[string]any) {
	t.Helper()
	resp, err := client.Get(url)
	if err != nil {
		t.Fatal(err)
	}
	defer resp.Body.Close()
	data, _ := io.ReadAll(resp.Body)
	var out map[string]any
	_ = json.Unmarshal(data, &out)
	return resp.StatusCode, out
}

func TestHealth(t *testing.T) {
	srv := newTestServer(t)
	defer srv.Close()

	code, body := getJSON(t, srv.Client(), srv.URL+"/health")
	if code != http.StatusOK {
		t.Fatalf("status=%d body=%v", code, body)
	}
	if body["status"] != "ok" {
		t.Fatalf("body=%v", body)
	}
}

func TestFullChatJourney(t *testing.T) {
	srv := newTestServer(t)
	defer srv.Close()
	client := srv.Client()
	base := srv.URL

	// 1) Start conversation
	code, body := postJSON(t, client, base+"/api/v1/conversations", map[string]string{
		"buyer_id": buyerID, "seller_id": sellerID, "listing_id": listingID,
	})
	if code != http.StatusCreated {
		t.Fatalf("start status=%d body=%v", code, body)
	}
	convID, _ := body["conversation_id"].(string)
	if convID == "" || body["created"] != true {
		t.Fatalf("body=%v", body)
	}

	// 2) Idempotent start returns same conversation
	code, body = postJSON(t, client, base+"/api/v1/conversations", map[string]string{
		"buyer_id": buyerID, "seller_id": sellerID, "listing_id": listingID,
	})
	if code != http.StatusOK {
		t.Fatalf("idempotent status=%d", code)
	}
	if body["created"] != false || body["conversation_id"] != convID {
		t.Fatalf("body=%v", body)
	}

	// 3) Buyer sends message
	code, body = postJSON(t, client, base+"/api/v1/conversations/"+convID+"/messages", map[string]string{
		"sender_id": buyerID, "content": "Is this still available?",
	})
	if code != http.StatusCreated {
		t.Fatalf("send status=%d body=%v", code, body)
	}
	if body["message_id"] == nil {
		t.Fatal("missing message_id")
	}

	// 4) Seller replies
	code, body = postJSON(t, client, base+"/api/v1/conversations/"+convID+"/messages", map[string]string{
		"sender_id": sellerID, "content": "Yes, it is!",
	})
	if code != http.StatusCreated {
		t.Fatalf("reply status=%d body=%v", code, body)
	}

	// 5) Get messages as buyer
	code, body = getJSON(t, client, base+"/api/v1/conversations/"+convID+"/messages?requester_id="+buyerID)
	if code != http.StatusOK {
		t.Fatalf("get messages status=%d body=%v", code, body)
	}
	msgs, _ := body["messages"].([]any)
	if len(msgs) != 2 {
		t.Fatalf("expected 2 messages, got %d body=%v", len(msgs), body)
	}

	// 6) Mark read as seller
	code, body = postJSON(t, client, base+"/api/v1/conversations/"+convID+"/read", map[string]string{
		"reader_id": sellerID,
	})
	if code != http.StatusOK {
		t.Fatalf("mark read status=%d body=%v", code, body)
	}

	// 7) List conversations for buyer
	code, body = getJSON(t, client, base+"/api/v1/conversations?user_id="+buyerID)
	if code != http.StatusOK {
		t.Fatalf("list status=%d body=%v", code, body)
	}
	items, _ := body["items"].([]any)
	if len(items) != 1 {
		t.Fatalf("items=%d body=%v", len(items), body)
	}

	// 8) Close conversation
	code, body = postJSON(t, client, base+"/api/v1/conversations/"+convID+"/status", map[string]string{
		"actor_id": buyerID, "new_status": "CLOSED",
	})
	if code != http.StatusOK {
		t.Fatalf("close status=%d body=%v", code, body)
	}
	if body["status"] != "CLOSED" {
		t.Fatalf("body=%v", body)
	}

	// 9) Cannot send when closed
	code, body = postJSON(t, client, base+"/api/v1/conversations/"+convID+"/messages", map[string]string{
		"sender_id": buyerID, "content": "one more",
	})
	if code != http.StatusConflict {
		t.Fatalf("expected conflict, got %d body=%v", code, body)
	}

	// 10) Reopen then archive
	code, body = postJSON(t, client, base+"/api/v1/conversations/"+convID+"/status", map[string]string{
		"actor_id": sellerID, "new_status": "OPEN",
	})
	if code != http.StatusOK {
		t.Fatalf("reopen status=%d body=%v", code, body)
	}
	code, body = postJSON(t, client, base+"/api/v1/conversations/"+convID+"/status", map[string]string{
		"actor_id": buyerID, "new_status": "ARCHIVED",
	})
	if code != http.StatusOK {
		t.Fatalf("archive status=%d body=%v", code, body)
	}
}

func TestStartConversation_SameBuyerSeller(t *testing.T) {
	srv := newTestServer(t)
	defer srv.Close()

	code, body := postJSON(t, srv.Client(), srv.URL+"/api/v1/conversations", map[string]string{
		"buyer_id": buyerID, "seller_id": buyerID, "listing_id": listingID,
	})
	if code != http.StatusConflict {
		t.Fatalf("status=%d body=%v", code, body)
	}
}

func TestSendMessage_NotParticipant(t *testing.T) {
	srv := newTestServer(t)
	defer srv.Close()
	client := srv.Client()

	_, body := postJSON(t, client, srv.URL+"/api/v1/conversations", map[string]string{
		"buyer_id": buyerID, "seller_id": sellerID, "listing_id": listingID,
	})
	convID, _ := body["conversation_id"].(string)

	code, body := postJSON(t, client, srv.URL+"/api/v1/conversations/"+convID+"/messages", map[string]string{
		"sender_id": stranger, "content": "intruding",
	})
	if code != http.StatusForbidden {
		t.Fatalf("status=%d body=%v", code, body)
	}
}

func TestGetMessages_RequiresRequester(t *testing.T) {
	srv := newTestServer(t)
	defer srv.Close()
	client := srv.Client()

	_, body := postJSON(t, client, srv.URL+"/api/v1/conversations", map[string]string{
		"buyer_id": buyerID, "seller_id": sellerID, "listing_id": listingID,
	})
	convID, _ := body["conversation_id"].(string)

	code, body := getJSON(t, client, srv.URL+"/api/v1/conversations/"+convID+"/messages")
	if code != http.StatusUnprocessableEntity {
		t.Fatalf("status=%d body=%v", code, body)
	}
}

func TestListConversations_RequiresUserID(t *testing.T) {
	srv := newTestServer(t)
	defer srv.Close()

	code, body := getJSON(t, srv.Client(), srv.URL+"/api/v1/conversations")
	if code != http.StatusUnprocessableEntity {
		t.Fatalf("status=%d body=%v", code, body)
	}
}

func TestInvalidIDs(t *testing.T) {
	srv := newTestServer(t)
	defer srv.Close()

	code, body := postJSON(t, srv.Client(), srv.URL+"/api/v1/conversations", map[string]string{
		"buyer_id": "not-uuid", "seller_id": sellerID, "listing_id": listingID,
	})
	if code != http.StatusUnprocessableEntity {
		t.Fatalf("status=%d body=%v", code, body)
	}
}

func TestConversationNotFound(t *testing.T) {
	srv := newTestServer(t)
	defer srv.Close()
	fake := "550e8400-e29b-41d4-a716-4466554400aa"

	code, body := postJSON(t, srv.Client(), srv.URL+"/api/v1/conversations/"+fake+"/messages", map[string]string{
		"sender_id": buyerID, "content": "hello",
	})
	if code != http.StatusNotFound {
		t.Fatalf("status=%d body=%v", code, body)
	}
}
