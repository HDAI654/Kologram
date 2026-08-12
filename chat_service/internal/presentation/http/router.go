package httpapi

import (
	"net/http"
)

// NewRouter builds the HTTP mux for Chat Service REST + optional WebSocket upgrade handler.
func NewRouter(h *Handlers, ws http.Handler) http.Handler {
	mux := http.NewServeMux()

	mux.HandleFunc("GET /health", h.Health)

	// Conversations
	mux.HandleFunc("POST /api/v1/conversations", h.StartConversation)
	mux.HandleFunc("GET /api/v1/conversations", h.ListConversations)

	mux.HandleFunc("POST /api/v1/conversations/{id}/messages", h.SendMessage)
	mux.HandleFunc("GET /api/v1/conversations/{id}/messages", h.GetMessages)
	mux.HandleFunc("POST /api/v1/conversations/{id}/read", h.MarkRead)
	mux.HandleFunc("POST /api/v1/conversations/{id}/status", h.ChangeStatus)

	if ws != nil {
		mux.Handle("GET /ws", ws)
	}

	return mux
}
