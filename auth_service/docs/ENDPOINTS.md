# Auth Service — Endpoints

REST API for authentication, account lifecycle, password management, and session management.

- **Protocol:** REST/HTTP via FastAPI.
- **API version:** `/api/v1`.
- **Auth:** protected endpoints require `Authorization: Bearer <access-token>`. The bearer header is parsed explicitly by the auth router; missing/invalid headers return `401 Unauthorized`.
- **Validation:** request bodies are validated by Pydantic. Schema validation failures use FastAPI's standard `422 Unprocessable Content` response.
- **Responses:** successful no-content operations return `204 No Content`; token operations return JSON bodies.
- **Health:** `GET /health` is outside the `/api/v1` prefix.

The service is mounted under `/api/v1` and the authentication router uses the `/auth` prefix. Therefore all authentication endpoints below are under `/api/v1/auth`.

---

## Endpoints

### `POST /api/v1/auth/verification` — send email verification link

Sends an email verification link for the supplied email address.

**Authentication:** public.

**Request body:**

```json
{
  "email": "user@example.com"
}
```

| Field | Type | Constraints |
|---|---|---|
| `email` | string | 3–254 characters |

**Success:** `204 No Content`.

**Errors:**

- `403 Forbidden` — email is blocked, or the account is suspended.
- `422 Unprocessable Content` — invalid email input.

The endpoint is implemented as `POST /verification` with a `204` response and maps `EmailBlockedError` / `AccountSuspendedError` to `403` and `InvalidEmailError` to `422`.

**Example:**

```http
POST /api/v1/auth/verification
Content-Type: application/json

{
  "email": "user@example.com"
}
```

---

### `POST /api/v1/auth/signup` — complete signup

Completes account signup using a verification token and returns an authenticated token pair.

**Authentication:** public; the verification token is supplied in the request body.

**Request body:**

```json
{
  "verify_token": "550e8400-e29b-41d4-a716-446655440000",
  "password": "correct-horse-battery-staple",
  "device": "web"
}
```

| Field | Type | Constraints |
|---|---|---|
| `verify_token` | string | exactly 36 characters |
| `password` | string | 8–128 characters |
| `device` | string | 1–50 characters; defaults to `"unknown"` |

**Success:** `201 Created`.

**Response:**

```json
{
  "access_token": "<jwt>",
  "refresh_token": "<refresh-token>"
}
```

**Errors:**

- `400 Bad Request` — invalid verification token.
- `409 Conflict` — user already exists.
- `422 Unprocessable Content` — invalid password.
- `503 Service Unavailable` — database connection/timeout failure.
- `500 Internal Server Error` — database operation failure.

The success status, response model, and exception-to-status mappings are defined in the router.

---

### `POST /api/v1/auth/login` — authenticate user

Authenticates a user with email/password for the supplied device context and returns an authenticated token pair.

**Authentication:** public.

**Request body:**

```json
{
  "email": "user@example.com",
  "password": "correct-horse-battery-staple",
  "device": "web"
}
```

| Field | Type | Constraints |
|---|---|---|
| `email` | string | 3–254 characters |
| `password` | string | 1–128 characters |
| `device` | string | 1–50 characters; defaults to `"unknown"` |

**Success:** `200 OK`.

**Response:**

```json
{
  "access_token": "<jwt>",
  "refresh_token": "<refresh-token>"
}
```

**Errors:**

- `401 Unauthorized` — invalid email/password.
- `422 Unprocessable Content` — invalid email input.
- `403 Forbidden` — account is suspended.

Login deliberately maps `InvalidEmailOrPasswordError` to the generic message `Invalid email or password`.

---

### `POST /api/v1/auth/logout` — logout current session

Terminates the current authenticated session using the access token and device context.

**Authentication:** required.

**Headers:**

```http
Authorization: Bearer <access-token>
```

**Request body:**

```json
{
  "device": "web"
}
```

| Field | Type | Constraints |
|---|---|---|
| `device` | string | 1–50 characters; defaults to `"unknown"` |

**Success:** `204 No Content`.

**Errors:**

- `401 Unauthorized` — missing/invalid bearer header, session not found, or token infrastructure failure.
- `403 Forbidden` — device does not match the authenticated session.

