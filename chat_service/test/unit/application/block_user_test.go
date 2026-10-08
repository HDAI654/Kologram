package application_test

import (
	"context"
	"errors"
	"testing"

	"github.com/HDAI654/Kologram/chat_service/internal/application"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
)

func mustBlock(t *testing.T, blockerID, blockedID string) *entities.UserBlock {
	t.Helper()
	b, err := entities.NewUserBlock(mustUserID(t, blockerID), mustUserID(t, blockedID))
	if err != nil {
		t.Fatalf("NewUserBlock: %v", err)
	}
	return b
}

func TestBlockUser_Success(t *testing.T) {
	t.Parallel()

	_, _, _, blocks, uow, factory := NewFakeUowBundle()
	h := application.NewBlockUserHandler(factory, nil)

	result, err := h.Handle(context.Background(), application.BlockUserCommand{
		BlockerID: BuyerIDRaw,
		BlockedID: SellerIDRaw,
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result.BlockerID != BuyerIDRaw || result.BlockedID != SellerIDRaw {
		t.Fatalf("result mismatch: %+v", result)
	}
	if !uow.Committed {
		t.Fatalf("expected commit")
	}

	exists, err := blocks.Exists(context.Background(), mustUserID(t, BuyerIDRaw), mustUserID(t, SellerIDRaw))
	if err != nil || !exists {
		t.Fatalf("block not stored")
	}
}

func TestBlockUser_RejectsSelf(t *testing.T) {
	t.Parallel()

	_, _, _, _, _, factory := NewFakeUowBundle()
	h := application.NewBlockUserHandler(factory, nil)

	_, err := h.Handle(context.Background(), application.BlockUserCommand{
		BlockerID: BuyerIDRaw,
		BlockedID: BuyerIDRaw,
	})
	if !errors.Is(err, domainerrors.ErrCannotBlockSelf) {
		t.Fatalf("err = %v, want ErrCannotBlockSelf", err)
	}
}

func TestBlockUser_InvalidIDs(t *testing.T) {
	t.Parallel()

	_, _, _, _, _, factory := NewFakeUowBundle()
	h := application.NewBlockUserHandler(factory, nil)

	_, err := h.Handle(context.Background(), application.BlockUserCommand{
		BlockerID: "bad",
		BlockedID: SellerIDRaw,
	})
	if !errors.Is(err, domainerrors.ErrInvalidArgument) {
		t.Fatalf("err = %v, want ErrInvalidArgument", err)
	}
}

func TestBlockUser_CommitError(t *testing.T) {
	t.Parallel()

	_, _, _, _, uow, factory := NewFakeUowBundle()
	uow.CommitErr = errors.New("commit failed")
	h := application.NewBlockUserHandler(factory, nil)

	_, err := h.Handle(context.Background(), application.BlockUserCommand{
		BlockerID: BuyerIDRaw,
		BlockedID: SellerIDRaw,
	})
	if err == nil || err.Error() != "commit failed" {
		t.Fatalf("err = %v, want commit failed", err)
	}
}

func TestUnblockUser_Success(t *testing.T) {
	t.Parallel()

	_, _, _, blocks, uow, factory := NewFakeUowBundle()
	_ = blocks.Add(context.Background(), mustBlock(t, BuyerIDRaw, SellerIDRaw))

	h := application.NewUnblockUserHandler(factory, nil)
	result, err := h.Handle(context.Background(), application.UnblockUserCommand{
		BlockerID: BuyerIDRaw,
		BlockedID: SellerIDRaw,
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result.BlockerID != BuyerIDRaw {
		t.Fatalf("result mismatch")
	}
	if !uow.Committed {
		t.Fatalf("expected commit")
	}

	exists, _ := blocks.Exists(context.Background(), mustUserID(t, BuyerIDRaw), mustUserID(t, SellerIDRaw))
	if exists {
		t.Fatalf("block still present after unblock")
	}
}

func TestUnblockUser_NoOpWhenAbsent(t *testing.T) {
	t.Parallel()

	_, _, _, _, uow, factory := NewFakeUowBundle()
	h := application.NewUnblockUserHandler(factory, nil)

	_, err := h.Handle(context.Background(), application.UnblockUserCommand{
		BlockerID: BuyerIDRaw,
		BlockedID: SellerIDRaw,
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !uow.Committed {
		t.Fatalf("expected commit even when block absent")
	}
}

func TestUnblockUser_InvalidIDs(t *testing.T) {
	t.Parallel()

	_, _, _, _, _, factory := NewFakeUowBundle()
	h := application.NewUnblockUserHandler(factory, nil)

	_, err := h.Handle(context.Background(), application.UnblockUserCommand{
		BlockerID: BuyerIDRaw,
		BlockedID: "bad",
	})
	if !errors.Is(err, domainerrors.ErrInvalidArgument) {
		t.Fatalf("err = %v, want ErrInvalidArgument", err)
	}
}
