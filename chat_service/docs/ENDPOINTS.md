# Chat Service — Endpoints

WebSocket-first chat API for marketplace buyer/seller messaging.

- **WebSocket:** `GET /ws` (upgrade)
- **Health:** `GET /health`
- **Auth:** handled at the API Gateway. The gateway must forward identity on the upgrade request:
  - `X-User-Id` (required) — UUID of the authenticated user
  - `X-User-Admin` (optional) — `true` / `1` / `yes` for admin-only actions

---

## `GET /health`

```json
{ "status": "ok", "service": "chat_service" }
```

Used for container/orchestrator health checks.

---

## `GET /ws`

Upgrade to WebSocket. Missing or invalid `X-User-Id` → HTTP `401` before upgrade.

### Envelope (client → server)

```json
{ "id": "req-1", "type": "send_message", "payload": { ... } }
```

### Envelope (server → client, reply)

```json
{
  "id": "req-1",
  "type": "send_message_result",
  "ok": true,
  "payload": { ... }
}
```

Error reply:

```json
{
  "id": "req-1",
  "type": "send_message_result",
  "ok": false,
  "error": { "code": "NOT_FOUND", "message": "...", "field": "conversation_id" }
}
```

### Push events (server → client, no `id`)

Published via the in-process realtime hub when the recipient is connected:

```json
{ "type": "message_sent", "conversation_id": "...", "message_id": "...", "sender_id": "..." }
```

```json
{ "type": "message_deleted", "conversation_id": "...", "message_id": "..." }
```

### Error codes

| Code | Meaning |
|---|---|
| `INVALID_REQUEST` | Bad envelope/payload/unknown action |
| `VALIDATION_ERROR` | Domain/input validation |
| `NOT_FOUND` | Missing resource |
| `FORBIDDEN` | Not participant / blocked / not author / not admin |
| `CONFLICT` | Business conflict (read-only, delete window, listing not messageable, …) |
| `INTERNAL_ERROR` | Unexpected failure |

### Actor identity

The connection `X-User-Id` is always used as buyer/sender/actor/blocker.  
Payload must **not** supply those fields; resource fields (`listing_id`, `conversation_id`, `content`, …) come from `payload`.

### Actions

| `type` | Payload (main fields) | Notes |
|---|---|---|
| `start_conversation` | `listing_id` | Creates or returns existing |
| `send_message` | `conversation_id`, `client_message_id`, `content` | Idempotent via client_message_id (UUID v4) |
| `list_messages` | `conversation_id`, optional cursor/direction/limit | Soft-deleted excluded |
| `list_conversations` | optional `filter`, cursor, limit | `active` (default) \| `archived` |
| `get_conversation` | `conversation_id` | Includes per-user state |
| `mark_conversation_read` | `conversation_id`, `last_read_message_id` | Soft-deleted message → NOT_FOUND |
| `delete_message_for_everyone` | `message_id` | Author only; time window |
| `archive_conversation` | `conversation_id`, `archive` | |
| `hide_conversation` | `conversation_id`, `hide` | |
| `pin_conversation` | `conversation_id`, `pin` | |
| `mute_conversation` | `conversation_id`, `mute`, optional `until` (RFC3339) | `until` required when mute=true |
| `block_user` | `blocked_id` | |
| `unblock_user` | `blocked_id` | |
| `mark_listing_unavailable` | `listing_id` | **Requires** `X-User-Admin: true` |

Result `type` is always `{action}_result`. Payload fields are **snake_case**.

---

## Schema

PostgreSQL schema (manual apply; no migration runner):

`internal/infrastructure/persistence/postgres/schema.sql`

Also copied into the container image at `/app/schema.sql`.
