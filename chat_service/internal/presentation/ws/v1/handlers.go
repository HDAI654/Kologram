package v1

import (
	"context"
	"encoding/json"
	"errors"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/application"
	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
)

// Handlers holds application use-case handlers and registers WS actions on a Router.
type Handlers struct {
	StartConversation       *application.StartConversationHandler
	SendMessage             *application.SendMessageHandler
	ListMessages            *application.ListMessagesHandler
	ListConversations       *application.ListConversationsHandler
	GetConversation         *application.GetConversationHandler
	MarkConversationRead    *application.MarkConversationReadHandler
	DeleteMessageForEveryone *application.DeleteMessageForEveryoneHandler
	ArchiveConversation     *application.ArchiveConversationHandler
	HideConversation        *application.HideConversationHandler
	PinConversation         *application.PinConversationHandler
	MuteConversation        *application.MuteConversationHandler
	BlockUser               *application.BlockUserHandler
	UnblockUser             *application.UnblockUserHandler
	MarkListingUnavailable  *application.MarkListingUnavailableHandler
}

func (h *Handlers) Register(r *Router) {
	r.Register(TypeStartConversation, h.handleStartConversation)
	r.Register(TypeSendMessage, h.handleSendMessage)
	r.Register(TypeListMessages, h.handleListMessages)
	r.Register(TypeListConversations, h.handleListConversations)
	r.Register(TypeGetConversation, h.handleGetConversation)
	r.Register(TypeMarkConversationRead, h.handleMarkConversationRead)
	r.Register(TypeDeleteMessageForEveryone, h.handleDeleteMessageForEveryone)
	r.Register(TypeArchiveConversation, h.handleArchiveConversation)
	r.Register(TypeHideConversation, h.handleHideConversation)
	r.Register(TypePinConversation, h.handlePinConversation)
	r.Register(TypeMuteConversation, h.handleMuteConversation)
	r.Register(TypeBlockUser, h.handleBlockUser)
	r.Register(TypeUnblockUser, h.handleUnblockUser)
	r.RegisterAdmin(TypeMarkListingUnavailable, h.handleMarkListingUnavailable)
}

func decodePayload[T any](raw json.RawMessage, dst *T) error {
	if len(raw) == 0 {
		return errors.New("payload is required")
	}
	return json.Unmarshal(raw, dst)
}

func (h *Handlers) handleStartConversation(ctx context.Context, userID string, req Request) Response {
	respType := TypeStartConversationResult
	var p StartConversationPayload
	if err := decodePayload(req.Payload, &p); err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: &ErrorBody{Code: CodeInvalidRequest, Message: "invalid payload"}}
	}
	result, err := h.StartConversation.Handle(ctx, application.StartConversationCommand{
		BuyerID:   userID,
		ListingID: p.ListingID,
	})
	if err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: mapStartConversationError(err)}
	}
	return Response{ID: req.ID, Type: respType, OK: true, Payload: toPayload(result)}
}

func mapStartConversationError(err error) *ErrorBody {
	var ve *domainerrors.ValidationError
	if errors.As(err, &ve) {
		return &ErrorBody{Code: CodeValidation, Message: ve.Error(), Field: ve.Field}
	}
	var nf *domainerrors.NotFoundError
	if errors.As(err, &nf) {
		return &ErrorBody{Code: CodeNotFound, Message: nf.Error(), Field: nf.Field}
	}
	switch {
	case errors.Is(err, domainerrors.ErrInvalidArgument):
		return &ErrorBody{Code: CodeValidation, Message: err.Error()}
	case errors.Is(err, domainerrors.ErrBuyerSellerSame):
		return &ErrorBody{Code: CodeValidation, Message: err.Error()}
	case errors.Is(err, domainerrors.ErrListingNotMessageable):
		return &ErrorBody{Code: CodeConflict, Message: err.Error()}
	case errors.Is(err, domainerrors.ErrUsersBlocked):
		return &ErrorBody{Code: CodeForbidden, Message: err.Error()}
	default:
		return &ErrorBody{Code: CodeInternal, Message: "internal error"}
	}
}

func (h *Handlers) handleSendMessage(ctx context.Context, userID string, req Request) Response {
	respType := TypeSendMessageResult
	var p SendMessagePayload
	if err := decodePayload(req.Payload, &p); err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: &ErrorBody{Code: CodeInvalidRequest, Message: "invalid payload"}}
	}
	result, err := h.SendMessage.Handle(ctx, application.SendMessageCommand{
		ConversationID:  p.ConversationID,
		SenderID:        userID,
		ClientMessageID: p.ClientMessageID,
		Content:         p.Content,
	})
	if err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: mapSendMessageError(err)}
	}
	return Response{ID: req.ID, Type: respType, OK: true, Payload: toPayload(result)}
}

