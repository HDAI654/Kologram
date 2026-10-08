package app

import (
	"context"
	"database/sql"
	"fmt"
	"log/slog"
	"net/http"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/application"
	"github.com/HDAI654/Kologram/chat_service/internal/config"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/market"
	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/messaging"
	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/persistence/postgres"
	httpapi "github.com/HDAI654/Kologram/chat_service/internal/presentation/http"
	wsv1 "github.com/HDAI654/Kologram/chat_service/internal/presentation/ws/v1"
)

type Application struct {
	Config     config.Config
	DB         *sql.DB
	HTTP       http.Handler
	Hub        *wsv1.MemoryHub
	Events     ports.EventPublisher
	log        *slog.Logger
	httpServer *http.Server
	closeFns   []func() error
}

func New(ctx context.Context, log *slog.Logger) (*Application, error) {
	if log == nil {
		log = slog.Default()
	}
	cfg, err := config.Load()
	if err != nil {
		return nil, fmt.Errorf("config: %w", err)
	}

	db, err := postgres.OpenDB(ctx, cfg.DatabaseURL)
	if err != nil {
		return nil, fmt.Errorf("database: %w", err)
	}

	var events ports.EventPublisher
	var closeFns []func() error
	if cfg.EventPublisherNoOp {
		events = messaging.NewNoOpEventPublisher()
	} else {
		pub, err := messaging.NewRabbitMQEventPublisher(cfg.RabbitMQURL, cfg.RabbitMQExchange)
		if err != nil {
			_ = db.Close()
			return nil, fmt.Errorf("rabbitmq: %w", err)
		}
		events = pub
		closeFns = append(closeFns, pub.Close)
	}

	hub := wsv1.NewMemoryHub()
	var realtime ports.RealtimeNotifier = hub

	uowFactory := postgres.NewUnitOfWorkFactory(db)
	listingRepo := market.NewListingRepository(cfg.MarketServiceURL, &http.Client{
		Timeout: cfg.MarketHTTPTimeout,
	})
	convRepo := postgres.NewConversationRepository(db)
	stateRepo := postgres.NewConversationUserStateRepository(db)
	msgRepo := postgres.NewMessageRepository(db)

	handlers := &wsv1.Handlers{
		StartConversation:        application.NewStartConversationHandler(uowFactory, listingRepo, events, log),
		SendMessage:              application.NewSendMessageHandler(uowFactory, events, realtime, log),
		ListMessages:             application.NewListMessagesHandler(convRepo, msgRepo),
		ListConversations:        application.NewListConversationsHandler(convRepo),
		GetConversation:          application.NewGetConversationHandler(convRepo, stateRepo),
		MarkConversationRead:     application.NewMarkConversationReadHandler(uowFactory),
		DeleteMessageForEveryone: application.NewDeleteMessageForEveryoneHandler(uowFactory, realtime, log),
		ArchiveConversation:      application.NewArchiveConversationHandler(uowFactory),
		HideConversation:         application.NewHideConversationHandler(uowFactory),
		PinConversation:          application.NewPinConversationHandler(uowFactory),
		MuteConversation:         application.NewMuteConversationHandler(uowFactory),
		BlockUser:                application.NewBlockUserHandler(uowFactory, log),
		UnblockUser:              application.NewUnblockUserHandler(uowFactory, log),
		MarkListingUnavailable:   application.NewMarkListingUnavailableHandler(uowFactory, log),
	}

	wsRouter := wsv1.NewRouter()
	handlers.Register(wsRouter)
	wsServer := wsv1.NewServer(hub, wsRouter, log)
	httpHandler := httpapi.NewRouter(wsServer)

	return &Application{
		Config:   cfg,
		DB:       db,
		HTTP:     httpHandler,
		Hub:      hub,
		Events:   events,
		log:      log,
		closeFns: append(closeFns, db.Close),
	}, nil
}

func (a *Application) Close() error {
	var first error
	for i := len(a.closeFns) - 1; i >= 0; i-- {
		if err := a.closeFns[i](); err != nil && first == nil {
			first = err
		}
	}
	return first
}

func (a *Application) ListenAndServe() error {
	a.httpServer = &http.Server{
		Addr:              a.Config.HTTPAddr,
		Handler:           a.HTTP,
		ReadHeaderTimeout: 10 * time.Second,
	}
	a.log.Info("chat service listening", "addr", a.Config.HTTPAddr)
	return a.httpServer.ListenAndServe()
}

// Shutdown gracefully stops the HTTP server.
func (a *Application) Shutdown(ctx context.Context) error {
	if a.httpServer == nil {
		return nil
	}
	return a.httpServer.Shutdown(ctx)
}
