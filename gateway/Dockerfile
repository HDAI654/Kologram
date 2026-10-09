# syntax=docker/dockerfile:1

FROM golang:1.22-bookworm AS builder
WORKDIR /src
ENV GOTOOLCHAIN=auto
COPY go.mod go.sum* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -trimpath -ldflags="-s -w" -o /out/gateway ./cmd/gateway

FROM gcr.io/distroless/static-debian12:nonroot
WORKDIR /app
COPY --from=builder /out/gateway /app/gateway
ENV HTTP_ADDR=:8000
EXPOSE 8000
USER nonroot:nonroot
ENTRYPOINT ["/app/gateway"]
