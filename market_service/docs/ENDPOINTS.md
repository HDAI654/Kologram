# Market Service — Endpoints

GraphQL API for listings, categories, and search.

- **GraphQL:** `POST /graphql` (GraphiQL enabled)
- **Health:** `GET /health`
- **Auth:** handled at the API Gateway. Seller-ownership checks happen in the service and return `FORBIDDEN` on mismatch.
- **Errors:** every GraphQL error carries `extensions.code` — `NOT_FOUND`, `FORBIDDEN`, `CONFLICT`, `VALIDATION_ERROR`, or `INTERNAL_ERROR`. HTTP status is always `200`; branch on the code, not the status.

---

## Queries

### `listing` — fetch one listing

```graphql
query {
  listing(listingId: "e2c8ebb5-2c85-4803-b680-30014786b6a3") {
    listingId
    title
    priceAmount
    currency
    status
    location
    images { url sortOrder }
    createdAt
  }
}
```

```json
{
  "data": {
    "listing": {
      "listingId": "e2c8ebb5-2c85-4803-b680-30014786b6a3",
      "title": "Vintage Film Camera",
      "priceAmount": "249.99",
      "currency": "USD",
      "status": "ACTIVE",
      "location": "Berlin",
      "images": [{ "url": "https://example.com/camera.jpg", "sortOrder": 0 }],
      "createdAt": "2025-01-01T12:00:00+00:00"
    }
  }
}
```

Unknown id → `NOT_FOUND`. Malformed UUID → `VALIDATION_ERROR`.

---

### `searchListings` — search & filter

Defaults: `status = "ACTIVE"`, `limit = 20`, `offset = 0`. `limit` is clamped to `[1, 100]`.

```graphql
query {
  searchListings(input: {
    query: "camera"
    categoryId: "34567b47-485f-41e0-9821-7ddac63603c4"
    minPrice: "100.00"
    maxPrice: "500.00"
    location: "Berlin"
  }) {
    items { listingId title priceAmount currency status location }
    limit
    offset
  }
}
```

```json
{
  "data": {
    "searchListings": {
      "items": [
        {
          "listingId": "e2c8ebb5-...",
          "title": "Vintage Film Camera",
          "priceAmount": "249.99",
          "currency": "USD",
          "status": "ACTIVE",
          "location": "Berlin"
        }
      ],
      "limit": 20,
      "offset": 0
    }
  }
}
```

No matches → `items: []`.

---

### `sellerListings` — listings for one seller

Returns newest first. `limit` defaults to `50`, `offset` to `0`.

```graphql
query {
  sellerListings(sellerId: "ec887b84-ef6b-4137-b7bd-8bcb83cf2f61", limit: 20) {
    listingId title status priceAmount currency createdAt
  }
}
```

```json
{
  "data": {
    "sellerListings": [
      { "listingId": "...", "title": "Vintage Film Camera", "status": "ACTIVE",
        "priceAmount": "249.99", "currency": "USD",
        "createdAt": "2025-01-01T12:00:00+00:00" }
    ]
  }
}
```

Unknown seller → `[]`.

---

### `categories` — taxonomy list

```graphql
query {
  categories(activeOnly: true) {
    categoryId name parentId isActive createdAt
  }
}
```

```json
{
  "data": {
    "categories": [
      { "categoryId": "34567b47-...", "name": "Electronics",
        "parentId": null, "isActive": true,
        "createdAt": "2025-01-01T12:00:00+00:00" }
    ]
  }
}
```

---

## Mutations

### `createListing` — new DRAFT listing

```graphql
mutation {
  createListing(input: {
    sellerId: "ec887b84-ef6b-4137-b7bd-8bcb83cf2f61"
    categoryId: "34567b47-485f-41e0-9821-7ddac63603c4"
    title: "Mechanical Keyboard"
    description: "Hot-swappable, tactile."
    priceAmount: "129.00"
    currency: "USD"
    quantity: 2
    location: "Berlin"
    imageUrls: ["https://example.com/kb.jpg"]
  }) { listingId status }
}
```

