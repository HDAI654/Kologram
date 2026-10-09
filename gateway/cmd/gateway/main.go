package main

import (
	"context"
	"errors"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/HDAI654/Kologram/gateway/internal/auth"
	"github.com/HDAI654/Kologram/gateway/internal/config"
	"github.com/HDAI654/Kologram/gateway/internal/middleware"
	"github.com/HDAI654/Kologram/gateway/internal/server"
)

func main() {
	slog.SetDefault(slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo})))

	cfg, err := config.Load()
	if err != nil {
		slog.Error("config", "err", err)
		os.Exit(1)
	}

	jwt, err := auth.NewValidator(cfg.PublicKeyPath)
	if err != nil {
		slog.Error("jwt validator", "err", err)
		os.Exit(1)
	}

	srv, err := server.New(cfg, jwt)
	if err != nil {
		slog.Error("server", "err", err)
		os.Exit(1)
	}

	handler := middleware.CORS(cfg.CORSOrigin, srv.Handler())
	httpServer := &http.Server{
		Addr:              cfg.HTTPAddr,
		Handler:           handler,
		ReadHeaderTimeout: 10 * time.Second,
	}

	go func() {
		slog.Info("gateway listening", "addr", cfg.HTTPAddr)
		if err := httpServer.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			slog.Error("listen", "err", err)
			os.Exit(1)
		}
	}()

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGINT, syscall.SIGTERM)
	<-stop

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	_ = httpServer.Shutdown(ctx)
	slog.Info("gateway stopped")
}
