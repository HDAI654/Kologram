package application

import (
	"io"
	"log/slog"
)

// loggerOrDefault returns a discard logger when log is nil so handlers never
// depend on the process-wide default logger (keeps tests and libraries quiet).
func loggerOrDefault(log *slog.Logger) *slog.Logger {
	if log == nil {
		return slog.New(slog.NewTextHandler(io.Discard, nil))
	}
	return log
}
