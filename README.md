# Kologram

Kologram is a marketplace backend split into focused services: auth, listings, chat, admin, and email notifications.
A single gateway fronts the APIs; each service owns its data and talks over HTTP, GraphQL, WebSocket, and RabbitMQ events.
Built with clean architecture, Docker Compose, and Postgres, Redis, and RabbitMQ for local and production-style runs.

## Services

| Service | Role | Port |
|---------|------|------|
| **gateway** | JWT validation, CORS, rate limit, reverse proxy + WS | **8000** |
| **auth_service** | Signup, login, sessions, password reset, RS256 JWT | 8001 |
| **market_service** | Categories, listings, search (GraphQL) | 8002 |
| **chat_service** | Conversations & messages (WebSocket) | 8003 → 8080 |
| **admin_service** | Django admin (unmanaged Auth/Market tables) | 8004 |
| **notification_dispatcher** | RabbitMQ consumer → email (console or SMTP) | — |

Infra: Postgres 16 (`auth`, `market`, `chat`, `admin`), Redis 7, RabbitMQ 3.13.

## Quick start

```bash
# JWT keys (required once)
mkdir -p auth_service/keys
openssl genrsa -out auth_service/keys/private.pem 2048
openssl rsa -in auth_service/keys/private.pem -pubout -out auth_service/keys/public.pem

docker compose up --build
```

| Check | URL |
|-------|-----|
| Gateway | http://localhost:8000/health |
| Auth | http://localhost:8001/health |
| Market GraphQL | http://localhost:8002/graphql |
| Chat | http://localhost:8003/health |
| Admin | http://localhost:8004/admin/ |
| RabbitMQ UI | http://localhost:15672 (`guest`/`guest`) |

Optional mail sink:

```bash
docker compose --profile mail up -d   # MailHog UI :8025
# set EMAIL_ENABLED=true on notification_dispatcher to use SMTP
```

Dev defaults (`postgres`/`postgres`, Rabbit `guest`/`guest`) are local-only.

## Layout

```
gateway/                    # Go edge proxy
auth_service/               # FastAPI + SQLAlchemy + Redis + JWT
market_service/             # FastAPI + Strawberry GraphQL
chat_service/               # Go HTTP/WS
admin_service/              # Django multi-DB admin
notification_dispatcher/    # Python worker (pika)
docker/postgres/            # multi-DB init
docs/                       # architecture + domain model
docker-compose.yml
```

API notes: `*/docs/ENDPOINTS.md`.

## Architecture (summary)

```text
Client ──► Gateway :8000 ──► auth / market / chat
                │
                └── JWT → X-User-Id (+ X-User-Admin if claim)
                              │
Services ──publish──► RabbitMQ ──► notification_dispatcher ──► email
```

Full diagrams: [docs/high-level-architecture.md](docs/high-level-architecture.md), [docs/domain-model.md](docs/domain-model.md).

## Tests

```bash
./auth_service/run_tests.sh
./market_service/run_tests.sh
./notification_dispatcher/run_tests.sh
cd chat_service && go test ./...
```

## Notes

- Public entry point is the **gateway** (`:8000`), not the service ports.
- Chat process binds `:8080` in-container; host maps **8003→8080**.
- With `APP_ENV=development`, auth/market may use in-memory stores; use a non-`development` value for Postgres-backed runs.
- Notification: `EMAIL_ENABLED=false` logs mail to console; `true` uses SMTP env vars.
