package auth

import (
	"crypto/rsa"
	"errors"
	"fmt"
	"os"
	"strings"

	"github.com/golang-jwt/jwt/v5"
)

var (
	ErrMissingBearer = errors.New("missing bearer token")
	ErrInvalidToken  = errors.New("invalid token")
)

type Claims struct {
	Sub   string `json:"sub"`
	Sid   string `json:"sid"`
	Dev   string `json:"dev"`
	Type  string `json:"type"`
	Admin bool   `json:"admin"`
	jwt.RegisteredClaims
}

type Validator struct {
	key *rsa.PublicKey
}

func NewValidator(publicKeyPath string) (*Validator, error) {
	pemBytes, err := os.ReadFile(publicKeyPath)
	if err != nil {
		return nil, fmt.Errorf("read public key: %w", err)
	}
	key, err := jwt.ParseRSAPublicKeyFromPEM(pemBytes)
	if err != nil {
		return nil, fmt.Errorf("parse public key: %w", err)
	}
	return &Validator{key: key}, nil
}

// ParseAccess validates an access JWT and returns claims.
func (v *Validator) ParseAccess(authorizationHeader string) (*Claims, error) {
	raw, err := bearerToken(authorizationHeader)
	if err != nil {
		return nil, err
	}
	claims := &Claims{}
	token, err := jwt.ParseWithClaims(raw, claims, func(t *jwt.Token) (any, error) {
		if t.Method.Alg() != jwt.SigningMethodRS256.Alg() {
			return nil, fmt.Errorf("unexpected alg %s", t.Method.Alg())
		}
		return v.key, nil
	})
	if err != nil || !token.Valid {
		return nil, ErrInvalidToken
	}
	if !strings.EqualFold(claims.Type, "access") {
		return nil, ErrInvalidToken
	}
	if claims.Sub == "" {
		return nil, ErrInvalidToken
	}
	return claims, nil
}

func bearerToken(h string) (string, error) {
	h = strings.TrimSpace(h)
	if h == "" {
		return "", ErrMissingBearer
	}
	const prefix = "Bearer "
	if len(h) < len(prefix) || !strings.EqualFold(h[:len(prefix)], prefix) {
		return "", ErrMissingBearer
	}
	tok := strings.TrimSpace(h[len(prefix):])
	if tok == "" {
		return "", ErrMissingBearer
	}
	return tok, nil
}
