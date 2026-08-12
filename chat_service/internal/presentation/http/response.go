package httpapi

import (
	"encoding/json"
	"errors"
	"net/http"
	"strings"

	"github.com/HDAI654/Kologram/chat_service/internal/domain"
)

func writeJSON(w http.ResponseWriter, status int, payload any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(payload)
}

func writeError(w http.ResponseWriter, status int, detail string) {
	writeJSON(w, status, map[string]string{"detail": detail})
}

// mapError translates domain / value-object errors to standard HTTP status codes.
func mapError(w http.ResponseWriter, err error) {
	switch {
	case errors.Is(err, domain.ErrConversationNotFound),
		errors.Is(err, domain.ErrMessageNotFound):
		writeError(w, http.StatusNotFound, err.Error())
	case errors.Is(err, domain.ErrNotParticipant):
		writeError(w, http.StatusForbidden, err.Error())
	case errors.Is(err, domain.ErrConversationNotOpen),
		errors.Is(err, domain.ErrInvalidStatusTransition),
		errors.Is(err, domain.ErrBuyerSellerSame),
		errors.Is(err, domain.ErrConversationAlreadyExists):
		writeError(w, http.StatusConflict, err.Error())
	default:
		msg := err.Error()
		if strings.Contains(msg, "invalid") || strings.Contains(msg, "length must") {
			writeError(w, http.StatusUnprocessableEntity, msg)
			return
		}
		writeError(w, http.StatusInternalServerError, msg)
	}
}