func mapSendMessageError(err error) *ErrorBody {
	var ve *domainerrors.ValidationError
	if errors.As(err, &ve) {
		return &ErrorBody{Code: CodeValidation, Message: ve.Error(), Field: ve.Field}
	}
	var nf *domainerrors.NotFoundError
	if errors.As(err, &nf) {
		return &ErrorBody{Code: CodeNotFound, Message: nf.Error(), Field: nf.Field}
	}
	switch {
	case errors.Is(err, domainerrors.ErrInvalidArgument):
		return &ErrorBody{Code: CodeValidation, Message: err.Error()}
	case errors.Is(err, domainerrors.ErrNotParticipant):
		return &ErrorBody{Code: CodeForbidden, Message: err.Error()}
	case errors.Is(err, domainerrors.ErrUsersBlocked):
		return &ErrorBody{Code: CodeForbidden, Message: err.Error()}
	case errors.Is(err, domainerrors.ErrConversationNotOpen):
		return &ErrorBody{Code: CodeConflict, Message: err.Error()}
	default:
		return &ErrorBody{Code: CodeInternal, Message: "internal error"}
	}
}

func (h *Handlers) handleListMessages(ctx context.Context, userID string, req Request) Response {
	respType := TypeListMessagesResult
	var p ListMessagesPayload
	if err := decodePayload(req.Payload, &p); err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: &ErrorBody{Code: CodeInvalidRequest, Message: "invalid payload"}}
	}
	result, err := h.ListMessages.Handle(ctx, application.ListMessagesQuery{
		ConversationID:  p.ConversationID,
		RequesterID:     userID,
		CursorMessageID: p.CursorMessageID,
		CursorSentAt:    p.CursorSentAt,
		Direction:       p.Direction,
		Limit:           p.Limit,
	})
	if err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: mapListMessagesError(err)}
	}
	return Response{ID: req.ID, Type: respType, OK: true, Payload: toPayload(result)}
}

func mapListMessagesError(err error) *ErrorBody {
	var ve *domainerrors.ValidationError
	if errors.As(err, &ve) {
		return &ErrorBody{Code: CodeValidation, Message: ve.Error(), Field: ve.Field}
	}
	var nf *domainerrors.NotFoundError
	if errors.As(err, &nf) {
		return &ErrorBody{Code: CodeNotFound, Message: nf.Error(), Field: nf.Field}
	}
	switch {
	case errors.Is(err, domainerrors.ErrInvalidArgument):
		return &ErrorBody{Code: CodeValidation, Message: err.Error()}
	case errors.Is(err, domainerrors.ErrNotParticipant):
		return &ErrorBody{Code: CodeForbidden, Message: err.Error()}
	default:
		return &ErrorBody{Code: CodeInternal, Message: "internal error"}
	}
}

func (h *Handlers) handleListConversations(ctx context.Context, userID string, req Request) Response {
	respType := TypeListConversationsResult
	var p ListConversationsPayload
	if len(req.Payload) > 0 {
		if err := json.Unmarshal(req.Payload, &p); err != nil {
			return Response{ID: req.ID, Type: respType, OK: false, Error: &ErrorBody{Code: CodeInvalidRequest, Message: "invalid payload"}}
		}
	}
	q := application.ListConversationsQuery{
		UserID:              userID,
		Filter:              p.Filter,
		CursorID:            p.CursorID,
		CursorLastMessageAt: p.CursorLastMessageAt,
		Limit:               p.Limit,
	}
	if p.CursorIsPinned != nil {
		q.CursorIsPinned = p.CursorIsPinned
	}
	result, err := h.ListConversations.Handle(ctx, q)
	if err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: mapListConversationsError(err)}
	}
	return Response{ID: req.ID, Type: respType, OK: true, Payload: toPayload(result)}
}

func mapListConversationsError(err error) *ErrorBody {
	var ve *domainerrors.ValidationError
	if errors.As(err, &ve) {
		return &ErrorBody{Code: CodeValidation, Message: ve.Error(), Field: ve.Field}
	}
	if errors.Is(err, domainerrors.ErrInvalidArgument) {
		return &ErrorBody{Code: CodeValidation, Message: err.Error()}
	}
	return &ErrorBody{Code: CodeInternal, Message: "internal error"}
}

