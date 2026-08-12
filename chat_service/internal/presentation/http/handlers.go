package httpapi

import (
	"encoding/json"
	"net/http"
	"strconv"

	"github.com/HDAI654/Kologram/chat_service/internal/application"
)

// Handlers is the thin HTTP presentation layer. It only parses, calls handlers, maps errors.
type Handlers struct {
	Start   *application.StartConversationHandler
	Send    *application.SendMessageHandler
	List    *application.ListConversationsHandler
	Get     *application.GetMessagesHandler
	Read    *application.MarkReadHandler
	Status  *application.ChangeStatusHandler
	AppName string
}

func (h *Handlers) Health(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, map[string]string{"status": "ok", "service": h.AppName})
}

// --- Conversations collection ---

type startConversationRequest struct {
	BuyerID   string `json:"buyer_id"`
	SellerID  string `json:"seller_id"`
	ListingID string `json:"listing_id"`
}

// StartConversation POST /api/v1/conversations
func (h *Handlers) StartConversation(w http.ResponseWriter, r *http.Request) {
	var req startConversationRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusUnprocessableEntity, "invalid JSON body")
		return
	}
	result, err := h.Start.Handle(r.Context(), application.StartConversationCommand{
		BuyerID: req.BuyerID, SellerID: req.SellerID, ListingID: req.ListingID,
	})
	if err != nil {
		mapError(w, err)
		return
	}
	status := http.StatusOK
	if result.Created {
		status = http.StatusCreated
	}
	writeJSON(w, status, result)
}

// ListConversations GET /api/v1/conversations?user_id=
func (h *Handlers) ListConversations(w http.ResponseWriter, r *http.Request) {
	userID := r.URL.Query().Get("user_id")
	if userID == "" {
		writeError(w, http.StatusUnprocessableEntity, "user_id is required")
		return
	}
	limit, _ := strconv.Atoi(r.URL.Query().Get("limit"))
	offset, _ := strconv.Atoi(r.URL.Query().Get("offset"))
	result, err := h.List.Handle(r.Context(), application.ListConversationsQuery{
		UserID: userID, Limit: limit, Offset: offset,
	})
	if err != nil {
		mapError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, result)
}

// --- Conversation resources ---

type sendMessageRequest struct {
	SenderID string `json:"sender_id"`
	Content  string `json:"content"`
}

// SendMessage POST /api/v1/conversations/{id}/messages
func (h *Handlers) SendMessage(w http.ResponseWriter, r *http.Request) {
	conversationID := r.PathValue("id")
	var req sendMessageRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusUnprocessableEntity, "invalid JSON body")
		return
	}
	result, err := h.Send.Handle(r.Context(), application.SendMessageCommand{
		ConversationID: conversationID,
		SenderID:       req.SenderID,
		Content:        req.Content,
	})
	if err != nil {
		mapError(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, result)
}

// GetMessages GET /api/v1/conversations/{id}/messages?requester_id=
func (h *Handlers) GetMessages(w http.ResponseWriter, r *http.Request) {
	conversationID := r.PathValue("id")
	requesterID := r.URL.Query().Get("requester_id")
	if requesterID == "" {
		writeError(w, http.StatusUnprocessableEntity, "requester_id is required")
		return
	}
	result, err := h.Get.Handle(r.Context(), application.GetMessagesQuery{
		ConversationID: conversationID,
		RequesterID:    requesterID,
	})
	if err != nil {
		mapError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, result)
}

type markReadRequest struct {
	ReaderID string `json:"reader_id"`
}

// MarkRead POST /api/v1/conversations/{id}/read
func (h *Handlers) MarkRead(w http.ResponseWriter, r *http.Request) {
	conversationID := r.PathValue("id")
	var req markReadRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusUnprocessableEntity, "invalid JSON body")
		return
	}
	result, err := h.Read.Handle(r.Context(), application.MarkReadCommand{
		ConversationID: conversationID,
		ReaderID:       req.ReaderID,
	})
	if err != nil {
		mapError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, result)
}

type changeStatusRequest struct {
	ActorID   string `json:"actor_id"`
	NewStatus string `json:"new_status"`
}

// ChangeStatus POST /api/v1/conversations/{id}/status
func (h *Handlers) ChangeStatus(w http.ResponseWriter, r *http.Request) {
	conversationID := r.PathValue("id")
	var req changeStatusRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusUnprocessableEntity, "invalid JSON body")
		return
	}
	result, err := h.Status.Handle(r.Context(), application.ChangeStatusCommand{
		ConversationID: conversationID,
		ActorID:        req.ActorID,
		NewStatus:      req.NewStatus,
	})
	if err != nil {
		mapError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, result)
}
