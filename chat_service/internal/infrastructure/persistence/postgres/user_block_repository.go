package postgres

import (
	"context"
	"database/sql"
	"errors"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

type UserBlockRepository struct {
	db DBTX
}

func NewUserBlockRepository(db DBTX) *UserBlockRepository {
	return &UserBlockRepository{db: db}
}

func (r *UserBlockRepository) Add(ctx context.Context, block *entities.UserBlock) error {
	row := userBlockToRow(block)
	_, err := r.db.ExecContext(ctx, `
		INSERT INTO user_blocks (blocker_id, blocked_id, created_at)
		VALUES ($1, $2, $3)
		ON CONFLICT (blocker_id, blocked_id) DO NOTHING`,
		row.BlockerID, row.BlockedID, row.CreatedAt,
	)
	return translateDBError("UserBlockRepository.Add", err)
}

func (r *UserBlockRepository) Remove(
	ctx context.Context,
	blockerID valueobjects.UserID,
	blockedID valueobjects.UserID,
) error {
	_, err := r.db.ExecContext(ctx, `
		DELETE FROM user_blocks WHERE blocker_id = $1 AND blocked_id = $2`,
		blockerID.String(), blockedID.String(),
	)
	return translateDBError("UserBlockRepository.Remove", err)
}

func (r *UserBlockRepository) Exists(
	ctx context.Context,
	blockerID valueobjects.UserID,
	blockedID valueobjects.UserID,
) (bool, error) {
	var one int
	err := r.db.QueryRowContext(ctx, `
		SELECT 1 FROM user_blocks WHERE blocker_id = $1 AND blocked_id = $2`,
		blockerID.String(), blockedID.String(),
	).Scan(&one)
	if errors.Is(err, sql.ErrNoRows) {
		return false, nil
	}
	if err != nil {
		return false, translateDBError("UserBlockRepository.Exists", err)
	}
	return true, nil
}

func (r *UserBlockRepository) IsBlockedEitherWay(
	ctx context.Context,
	userA valueobjects.UserID,
	userB valueobjects.UserID,
) (bool, error) {
	var one int
	err := r.db.QueryRowContext(ctx, `
		SELECT 1 FROM user_blocks
		WHERE (blocker_id = $1 AND blocked_id = $2)
		   OR (blocker_id = $2 AND blocked_id = $1)
		LIMIT 1`,
		userA.String(), userB.String(),
	).Scan(&one)
	if errors.Is(err, sql.ErrNoRows) {
		return false, nil
	}
	if err != nil {
		return false, translateDBError("UserBlockRepository.IsBlockedEitherWay", err)
	}
	return true, nil
}
