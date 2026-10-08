# High-level architecture

Kologram is a **multi-service marketplace**: sellers publish listings, buyers discover and message sellers, and auth issues identity for the platform.

---

## Goals

| Goal | How it is achieved |
|------|--------------------|
| Clear bounded contexts | One database and deployable unit per service |
| Framework-independent business rules | Domain + application layers; infrastructure & presentation as adapters (AGENT.md) |
| Safe cross-service collaboration | RabbitMQ domain events; no shared writable schemas between product services |
| Live messaging | Chat owns conversations; WebSocket + in-process hub for online users |
| Outbound notifications | `notification_dispatcher` consumes events and sends email (console or SMTP) |
| Staff operations | Django admin over Auth + Market tables (`managed = False`) |

---

## Runtime topology

```text
                         ┌─────────────────┐
                         │   API Gateway   │  (future: JWT check, rate limit)
                         │  X-User-Id /    │
                         │  X-User-Admin   │
                         └────────┬────────┘
            ┌─────────────────────┼─────────────────────┐
            │                     │                     │
            ▼                     ▼                     ▼
   ┌────────────────┐   ┌────────────────┐   ┌────────────────┐
   │  auth_service  │   │ market_service │   │  chat_service  │
   │  FastAPI REST  │   │ FastAPI+GQL    │   │ Go HTTP + WS   │
   │  :8001         │   │ :8002          │   │ :8003→:8080    │
   └───────┬────────┘   └───────┬────────┘   └───────┬────────┘
           │                    │                    │
           │                    │         GraphQL    │
           │                    │◄───────────────────┤
           │                    │  listing ACTIVE?   │
           ▼                    ▼                    ▼
   ┌────────────┐      ┌────────────┐      ┌────────────┐
   │ Postgres   │      │ Postgres   │      │ Postgres   │
   │  auth      │      │  market    │      │  chat      │
   └────────────┘      └────────────┘      └────────────┘
           │                                         │
           │ Redis (sessions / verify tokens)        │
           ▼                                         │
   ┌────────────┐                                    │
   │   Redis    │                                    │
   └────────────┘                                    │
           │                                         │
           └──────────────┬──────────────────────────┘
                          ▼
                  ┌──────────────┐         ┌─────────────────────────┐
                  │   RabbitMQ   │────────►│ notification_dispatcher │
                  │ auth.events  │         │ email: console │ SMTP     │
                  │ listing.events│        └─────────────────────────┘
                  │ chat.events  │
                  └──────────────┘

   ┌────────────────┐
   │ admin_service  │  Django :8004
   │ unmanaged ORM  │──► Auth DB + Market DB
   │ + admin DB     │──► Postgres `admin` (Django auth/session tables)
   └────────────────┘
```

| Service | Role | Protocol | Data ownership |
|---------|------|----------|----------------|
| **auth_service** | Signup, login, sessions, password reset, JWT (RS256) | REST | `auth` DB + Redis |
| **market_service** | Categories, listings, search, status lifecycle | GraphQL | `market` DB |
| **chat_service** | Conversations, messages, blocks, per-user inbox state | HTTP health + **WebSocket** | `chat` DB |
| **admin_service** | Staff UI over users / categories / listings | Django admin | Does **not** own Auth/Market schemas |
| **notification_dispatcher** | Consume domain events → email | Worker (pika) | SQLite idempotency only |

---

## Architectural style (product services)

```text
Presentation  →  Application  →  Domain
                                      ↑
                               Ports (interfaces)
                                      ↑
                               Infrastructure
```

| Layer | Responsibility |
|-------|----------------|
| **Domain** | Entities, value objects, invariants, domain events (facts) |
| **Application** | Use cases; UoW for writes; publish events after commit (best-effort) |
| **Infrastructure** | Postgres, Redis, RabbitMQ, JWT/bcrypt, SMTP, GraphQL/HTTP clients |
| **Presentation** | REST, GraphQL, or WebSocket; error mapping at the edge |

**Admin** is a thin multi-DB Django panel, not a DDD marketplace core.  
**notification_dispatcher** is an application worker: trusted event DTOs → jobs → `EmailSender` port (no domain validation of payloads).

---

## Cross-service communication

### Synchronous

| Caller | Callee | Purpose |
|--------|--------|---------|
| chat_service | market GraphQL | Resolve seller + messaging allowed (`status == ACTIVE`) |
| Clients / gateway | auth, market, chat | Public APIs |

Chat does **not** call auth for identity: the gateway attaches `X-User-Id` (and optional `X-User-Admin`) on the WebSocket upgrade.

### Asynchronous (RabbitMQ topic exchanges)

| Exchange | Publisher | Consumer |
|----------|-----------|----------|
| `auth.events` | auth_service | notification_dispatcher |
| `listing.events` | market_service | notification_dispatcher |
| `chat.events` | chat_service | notification_dispatcher |

Publishing is **best-effort after successful commit** (not dual-write with the DB transaction).

#### What notification_dispatcher does today

| Event | Action |
|-------|--------|
| `UserRegistered` | Welcome email |
| `UserLoggedIn` | New login email (device) |
| `UserLoggedOut` | Signed-out email |
| `VerificationTokenCreated` (`verifyemail`) | Email verification token |
| `VerificationTokenCreated` (`forget_pass_verify`) | Password-reset token email |
| `AccountDeleted` | Temporary NOTHING |
| All market events | Temporary NOTHING |
| `ConversationStarted`, `MessageSent` | Temporary NOTHING |

Email delivery: **`EMAIL_ENABLED`** truthy → SMTP; otherwise **console** (log only). Up to **3** send attempts, then skip. SQLite idempotency avoids duplicate sends.

---

## Identity and security

```text
Client  →  Gateway (authenticate JWT)  →  Service
                │
                ├─ X-User-Id: <uuid>
                └─ X-User-Admin: true|…   (elevated chat ops)
```

- **auth_service** issues access + refresh (RS256); sessions in Redis (or in-memory in pure dev).
- **market** / **chat** trust gateway-forwarded actor identity in the current design.
- Passwords: bcrypt. Login failures stay opaque where required.

---

## Data isolation

1. No product service writes another service’s database.  
2. Auth owns users; market owns categories/listings; chat owns conversations/messages/blocks/user state.  
3. Admin may read/update Auth/Market via unmanaged models; **schema ownership stays with the owning service**.  
4. Chat stores foreign ids (`listing_id`, `buyer_id`, `seller_id`), not full listing copies.

---

## Local / Docker deployment

| Component | Host port |
|-----------|-----------|
| auth_service | 8001 |
| market_service | 8002 |
| chat_service | **8003** → container **8080** (`HTTP_ADDR`) |
| admin_service | 8004 |
| Postgres | 5432 (DBs: `auth`, `market`, `chat`, `admin`) |
| Redis | 6379 |
| RabbitMQ | 5672 / UI 15672 |
| MailHog (profile `mail`) | SMTP 1025 / UI 8025 |

```bash
docker compose up --build
# optional email sink:
docker compose --profile mail up -d
# then set EMAIL_ENABLED=true on notification_dispatcher
```

Compose notes:

- JWT keys mounted from `auth_service/keys/`.  
- Chat DDL applied once by **`chat_schema_init`** (`schema.sql`).  
- Notification binds all three exchanges on queue `notification.dispatcher`.

---

## Explicit non-goals (today)

- Full API gateway implementation in-repo  
- Reviews / ratings  
- Automatic chat freeze from market status events (admin `X-User-Admin` path exists in chat)  
- Rich HTML email templates / multi-channel push beyond email  

Extend without relocating existing aggregates.
