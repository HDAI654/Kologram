package v1

import "context"

type handlerFunc func(ctx context.Context, userID string, isAdmin bool, req Request) Response

// Router dispatches by request type.
type Router struct {
	handlers map[string]handlerFunc
}

func NewRouter() *Router {
	return &Router{handlers: make(map[string]handlerFunc)}
}

func (r *Router) Register(actionType string, h func(ctx context.Context, userID string, req Request) Response) {
	r.handlers[actionType] = func(ctx context.Context, userID string, isAdmin bool, req Request) Response {
		return h(ctx, userID, req)
	}
}

func (r *Router) RegisterAdmin(actionType string, h handlerFunc) {
	r.handlers[actionType] = h
}

func (r *Router) Dispatch(ctx context.Context, userID string, req Request) Response {
	return r.DispatchAdmin(ctx, userID, false, req)
}

func (r *Router) DispatchAdmin(ctx context.Context, userID string, isAdmin bool, req Request) Response {
	h, ok := r.handlers[req.Type]
	if !ok {
		return Response{
			ID:   req.ID,
			Type: resultType(req.Type),
			OK:   false,
			Error: &ErrorBody{
				Code:    CodeInvalidRequest,
				Message: "unknown action type: " + req.Type,
			},
		}
	}
	return h(ctx, userID, isAdmin, req)
}

var _ Dispatcher = (*Router)(nil)
var _ AdminAwareDispatcher = (*Router)(nil)
