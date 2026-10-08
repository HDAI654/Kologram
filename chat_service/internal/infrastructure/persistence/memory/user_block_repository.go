package memory

import (
	"context"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

type UserBlockRepository struct {
	store *Store
}

func NewUserBlockRepository(store *Store) *UserBlockRepository {
	return &UserBlockRepository{store: store}
}

func (r *UserBlockRepository) Add(ctx context.Context, block *entities.UserBlock) error {
	r.store.mu.Lock()
	defer r.store.mu.Unlock()
	r.store.Blocks[blockKey(block.BlockerID.String(), block.BlockedID.String())] = struct{}{}
	return nil
}

func (r *UserBlockRepository) Remove(
	ctx context.Context,
	blockerID valueobjects.UserID,
	blockedID valueobjects.UserID,
) error {
	r.store.mu.Lock()
	defer r.store.mu.Unlock()
	delete(r.store.Blocks, blockKey(blockerID.String(), blockedID.String()))
	return nil
}

func (r *UserBlockRepository) Exists(
	ctx context.Context,
	blockerID valueobjects.UserID,
	blockedID valueobjects.UserID,
) (bool, error) {
	r.store.mu.RLock()
	defer r.store.mu.RUnlock()
	_, ok := r.store.Blocks[blockKey(blockerID.String(), blockedID.String())]
	return ok, nil
}

func (r *UserBlockRepository) IsBlockedEitherWay(
	ctx context.Context,
	userA valueobjects.UserID,
	userB valueobjects.UserID,
) (bool, error) {
	r.store.mu.RLock()
	defer r.store.mu.RUnlock()
	_, ab := r.store.Blocks[blockKey(userA.String(), userB.String())]
	_, ba := r.store.Blocks[blockKey(userB.String(), userA.String())]
	return ab || ba, nil
}
