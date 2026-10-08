package postgres

import (
	"context"
	"database/sql"
	"errors"
	"strings"

	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
)

func translateDBError(op string, err error) error {
	if err == nil {
		return nil
	}
	if errors.Is(err, sql.ErrNoRows) {
		return err
	}
	if errors.Is(err, context.DeadlineExceeded) || errors.Is(err, context.Canceled) {
		return &domainerrors.DatabaseTimeoutError{
			Message: op + ": timeout",
			Err:     err,
		}
	}
	msg := err.Error()
	lower := strings.ToLower(msg)
	if strings.Contains(lower, "connection") || strings.Contains(lower, "connect") {
		return &domainerrors.DatabaseConnectionError{
			Message: op + ": " + msg,
			Err:     err,
		}
	}
	return &domainerrors.DatabaseOperationError{
		Message: op + ": " + msg,
		Err:     err,
	}
}