func (h *Handlers) handleGetConversation(ctx context.Context, userID string, req Request) Response {
	respType := TypeGetConversationResult
	var p GetConversationPayload
	if err := decodePayload(req.Payload, &p); err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: &ErrorBody{Code: CodeInvalidRequest, Message: "invalid payload"}}
	}
	result, err := h.GetConversation.Handle(ctx, application.GetConversationQuery{
		ConversationID: p.ConversationID,
		RequesterID:    userID,
	})
	if err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: mapGetConversationError(err)}
	}
	return Response{ID: req.ID, Type: respType, OK: true, Payload: toPayload(result)}
}

func mapGetConversationError(err error) *ErrorBody {
	var ve *domainerrors.ValidationError
	if errors.As(err, &ve) {
		return &ErrorBody{Code: CodeValidation, Message: ve.Error(), Field: ve.Field}
	}
	var nf *domainerrors.NotFoundError
	if errors.As(err, &nf) {
		return &ErrorBody{Code: CodeNotFound, Message: nf.Error(), Field: nf.Field}
	}
	switch {
	case errors.Is(err, domainerrors.ErrInvalidArgument):
		return &ErrorBody{Code: CodeValidation, Message: err.Error()}
	case errors.Is(err, domainerrors.ErrNotParticipant):
		return &ErrorBody{Code: CodeForbidden, Message: err.Error()}
	default:
		return &ErrorBody{Code: CodeInternal, Message: "internal error"}
	}
}

func (h *Handlers) handleMarkConversationRead(ctx context.Context, userID string, req Request) Response {
	respType := TypeMarkConversationReadResult
	var p MarkConversationReadPayload
	if err := decodePayload(req.Payload, &p); err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: &ErrorBody{Code: CodeInvalidRequest, Message: "invalid payload"}}
	}
	result, err := h.MarkConversationRead.Handle(ctx, application.MarkConversationReadCommand{
		ConversationID:    p.ConversationID,
		UserID:            userID,
		LastReadMessageID: p.LastReadMessageID,
	})
	if err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: mapMarkReadError(err)}
	}
	return Response{ID: req.ID, Type: respType, OK: true, Payload: toPayload(result)}
}

func mapMarkReadError(err error) *ErrorBody {
	var ve *domainerrors.ValidationError
	if errors.As(err, &ve) {
		return &ErrorBody{Code: CodeValidation, Message: ve.Error(), Field: ve.Field}
	}
	var nf *domainerrors.NotFoundError
	if errors.As(err, &nf) {
		return &ErrorBody{Code: CodeNotFound, Message: nf.Error(), Field: nf.Field}
	}
	switch {
	case errors.Is(err, domainerrors.ErrInvalidArgument):
		return &ErrorBody{Code: CodeValidation, Message: err.Error()}
	case errors.Is(err, domainerrors.ErrNotParticipant):
		return &ErrorBody{Code: CodeForbidden, Message: err.Error()}
	default:
		return &ErrorBody{Code: CodeInternal, Message: "internal error"}
	}
}

func (h *Handlers) handleDeleteMessageForEveryone(ctx context.Context, userID string, req Request) Response {
	respType := TypeDeleteMessageForEveryoneResult
	var p DeleteMessageForEveryonePayload
	if err := decodePayload(req.Payload, &p); err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: &ErrorBody{Code: CodeInvalidRequest, Message: "invalid payload"}}
	}
	result, err := h.DeleteMessageForEveryone.Handle(ctx, application.DeleteMessageForEveryoneCommand{
		MessageID: p.MessageID,
		ActorID:   userID,
	})
	if err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: mapDeleteMessageError(err)}
	}
	return Response{ID: req.ID, Type: respType, OK: true, Payload: toPayload(result)}
}

func mapDeleteMessageError(err error) *ErrorBody {
	var ve *domainerrors.ValidationError
	if errors.As(err, &ve) {
		return &ErrorBody{Code: CodeValidation, Message: ve.Error(), Field: ve.Field}
	}
	var nf *domainerrors.NotFoundError
	if errors.As(err, &nf) {
		return &ErrorBody{Code: CodeNotFound, Message: nf.Error(), Field: nf.Field}
	}
	switch {
	case errors.Is(err, domainerrors.ErrInvalidArgument):
		return &ErrorBody{Code: CodeValidation, Message: err.Error()}
	case errors.Is(err, domainerrors.ErrNotParticipant):
		return &ErrorBody{Code: CodeForbidden, Message: err.Error()}
	case errors.Is(err, domainerrors.ErrNotMessageAuthor):
		return &ErrorBody{Code: CodeForbidden, Message: err.Error()}
	case errors.Is(err, domainerrors.ErrDeleteWindowExpired):
		return &ErrorBody{Code: CodeConflict, Message: err.Error()}
	default:
		return &ErrorBody{Code: CodeInternal, Message: "internal error"}
	}
}

