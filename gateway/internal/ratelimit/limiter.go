package ratelimit

import (
	"net"
	"net/http"
	"strings"
	"sync"

	"golang.org/x/time/rate"
)

type Limiter struct {
	mu       sync.Mutex
	visitors map[string]*rate.Limiter
	r        rate.Limit
	b        int
}

func New(rps float64, burst int) *Limiter {
	return &Limiter{
		visitors: make(map[string]*rate.Limiter),
		r:        rate.Limit(rps),
		b:        burst,
	}
}

func (l *Limiter) Allow(key string) bool {
	l.mu.Lock()
	defer l.mu.Unlock()
	lim, ok := l.visitors[key]
	if !ok {
		lim = rate.NewLimiter(l.r, l.b)
		l.visitors[key] = lim
	}
	return lim.Allow()
}

func ClientIP(r *http.Request) string {
	if xff := r.Header.Get("X-Forwarded-For"); xff != "" {
		parts := strings.Split(xff, ",")
		return strings.TrimSpace(parts[0])
	}
	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		return r.RemoteAddr
	}
	return host
}
