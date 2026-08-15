# Kologram

Kologram is a marketplace backend built as a set of small services that talk to each other over HTTP and an event bus. Buyers and sellers can register, list items, search the catalog, and message each other. Admins get a separate panel for moderation. Notifications (mostly email) are handled by a dedicated worker that listens to domain events.

The codebase follows a clean / hexagonal style: domain and application layers stay free of frameworks; infrastructure (Postgres, Redis, RabbitMQ, JWT, etc.) sits behind ports.

---

## What’s in the box

| Service | Role | Port |
|---------|------|------|
| **auth_service** | Signup, login, sessions, password reset, JWT (RS256) | 8001 |
| **market_service** | Categories, listings, search, status lifecycle (GraphQL) | 8002 |
| **chat_service** | Buyer–seller conversations and messages (HTTP + WebSocket) | 8003 |
| **admin_service** | Django admin over Auth + Market tables (unmanaged models) | 8004 |
| **notification_dispatcher** | Consumes events and sends email (console or SMTP) | — |

Shared helpers live under `shared/`. Docs and a high-level architecture diagram are in `docs/`.

---

## Tech stack

**Languages & frameworks**
- Python 3.12 — FastAPI (auth, market), Django 5 (admin), plain async worker (notifications)
- Go 1.2x — chat service

**API style**
- REST (auth, chat)
- GraphQL via Strawberry (market)
- WebSocket for live chat updates

**Data & messaging**
- PostgreSQL 16 — one database per bounded context (`auth`, `market`, `chat`, `admin`)
- Redis 7 — sessions, verification tokens, email blocklist (auth)
- RabbitMQ 3.13 — domain events (`auth.events`, `listing.events`, `chat.events`)
- SQLite only for local/dev shortcuts and notification idempotency store

**Auth**
- RS256 JWT (access + refresh), bcrypt password hashing
- Keys under `auth_service/keys/`

**Architecture patterns**
- Domain-driven design / hexagonal: entities, value objects, application handlers, ports & adapters
- Unit of Work for write flows
- Event-driven side effects (registration, listing changes, messages → notification worker)

**Tooling**
- Docker + Docker Compose for the full stack
- pytest / pytest-asyncio (Python), Go `testing` package
- MailHog optional profile for catching outbound mail in dev

---

## Quick start with Docker

You need Docker and Docker Compose v2.

```bash
# from the repo root
docker compose up --build
```

That brings up Postgres, Redis, RabbitMQ, and all application services. First boot creates the four Postgres databases via `docker/postgres/init-databases.sh`.

Useful URLs once everything is healthy:

| What | URL |
|------|-----|
| Auth health | http://localhost:8001/health |
| Market GraphQL | http://localhost:8002/graphql |
| Chat health | http://localhost:8003/health |
| Admin panel | http://localhost:8004/admin/ |
| RabbitMQ management | http://localhost:15672 (guest / guest) |

Optional email sink:

```bash
docker compose --profile mail up -d mailhog
# UI: http://localhost:8025
```

Default credentials are for local use only (`postgres` / `postgres`, RabbitMQ `guest` / `guest`). Change them before any shared or production environment.

> **Note on chat image:** if pulling `gcr.io/distroless/...` fails with 403 in your network, switch the runtime stage in `chat_service/Dockerfile` to `alpine:3.20` (or `debian:bookworm-slim`) and rebuild. The binary is statically linked, so Alpine works fine.

---

## Project layout

```
Kologram-1.0.0/
├── auth_service/          # FastAPI + SQLAlchemy async + Redis + JWT
├── market_service/        # FastAPI + Strawberry GraphQL + SQLAlchemy
├── chat_service/          # Go (cmd/server + internal/...)
├── admin_service/         # Django admin, multi-DB router
├── notification_dispatcher/
├── shared/                # small shared Python bits (entity base, id VOs, …)
├── docker/postgres/       # init script for multiple DBs
├── docs/                  # architecture + domain model notes
├── docker-compose.yml
└── run_tests.sh
```

Each Python service keeps the usual split: `domain/`, `application/`, `infrastructure/`, `presentation/` (or Django’s `config/` + `core/`). Chat follows the same idea under `internal/`.

---

## Running tests

From the repo root (with `PYTHONPATH` including the root and the service you care about):

```bash
# all Python unit tests (example)
./run_tests.sh auth_service test/unit
./run_tests.sh market_service test/unit

# auth e2e (in-memory stack)
./run_tests.sh auth_service test/e2e

# chat (Go)
cd chat_service && go test ./test/...
```

Application tests use mocks so they don’t need Postgres/Redis/RabbitMQ. E2E tests spin up the real ASGI (or httptest) app with in-memory adapters where possible.

---

## Configuration

Services read environment variables (and optional `.env` files). The important ones:

| Variable | Used by | Notes |
|----------|---------|--------|
| `DATABASE_URL` | auth, market, chat | asyncpg / Postgres URL |
| `REDIS_URL` / `REDIS_ENABLED` | auth | sessions & tokens |
| `RABBITMQ_URL` / `RABBITMQ_ENABLED` | most services | event bus |
| `RABBITMQ_EXCHANGE` | producers | e.g. `auth.events`, `listing.events` |
| `AUTH_*_KEY_PATH` | auth | RS256 PEM files |
| `DJANGO_SECRET_KEY`, `*_DB_*` | admin | multi-database settings |
| `EMAIL_PROVIDER`, `SMTP_*` | notification_dispatcher | `console` or `smtp` |

See `docker-compose.yml` for a complete working set aimed at local development.

---

## Typical flows

1. **Register / login** — client hits auth (`/api/v1/auth/...`), gets access + refresh tokens.
2. **List something** — authenticated seller creates a draft listing on market, publishes it; events go to RabbitMQ.
3. **Chat** — buyer starts a conversation about a listing; both sides exchange messages over HTTP (and can subscribe via WebSocket).
4. **Notifications** — dispatcher consumes events (e.g. verification token created, listing published) and sends email through the configured provider.
5. **Moderation** — staff use the Django admin, which reads/writes the same Auth and Market tables (unmanaged models + DB router).

---

## Development notes

- Prefer keeping domain pure: no SQLAlchemy/Django/Go HTTP types inside entities or application handlers.
- New write use-cases should go through a Unit of Work and publish events only after a successful commit.
- Auth tokens are RS256; keep the private key out of the image in real deployments (mount or inject at runtime).
- Admin models are `managed = False` — schema ownership stays with auth_service and market_service.

If something fails on first `docker compose up`, check service logs (`docker compose logs auth_service`) and that the Postgres init script created the four databases.

---

## License

Released under the [MIT License](LICENSE).