# syntax=docker/dockerfile:1

# --- build ---
FROM golang:1.23-bookworm AS builder

WORKDIR /src

# Module files first for better layer caching
COPY go.mod go.sum ./
# go.mod may request a newer toolchain; auto-download is fine in build image
ENV GOTOOLCHAIN=auto
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -trimpath -ldflags="-s -w" -o /out/chat_service ./cmd/server

# --- runtime ---
FROM gcr.io/distroless/static-debian12:nonroot

WORKDIR /app

COPY --from=builder /out/chat_service /app/chat_service
# Schema is applied externally (no migration runner); ship for operators.
COPY --from=builder /src/internal/infrastructure/persistence/postgres/schema.sql /app/schema.sql

ENV HTTP_ADDR=:8080
EXPOSE 8080

USER nonroot:nonroot

ENTRYPOINT ["/app/chat_service"]
