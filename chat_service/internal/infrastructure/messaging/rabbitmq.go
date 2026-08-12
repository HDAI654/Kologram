package messaging

import (
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
	"sync"
	"time"

	"cap/chat_service/internal/domain/event"

	amqp "github.com/rabbitmq/amqp091-go"
)

// RabbitMQEventPublisher publishes domain events to a durable topic exchange.
// Feature-flagged: only used when RABBITMQ_ENABLED=true.
type RabbitMQEventPublisher struct {
	url          string
	exchangeName string
	exchangeType string

	mu   sync.Mutex
	conn *amqp.Connection
	ch   *amqp.Channel
}

func NewRabbitMQEventPublisher(url, exchangeName string) *RabbitMQEventPublisher {
	return &RabbitMQEventPublisher{
		url:          url,
		exchangeName: exchangeName,
		exchangeType: "topic",
	}
}

// Connect opens the AMQP connection, channel, and declares the exchange.
func (p *RabbitMQEventPublisher) Connect(ctx context.Context) error {
	p.mu.Lock()
	defer p.mu.Unlock()

	slog.Info("connecting RabbitMQEventPublisher",
		"exchange", p.exchangeName,
		"type", p.exchangeType,
	)

	conn, err := amqp.Dial(p.url)
	if err != nil {
		slog.Error("failed to connect RabbitMQ", "error", err, "exchange", p.exchangeName)
		return fmt.Errorf("rabbitmq connect: %w", err)
	}
	ch, err := conn.Channel()
	if err != nil {
		_ = conn.Close()
		slog.Error("failed to open RabbitMQ channel", "error", err)
		return fmt.Errorf("rabbitmq channel: %w", err)
	}
	if err := ch.ExchangeDeclare(
		p.exchangeName,
		p.exchangeType,
		true,  // durable
		false, // auto-deleted
		false, // internal
		false, // no-wait
		nil,
	); err != nil {
		_ = ch.Close()
		_ = conn.Close()
		slog.Error("failed to declare exchange", "error", err, "exchange", p.exchangeName)
		return fmt.Errorf("rabbitmq declare exchange: %w", err)
	}

	p.conn = conn
	p.ch = ch
	slog.Info("RabbitMQEventPublisher connected",
		"exchange", p.exchangeName,
		"type", p.exchangeType,
	)
	return nil
}

// Close shuts down channel and connection.
func (p *RabbitMQEventPublisher) Close() error {
	p.mu.Lock()
	defer p.mu.Unlock()

	slog.Info("closing RabbitMQEventPublisher", "exchange", p.exchangeName)
	var firstErr error
	if p.ch != nil {
		if err := p.ch.Close(); err != nil && firstErr == nil {
			firstErr = err
			slog.Error("error closing RabbitMQ channel", "error", err)
		}
		p.ch = nil
	}
	if p.conn != nil {
		if err := p.conn.Close(); err != nil && firstErr == nil {
			firstErr = err
			slog.Error("error closing RabbitMQ connection", "error", err)
		}
		p.conn = nil
	}
	slog.Info("RabbitMQEventPublisher closed", "exchange", p.exchangeName)
	return firstErr
}

// Publish serializes the event and publishes it with persistent delivery.
func (p *RabbitMQEventPublisher) Publish(ctx context.Context, evt event.DomainEvent) error {
	p.mu.Lock()
	ch := p.ch
	p.mu.Unlock()

	eventType := evt.EventType()
	if ch == nil {
		slog.Error("publish rejected: publisher not connected", "event_type", eventType)
		return fmt.Errorf("rabbitmq publisher is not connected")
	}

	payload, err := serializeEvent(evt)
	if err != nil {
		return fmt.Errorf("serialize event: %w", err)
	}
	body, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("marshal event: %w", err)
	}

	routingKey := eventType
	slog.Info("publishing event",
		"event_type", eventType,
		"routing_key", routingKey,
		"exchange", p.exchangeName,
	)

	pubCtx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()

	err = ch.PublishWithContext(
		pubCtx,
		p.exchangeName,
		routingKey,
		false, // mandatory
		false, // immediate
		amqp.Publishing{
			ContentType:  "application/json",
			DeliveryMode: amqp.Persistent,
			Timestamp:    evt.OccurredAt(),
			Type:         eventType,
			Body:         body,
		},
	)
	if err != nil {
		slog.Error("failed to publish event",
			"event_type", eventType,
			"exchange", p.exchangeName,
			"error", err,
		)
		return fmt.Errorf("rabbitmq publish: %w", err)
	}

	slog.Info("published event",
		"event_type", eventType,
		"routing_key", routingKey,
		"exchange", p.exchangeName,
	)
	return nil
}

func serializeEvent(evt event.DomainEvent) (map[string]any, error) {
	// Marshal via JSON round-trip so struct fields become a generic map.
	raw, err := json.Marshal(evt)
	if err != nil {
		return nil, err
	}
	var payload map[string]any
	if err := json.Unmarshal(raw, &payload); err != nil {
		return nil, err
	}
	payload["event_type"] = evt.EventType()
	payload["occurred_at"] = evt.OccurredAt().UTC().Format(time.RFC3339Nano)
	return payload, nil
}
