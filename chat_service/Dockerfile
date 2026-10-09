# syntax=docker/dockerfile:1

FROM golang:1.22-bookworm AS builder
WORKDIR /src
ENV GOTOOLCHAIN=local
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -trimpath -ldflags="-s -w" -o /out/chat_service ./cmd/server

FROM alpine:3.20
RUN apk add --no-cache ca-certificates \
  && adduser -D -u 65532 -H nonroot
WORKDIR /app
COPY --from=builder /out/chat_service /app/chat_service
COPY --from=builder /src/internal/infrastructure/persistence/postgres/schema.sql /app/schema.sql
ENV HTTP_ADDR=:8080
EXPOSE 8080
USER nonroot
ENTRYPOINT ["/app/chat_service"]
