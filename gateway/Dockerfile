# syntax=docker/dockerfile:1

FROM golang:1.22-bookworm AS builder
WORKDIR /src
ENV GOTOOLCHAIN=local
COPY go.mod go.sum* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -trimpath -ldflags="-s -w" -o /out/gateway ./cmd/gateway

FROM alpine:3.20
RUN apk add --no-cache ca-certificates \
  && adduser -D -u 65532 -H nonroot
WORKDIR /app
COPY --from=builder /out/gateway /app/gateway
ENV HTTP_ADDR=:8000
EXPOSE 8000
USER nonroot
ENTRYPOINT ["/app/gateway"]