The bearer-token parser returns `401` for a missing/invalid `Authorization` header, and the logout route maps session/token failures to `401` and device mismatch to `403`.

---

### `DELETE /api/v1/auth/account` — delete authenticated account

Deletes the account associated with the authenticated access token and device context.

**Authentication:** required.

**Headers:**

```http
Authorization: Bearer <access-token>
```

**Request body:**

```json
{
  "device": "web"
}
```

| Field | Type | Constraints |
|---|---|---|
| `device` | string | 1–50 characters; defaults to `"unknown"` |

**Success:** `204 No Content`.

**Errors:**

- `401 Unauthorized` — missing/invalid bearer header or token infrastructure failure.
- `403 Forbidden` — device mismatch.
- `404 Not Found` — authenticated user/account was not found.

The route requires the bearer header and maps `DeviceMismatchError` to `403`, token infrastructure failures to `401`, and `UserNotFoundError` to `404`.

---

### `POST /api/v1/auth/password/forgot` — request password-reset email

Starts the password-reset flow for the supplied email address.

**Authentication:** public.

**Request body:**

```json
{
  "email": "user@example.com"
}
```

| Field | Type | Constraints |
|---|---|---|
| `email` | string | 3–254 characters |

**Success:** `204 No Content`.

**Errors:**

- `422 Unprocessable Content` — invalid email input.

The route invokes the password-reset verification use case and is configured with an `EventPublisher`.

---

### `POST /api/v1/auth/password/reset` — reset password with verification token

Resets a user's password using the verification token from the password-reset flow.

**Authentication:** public; authorization is provided by the reset token.

**Request body:**

```json
{
  "verify_token": "550e8400-e29b-41d4-a716-446655440000",
  "new_password": "new-secure-password"
}
```

| Field | Type | Constraints |
|---|---|---|
| `verify_token` | string | exactly 36 characters |
| `new_password` | string | 8–128 characters |

**Success:** `204 No Content`.

**Errors:**

- `400 Bad Request` — invalid verification token.
- `404 Not Found` — target user was not found.
- `422 Unprocessable Content` — invalid new password.

These mappings are defined directly by the reset route.

---

### `POST /api/v1/auth/password` — change password

Changes the password for the currently authenticated account.

**Authentication:** required.

**Headers:**

```http
Authorization: Bearer <access-token>
```

**Request body:**

```json
{
  "new_password": "new-secure-password",
  "device": "web"
}
```

| Field | Type | Constraints |
|---|---|---|
| `new_password` | string | 8–128 characters |
| `device` | string | 1–50 characters; defaults to `"unknown"` |

**Success:** `204 No Content`.

**Errors:**

- `401 Unauthorized` — missing/invalid bearer header, session not found, or token infrastructure failure.
- `403 Forbidden` — device mismatch.
- `422 Unprocessable Content` — invalid password.

The route requires the bearer header and maps session/token/device/password failures to the statuses above.

---

### `POST /api/v1/auth/sessions/revoke` — revoke a specific session

Revokes the session identified by `session_id` while authenticating the request with the current access token and device context.

**Authentication:** required.

**Headers:**

```http
Authorization: Bearer <access-token>
```

