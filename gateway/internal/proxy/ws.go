package proxy

import (
	"log/slog"
	"net/http"
	"net/url"
	"time"

	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	CheckOrigin:     func(r *http.Request) bool { return true },
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
}

// WSProxy upgrades the client connection and dials the upstream chat /ws.
func WSProxy(chatBase string, originAllowed string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if origin := r.Header.Get("Origin"); origin != "" && origin != originAllowed {
			http.Error(w, "origin not allowed", http.StatusForbidden)
			return
		}

		userID := r.Header.Get("X-User-Id")
		if userID == "" {
			http.Error(w, "unauthorized", http.StatusUnauthorized)
			return
		}

		clientConn, err := upgrader.Upgrade(w, r, nil)
		if err != nil {
			slog.Warn("ws upgrade failed", "err", err)
			return
		}
		defer clientConn.Close()

		u, err := url.Parse(chatBase)
		if err != nil {
			return
		}
		u.Path = "/ws"
		switch u.Scheme {
		case "https":
			u.Scheme = "wss"
		default:
			u.Scheme = "ws"
		}

		hdr := http.Header{}
		hdr.Set("X-User-Id", userID)
		if admin := r.Header.Get("X-User-Admin"); admin != "" {
			hdr.Set("X-User-Admin", admin)
		}

		dialer := websocket.Dialer{HandshakeTimeout: 10 * time.Second}
		upConn, resp, err := dialer.Dial(u.String(), hdr)
		if err != nil {
			slog.Warn("ws dial upstream failed", "err", err)
			if resp != nil {
				_ = resp.Body.Close()
			}
			return
		}
		defer upConn.Close()

		errc := make(chan struct{}, 2)
		go pipeWS(clientConn, upConn, errc)
		go pipeWS(upConn, clientConn, errc)
		<-errc
	}
}

func pipeWS(src, dst *websocket.Conn, done chan struct{}) {
	defer func() { done <- struct{}{} }()
	for {
		mt, msg, err := src.ReadMessage()
		if err != nil {
			return
		}
		if err := dst.WriteMessage(mt, msg); err != nil {
			return
		}
	}
}
