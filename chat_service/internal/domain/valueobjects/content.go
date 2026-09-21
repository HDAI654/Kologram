package valueobjects

import (
	"fmt"
	"strings"
	"unicode/utf8"

	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
)

const (
	minContentLen = 1
	maxContentLen = 4000
)

// MessageContent is validated chat message text.
type MessageContent struct {
	value string
}

func NewMessageContent(raw string) (MessageContent, error) {
	value := strings.TrimSpace(raw)
	length := utf8.RuneCountInString(value)
	if length < minContentLen || length > maxContentLen {
		return MessageContent{}, &domainerrors.ValidationError{
			Field: "content",
			Message: fmt.Sprintf(
				"length must be between %d and %d",
				minContentLen, maxContentLen,
			),
		}
	}
	return MessageContent{value: value}, nil
}

func (c MessageContent) String() string { return c.value }