**Request body:**

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "device": "web"
}
```

| Field | Type | Constraints |
|---|---|---|
| `session_id` | string | exactly 36 characters |
| `device` | string | 1–50 characters; defaults to `"unknown"` |

**Success:** `204 No Content`.

**Errors:**

- `401 Unauthorized` — missing/invalid bearer header or token infrastructure failure.
- `403 Forbidden` — permission denied or device mismatch.
- `404 Not Found` — target session was not found.

The route explicitly distinguishes permission/device failures from a missing target session.

---

### `POST /api/v1/auth/sessions/revoke-others` — revoke all other sessions

Revokes all sessions other than the current authenticated session.

**Authentication:** required.

**Headers:**

```http
Authorization: Bearer <access-token>
```

**Request body:**

```json
{
  "device": "web"
}
```

| Field | Type | Constraints |
|---|---|---|
| `device` | string | 1–50 characters; defaults to `"unknown"` |

**Success:** `204 No Content`.

**Errors:**

- `401 Unauthorized` — missing/invalid bearer header, session not found, or token infrastructure failure.
- `403 Forbidden` — device mismatch.

The route uses the current access token to identify the caller and maps session/token failures to `401`.

---

### `POST /api/v1/auth/token/refresh` — rotate access/refresh tokens

Accepts a refresh token and returns a new access token and, when applicable, a rotated refresh token.

**Authentication:** public endpoint; the refresh token is supplied in the request body.

**Request body:**

```json
{
  "refresh_token": "<refresh-token>",
  "device": "web"
}
```

| Field | Type | Constraints |
|---|---|---|
| `refresh_token` | string | minimum 10 characters |
| `device` | string | 1–50 characters; defaults to `"unknown"` |

**Success:** `200 OK`.

**Response:**

```json
{
  "access_token": "<jwt>",
  "refresh_token": "<refresh-token-or-null>"
}
```

`refresh_token` in the response is nullable; the response model is `AccessTokenResponse`.

**Errors:**

- `401 Unauthorized` — session not found or token infrastructure failure.
- `403 Forbidden` — device mismatch.

The endpoint is implemented as `POST /token/refresh` and returns `200 OK`.

---

## `GET /health` — service health

Returns a lightweight application health response.

**Authentication:** public.

**Response:** `200 OK`.

```json
{
  "status": "ok",
  "service": "KologramAuth"
}
```

The `service` value is taken from `Config.APP_NAME`, so deployments can override the displayed service name. The health handler itself only returns this response; it does not perform a dependency health probe.

---

## Authentication

Protected endpoints use a bearer access token:

```http
Authorization: Bearer <access-token>
```

The router accepts only an `Authorization` value beginning with `Bearer ` and returns `401 Unauthorized` when the header is missing or does not use that form.

The service is configured with JWT tokens. The default signing algorithm is `RS256`, with configurable access-token and refresh-token lifetimes of 15 minutes and 43,200 minutes respectively. The rotate threshold defaults to 4,320 minutes. These are configuration defaults and can be overridden by environment variables.

---

## Request schemas

The current request models define the following reusable constraints: verification/login/forgot-password emails are 3–254 characters; signup/reset verification tokens and session IDs are 36 characters; passwords are 8–128 characters where password creation/reset applies; login passwords accept 1–128 characters; device values default to `"unknown"` and accept 1–50 characters; refresh tokens require at least 10 characters.

---

## Response schemas

### `TokenPairResponse`

Used by signup and login.

```json
{
  "access_token": "<jwt>",
  "refresh_token": "<refresh-token>"
}
```

Both fields are strings.

### `AccessTokenResponse`

Used by token refresh.

```json
{
  "access_token": "<jwt>",
  "refresh_token": "<refresh-token-or-null>"
}
```

`refresh_token` may be `null`.

### No-content responses

Logout, account deletion, password verification/reset/change, and session revocation endpoints return `204 No Content` with no response body. Their route declarations explicitly set the `204` status.

---

## Error response shape

Application/domain/infrastructure failures are translated at the HTTP presentation boundary into FastAPI `HTTPException` responses. The documented application errors therefore use the standard FastAPI JSON shape:

```json
{
  "detail": "Human-readable error message"
}
```

For request-schema validation failures generated by FastAPI/Pydantic, the standard `422` validation response is used.

The router maps known failures to transport statuses rather than exposing lower-layer exceptions directly.

---

## Endpoint summary

| Method | Path | Auth | Success |
|---|---|---|---|
| `POST` | `/api/v1/auth/verification` | Public | `204` |
| `POST` | `/api/v1/auth/signup` | Public | `201` |
| `POST` | `/api/v1/auth/login` | Public | `200` |
| `POST` | `/api/v1/auth/logout` | Bearer | `204` |
| `DELETE` | `/api/v1/auth/account` | Bearer | `204` |
| `POST` | `/api/v1/auth/password/forgot` | Public | `204` |
| `POST` | `/api/v1/auth/password/reset` | Public | `204` |
| `POST` | `/api/v1/auth/password` | Bearer | `204` |
| `POST` | `/api/v1/auth/sessions/revoke` | Bearer | `204` |
| `POST` | `/api/v1/auth/sessions/revoke-others` | Bearer | `204` |
| `POST` | `/api/v1/auth/token/refresh` | Public + refresh token | `200` |
| `GET` | `/health` | Public | `200` |