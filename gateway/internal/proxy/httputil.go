package proxy

import (
	"net/http"
	"net/http/httputil"
	"net/url"
	"strings"
)

func NewReverseProxy(target string) (*httputil.ReverseProxy, error) {
	u, err := url.Parse(target)
	if err != nil {
		return nil, err
	}
	p := httputil.NewSingleHostReverseProxy(u)
	orig := p.Director
	p.Director = func(r *http.Request) {
		orig(r)
		r.Host = u.Host
		// Gateway is the only source of identity headers.
		r.Header.Del("X-User-Id")
		r.Header.Del("X-User-Admin")
	}
	return p, nil
}

// JoinPath ensures a single slash between base path and suffix.
func JoinPath(a, b string) string {
	return strings.TrimRight(a, "/") + "/" + strings.TrimLeft(b, "/")
}
