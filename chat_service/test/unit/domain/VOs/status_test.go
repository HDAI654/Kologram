package valueobject_test

import (
	"testing"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

func TestNewConversationStatus_Valid(t *testing.T) {
	t.Parallel()

	cases := []struct {
		name     string
		input    string
		expected string
	}{
		{"uppercase open", "OPEN", "OPEN"},
		{"lowercase open", "open", "OPEN"},
		{"mixed case open", "Open", "OPEN"},
		{"open with whitespace", "  OPEN  ", "OPEN"},
		{"lowercase closed with whitespace", " closed ", "CLOSED"},
		{"uppercase archived", "ARCHIVED", "ARCHIVED"},
		{"mixed case archived", "Archived", "ARCHIVED"},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			s, err := valueobject.NewConversationStatus(tc.input)
			if err != nil {
				t.Fatalf("NewConversationStatus(%q): unexpected error: %v", tc.input, err)
			}
			if got := s.String(); got != tc.expected {
				t.Fatalf("String() = %q, want %q", got, tc.expected)
			}
		})
	}
}

func TestNewConversationStatus_Invalid(t *testing.T) {
	t.Parallel()

	cases := []struct {
		name  string
		input string
	}{
		{"empty", ""},
		{"whitespace only", "   "},
		{"unknown value", "PENDING"},
		{"near miss", "OPENED"},
		{"trailing punctuation", "OPEN!"},
		{"numeric", "1"},
	}

	for _, tc := range cases {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			if _, err := valueobject.NewConversationStatus(tc.input); err == nil {
				t.Fatalf("expected error for %q, got nil", tc.input)
			}
		})
	}
}

func TestConversationStatus_Equals(t *testing.T) {
	t.Parallel()

	if !valueobject.StatusOpen.Equals(valueobject.StatusOpen) {
		t.Fatalf("StatusOpen.Equals(StatusOpen) = false, want true")
	}
	if valueobject.StatusOpen.Equals(valueobject.StatusClosed) {
		t.Fatalf("StatusOpen.Equals(StatusClosed) = true, want false")
	}
	if valueobject.StatusClosed.Equals(valueobject.StatusArchived) {
		t.Fatalf("StatusClosed.Equals(StatusArchived) = true, want false")
	}
}

func TestConversationStatus_CanTransitionTo(t *testing.T) {
	t.Parallel()

	cases := []struct {
		name string
		from valueobject.ConversationStatus
		to   valueobject.ConversationStatus
		want bool
	}{
		{"open to open", valueobject.StatusOpen, valueobject.StatusOpen, false},
		{"open to closed", valueobject.StatusOpen, valueobject.StatusClosed, true},
		{"open to archived", valueobject.StatusOpen, valueobject.StatusArchived, true},

		{"closed to open", valueobject.StatusClosed, valueobject.StatusOpen, true},
		{"closed to closed", valueobject.StatusClosed, valueobject.StatusClosed, false},
		{"closed to archived", valueobject.StatusClosed, valueobject.StatusArchived, true},

		{"archived to open", valueobject.StatusArchived, valueobject.StatusOpen, false},
		{"archived to closed", valueobject.StatusArchived, valueobject.StatusClosed, false},
		{"archived to archived", valueobject.StatusArchived, valueobject.StatusArchived, false},
	}

	for _, tc := range cases {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			if got := tc.from.CanTransitionTo(tc.to); got != tc.want {
				t.Fatalf("CanTransitionTo(%s, %s) = %v, want %v",
					tc.from.String(), tc.to.String(), got, tc.want)
			}
		})
	}
}

func TestConversationStatus_AllowsMessages(t *testing.T) {
	t.Parallel()

	cases := []struct {
		name   string
		status valueobject.ConversationStatus
		want   bool
	}{
		{"open allows messages", valueobject.StatusOpen, true},
		{"closed rejects messages", valueobject.StatusClosed, false},
		{"archived rejects messages", valueobject.StatusArchived, false},
	}

	for _, tc := range cases {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			if got := tc.status.AllowsMessages(); got != tc.want {
				t.Fatalf("AllowsMessages(%s) = %v, want %v",
					tc.status.String(), got, tc.want)
			}
		})
	}
}
