package httpapi

import (
	"net/http"

	wsv1 "github.com/HDAI654/Kologram/chat_service/internal/presentation/ws/v1"
)

func NewRouter(ws *wsv1.Server) http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /health", Health)
	mux.HandleFunc("GET /ws", ws.ServeWS)
	return mux
}
