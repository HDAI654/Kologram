package ws

import (
	"log/slog"
	"net/http"

	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/realtime"

	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		// Gateway terminates auth / origin checks in production.
		return true
	},
}

// Handler upgrades HTTP connections to WebSocket, keyed by user_id query param.
func Handler(hub *realtime.Hub) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		userID := r.URL.Query().Get("user_id")
		if userID == "" {
			http.Error(w, `{"detail":"user_id is required"}`, http.StatusUnprocessableEntity)
			return
		}

		conn, err := upgrader.Upgrade(w, r, nil)
		if err != nil {
			slog.Error("websocket upgrade failed", "user_id", userID, "error", err)
			return
		}

		client := hub.Register(userID, conn)
		defer hub.Unregister(userID, client)

		slog.Info("websocket connected", "user_id", userID)

		// Read loop: keep connection alive; server pushes outbound events via Hub.
		for {
			if _, _, err := conn.ReadMessage(); err != nil {
				slog.Info("websocket disconnected", "user_id", userID, "error", err)
				return
			}
		}
	})
}
