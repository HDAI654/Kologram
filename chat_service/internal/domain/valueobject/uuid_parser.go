package valueobject

import (
	"fmt"

	"github.com/google/uuid"
)

func parseUUIDv4(raw string) (string, error) {
	if raw == "" {
		return "", fmt.Errorf("empty id")
	}
	parsed, err := uuid.Parse(raw)
	if err != nil {
		return "", err
	}
	if parsed.Version() != 4 {
		return "", fmt.Errorf("expected UUID v4")
	}
	return parsed.String(), nil
}