func (h *Handlers) handleArchiveConversation(ctx context.Context, userID string, req Request) Response {
	respType := TypeArchiveConversationResult
	var p ArchiveConversationPayload
	if err := decodePayload(req.Payload, &p); err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: &ErrorBody{Code: CodeInvalidRequest, Message: "invalid payload"}}
	}
	result, err := h.ArchiveConversation.Handle(ctx, application.ArchiveConversationCommand{
		ConversationID: p.ConversationID,
		UserID:         userID,
		Archive:        p.Archive,
	})
	if err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: mapStateActionError(err)}
	}
	return Response{ID: req.ID, Type: respType, OK: true, Payload: toPayload(result)}
}

func (h *Handlers) handleHideConversation(ctx context.Context, userID string, req Request) Response {
	respType := TypeHideConversationResult
	var p HideConversationPayload
	if err := decodePayload(req.Payload, &p); err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: &ErrorBody{Code: CodeInvalidRequest, Message: "invalid payload"}}
	}
	result, err := h.HideConversation.Handle(ctx, application.HideConversationCommand{
		ConversationID: p.ConversationID,
		UserID:         userID,
		Hide:           p.Hide,
	})
	if err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: mapStateActionError(err)}
	}
	return Response{ID: req.ID, Type: respType, OK: true, Payload: toPayload(result)}
}

func (h *Handlers) handlePinConversation(ctx context.Context, userID string, req Request) Response {
	respType := TypePinConversationResult
	var p PinConversationPayload
	if err := decodePayload(req.Payload, &p); err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: &ErrorBody{Code: CodeInvalidRequest, Message: "invalid payload"}}
	}
	result, err := h.PinConversation.Handle(ctx, application.PinConversationCommand{
		ConversationID: p.ConversationID,
		UserID:         userID,
		Pin:            p.Pin,
	})
	if err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: mapStateActionError(err)}
	}
	return Response{ID: req.ID, Type: respType, OK: true, Payload: toPayload(result)}
}

func (h *Handlers) handleMuteConversation(ctx context.Context, userID string, req Request) Response {
	respType := TypeMuteConversationResult
	var p MuteConversationPayload
	if err := decodePayload(req.Payload, &p); err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: &ErrorBody{Code: CodeInvalidRequest, Message: "invalid payload"}}
	}
	cmd := application.MuteConversationCommand{
		ConversationID: p.ConversationID,
		UserID:         userID,
		Mute:           p.Mute,
	}
	if p.Mute && p.Until != nil && *p.Until != "" {
		t, err := time.Parse(time.RFC3339, *p.Until)
		if err != nil {
			return Response{ID: req.ID, Type: respType, OK: false, Error: &ErrorBody{Code: CodeValidation, Message: "until must be RFC3339", Field: "until"}}
		}
		utc := t.UTC()
		cmd.Until = &utc
	}
	result, err := h.MuteConversation.Handle(ctx, cmd)
	if err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: mapMuteError(err)}
	}
	return Response{ID: req.ID, Type: respType, OK: true, Payload: toPayload(result)}
}

func mapMuteError(err error) *ErrorBody {
	var ve *domainerrors.ValidationError
	if errors.As(err, &ve) {
		return &ErrorBody{Code: CodeValidation, Message: ve.Error(), Field: ve.Field}
	}
	var nf *domainerrors.NotFoundError
	if errors.As(err, &nf) {
		return &ErrorBody{Code: CodeNotFound, Message: nf.Error(), Field: nf.Field}
	}
	switch {
	case errors.Is(err, domainerrors.ErrInvalidArgument):
		return &ErrorBody{Code: CodeValidation, Message: err.Error()}
	case errors.Is(err, domainerrors.ErrNotParticipant):
		return &ErrorBody{Code: CodeForbidden, Message: err.Error()}
	default:
		return &ErrorBody{Code: CodeInternal, Message: "internal error"}
	}
}

