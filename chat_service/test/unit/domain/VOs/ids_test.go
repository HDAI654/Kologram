package valueobject_test

import (
	"testing"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobject"
)

func TestUserID(t *testing.T) {
	raw := "550e8400-e29b-41d4-a716-446655440001"
	uid, err := valueobject.NewUserID(raw)
	if err != nil {
		t.Fatal(err)
	}
	if uid.String() != raw {
		t.Fatalf("got %s", uid.String())
	}
	if !uid.Equals(uid) {
		t.Fatal("expected equal")
	}
	if _, err := valueobject.NewUserID(""); err == nil {
		t.Fatal("expected error")
	}
	if _, err := valueobject.NewUserID("not-a-uuid"); err == nil {
		t.Fatal("expected error")
	}
}

func TestConversationID(t *testing.T) {
	cid := valueobject.GenerateConversationID()
	if cid.String() == "" {
		t.Fatal("empty")
	}
	parsed, err := valueobject.NewConversationID(cid.String())
	if err != nil {
		t.Fatal(err)
	}
	if parsed.String() != cid.String() {
		t.Fatal("mismatch")
	}
}

func TestMessageID(t *testing.T) {
	mid := valueobject.GenerateMessageID()
	if mid.String() == "" {
		t.Fatal("empty")
	}
	if _, err := valueobject.NewMessageID("bad"); err == nil {
		t.Fatal("expected error")
	}
}

func TestListingID(t *testing.T) {
	raw := "550e8400-e29b-41d4-a716-446655440003"
	lid, err := valueobject.NewListingID(raw)
	if err != nil {
		t.Fatal(err)
	}
	if lid.String() != raw {
		t.Fatal("mismatch")
	}
}
