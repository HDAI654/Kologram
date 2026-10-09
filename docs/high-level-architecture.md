# High-level architecture

Marketplace platform: identity, catalog, messaging, staff admin, and outbound email.

---

## System context

Who uses the system and what sits outside it.

```mermaid
C4Context
  title System context — Kologram

  Person(buyer, "Buyer", "Browses listings, chats with sellers")
  Person(seller, "Seller", "Publishes listings, replies in chat")
  Person(staff, "Staff", "Moderates via admin panel")

  System(kologram, "Kologram", "Marketplace backend")

  System_Ext(email, "Email / SMTP", "Delivery of account mail")
  System_Ext(browser, "Browser / client", "REST, GraphQL, WebSocket")

  Rel(buyer, browser, "Uses")
  Rel(seller, browser, "Uses")
  Rel(staff, kologram, "Django admin")
  Rel(browser, kologram, "HTTPS / WS via gateway")
  Rel(kologram, email, "Sends mail")
```

---

## Containers

Deployable units and infrastructure (one process or data store each).

```mermaid
C4Container
  title Containers — Kologram

  Person(user, "User", "Buyer / seller client")
  Person(staff, "Staff", "Admin UI")

  Container(gw, "Gateway", "Go", "JWT, CORS, rate limit, HTTP/WS proxy")
  Container(auth, "auth_service", "Python FastAPI", "Accounts, sessions, JWT")
  Container(market, "market_service", "Python GraphQL", "Categories, listings")
  Container(chat, "chat_service", "Go", "Conversations, messages, WS")
  Container(admin, "admin_service", "Django", "Staff panel")
  Container(notif, "notification_dispatcher", "Python worker", "Event → email")

  ContainerDb(pg, "PostgreSQL", "auth / market / chat / admin DBs")
  ContainerDb(redis, "Redis", "Sessions, verify tokens")
  ContainerQueue(mq, "RabbitMQ", "Domain events")

  Rel(user, gw, "HTTP, WS", "JSON")
  Rel(staff, admin, "HTTP")
  Rel(gw, auth, "REST")
  Rel(gw, market, "GraphQL")
  Rel(gw, chat, "WS /health")
  Rel(chat, market, "Listing ACTIVE?", "GraphQL")
  Rel(auth, pg, "SQL")
  Rel(auth, redis, "Cache")
  Rel(market, pg, "SQL")
  Rel(chat, pg, "SQL")
  Rel(admin, pg, "SQL (read Auth/Market)")
  Rel(auth, mq, "Publish")
  Rel(market, mq, "Publish")
  Rel(chat, mq, "Publish")
  Rel(mq, notif, "Consume")
```

| Container | Owns | Protocol |
|-----------|------|----------|
| gateway | Edge only | :8000 |
| auth_service | Users, sessions | REST :8001 |
| market_service | Categories, listings | GraphQL :8002 |
| chat_service | Conversations, messages, blocks | WS :8080 (host 8003) |
| admin_service | Staff UI (no domain ownership) | HTTP :8004 |
| notification_dispatcher | Idempotent email side-effects | Worker |

---

## Communication

**Synchronous**

| From | To | Why |
|------|-----|-----|
| Client | Gateway | Single public entry |
| Gateway | auth / market / chat | Proxy after JWT (public auth routes excepted) |
| chat | market GraphQL | Seller + `message_allowed` (listing ACTIVE) |

Identity: gateway validates access JWT, sets `X-User-Id` from `sub`, and `X-User-Admin: true` when claim `admin` is true. Client-supplied identity headers are stripped.

**Asynchronous (RabbitMQ topic)**

| Exchange | Publisher | Consumer |
|----------|-----------|----------|
| `auth.events` | auth | notification_dispatcher |
| `listing.events` | market | notification_dispatcher |
| `chat.events` | chat | notification_dispatcher |

Publish is **best-effort after commit** (not dual-write with the DB).

| Event | Email action today |
|-------|--------------------|
| UserRegistered, UserLoggedIn, UserLoggedOut | Send |
| VerificationTokenCreated | Send token |
| AccountDeleted, market events, ConversationStarted, MessageSent | Temporary no-op |

---

## Layering (product services)

```text
Presentation → Application → Domain
                              ↑ ports
                         Infrastructure
```

Admin is a thin multi-DB Django app. The notification worker uses trusted event DTOs → jobs → `EmailSender` (no domain validation of payloads).

---

## Local topology

| Host port | Target |
|-----------|--------|
| 8000 | gateway |
| 8001–8004 | auth, market, chat (mapped), admin |
| 5432 / 6379 / 5672 / 15672 | Postgres, Redis, RabbitMQ |

Chat schema: one-shot `chat_schema_init`. JWT keys: `auth_service/keys/`.

---

## Non-goals (current)

API gateway product features beyond JWT/CORS/rate-limit/proxy · reviews/ratings · rich HTML email templates · automatic freeze of chat from market status events (admin path exists on chat).
