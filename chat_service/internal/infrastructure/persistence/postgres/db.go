package postgres

import (
	"context"
	"database/sql"
)

// DBTX is satisfied by *sql.DB and *sql.Tx so repositories work inside a Unit of Work.
type DBTX interface {
	ExecContext(ctx context.Context, query string, args ...any) (sql.Result, error)
	QueryContext(ctx context.Context, query string, args ...any) (*sql.Rows, error)
	QueryRowContext(ctx context.Context, query string, args ...any) *sql.Row
}
