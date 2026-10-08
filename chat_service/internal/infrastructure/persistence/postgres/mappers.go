package postgres

import (
	"fmt"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/persistence/postgres/models"
)

// --- Conversation ---

func conversationToRow(c *entities.Conversation) models.ConversationRow {
	row := models.ConversationRow{
		ID:                 c.ID.String(),
		BuyerID:            c.BuyerID.String(),
		SellerID:           c.SellerID.String(),
		ListingID:          c.ListingID.String(),
		IsReadOnly:         c.IsReadOnly,
		LastMessagePreview: c.LastMessagePreview,
		LastMessageAt:      c.LastMessageAt.UTC(),
		CreatedAt:          c.CreatedAt.UTC(),
		UpdatedAt:          c.UpdatedAt.UTC(),
	}
	if !c.LastMessageID.IsZero() {
		id := c.LastMessageID.String()
		row.LastMessageID = &id
	}
	return row
}

func conversationFromRow(row models.ConversationRow) (*entities.Conversation, error) {
	id, err := valueobjects.NewConversationID(row.ID)
	if err != nil {
		return nil, fmt.Errorf("conversation id: %w", err)
	}
	buyerID, err := valueobjects.NewUserID(row.BuyerID)
	if err != nil {
		return nil, fmt.Errorf("buyer id: %w", err)
	}
	sellerID, err := valueobjects.NewUserID(row.SellerID)
	if err != nil {
		return nil, fmt.Errorf("seller id: %w", err)
	}
	listingID, err := valueobjects.NewListingID(row.ListingID)
	if err != nil {
		return nil, fmt.Errorf("listing id: %w", err)
	}

	c := &entities.Conversation{
		ID:                 id,
		BuyerID:            buyerID,
		SellerID:           sellerID,
		ListingID:          listingID,
		IsReadOnly:         row.IsReadOnly,
		LastMessagePreview: row.LastMessagePreview,
		LastMessageAt:      row.LastMessageAt.UTC(),
		CreatedAt:          row.CreatedAt.UTC(),
		UpdatedAt:          row.UpdatedAt.UTC(),
	}
	if row.LastMessageID != nil && *row.LastMessageID != "" {
		mid, err := valueobjects.NewMessageID(*row.LastMessageID)
		if err != nil {
			return nil, fmt.Errorf("last message id: %w", err)
		}
		c.LastMessageID = mid
	}
	return c, nil
}

// --- ConversationUserState ---

func stateToRow(s *entities.ConversationUserState) models.ConversationUserStateRow {
	row := models.ConversationUserStateRow{
		ConversationID: s.ConversationID.String(),
		UserID:         s.UserID.String(),
		UnreadCount:    s.UnreadCount,
		IsArchived:     s.IsArchived,
		IsHidden:       s.IsHidden,
		IsPinned:       s.IsPinned,
		UpdatedAt:      s.UpdatedAt.UTC(),
	}
	if !s.LastReadMessageID.IsZero() {
		id := s.LastReadMessageID.String()
		row.LastReadMessageID = &id
	}
	if s.MutedUntil != nil {
		t := s.MutedUntil.UTC()
		row.MutedUntil = &t
	}
	return row
}

func stateFromRow(row models.ConversationUserStateRow) (*entities.ConversationUserState, error) {
	conversationID, err := valueobjects.NewConversationID(row.ConversationID)
	if err != nil {
		return nil, fmt.Errorf("conversation id: %w", err)
	}
	userID, err := valueobjects.NewUserID(row.UserID)
	if err != nil {
		return nil, fmt.Errorf("user id: %w", err)
	}

	s := &entities.ConversationUserState{
		ConversationID: conversationID,
		UserID:         userID,
		UnreadCount:    row.UnreadCount,
		IsArchived:     row.IsArchived,
		IsHidden:       row.IsHidden,
		IsPinned:       row.IsPinned,
		UpdatedAt:      row.UpdatedAt.UTC(),
	}
	if row.LastReadMessageID != nil && *row.LastReadMessageID != "" {
		mid, err := valueobjects.NewMessageID(*row.LastReadMessageID)
		if err != nil {
			return nil, fmt.Errorf("last read message id: %w", err)
		}
		s.LastReadMessageID = mid
	}
	if row.MutedUntil != nil {
		t := row.MutedUntil.UTC()
		s.MutedUntil = &t
	}
	return s, nil
}

