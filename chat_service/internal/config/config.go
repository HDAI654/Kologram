package config

import (
	"fmt"
	"os"
	"strconv"
	"strings"
	"time"
)

// Config holds process configuration loaded from environment variables.
// Required values are validated in Load; invalid config fails fast at startup.
type Config struct {
	// HTTP listen address for the chat service (used when Presentation is wired).
	HTTPAddr string

	// PostgreSQL DSN, e.g. postgres://user:pass@localhost:5432/chat?sslmode=disable
	DatabaseURL string

	// Market service origin (no trailing path), e.g. http://market:8080
	MarketServiceURL string

	// RabbitMQ AMQP URL, e.g. amqp://guest:guest@localhost:5672/
	RabbitMQURL string

	// Topic exchange for domain events.
	RabbitMQExchange string

	// Optional: use no-op event publisher instead of RabbitMQ (local/dev).
	EventPublisherNoOp bool

	// HTTP client timeout for outbound market calls.
	MarketHTTPTimeout time.Duration
}

// Load reads configuration from the environment.
//
// Required:
//   - DATABASE_URL
//   - MARKET_SERVICE_URL
//
// Optional:
//   - HTTP_ADDR (default :8080)
//   - RABBITMQ_URL (required unless EVENT_PUBLISHER=noop)
//   - RABBITMQ_EXCHANGE (default chat.events)
//   - EVENT_PUBLISHER (rabbitmq|noop, default rabbitmq)
//   - MARKET_HTTP_TIMEOUT (default 5s)
func Load() (Config, error) {
	cfg := Config{
		HTTPAddr:           getEnv("HTTP_ADDR", ":8080"),
		DatabaseURL:        strings.TrimSpace(os.Getenv("DATABASE_URL")),
		MarketServiceURL:   strings.TrimRight(strings.TrimSpace(os.Getenv("MARKET_SERVICE_URL")), "/"),
		RabbitMQURL:        strings.TrimSpace(os.Getenv("RABBITMQ_URL")),
		RabbitMQExchange:   getEnv("RABBITMQ_EXCHANGE", "chat.events"),
		EventPublisherNoOp: strings.EqualFold(getEnv("EVENT_PUBLISHER", "rabbitmq"), "noop"),
		MarketHTTPTimeout:  5 * time.Second,
	}

	if v := strings.TrimSpace(os.Getenv("MARKET_HTTP_TIMEOUT")); v != "" {
		d, err := time.ParseDuration(v)
		if err != nil {
			return Config{}, fmt.Errorf("MARKET_HTTP_TIMEOUT: %w", err)
		}
		if d <= 0 {
			return Config{}, fmt.Errorf("MARKET_HTTP_TIMEOUT must be positive")
		}
		cfg.MarketHTTPTimeout = d
	}

	if cfg.DatabaseURL == "" {
		return Config{}, fmt.Errorf("DATABASE_URL is required")
	}
	if cfg.MarketServiceURL == "" {
		return Config{}, fmt.Errorf("MARKET_SERVICE_URL is required")
	}
	if !cfg.EventPublisherNoOp && cfg.RabbitMQURL == "" {
		return Config{}, fmt.Errorf("RABBITMQ_URL is required when EVENT_PUBLISHER is not noop")
	}

	return cfg, nil
}

func getEnv(key, fallback string) string {
	if v := strings.TrimSpace(os.Getenv(key)); v != "" {
		return v
	}
	return fallback
}

// Bool helper kept for future flags without importing strconv at every call site.
func envBool(key string, fallback bool) bool {
	v := strings.TrimSpace(os.Getenv(key))
	if v == "" {
		return fallback
	}
	b, err := strconv.ParseBool(v)
	if err != nil {
		return fallback
	}
	return b
}
