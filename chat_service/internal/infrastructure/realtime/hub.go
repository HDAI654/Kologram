package realtime

import (
	"context"
	"encoding/json"
	"log/slog"
	"sync"

	"github.com/gorilla/websocket"
)

// clientConn serializes writes; gorilla/websocket forbids concurrent writes on one connection.
type clientConn struct {
	conn *websocket.Conn
	mu   sync.Mutex
}

func (c *clientConn) writeText(data []byte) error {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.conn.WriteMessage(websocket.TextMessage, data)
}

func (c *clientConn) close() {
	c.mu.Lock()
	defer c.mu.Unlock()
	_ = c.conn.Close()
}

// Hub manages WebSocket connections keyed by user id and implements RealtimeNotifier.
type Hub struct {
	mu      sync.RWMutex
	clients map[string]map[*clientConn]struct{}
}

func NewHub() *Hub {
	return &Hub{
		clients: make(map[string]map[*clientConn]struct{}),
	}
}

func (h *Hub) Register(userID string, conn *websocket.Conn) *clientConn {
	wrapped := &clientConn{conn: conn}
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.clients[userID] == nil {
		h.clients[userID] = make(map[*clientConn]struct{})
	}
	h.clients[userID][wrapped] = struct{}{}
	slog.Info("ws registered", "user_id", userID)
	return wrapped
}

func (h *Hub) Unregister(userID string, wrapped *clientConn) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if conns, ok := h.clients[userID]; ok {
		delete(conns, wrapped)
		if len(conns) == 0 {
			delete(h.clients, userID)
		}
	}
	wrapped.close()
}

func (h *Hub) NotifyUser(_ context.Context, userID string, payload any) error {
	body, err := json.Marshal(payload)
	if err != nil {
		return err
	}
	h.mu.RLock()
	conns := make([]*clientConn, 0)
	for c := range h.clients[userID] {
		conns = append(conns, c)
	}
	h.mu.RUnlock()

	for _, c := range conns {
		if err := c.writeText(body); err != nil {
			slog.Warn("ws write failed", "user_id", userID, "error", err)
		}
	}
	return nil
}

// ConnectedCount reports how many sockets a user currently has open (tests / diagnostics).
func (h *Hub) ConnectedCount(userID string) int {
	h.mu.RLock()
	defer h.mu.RUnlock()
	return len(h.clients[userID])
}
