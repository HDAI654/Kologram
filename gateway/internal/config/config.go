package config

import (
	"fmt"
	"os"
	"strconv"
	"strings"
	"time"
)

type Config struct {
	HTTPAddr string

	AuthURL   string
	MarketURL string
	ChatURL   string

	PublicKeyPath string

	CORSOrigin string

	// Rate limits (tokens per interval).
	PublicRPS   float64
	PublicBurst int
	AuthRPS     float64 // login/signup/forgot — stricter
	AuthBurst   int
	UserRPS     float64
	UserBurst   int
}

func Load() (Config, error) {
	cfg := Config{
		HTTPAddr:      getEnv("HTTP_ADDR", ":8000"),
		AuthURL:       strings.TrimRight(getEnv("AUTH_SERVICE_URL", "http://auth_service:8001"), "/"),
		MarketURL:     strings.TrimRight(getEnv("MARKET_SERVICE_URL", "http://market_service:8002"), "/"),
		ChatURL:       strings.TrimRight(getEnv("CHAT_SERVICE_URL", "http://chat_service:8080"), "/"),
		PublicKeyPath: getEnv("AUTH_PUBLIC_KEY_PATH", "/keys/public.pem"),
		CORSOrigin:    getEnv("CORS_ORIGIN", "http://localhost:3030"),
		PublicRPS:     30,
		PublicBurst:   60,
		AuthRPS:       5,
		AuthBurst:     10,
		UserRPS:       60,
		UserBurst:     120,
	}
	if v := os.Getenv("PUBLIC_RPS"); v != "" {
		f, err := strconv.ParseFloat(v, 64)
		if err != nil {
			return Config{}, fmt.Errorf("PUBLIC_RPS: %w", err)
		}
		cfg.PublicRPS = f
	}
	if v := os.Getenv("USER_RPS"); v != "" {
		f, err := strconv.ParseFloat(v, 64)
		if err != nil {
			return Config{}, fmt.Errorf("USER_RPS: %w", err)
		}
		cfg.UserRPS = f
	}
	_ = time.Second // keep time import stable if unused later
	return cfg, nil
}

func getEnv(k, def string) string {
	if v := strings.TrimSpace(os.Getenv(k)); v != "" {
		return v
	}
	return def
}
