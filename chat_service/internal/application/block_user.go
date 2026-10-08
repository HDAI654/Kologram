package application

import (
	"context"
	"log/slog"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

type BlockUserCommand struct {
	BlockerID string
	BlockedID string
}

type BlockUserResult struct {
	BlockerID string
	BlockedID string
}

type BlockUserHandler struct {
	uowFactory ports.UnitOfWorkFactory
	log        *slog.Logger
}

func NewBlockUserHandler(
	uowFactory ports.UnitOfWorkFactory,
	log *slog.Logger,
) *BlockUserHandler {
	return &BlockUserHandler{
		uowFactory: uowFactory,
		log:        loggerOrDefault(log),
	}
}

func (h *BlockUserHandler) Handle(
	ctx context.Context,
	cmd BlockUserCommand,
) (BlockUserResult, error) {
	blockerID, err := valueobjects.NewUserID(cmd.BlockerID)
	if err != nil {
		return BlockUserResult{}, err
	}
	blockedID, err := valueobjects.NewUserID(cmd.BlockedID)
	if err != nil {
		return BlockUserResult{}, err
	}

	block, err := entities.NewUserBlock(blockerID, blockedID)
	if err != nil {
		return BlockUserResult{}, err
	}

	uow, err := h.uowFactory.New(ctx)
	if err != nil {
		return BlockUserResult{}, err
	}
	defer func() { _ = uow.Rollback(ctx) }()

	if err := uow.UserBlocks().Add(ctx, block); err != nil {
		return BlockUserResult{}, err
	}
	if err := uow.Commit(ctx); err != nil {
		return BlockUserResult{}, err
	}

	h.log.Info("user blocked",
		"blocker_id", blockerID.String(),
		"blocked_id", blockedID.String(),
	)

	return BlockUserResult{
		BlockerID: blockerID.String(),
		BlockedID: blockedID.String(),
	}, nil
}
