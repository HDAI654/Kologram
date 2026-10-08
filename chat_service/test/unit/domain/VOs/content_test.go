package valueobjects_test

import (
	"errors"
	"strings"
	"testing"

	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

func TestNewMessageContent_Valid(t *testing.T) {
	t.Parallel()

	maxAscii := strings.Repeat("a", 4000)
	maxMultibyte := strings.Repeat("😀", 4000)

	cases := []struct {
		name     string
		input    string
		expected string
	}{
		{"single ascii rune", "a", "a"},
		{"simple sentence", "hello world", "hello world"},
		{"min length boundary", "x", "x"},
		{"max length boundary ascii", maxAscii, maxAscii},
		{"max length boundary multibyte", maxMultibyte, maxMultibyte},
		{"trims leading whitespace", "   hello", "hello"},
		{"trims trailing whitespace", "hello   ", "hello"},
		{"trims both sides", "  hello  ", "hello"},
		{"trims tabs and newlines", "\t\nhello\n\t", "hello"},
		{"interior whitespace preserved", "hello   world", "hello   world"},
		{"unicode preserved", "héllo wörld", "héllo wörld"},
		{"emoji at min length", "👍", "👍"},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			c, err := valueobjects.NewMessageContent(tc.input)
			if err != nil {
				t.Fatalf("NewMessageContent(%q): unexpected error: %v", tc.input, err)
			}
			if got := c.String(); got != tc.expected {
				t.Fatalf("String() = %q, want %q", got, tc.expected)
			}
		})
	}
}

func TestNewMessageContent_Invalid(t *testing.T) {
	t.Parallel()

	overMaxAscii := strings.Repeat("a", 4001)
	overMaxMultibyte := strings.Repeat("😀", 4001)

	cases := []struct {
		name  string
		input string
	}{
		{"empty string", ""},
		{"whitespace only spaces", "   "},
		{"whitespace only tabs and newlines", "\t\n\r "},
		{"one ascii rune over max", overMaxAscii},
		{"one multibyte rune over max", overMaxMultibyte},
	}

	for _, tc := range cases {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			_, err := valueobjects.NewMessageContent(tc.input)
			if err == nil {
				t.Fatalf("NewMessageContent(%q): expected error, got nil", tc.input)
			}
			if !errors.Is(err, domainerrors.ErrInvalidArgument) {
				t.Fatalf("err = %v, want category ErrInvalidArgument", err)
			}
			var ve *domainerrors.ValidationError
			if !errors.As(err, &ve) {
				t.Fatalf("err = %v, want ValidationError", err)
			}
			if ve.Field != "content" {
				t.Fatalf("Field = %q, want content", ve.Field)
			}
		})
	}
}
