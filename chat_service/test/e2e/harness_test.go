package e2e_test

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"github.com/gorilla/websocket"
	"github.com/HDAI654/Kologram/chat_service/internal/application"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/messaging"
	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/persistence/memory"
	httpapi "github.com/HDAI654/Kologram/chat_service/internal/presentation/http"
	wsv1 "github.com/HDAI654/Kologram/chat_service/internal/presentation/ws/v1"
)

const (
	buyerID        = "0d47ddfe-a4ca-446a-839e-d3bbcba824c6"
	sellerID       = "bdf038e5-8b16-4825-a895-ce7d0648e845"
	strangerID     = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
	listingActive  = "431f7a61-1a30-4c3a-b2d4-5282ca2799b5"
	listingSold    = "531f7a61-1a30-4c3a-b2d4-5282ca2799b5"
	listingMissing = "631f7a61-1a30-4c3a-b2d4-5282ca2799b5"
)

type listingStub struct {
	byID map[string]*entities.Listing
}

func (s *listingStub) GetByID(ctx context.Context, id valueobjects.ListingID) (*entities.Listing, error) {
	_ = ctx
	l, ok := s.byID[id.String()]
	if !ok {
		return nil, nil
	}
	return l, nil
}

func defaultListings() *listingStub {
	seller, _ := valueobjects.NewUserID(sellerID)
	activeID, _ := valueobjects.NewListingID(listingActive)
	soldID, _ := valueobjects.NewListingID(listingSold)
	return &listingStub{byID: map[string]*entities.Listing{
		listingActive: {ID: activeID, SellerID: seller, MessageAllowed: true},
		listingSold:   {ID: soldID, SellerID: seller, MessageAllowed: false},
	}}
}

type harness struct {
	t      *testing.T
	server *httptest.Server
	store  *memory.Store
	hub    *wsv1.MemoryHub
}

func newHarness(t *testing.T) *harness {
	t.Helper()
	store := memory.NewStore()
	factory := memory.NewUnitOfWorkFactory(store)
	convs := memory.NewConversationRepository(store)
	states := memory.NewConversationUserStateRepository(store)
	msgs := memory.NewMessageRepository(store)
	hub := wsv1.NewMemoryHub()
	events := messaging.NewNoOpEventPublisher()
	listings := defaultListings()

	handlers := &wsv1.Handlers{
		StartConversation:        application.NewStartConversationHandler(factory, listings, events, nil),
		SendMessage:              application.NewSendMessageHandler(factory, events, hub, nil),
		ListMessages:             application.NewListMessagesHandler(convs, msgs),
		ListConversations:        application.NewListConversationsHandler(convs),
		GetConversation:          application.NewGetConversationHandler(convs, states),
		MarkConversationRead:     application.NewMarkConversationReadHandler(factory),
		DeleteMessageForEveryone: application.NewDeleteMessageForEveryoneHandler(factory, hub, nil),
		ArchiveConversation:      application.NewArchiveConversationHandler(factory),
		HideConversation:         application.NewHideConversationHandler(factory),
		PinConversation:          application.NewPinConversationHandler(factory),
		MuteConversation:         application.NewMuteConversationHandler(factory),
		BlockUser:                application.NewBlockUserHandler(factory, nil),
		UnblockUser:              application.NewUnblockUserHandler(factory, nil),
		MarkListingUnavailable:   application.NewMarkListingUnavailableHandler(factory, nil),
	}
	router := wsv1.NewRouter()
	handlers.Register(router)
	wsServer := wsv1.NewServer(hub, router, nil)
	httpHandler := httpapi.NewRouter(wsServer)
	srv := httptest.NewServer(httpHandler)
	t.Cleanup(srv.Close)

	return &harness{t: t, server: srv, store: store, hub: hub}
}

type wsClient struct {
	t    *testing.T
	conn *websocket.Conn
}

func (h *harness) dial(t *testing.T, userID string, admin bool) *wsClient {
	t.Helper()
	url := "ws" + strings.TrimPrefix(h.server.URL, "http") + "/ws"
	header := http.Header{}
	header.Set("X-User-Id", userID)
	if admin {
		header.Set("X-User-Admin", "true")
	}
	conn, resp, err := websocket.DefaultDialer.Dial(url, header)
	if err != nil {
		if resp != nil {
			t.Fatalf("dial: %v status=%d", err, resp.StatusCode)
		}
		t.Fatalf("dial: %v", err)
	}
	t.Cleanup(func() { _ = conn.Close() })
	return &wsClient{t: t, conn: conn}
}

func (h *harness) dialExpectHTTP(t *testing.T, userID string, wantStatus int) {
	t.Helper()
	url := "ws" + strings.TrimPrefix(h.server.URL, "http") + "/ws"
	header := http.Header{}
	if userID != "" {
		header.Set("X-User-Id", userID)
	}
	_, resp, err := websocket.DefaultDialer.Dial(url, header)
	if err == nil {
		t.Fatalf("expected dial failure")
	}
	if resp == nil || resp.StatusCode != wantStatus {
		t.Fatalf("status = %v, want %d err=%v", resp, wantStatus, err)
	}
}

type envelope struct {
	ID      string          `json:"id"`
	Type    string          `json:"type"`
	OK      *bool           `json:"ok"`
	Payload json.RawMessage `json:"payload"`
	Error   *struct {
		Code    string `json:"code"`
		Message string `json:"message"`
		Field   string `json:"field"`
	} `json:"error"`
}

func (c *wsClient) call(id, typ string, payload any) envelope {
	c.t.Helper()
	body := map[string]any{"id": id, "type": typ}
	if payload != nil {
		body["payload"] = payload
	}
	if err := c.conn.WriteJSON(body); err != nil {
		c.t.Fatalf("write: %v", err)
	}
	_ = c.conn.SetReadDeadline(time.Now().Add(3 * time.Second))
	var env envelope
	if err := c.conn.ReadJSON(&env); err != nil {
		c.t.Fatalf("read: %v", err)
	}
	return env
}

func (c *wsClient) mustOK(id, typ string, payload any) envelope {
	c.t.Helper()
	env := c.call(id, typ, payload)
	if env.OK == nil || !*env.OK {
		c.t.Fatalf("want ok response, got %+v", env)
	}
	if env.ID != id {
		c.t.Fatalf("id = %s want %s", env.ID, id)
	}
	return env
}

func (c *wsClient) mustErr(id, typ string, payload any, code string) envelope {
	c.t.Helper()
	env := c.call(id, typ, payload)
	if env.OK != nil && *env.OK {
		c.t.Fatalf("want error, got ok %+v", env)
	}
	if env.Error == nil || env.Error.Code != code {
		c.t.Fatalf("want code %s, got %+v", code, env)
	}
	return env
}

func (c *wsClient) readPush(timeout time.Duration) map[string]any {
	c.t.Helper()
	_ = c.conn.SetReadDeadline(time.Now().Add(timeout))
	var m map[string]any
	if err := c.conn.ReadJSON(&m); err != nil {
		c.t.Fatalf("read push: %v", err)
	}
	return m
}

func payloadMap(env envelope) map[string]any {
	var m map[string]any
	_ = json.Unmarshal(env.Payload, &m)
	return m
}
