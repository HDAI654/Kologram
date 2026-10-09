package server

import (
	"encoding/json"
	"log/slog"
	"net/http"

	"github.com/HDAI654/Kologram/gateway/internal/auth"
	"github.com/HDAI654/Kologram/gateway/internal/config"
	"github.com/HDAI654/Kologram/gateway/internal/proxy"
	"github.com/HDAI654/Kologram/gateway/internal/ratelimit"
)

type Server struct {
	cfg      config.Config
	jwt      *auth.Validator
	publicRL *ratelimit.Limiter
	authRL   *ratelimit.Limiter
	userRL   *ratelimit.Limiter
	authP    http.Handler
	marketP  http.Handler
	ws       http.Handler
}

func New(cfg config.Config, jwt *auth.Validator) (*Server, error) {
	authP, err := proxy.NewReverseProxy(cfg.AuthURL)
	if err != nil {
		return nil, err
	}
	marketP, err := proxy.NewReverseProxy(cfg.MarketURL)
	if err != nil {
		return nil, err
	}
	return &Server{
		cfg:      cfg,
		jwt:      jwt,
		publicRL: ratelimit.New(cfg.PublicRPS, cfg.PublicBurst),
		authRL:   ratelimit.New(cfg.AuthRPS, cfg.AuthBurst),
		userRL:   ratelimit.New(cfg.UserRPS, cfg.UserBurst),
		authP:    authP,
		marketP:  marketP,
		ws:       proxy.WSProxy(cfg.ChatURL, cfg.CORSOrigin),
	}, nil
}

func (s *Server) Handler() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /health", s.health)
	mux.HandleFunc("/api/v1/auth/", s.handleAuth)
	mux.HandleFunc("/graphql", s.handleGraphQL)
	mux.HandleFunc("GET /ws", s.handleWS)
	return mux
}

func (s *Server) health(w http.ResponseWriter, _ *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(map[string]string{"status": "ok", "service": "gateway"})
}

func isPublicAuth(method, path string) bool {
	if method != http.MethodPost {
		return false
	}
	switch path {
	case "/api/v1/auth/verification",
		"/api/v1/auth/signup",
		"/api/v1/auth/login",
		"/api/v1/auth/password/forgot",
		"/api/v1/auth/password/reset",
		"/api/v1/auth/token/refresh":
		return true
	default:
		return false
	}
}

func (s *Server) handleAuth(w http.ResponseWriter, r *http.Request) {
	ip := ratelimit.ClientIP(r)
	if isPublicAuth(r.Method, r.URL.Path) {
		strict := r.URL.Path == "/api/v1/auth/login" ||
			r.URL.Path == "/api/v1/auth/signup" ||
			r.URL.Path == "/api/v1/auth/password/forgot"
		if strict {
			if !s.authRL.Allow(ip) {
				http.Error(w, "rate limit exceeded", http.StatusTooManyRequests)
				return
			}
		} else if !s.publicRL.Allow(ip) {
			http.Error(w, "rate limit exceeded", http.StatusTooManyRequests)
			return
		}
		s.authP.ServeHTTP(w, r)
		return
	}

	claims, err := s.jwt.ParseAccess(r.Header.Get("Authorization"))
	if err != nil {
		http.Error(w, "unauthorized", http.StatusUnauthorized)
		return
	}
	if !s.userRL.Allow(claims.Sub) {
		http.Error(w, "rate limit exceeded", http.StatusTooManyRequests)
		return
	}
	injectIdentity(r, claims)
	s.authP.ServeHTTP(w, r)
}

func (s *Server) handleGraphQL(w http.ResponseWriter, r *http.Request) {
	claims, err := s.jwt.ParseAccess(r.Header.Get("Authorization"))
	if err != nil {
		http.Error(w, "unauthorized", http.StatusUnauthorized)
		return
	}
	if !s.userRL.Allow(claims.Sub) {
		http.Error(w, "rate limit exceeded", http.StatusTooManyRequests)
		return
	}
	injectIdentity(r, claims)
	s.marketP.ServeHTTP(w, r)
}

func (s *Server) handleWS(w http.ResponseWriter, r *http.Request) {
	claims, err := s.jwt.ParseAccess(r.Header.Get("Authorization"))
	if err != nil {
		tok := r.URL.Query().Get("access_token")
		if tok == "" {
			http.Error(w, "unauthorized", http.StatusUnauthorized)
			return
		}
		claims, err = s.jwt.ParseAccess("Bearer " + tok)
		if err != nil {
			http.Error(w, "unauthorized", http.StatusUnauthorized)
			return
		}
	}
	if !s.userRL.Allow(claims.Sub) {
		http.Error(w, "rate limit exceeded", http.StatusTooManyRequests)
		return
	}
	injectIdentity(r, claims)
	s.ws.ServeHTTP(w, r)
}

func injectIdentity(r *http.Request, claims *auth.Claims) {
	r.Header.Del("X-User-Id")
	r.Header.Del("X-User-Admin")
	r.Header.Set("X-User-Id", claims.Sub)
	if claims.Admin {
		r.Header.Set("X-User-Admin", "true")
	}
	slog.Debug("identity injected", "user_id", claims.Sub, "admin", claims.Admin)
}