// mapStateActionError is used only by archive/hide/pin (same domain outcomes).
func mapStateActionError(err error) *ErrorBody {
	var ve *domainerrors.ValidationError
	if errors.As(err, &ve) {
		return &ErrorBody{Code: CodeValidation, Message: ve.Error(), Field: ve.Field}
	}
	var nf *domainerrors.NotFoundError
	if errors.As(err, &nf) {
		return &ErrorBody{Code: CodeNotFound, Message: nf.Error(), Field: nf.Field}
	}
	switch {
	case errors.Is(err, domainerrors.ErrInvalidArgument):
		return &ErrorBody{Code: CodeValidation, Message: err.Error()}
	case errors.Is(err, domainerrors.ErrNotParticipant):
		return &ErrorBody{Code: CodeForbidden, Message: err.Error()}
	default:
		return &ErrorBody{Code: CodeInternal, Message: "internal error"}
	}
}

func (h *Handlers) handleBlockUser(ctx context.Context, userID string, req Request) Response {
	respType := TypeBlockUserResult
	var p BlockUserPayload
	if err := decodePayload(req.Payload, &p); err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: &ErrorBody{Code: CodeInvalidRequest, Message: "invalid payload"}}
	}
	result, err := h.BlockUser.Handle(ctx, application.BlockUserCommand{
		BlockerID: userID,
		BlockedID: p.BlockedID,
	})
	if err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: mapBlockError(err)}
	}
	return Response{ID: req.ID, Type: respType, OK: true, Payload: toPayload(result)}
}

func mapBlockError(err error) *ErrorBody {
	var ve *domainerrors.ValidationError
	if errors.As(err, &ve) {
		return &ErrorBody{Code: CodeValidation, Message: ve.Error(), Field: ve.Field}
	}
	switch {
	case errors.Is(err, domainerrors.ErrInvalidArgument):
		return &ErrorBody{Code: CodeValidation, Message: err.Error()}
	case errors.Is(err, domainerrors.ErrCannotBlockSelf):
		return &ErrorBody{Code: CodeValidation, Message: err.Error()}
	default:
		return &ErrorBody{Code: CodeInternal, Message: "internal error"}
	}
}

func (h *Handlers) handleUnblockUser(ctx context.Context, userID string, req Request) Response {
	respType := TypeUnblockUserResult
	var p UnblockUserPayload
	if err := decodePayload(req.Payload, &p); err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: &ErrorBody{Code: CodeInvalidRequest, Message: "invalid payload"}}
	}
	result, err := h.UnblockUser.Handle(ctx, application.UnblockUserCommand{
		BlockerID: userID,
		BlockedID: p.BlockedID,
	})
	if err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: mapUnblockError(err)}
	}
	return Response{ID: req.ID, Type: respType, OK: true, Payload: toPayload(result)}
}

func mapUnblockError(err error) *ErrorBody {
	if errors.Is(err, domainerrors.ErrInvalidArgument) {
		return &ErrorBody{Code: CodeValidation, Message: err.Error()}
	}
	var ve *domainerrors.ValidationError
	if errors.As(err, &ve) {
		return &ErrorBody{Code: CodeValidation, Message: ve.Error(), Field: ve.Field}
	}
	return &ErrorBody{Code: CodeInternal, Message: "internal error"}
}

func (h *Handlers) handleMarkListingUnavailable(ctx context.Context, userID string, isAdmin bool, req Request) Response {
	respType := TypeMarkListingUnavailableResult
	if !isAdmin {
		return Response{ID: req.ID, Type: respType, OK: false, Error: &ErrorBody{Code: CodeForbidden, Message: "admin required"}}
	}
	var p MarkListingUnavailablePayload
	if err := decodePayload(req.Payload, &p); err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: &ErrorBody{Code: CodeInvalidRequest, Message: "invalid payload"}}
	}
	_ = userID
	result, err := h.MarkListingUnavailable.Handle(ctx, application.MarkListingUnavailableCommand{
		ListingID: p.ListingID,
	})
	if err != nil {
		return Response{ID: req.ID, Type: respType, OK: false, Error: mapMarkListingError(err)}
	}
	return Response{ID: req.ID, Type: respType, OK: true, Payload: toPayload(result)}
}

func mapMarkListingError(err error) *ErrorBody {
	if errors.Is(err, domainerrors.ErrInvalidArgument) {
		return &ErrorBody{Code: CodeValidation, Message: err.Error()}
	}
	var ve *domainerrors.ValidationError
	if errors.As(err, &ve) {
		return &ErrorBody{Code: CodeValidation, Message: ve.Error(), Field: ve.Field}
	}
	return &ErrorBody{Code: CodeInternal, Message: "internal error"}
}
