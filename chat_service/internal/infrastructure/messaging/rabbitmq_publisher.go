package messaging

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/events"
	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	amqp "github.com/rabbitmq/amqp091-go"
)

const (
	defaultExchange     = "chat.events"
	defaultPublishTimeout = 5 * time.Second
)

// RabbitMQEventPublisher publishes domain events as JSON to a topic exchange.
// Delivery is best-effort (callers ignore failures after commit by design).
type RabbitMQEventPublisher struct {
	conn     *amqp.Connection
	channel  *amqp.Channel
	exchange string
	mu       sync.Mutex // amqp.Channel is not safe for concurrent Publish
}

// NewRabbitMQEventPublisher dials RabbitMQ, declares the exchange, and returns a publisher.
// amqpURL example: amqp://guest:guest@localhost:5672/
func NewRabbitMQEventPublisher(amqpURL, exchange string) (*RabbitMQEventPublisher, error) {
	if exchange == "" {
		exchange = defaultExchange
	}
	conn, err := amqp.Dial(amqpURL)
	if err != nil {
		return nil, &domainerrors.MessageBrokerError{
			Message: "dial rabbitmq",
			Err:     err,
		}
	}
	ch, err := conn.Channel()
	if err != nil {
		_ = conn.Close()
		return nil, &domainerrors.MessageBrokerError{
			Message: "open channel",
			Err:     err,
		}
	}
	if err := ch.ExchangeDeclare(
		exchange,
		"topic",
		true,  // durable
		false, // auto-delete
		false, // internal
		false, // no-wait
		nil,
	); err != nil {
		_ = ch.Close()
		_ = conn.Close()
		return nil, &domainerrors.MessageBrokerError{
			Message: "declare exchange",
			Err:     err,
		}
	}
	return &RabbitMQEventPublisher{
		conn:     conn,
		channel:  ch,
		exchange: exchange,
	}, nil
}

var _ ports.EventPublisher = (*RabbitMQEventPublisher)(nil)

type eventEnvelope struct {
	Type       string          `json:"type"`
	OccurredAt time.Time       `json:"occurred_at"`
	Payload    json.RawMessage `json:"payload"`
}

func (p *RabbitMQEventPublisher) Publish(ctx context.Context, evt events.DomainEvent) error {
	if p == nil || p.channel == nil {
		return &domainerrors.MessageBrokerError{Message: "publisher is closed"}
	}

	p.mu.Lock()
	defer p.mu.Unlock()

	payload, err := json.Marshal(evt)
	if err != nil {
		return &domainerrors.MessageBrokerError{
			Message: "marshal event",
			Err:     err,
		}
	}
	envelope, err := json.Marshal(eventEnvelope{
		Type:       evt.EventType(),
		OccurredAt: evt.OccurredAt().UTC(),
		Payload:    payload,
	})
	if err != nil {
		return &domainerrors.MessageBrokerError{
			Message: "marshal envelope",
			Err:     err,
		}
	}

	pubCtx := ctx
	cancel := func() {}
	if _, ok := ctx.Deadline(); !ok {
		pubCtx, cancel = context.WithTimeout(ctx, defaultPublishTimeout)
	}
	defer cancel()

	routingKey := evt.EventType()
	err = p.channel.PublishWithContext(
		pubCtx,
		p.exchange,
		routingKey,
		false, // mandatory
		false, // immediate
		amqp.Publishing{
			ContentType:  "application/json",
			DeliveryMode: amqp.Persistent,
			Timestamp:    evt.OccurredAt().UTC(),
			Type:         evt.EventType(),
			Body:         envelope,
		},
	)
	if err != nil {
		return &domainerrors.MessageBrokerError{
			Message: fmt.Sprintf("publish %s", evt.EventType()),
			Err:     err,
		}
	}
	return nil
}

// Close releases the channel and connection.
func (p *RabbitMQEventPublisher) Close() error {
	if p == nil {
		return nil
	}
	var first error
	if p.channel != nil {
		if err := p.channel.Close(); err != nil {
			first = err
		}
	}
	if p.conn != nil {
		if err := p.conn.Close(); err != nil && first == nil {
			first = err
		}
	}
	if first != nil {
		return &domainerrors.MessageBrokerError{Message: "close rabbitmq", Err: first}
	}
	return nil
}

// NoOpEventPublisher discards all events (tests / local without broker).
type NoOpEventPublisher struct{}

func NewNoOpEventPublisher() *NoOpEventPublisher { return &NoOpEventPublisher{} }

func (NoOpEventPublisher) Publish(ctx context.Context, evt events.DomainEvent) error {
	return nil
}

var _ ports.EventPublisher = NoOpEventPublisher{}
