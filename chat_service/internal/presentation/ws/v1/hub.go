package v1

import (
	"context"
	"encoding/json"
	"sync"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
)

// MemoryHub tracks sessions by user ID and implements ports.RealtimeNotifier.
type MemoryHub struct {
	mu       sync.RWMutex
	sessions map[string]map[*Session]struct{}
}

func NewMemoryHub() *MemoryHub {
	return &MemoryHub{
		sessions: make(map[string]map[*Session]struct{}),
	}
}

func (h *MemoryHub) Register(s *Session) {
	if s == nil || s.UserID == "" {
		return
	}
	h.mu.Lock()
	defer h.mu.Unlock()
	set, ok := h.sessions[s.UserID]
	if !ok {
		set = make(map[*Session]struct{})
		h.sessions[s.UserID] = set
	}
	set[s] = struct{}{}
}

func (h *MemoryHub) Unregister(s *Session) {
	if s == nil || s.UserID == "" {
		return
	}
	h.mu.Lock()
	defer h.mu.Unlock()
	set, ok := h.sessions[s.UserID]
	if !ok {
		return
	}
	delete(set, s)
	if len(set) == 0 {
		delete(h.sessions, s.UserID)
	}
}

func (h *MemoryHub) NotifyUser(ctx context.Context, userID string, payload any) error {
	_ = ctx
	h.mu.RLock()
	set := h.sessions[userID]
	targets := make([]*Session, 0, len(set))
	for s := range set {
		targets = append(targets, s)
	}
	h.mu.RUnlock()

	if len(targets) == 0 {
		return nil
	}

	msg, err := encodePush(payload)
	if err != nil {
		return err
	}
	for _, s := range targets {
		_ = s.enqueue(msg) // ignores closed / full buffer
	}
	return nil
}

func encodePush(payload any) ([]byte, error) {
	if m, ok := payload.(map[string]any); ok {
		if _, hasType := m["type"]; hasType {
			return json.Marshal(m)
		}
	}
	return json.Marshal(Event{
		Type:    "realtime",
		Payload: payload,
	})
}

var _ Hub = (*MemoryHub)(nil)
var _ ports.RealtimeNotifier = (*MemoryHub)(nil)
