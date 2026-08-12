package main

import (
	"context"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/application"
	"github.com/HDAI654/Kologram/chat_service/internal/config"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/port"
	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/messaging"
	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/persistence/memory"
	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/persistence/postgres"
	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/realtime"
	httpapi "github.com/HDAI654/Kologram/chat_service/internal/presentation/http"
	wsapi "github.com/HDAI654/Kologram/chat_service/internal/presentation/ws"
)

func main() {
	cfg := config.Load()
	slog.SetDefault(slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelInfo,
	})))

	uowFactory, cleanupDB := buildPersistence(cfg)
	defer cleanupDB()

	hub := realtime.NewHub()
	events, closer := buildEventPublisher(cfg)
	defer closer()

	handlers := &httpapi.Handlers{
		Start:   application.NewStartConversationHandler(uowFactory, events),
		Send:    application.NewSendMessageHandler(uowFactory, events, hub),
		List:    application.NewListConversationsHandler(uowFactory),
		Get:     application.NewGetMessagesHandler(uowFactory),
		Read:    application.NewMarkReadHandler(uowFactory, events, hub),
		Status:  application.NewChangeStatusHandler(uowFactory, events),
		AppName: cfg.AppName,
	}

	router := httpapi.NewRouter(handlers, wsapi.Handler(hub))
	server := &http.Server{
		Addr:              cfg.HTTPAddr,
		Handler:           router,
		ReadHeaderTimeout: 5 * time.Second,
	}

	go func() {
		slog.Info("chat service listening", "addr", cfg.HTTPAddr, "service", cfg.AppName)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			slog.Error("server failed", "error", err)
			os.Exit(1)
		}
	}()

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGINT, syscall.SIGTERM)
	<-stop

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	if err := server.Shutdown(ctx); err != nil {
		slog.Error("shutdown error", "error", err)
	}
	slog.Info("chat service stopped")
}

func buildPersistence(cfg config.Config) (port.UnitOfWorkFactory, func()) {
	if !cfg.UsePostgres() {
		slog.Info("using in-memory persistence")
		repo := memory.NewConversationRepository()
		return memory.NewUnitOfWorkFactory(repo), func() {}
	}

	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()

	pool, err := postgres.OpenPool(ctx, cfg.DatabaseURL)
	if err != nil {
		slog.Error("postgres connect failed", "error", err)
		os.Exit(1)
	}
	if err := postgres.Migrate(ctx, pool); err != nil {
		slog.Error("postgres migrate failed", "error", err)
		pool.Close()
		os.Exit(1)
	}
	slog.Info("using postgresql persistence", "database_url_set", true)
	return postgres.NewUnitOfWorkFactory(pool), func() { pool.Close() }
}

func buildEventPublisher(cfg config.Config) (port.EventPublisher, func()) {
	if !cfg.RabbitMQEnabled {
		slog.Info("using NoOpEventPublisher (RABBITMQ_ENABLED=false)")
		return messaging.NewNoOpEventPublisher(), func() {}
	}

	pub := messaging.NewRabbitMQEventPublisher(cfg.RabbitMQURL, cfg.RabbitMQExchange)
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	if err := pub.Connect(ctx); err != nil {
		slog.Error("rabbitmq connect failed, falling back to NoOp", "error", err)
		return messaging.NewNoOpEventPublisher(), func() {}
	}
	return pub, func() {
		if err := pub.Close(); err != nil {
			slog.Error("rabbitmq close error", "error", err)
		}
	}
}
