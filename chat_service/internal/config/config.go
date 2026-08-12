package config

import (
	"os"
	"strconv"
	"strings"
)

type Config struct {
	AppName          string
	HTTPAddr         string
	DatabaseURL      string
	RabbitMQEnabled  bool
	RabbitMQURL      string
	RabbitMQExchange string
}

func Load() Config {
	return Config{
		AppName:  getenv("APP_NAME", "Kologram"),
		HTTPAddr: getenv("HTTP_ADDR", ":8003"),
		DatabaseURL: getenv(
			"DATABASE_URL",
			"postgres://postgres:postgres@localhost:5432/chat?sslmode=disable",
		),
		RabbitMQEnabled:  getenvBool("RABBITMQ_ENABLED", false),
		RabbitMQURL:      getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/"),
		RabbitMQExchange: getenv("RABBITMQ_EXCHANGE", "chat.events"),
	}
}

func getenv(key, fallback string) string {
	if v := strings.TrimSpace(os.Getenv(key)); v != "" {
		return v
	}
	return fallback
}

func getenvBool(key string, fallback bool) bool {
	v := strings.ToLower(strings.TrimSpace(os.Getenv(key)))
	if v == "" {
		return fallback
	}
	b, err := strconv.ParseBool(v)
	if err != nil {
		return fallback
	}
	return b
}

// UsePostgres is true when DATABASE_URL targets PostgreSQL.
func (c Config) UsePostgres() bool {
	u := strings.ToLower(c.DatabaseURL)
	return strings.HasPrefix(u, "postgres://") || strings.HasPrefix(u, "postgresql://")
}
