# Build stage
FROM golang:1.26.5-bookworm AS builder

WORKDIR /src

COPY go.mod go.sum ./
RUN GOPROXY=https://goproxy.io,direct go mod download

COPY . ./

RUN CGO_ENABLED=0 GOOS=linux \
    go build -o /out/chat-service ./cmd/server


# Runtime
FROM alpine:3.22

RUN addgroup -S app && adduser -S app -G app

COPY --from=builder /out/chat-service /chat-service

RUN chown app:app /chat-service

USER app

EXPOSE 8003

ENTRYPOINT ["/chat-service"]