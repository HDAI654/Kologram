package v1

import (
	"encoding/json"
	"errors"
	"sync"
	"time"

	"github.com/gorilla/websocket"
)

const (
	writeWait      = 10 * time.Second
	pongWait       = 60 * time.Second
	pingPeriod     = (pongWait * 9) / 10
	maxMessageSize = 64 << 10 // 64 KiB
)

var errSessionClosed = errors.New("session closed")

// Session is one authenticated WebSocket connection.
type Session struct {
	UserID  string
	IsAdmin bool
	conn    *websocket.Conn
	send    chan []byte
	hub     Hub
	mu      sync.Mutex // protects closed + send enqueue vs close
	closed  bool
	once    sync.Once
}

// Hub tracks live sessions for realtime push.
type Hub interface {
	Register(s *Session)
	Unregister(s *Session)
}

func NewSession(userID string, isAdmin bool, conn *websocket.Conn, hub Hub) *Session {
	return &Session{
		UserID:  userID,
		IsAdmin: isAdmin,
		conn:    conn,
		send:    make(chan []byte, 64),
		hub:     hub,
	}
}

func (s *Session) Close() {
	s.once.Do(func() {
		s.mu.Lock()
		s.closed = true
		close(s.send)
		s.mu.Unlock()
		_ = s.conn.Close()
	})
}

// enqueue is safe against concurrent Close (no send-on-closed-channel panic).
func (s *Session) enqueue(b []byte) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.closed {
		return errSessionClosed
	}
	select {
	case s.send <- b:
		return nil
	default:
		return websocket.ErrCloseSent
	}
}

// WriteJSON queues a JSON message to the write pump (safe for concurrent use).
func (s *Session) WriteJSON(v any) error {
	b, err := json.Marshal(v)
	if err != nil {
		return err
	}
	return s.enqueue(b)
}

func (s *Session) writePump() {
	ticker := time.NewTicker(pingPeriod)
	defer func() {
		ticker.Stop()
		s.Close()
	}()
	for {
		select {
		case msg, ok := <-s.send:
			_ = s.conn.SetWriteDeadline(time.Now().Add(writeWait))
			if !ok {
				_ = s.conn.WriteMessage(websocket.CloseMessage, []byte{})
				return
			}
			if err := s.conn.WriteMessage(websocket.TextMessage, msg); err != nil {
				return
			}
		case <-ticker.C:
			_ = s.conn.SetWriteDeadline(time.Now().Add(writeWait))
			if err := s.conn.WriteMessage(websocket.PingMessage, nil); err != nil {
				return
			}
		}
	}
}
