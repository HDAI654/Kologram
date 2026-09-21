package valueobjects_test

import (
	"testing"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
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

			s, err := valueobjects.NewConversationStatus(tc.input)
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

			if _, err := valueobjects.NewConversationStatus(tc.input); err == nil {
				t.Fatalf("expected error for %q, got nil", tc.input)
			}
		})
	}
}

func TestConversationStatus_Equals(t *testing.T) {
	t.Parallel()

	if !valueobjects.StatusOpen.Equals(valueobjects.StatusOpen) {
		t.Fatalf("StatusOpen.Equals(StatusOpen) = false, want true")
	}
	if valueobjects.StatusOpen.Equals(valueobjects.StatusClosed) {
		t.Fatalf("StatusOpen.Equals(StatusClosed) = true, want false")
	}
	if valueobjects.StatusClosed.Equals(valueobjects.StatusArchived) {
		t.Fatalf("StatusClosed.Equals(StatusArchived) = true, want false")
	}
}

func TestConversationStatus_CanTransitionTo(t *testing.T) {
	t.Parallel()

	cases := []struct {
		name string
		from valueobjects.ConversationStatus
		to   valueobjects.ConversationStatus
		want bool
	}{
		{"open to open", valueobjects.StatusOpen, valueobjects.StatusOpen, false},
		{"open to closed", valueobjects.StatusOpen, valueobjects.StatusClosed, true},
		{"open to archived", valueobjects.StatusOpen, valueobjects.StatusArchived, true},

		{"closed to open", valueobjects.StatusClosed, valueobjects.StatusOpen, true},
		{"closed to closed", valueobjects.StatusClosed, valueobjects.StatusClosed, false},
		{"closed to archived", valueobjects.StatusClosed, valueobjects.StatusArchived, true},

		{"archived to open", valueobjects.StatusArchived, valueobjects.StatusOpen, false},
		{"archived to closed", valueobjects.StatusArchived, valueobjects.StatusClosed, false},
		{"archived to archived", valueobjects.StatusArchived, valueobjects.StatusArchived, false},
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
		status valueobjects.ConversationStatus
		want   bool
	}{
		{"open allows messages", valueobjects.StatusOpen, true},
		{"closed rejects messages", valueobjects.StatusClosed, false},
		{"archived rejects messages", valueobjects.StatusArchived, false},
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
