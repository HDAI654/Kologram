# Build stage
FROM golang:1.24-bookworm AS builder

ENV GOTOOLCHAIN=auto
WORKDIR /src
COPY chat_service/go.mod chat_service/go.sum ./
RUN go mod download
COPY chat_service/ ./
RUN CGO_ENABLED=0 GOOS=linux go build -o /out/chat-service ./cmd/server

# Runtime
FROM gcr.io/distroless/static-debian12:nonroot

COPY --from=builder /out/chat-service /chat-service

EXPOSE 8003
USER nonroot:nonroot
ENTRYPOINT ["/chat-service"]
