package valueobject_test

import (
	"testing"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

func TestConversationStatus(t *testing.T) {
	open, err := valueobject.NewConversationStatus("open")
	if err != nil {
		t.Fatal(err)
	}
	if open.String() != "OPEN" || !open.AllowsMessages() {
		t.Fatal(open.String())
	}
	if valueobject.StatusClosed.AllowsMessages() {
		t.Fatal("closed should not allow messages")
	}
	if !open.CanTransitionTo(valueobject.StatusClosed) {
		t.Fatal("OPEN -> CLOSED")
	}
	if open.CanTransitionTo(open) {
		t.Fatal("same status")
	}
	if valueobject.StatusArchived.CanTransitionTo(open) {
		t.Fatal("ARCHIVED terminal")
	}
	if _, err := valueobject.NewConversationStatus("NOPE"); err == nil {
		t.Fatal("expected invalid")
	}
}
