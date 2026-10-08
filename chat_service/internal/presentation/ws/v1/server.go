package v1

import (
	"context"
	"encoding/json"
	"log/slog"
	"net/http"
	"strings"
	"time"

	"github.com/google/uuid"
	"github.com/gorilla/websocket"
)

const (
	userIDHeader    = "X-User-Id"
	userAdminHeader = "X-User-Admin"
)

var upgrader = websocket.Upgrader{
	ReadBufferSize:  4096,
	WriteBufferSize: 4096,
	// Origin checks are the gateway's responsibility.
	CheckOrigin: func(r *http.Request) bool { return true },
}

type Dispatcher interface {
	Dispatch(ctx context.Context, userID string, req Request) Response
}

// AdminAwareDispatcher can use connection admin flag (optional).
type AdminAwareDispatcher interface {
	DispatchAdmin(ctx context.Context, userID string, isAdmin bool, req Request) Response
}

type Server struct {
	hub        Hub
	dispatcher Dispatcher
	log        *slog.Logger
}

func NewServer(hub Hub, dispatcher Dispatcher, log *slog.Logger) *Server {
	if log == nil {
		log = slog.Default()
	}
	return &Server{hub: hub, dispatcher: dispatcher, log: log}
}

func (s *Server) ServeWS(w http.ResponseWriter, r *http.Request) {
	userID := strings.TrimSpace(r.Header.Get(userIDHeader))
	if userID == "" {
		http.Error(w, "missing X-User-Id", http.StatusUnauthorized)
		return
	}
	if _, err := uuid.Parse(userID); err != nil {
		http.Error(w, "invalid X-User-Id", http.StatusUnauthorized)
		return
	}
	isAdmin := parseAdminHeader(r.Header.Get(userAdminHeader))

	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		s.log.Warn("websocket upgrade failed", "error", err)
		return
	}

	session := NewSession(userID, isAdmin, conn, s.hub)
	if s.hub != nil {
		s.hub.Register(session)
	}

	// Connection-scoped context: canceled when the socket ends (not the upgrade request).
	connCtx, cancel := context.WithCancel(context.Background())
	defer cancel()

	go session.writePump()
	s.readLoop(connCtx, cancel, session)
}

func parseAdminHeader(v string) bool {
	v = strings.TrimSpace(strings.ToLower(v))
	return v == "true" || v == "1" || v == "yes"
}

func (s *Server) readLoop(ctx context.Context, cancel context.CancelFunc, session *Session) {
	defer func() {
		cancel()
		if s.hub != nil {
			s.hub.Unregister(session)
		}
		session.Close()
	}()

	session.conn.SetReadLimit(maxMessageSize)
	_ = session.conn.SetReadDeadline(time.Now().Add(pongWait))
	session.conn.SetPongHandler(func(string) error {
		_ = session.conn.SetReadDeadline(time.Now().Add(pongWait))
		return nil
	})

	for {
		_, data, err := session.conn.ReadMessage()
		if err != nil {
			return
		}

		var req Request
		if err := json.Unmarshal(data, &req); err != nil {
			_ = session.WriteJSON(Response{
				Type: "error",
				OK:   false,
				Error: &ErrorBody{
					Code:    CodeInvalidRequest,
					Message: "invalid JSON envelope",
				},
			})
			continue
		}
		if req.ID == "" || req.Type == "" {
			_ = session.WriteJSON(Response{
				ID:   req.ID,
				Type: resultType(req.Type),
				OK:   false,
				Error: &ErrorBody{
					Code:    CodeInvalidRequest,
					Message: "id and type are required",
				},
			})
			continue
		}

		var resp Response
		if ad, ok := s.dispatcher.(AdminAwareDispatcher); ok {
			resp = ad.DispatchAdmin(ctx, session.UserID, session.IsAdmin, req)
		} else {
			resp = s.dispatcher.Dispatch(ctx, session.UserID, req)
		}
		if resp.ID == "" {
			resp.ID = req.ID
		}
		if resp.Type == "" {
			resp.Type = resultType(req.Type)
		}
		_ = session.WriteJSON(resp)
	}
}

func resultType(requestType string) string {
	if requestType == "" {
		return "error"
	}
	return requestType + "_result"
}
