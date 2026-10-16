# Kologram

Marketplace backend: auth, listings, chat, admin, and email notifications.

Clients use a single **gateway**. Each service owns its database.

## Services

| Service | Role | Port |
|---------|------|------|
| gateway | JWT, CORS, rate limit, proxy + WS | 8000 |
| auth_service | Accounts, sessions, JWT | 8001 |
| market_service | Categories, listings (GraphQL) | 8002 |
| chat_service | Conversations, messages (WS) | 8003 |
| admin_service | Django admin | 8004 |
| notification_dispatcher | Events → email | — |
| frontend | Static test UI | 3030 |

Postgres · Redis · RabbitMQ

## Run

```bash
mkdir -p auth_service/keys
openssl genrsa -out auth_service/keys/private.pem 2048
openssl rsa -in auth_service/keys/private.pem -pubout -out auth_service/keys/public.pem

docker compose up --build