// --- Message ---

func messageToRow(m *entities.Message) models.MessageRow {
	row := models.MessageRow{
		ID:                 m.ID.String(),
		ConversationID:     m.ConversationID.String(),
		SenderID:           m.SenderID.String(),
		Content:            m.Content.String(),
		SentAt:             m.SentAt.UTC(),
		ClientMessageID:    m.ClientMessageID,
		DeletedForEveryone: m.DeletedForEveryone,
	}
	if m.DeletedAt != nil {
		t := m.DeletedAt.UTC()
		row.DeletedAt = &t
	}
	return row
}

func messageFromRow(row models.MessageRow) (*entities.Message, error) {
	id, err := valueobjects.NewMessageID(row.ID)
	if err != nil {
		return nil, fmt.Errorf("message id: %w", err)
	}
	conversationID, err := valueobjects.NewConversationID(row.ConversationID)
	if err != nil {
		return nil, fmt.Errorf("conversation id: %w", err)
	}
	senderID, err := valueobjects.NewUserID(row.SenderID)
	if err != nil {
		return nil, fmt.Errorf("sender id: %w", err)
	}
	// Soft-deleted rows still store original content for admin/security.
	content, err := valueobjects.NewMessageContent(row.Content)
	if err != nil {
		return nil, fmt.Errorf("content: %w", err)
	}
	if err := valueobjects.ValidateClientMessageID(row.ClientMessageID); err != nil {
		return nil, fmt.Errorf("client message id: %w", err)
	}

	m := &entities.Message{
		ID:                 id,
		ConversationID:     conversationID,
		SenderID:           senderID,
		Content:            content,
		SentAt:             row.SentAt.UTC(),
		ClientMessageID:    row.ClientMessageID,
		DeletedForEveryone: row.DeletedForEveryone,
	}
	if row.DeletedAt != nil {
		t := row.DeletedAt.UTC()
		m.DeletedAt = &t
	}
	return m, nil
}

// --- UserBlock ---

func userBlockToRow(b *entities.UserBlock) models.UserBlockRow {
	return models.UserBlockRow{
		BlockerID: b.BlockerID.String(),
		BlockedID: b.BlockedID.String(),
		CreatedAt: b.BlockedAt.UTC(),
	}
}

func userBlockFromRow(row models.UserBlockRow) (*entities.UserBlock, error) {
	blockerID, err := valueobjects.NewUserID(row.BlockerID)
	if err != nil {
		return nil, fmt.Errorf("blocker id: %w", err)
	}
	blockedID, err := valueobjects.NewUserID(row.BlockedID)
	if err != nil {
		return nil, fmt.Errorf("blocked id: %w", err)
	}
	return &entities.UserBlock{
		BlockerID: blockerID,
		BlockedID: blockedID,
		BlockedAt: row.CreatedAt.UTC(),
	}, nil
}

// --- Conversation list projection ---

func conversationListItemFromRow(row models.ConversationListRow, now time.Time) (ports.ConversationListItem, error) {
	conversationID, err := valueobjects.NewConversationID(row.ConversationID)
	if err != nil {
		return ports.ConversationListItem{}, err
	}
	buyerID, err := valueobjects.NewUserID(row.BuyerID)
	if err != nil {
		return ports.ConversationListItem{}, err
	}
	sellerID, err := valueobjects.NewUserID(row.SellerID)
	if err != nil {
		return ports.ConversationListItem{}, err
	}
	listingID, err := valueobjects.NewListingID(row.ListingID)
	if err != nil {
		return ports.ConversationListItem{}, err
	}

	item := ports.ConversationListItem{
		ConversationID:     conversationID,
		BuyerID:            buyerID,
		SellerID:           sellerID,
		ListingID:          listingID,
		IsReadOnly:         row.IsReadOnly,
		LastMessagePreview: row.LastMessagePreview,
		LastMessageAt:      row.LastMessageAt.UTC(),
		CreatedAt:          row.CreatedAt.UTC(),
		UpdatedAt:          row.UpdatedAt.UTC(),
		UnreadCount:        row.UnreadCount,
		IsArchived:         row.IsArchived,
		IsPinned:           row.IsPinned,
		IsMuted:            row.MutedUntil != nil && now.Before(row.MutedUntil.UTC()),
	}
	return item, nil
}
