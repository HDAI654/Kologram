package valueobject_test

import (
	"strings"
	"testing"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

func TestMessageContent(t *testing.T) {
	c, err := valueobject.NewMessageContent("  hello  ")
	if err != nil {
		t.Fatal(err)
	}
	if c.String() != "hello" {
		t.Fatalf("got %q", c.String())
	}
	if _, err := valueobject.NewMessageContent(""); err == nil {
		t.Fatal("expected empty error")
	}
	if _, err := valueobject.NewMessageContent(strings.Repeat("a", 4001)); err == nil {
		t.Fatal("expected max length error")
	}
	ok, err := valueobject.NewMessageContent(strings.Repeat("b", 4000))
	if err != nil {
		t.Fatal(err)
	}
	if len([]rune(ok.String())) != 4000 {
		t.Fatal("max should be accepted")
	}
}
