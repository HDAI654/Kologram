package postgres

import (
	"context"
	"database/sql"
	"time"

	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"

	_ "github.com/jackc/pgx/v5/stdlib" // PostgreSQL driver (database/sql)
)

// OpenDB opens a PostgreSQL pool via pgx stdlib. Caller owns Close.
// dsn example: postgres://user:pass@host:5432/chat?sslmode=disable
func OpenDB(ctx context.Context, dsn string) (*sql.DB, error) {
	db, err := sql.Open("pgx", dsn)
	if err != nil {
		return nil, &domainerrors.DatabaseConnectionError{
			Message: "open database",
			Err:     err,
		}
	}

	db.SetMaxOpenConns(25)
	db.SetMaxIdleConns(5)
	db.SetConnMaxLifetime(time.Hour)

	pingCtx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()
	if err := db.PingContext(pingCtx); err != nil {
		_ = db.Close()
		return nil, &domainerrors.DatabaseConnectionError{
			Message: "ping database",
			Err:     err,
		}
	}
	return db, nil
}
