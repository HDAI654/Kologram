# Gateway — Endpoints

Public edge for Kologram. Clients use **only** this service (`http://localhost:8000`).

- **Role:** reverse proxy, JWT validation, identity headers, CORS, rate limits
- **Upstreams:** auth (`/api/v1/auth/*`), market (`/graphql`), chat (`/ws`)
- **CORS origin:** `http://localhost:3030` (OPTIONS allowed)

---

## Authentication

| Kind | Rule |
|------|------|
| **Public** | Listed auth paths below — no Bearer required |
| **Protected** | Valid `Authorization: Bearer <access_token>` (JWT RS256, `type=access`) |

On protected traffic the gateway:

1. Validates the access token  
2. Strips any client `X-User-Id` / `X-User-Admin`  
3. Sets `X-User-Id` from JWT `sub`  
4. Sets `X-User-Admin: true` if claim `admin` is true  

WebSocket may pass the token as `?access_token=` when headers are unavailable.

---

## Routes

### `GET /health`

Gateway liveness (not proxied).

**Auth:** public  

**Success:** `200`

```json
{ "status": "ok", "service": "gateway" }
```

---

### `*` `/api/v1/auth/*` → auth service

Proxies the auth REST API as-is. Request/response contracts: `auth_service/docs/ENDPOINTS.md`.

**Public (POST only):**

| Path |
|------|
| `/api/v1/auth/verification` |
| `/api/v1/auth/signup` |
| `/api/v1/auth/login` |
| `/api/v1/auth/password/forgot` |
| `/api/v1/auth/password/reset` |
| `/api/v1/auth/token/refresh` |

All other `/api/v1/auth/*` methods/paths require Bearer.

---

### `*` `/graphql` → market service

Proxies GraphQL. Contract: `market_service/docs/ENDPOINTS.md`.

**Auth:** required  

```http
POST /graphql
Authorization: Bearer <access_token>
Content-Type: application/json
```

---

### `GET /ws` → chat service

Upgrades to WebSocket and proxies to chat `/ws` with identity headers.

**Auth:** required (`Authorization` or `?access_token=`)

```text
ws://localhost:8000/ws?access_token=<access_token>
```

Protocol and actions: `chat_service/docs/ENDPOINTS.md`.

---

## Gateway-only errors

| Status | Body / meaning |
|--------|----------------|
| `401` | `unauthorized` — missing/invalid access token |
| `403` | `origin not allowed` — WebSocket Origin not the configured CORS origin |
| `429` | `rate limit exceeded` |

Upstream status codes and bodies are forwarded unchanged (except the cases above).

---

## Summary

| Path | Upstream | Auth |
|------|----------|------|
| `GET /health` | gateway | public |
| `POST` public auth paths | auth | public |
| other `/api/v1/auth/*` | auth | Bearer |
| `/graphql` | market | Bearer |
| `GET /ws` | chat | Bearer / query token |
