package application

import (
	"context"
	"log/slog"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

type UnblockUserCommand struct {
	BlockerID string
	BlockedID string
}

type UnblockUserResult struct {
	BlockerID string
	BlockedID string
}

type UnblockUserHandler struct {
	uowFactory ports.UnitOfWorkFactory
	log        *slog.Logger
}

func NewUnblockUserHandler(
	uowFactory ports.UnitOfWorkFactory,
	log *slog.Logger,
) *UnblockUserHandler {
	return &UnblockUserHandler{
		uowFactory: uowFactory,
		log:        loggerOrDefault(log),
	}
}

func (h *UnblockUserHandler) Handle(
	ctx context.Context,
	cmd UnblockUserCommand,
) (UnblockUserResult, error) {
	blockerID, err := valueobjects.NewUserID(cmd.BlockerID)
	if err != nil {
		return UnblockUserResult{}, err
	}
	blockedID, err := valueobjects.NewUserID(cmd.BlockedID)
	if err != nil {
		return UnblockUserResult{}, err
	}

	uow, err := h.uowFactory.New(ctx)
	if err != nil {
		return UnblockUserResult{}, err
	}
	defer func() { _ = uow.Rollback(ctx) }()

	if err := uow.UserBlocks().Remove(ctx, blockerID, blockedID); err != nil {
		return UnblockUserResult{}, err
	}
	if err := uow.Commit(ctx); err != nil {
		return UnblockUserResult{}, err
	}

	h.log.Info("user unblocked",
		"blocker_id", blockerID.String(),
		"blocked_id", blockedID.String(),
	)

	return UnblockUserResult{
		BlockerID: blockerID.String(),
		BlockedID: blockedID.String(),
	}, nil
}