```json
{ "data": { "createListing": { "listingId": "...", "status": "DRAFT" } } }
```

Errors: `NOT_FOUND` (unknown category), `CONFLICT` (inactive category), `VALIDATION_ERROR`.

---

### `updateListing` — edit owned listing

Only allowed while status is `DRAFT`, `ACTIVE`, or `EXPIRED`. Omitted fields stay unchanged.

```graphql
mutation {
  updateListing(input: {
    listingId: "..."
    sellerId: "ec887b84-ef6b-4137-b7bd-8bcb83cf2f61"
    priceAmount: "119.00"
    location: "Amsterdam"
  }) { listingId status }
}
```

```json
{ "data": { "updateListing": { "listingId": "...", "status": "ACTIVE" } } }
```

Errors: `NOT_FOUND`, `FORBIDDEN`, `CONFLICT` (non-editable status), `VALIDATION_ERROR`.

---

### `deleteListing` — remove owned listing

```graphql
mutation {
  deleteListing(input: {
    listingId: "..."
    sellerId: "ec887b84-ef6b-4137-b7bd-8bcb83cf2f61"
  }) { listingId deleted }
}
```

```json
{ "data": { "deleteListing": { "listingId": "...", "deleted": true } } }
```

Errors: `NOT_FOUND`, `FORBIDDEN`.

---

### `publishListing` — DRAFT → ACTIVE

```graphql
mutation {
  publishListing(input: {
    listingId: "..."
    sellerId: "ec887b84-ef6b-4137-b7bd-8bcb83cf2f61"
  }) { listingId status }
}
```

```json
{ "data": { "publishListing": { "listingId": "...", "status": "ACTIVE" } } }
```

Errors: `NOT_FOUND`, `FORBIDDEN`, `CONFLICT` (not a DRAFT).

---

### `changeListingStatus` — lifecycle transitions

Allowed transitions:

```
DRAFT     → ACTIVE | CANCELLED
ACTIVE    → SOLD | EXPIRED | CANCELLED | SUSPENDED
EXPIRED   → ACTIVE | CANCELLED
SUSPENDED → ACTIVE | CANCELLED
SOLD      → terminal
CANCELLED → terminal
```

```graphql
mutation {
  changeListingStatus(input: {
    listingId: "..."
    sellerId: "ec887b84-ef6b-4137-b7bd-8bcb83cf2f61"
    newStatus: "SOLD"
  }) { listingId status }
}
```

```json
{ "data": { "changeListingStatus": { "listingId": "...", "status": "SOLD" } } }
```

Errors: `NOT_FOUND`, `FORBIDDEN`, `CONFLICT` (invalid transition), `VALIDATION_ERROR` (unknown status value).

---

### `createCategory` — taxonomy node

`name` is 2–80 chars after whitespace normalization. `parentId` is optional.

```graphql
mutation {
  createCategory(input: {
    name: "Watches"
    parentId: "34567b47-485f-41e0-9821-7ddac63603c4"
  }) { categoryId name parentId isActive }
}
```

```json
{
  "data": {
    "createCategory": {
      "categoryId": "...", "name": "Watches",
      "parentId": "34567b47-...", "isActive": true
    }
  }
}
```

Errors: `NOT_FOUND` (missing parent), `CONFLICT` (duplicate name), `VALIDATION_ERROR`.

---

## `GET /health`

```json
{ "status": "ok", "service": "Kologram" }
```

---

## Error response shape

```json
{
  "errors": [
    { "message": "Listing '...' not found",
      "extensions": { "code": "NOT_FOUND" } }
  ]
}
```

---

## Field notes

- **IDs** — UUID v4 strings.
- **Money** — `priceAmount` is a decimal string (≤ 2 decimals); `currency` ∈ `{USD, EUR, GBP, TRY, AED}`.
- **Timestamps** — ISO-8601 UTC strings.
- **Side effects** — mutations publish domain events through the configured `EventPublisher` after commit. Broker delivery is not atomic with the DB; consumers must dedupe.