package domainerrors

import (
	"errors"
	"fmt"
)

// Category for unexpected infrastructure failures.
var ErrInfrastructure = errors.New("infrastructure error")

// DatabaseConnectionError — cannot open or keep a connection.
type DatabaseConnectionError struct {
	Message string
	Err     error
}

func (e *DatabaseConnectionError) Error() string {
	if e.Message == "" {
		return "database connection failed"
	}
	return e.Message
}

func (e *DatabaseConnectionError) Unwrap() error {
	if e.Err != nil {
		return e.Err
	}
	return ErrInfrastructure
}

// DatabaseTimeoutError — query/statement exceeded deadline.
type DatabaseTimeoutError struct {
	Message string
	Err     error
}

func (e *DatabaseTimeoutError) Error() string {
	if e.Message == "" {
		return "database timeout"
	}
	return e.Message
}

func (e *DatabaseTimeoutError) Unwrap() error {
	if e.Err != nil {
		return e.Err
	}
	return ErrInfrastructure
}

// DatabaseOperationError — query/exec failed for a non-connection reason.
type DatabaseOperationError struct {
	Message string
	Err     error
}

func (e *DatabaseOperationError) Error() string {
	if e.Message == "" {
		return "database operation failed"
	}
	return e.Message
}

func (e *DatabaseOperationError) Unwrap() error {
	if e.Err != nil {
		return e.Err
	}
	return ErrInfrastructure
}

// MessageBrokerError — publish/consume failure (e.g. RabbitMQ).
type MessageBrokerError struct {
	Message string
	Err     error
}

func (e *MessageBrokerError) Error() string {
	if e.Message == "" {
		return "message broker error"
	}
	return e.Message
}

func (e *MessageBrokerError) Unwrap() error {
	if e.Err != nil {
		return e.Err
	}
	return ErrInfrastructure
}

// ExternalServiceError — outbound HTTP/GraphQL (e.g. market service).
type ExternalServiceError struct {
	Service string
	Message string
	Err     error
}

func (e *ExternalServiceError) Error() string {
	if e.Service == "" {
		return e.Message
	}
	if e.Message == "" {
		return fmt.Sprintf("%s: request failed", e.Service)
	}
	return fmt.Sprintf("%s: %s", e.Service, e.Message)
}

func (e *ExternalServiceError) Unwrap() error {
	if e.Err != nil {
		return e.Err
	}
	return ErrInfrastructure
}
