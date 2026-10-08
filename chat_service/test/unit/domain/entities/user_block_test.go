package entities_test

import (
	"errors"
	"testing"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
)

func TestNewUserBlock_Success(t *testing.T) {
	t.Parallel()

	before := time.Now().UTC()
	block, err := entities.NewUserBlock(FixedBuyerID, FixedSellerID)
	after := time.Now().UTC()
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if block == nil {
		t.Fatalf("block is nil")
	}
	if !block.BlockerID.Equals(FixedBuyerID) {
		t.Fatalf("BlockerID mismatch")
	}
	if !block.BlockedID.Equals(FixedSellerID) {
		t.Fatalf("BlockedID mismatch")
	}
	if block.BlockedAt.Before(before) || block.BlockedAt.After(after) {
		t.Fatalf("BlockedAt = %v, want within [%v, %v]", block.BlockedAt, before, after)
	}
}

func TestNewUserBlock_RejectsSelf(t *testing.T) {
	t.Parallel()

	block, err := entities.NewUserBlock(FixedBuyerID, FixedBuyerID)

	if !errors.Is(err, domainerrors.ErrCannotBlockSelf) {
		t.Fatalf("err = %v, want ErrCannotBlockSelf", err)
	}
	if !errors.Is(err, domainerrors.ErrInvalidArgument) {
		t.Fatalf("err = %v, want category ErrInvalidArgument", err)
	}
	if block != nil {
		t.Fatalf("block = %v, want nil", block)
	}
}
