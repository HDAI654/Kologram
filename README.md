# Kologram

Marketplace platform split into small services: accounts, listings, chat, staff admin, and outbound email.

Traffic enters through a single gateway. Each service owns its database and talks over HTTP, GraphQL, WebSocket, or RabbitMQ events.

## Services

| Service | What it does | Port |
|---------|--------------|------|
| gateway | JWT, CORS, rate limit, reverse proxy + WS | 8000 |
| auth_service | Signup, login, sessions, tokens | 8001 |
| market_service | Categories and listings (GraphQL) | 8002 |
| chat_service | Conversations and messages (WebSocket) | 8003 |
| admin_service | Django admin over auth + market data | 8004 |
| notification_dispatcher | Domain events → email | — |
| frontend | Test UI | 3030 |

Supporting stack: PostgreSQL, Redis, RabbitMQ.

## Quick start

Generate JWT keys (once):

```bash
mkdir -p auth_service/keys
openssl genrsa -out auth_service/keys/private.pem 2048
openssl rsa -in auth_service/keys/private.pem -pubout -out auth_service/keys/public.pem
```

Run:

```bash
docker compose up --build
```

| | URL |
|--|-----|
| UI | http://localhost:3030 |
| Gateway health | http://localhost:8000/health |
| Admin | http://localhost:8004/admin/ |
| RabbitMQ management | http://localhost:15672 (`guest` / `guest`) |

Default admin login (compose): `admin` / `admin123`.

## Layout

```text
auth_service/                 # REST auth
market_service/               # GraphQL listings
chat_service/                 # WebSocket messaging
gateway/                      # Edge proxy
admin_service/                # Django admin
notification_dispatcher/      # Event consumer → email
test_ui/                      # Static frontend
docs/                         # Architecture and domain notes
docker/                       # Postgres init scripts
```

## Docs

- [Architecture](docs/high-level-architecture.md)
- [Domain model](docs/domain-model.md)
- API contracts: `gateway/docs/ENDPOINTS.md`, `auth_service/docs/ENDPOINTS.md`, `market_service/docs/ENDPOINTS.md`, `chat_service/docs/ENDPOINTS.md`

## Notes

- Call the **gateway** (`:8000`) from clients, not the individual service ports.
- Chat listens on `:8080` inside the network; the host maps `8003→8080`.
- `EMAIL_ENABLED=false` logs mail to the console; set `true` and SMTP env vars to send real mail.
- Optional MailHog: `docker compose --profile mail up -d` (SMTP `1025`, UI `8025`).

## Tests

```bash
./auth_service/run_tests.sh
./market_service/run_tests.sh
./notification_dispatcher/run_tests.sh
cd chat_service && go test ./...
```

## License

MIT. See [LICENSE](LICENSE).