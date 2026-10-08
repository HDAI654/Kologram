package valueobjects_test

import (
	"errors"
	"testing"

	"github.com/google/uuid"

	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

type idConstructor struct {
	name  string
	field string
	new   func(string) (string, error)
}

func idConstructors() []idConstructor {
	return []idConstructor{
		{
			name:  "ConversationID",
			field: "conversation_id",
			new: func(s string) (string, error) {
				v, err := valueobjects.NewConversationID(s)
				if err != nil {
					return "", err
				}
				return v.String(), nil
			},
		},
		{
			name:  "MessageID",
			field: "message_id",
			new: func(s string) (string, error) {
				v, err := valueobjects.NewMessageID(s)
				if err != nil {
					return "", err
				}
				return v.String(), nil
			},
		},
		{
			name:  "UserID",
			field: "user_id",
			new: func(s string) (string, error) {
				v, err := valueobjects.NewUserID(s)
				if err != nil {
					return "", err
				}
				return v.String(), nil
			},
		},
		{
			name:  "ListingID",
			field: "listing_id",
			new: func(s string) (string, error) {
				v, err := valueobjects.NewListingID(s)
				if err != nil {
					return "", err
				}
				return v.String(), nil
			},
		},
	}
}

func TestIDConstructors_Valid(t *testing.T) {
	t.Parallel()

	const canonical = "3bb6a3ca-66dc-440e-8d11-d8cca7ad7792"

	cases := []struct {
		name     string
		input    string
		expected string
	}{
		{"canonical lowercase", canonical, canonical},
		{"uppercase normalized to lowercase", "3BB6A3CA-66DC-440E-8D11-D8CCA7AD7792", canonical},
		{"brace-wrapped normalized", "{3bb6a3ca-66dc-440e-8d11-d8cca7ad7792}", canonical},
	}

	for _, ctor := range idConstructors() {
		for _, tc := range cases {
			t.Run(ctor.name+"/"+tc.name, func(t *testing.T) {
				t.Parallel()

				got, err := ctor.new(tc.input)
				if err != nil {
					t.Fatalf("unexpected error: %v", err)
				}
				if got != tc.expected {
					t.Fatalf("String() = %q, want %q", got, tc.expected)
				}
			})
		}
	}
}

func TestIDConstructors_Invalid(t *testing.T) {
	t.Parallel()

	cases := []struct {
		name  string
		input string
	}{
		{"empty", ""},
		{"whitespace only", "   "},
		{"not a uuid", "not-a-uuid"},
		{"too short", "3bb6a3ca-66dc-440e-8d11"},
		{"non-hex characters", "zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz"},
		{"uuid v1 rejected", "a8098c1a-f86e-11da-bd1a-00112444be1e"},
		{"uuid v3 rejected", "6fa459ea-ee8a-3ca4-894e-db77e160355e"},
		{"uuid v5 rejected", "886313e1-3b8a-5372-9b90-0c9aee199e5d"},
	}

	for _, ctor := range idConstructors() {
		for _, tc := range cases {
			t.Run(ctor.name+"/"+tc.name, func(t *testing.T) {
				t.Parallel()

				_, err := ctor.new(tc.input)
				if err == nil {
					t.Fatalf("expected error for %q, got nil", tc.input)
				}
				if !errors.Is(err, domainerrors.ErrInvalidArgument) {
					t.Fatalf("err = %v, want category ErrInvalidArgument", err)
				}
				var ve *domainerrors.ValidationError
				if !errors.As(err, &ve) {
					t.Fatalf("err = %v, want ValidationError", err)
				}
				if ve.Field != ctor.field {
					t.Fatalf("Field = %q, want %q", ve.Field, ctor.field)
				}
			})
		}
	}
}

func TestGenerateConversationID(t *testing.T) {
	t.Parallel()

	id := valueobjects.GenerateConversationID()
	parsed, err := uuid.Parse(id.String())
	if err != nil {
		t.Fatalf("GenerateConversationID produced unparseable id: %v", err)
	}
	if parsed.Version() != 4 {
		t.Fatalf("version = %d, want 4", parsed.Version())
	}

	other := valueobjects.GenerateConversationID()
	if id.String() == other.String() {
		t.Fatalf("two consecutive calls returned identical id: %s", id.String())
	}
}

func TestGenerateMessageID(t *testing.T) {
	t.Parallel()

	id := valueobjects.GenerateMessageID()
	parsed, err := uuid.Parse(id.String())
	if err != nil {
		t.Fatalf("GenerateMessageID produced unparseable id: %v", err)
	}
	if parsed.Version() != 4 {
		t.Fatalf("version = %d, want 4", parsed.Version())
	}

	other := valueobjects.GenerateMessageID()
	if id.String() == other.String() {
		t.Fatalf("two consecutive calls returned identical id: %s", id.String())
	}
}

func TestUserID_Equals(t *testing.T) {
	t.Parallel()

	const raw = "3bb6a3ca-66dc-440e-8d11-d8cca7ad7792"

	a, err := valueobjects.NewUserID(raw)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	b, err := valueobjects.NewUserID(raw)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !a.Equals(b) {
		t.Fatalf("Equals returned false for identical values")
	}

	c, err := valueobjects.NewUserID("a8098c1a-f86e-41da-bd1a-00112444be1e")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if a.Equals(c) {
		t.Fatalf("Equals returned true for distinct values")
	}
}
