# Domain model

Bounded contexts and core concepts as implemented. Shared IDs are **references**, not shared aggregates.

---

## Context map

```mermaid
flowchart LR
  subgraph Auth
    User
    Session
  end
  subgraph Market
    Category
    Listing
  end
  subgraph Chat
    Conversation
    Message
    UserBlock
  end
  subgraph Side["Notifications"]
    Email["Email jobs"]
  end

  User -.->|user_id| Listing
  User -.->|buyer / seller| Conversation
  Listing -.->|listing_id| Conversation
  Auth -->|events| Email
  Market -->|events| Email
  Chat -->|events| Email
```

| Context | Question it answers |
|---------|---------------------|
| **Auth** | Who is the user; may they sign in? |
| **Market** | What is for sale, by whom, in what state? |
| **Chat** | How do buyer and seller talk about a listing? |
| **Notifications** | Which facts trigger email? (no domain ownership) |

Admin mirrors Auth/Market tables for staff; it does not define marketplace rules.

---

## Auth

| Concept | Notes |
|---------|--------|
| **User** | UUID id, email, hashed password, status (`ACTIVE` / `SUSPENDED`) |
| **Session** | Device-bound; stored in Redis (or memory in pure dev) |
| **VerificationToken** | UUID; email verify or password reset |

Behaviors: signup, login (opaque failures), logout, password reset, account delete. Events on `auth.events` (e.g. `UserRegistered`, `UserLoggedIn`, `VerificationTokenCreated`).

---

## Market

| Concept | Notes |
|---------|--------|
| **Category** | Optional parent; inactive categories block new listings |
| **Listing** | Seller-owned; price, quantity, location, status, images |

**Listing status**

```mermaid
stateDiagram-v2
  [*] --> DRAFT
  DRAFT --> ACTIVE: publish
  ACTIVE --> SOLD
  ACTIVE --> CANCELLED
  ACTIVE --> EXPIRED
  ACTIVE --> SUSPENDED
```

Events on `listing.events` (created, published, status changed, updated, deleted, category created). Notifier currently no-ops these.

---

## Chat

| Concept | Notes |
|---------|--------|
| **Conversation** | One thread per (buyer, listing); seller from listing |
| **Message** | Soft-delete for everyone; idempotent `client_message_id` |
| **ConversationUserState** | Unread, archive, hide, pin, mute (per user) |
| **UserBlock** | Blocks messaging either way |

Listing in chat is a **read model** from market (`seller_id`, messaging allowed when ACTIVE). `is_read_only` freezes a thread; no OPEN/CLOSED conversation enum.

Events on `chat.events`: `ConversationStarted`, `MessageSent` (notifier no-op today). Realtime pushes on the socket are separate from broker events.

---

## Aggregates (compact)

```mermaid
classDiagram
  direction LR
  class User {
    UserId
    Email
    status
  }
  class Listing {
    ListingId
    sellerId
    status
    price
  }
  class Conversation {
    ConversationId
    buyerId
    sellerId
    listingId
    isReadOnly
  }
  class Message {
    MessageId
    content
    deletedForEveryone
  }
  User "1" --> "*" Listing : sells
  Listing "1" --> "*" Conversation : subject
  Conversation "1" *-- "*" Message
  User --> Conversation : buyer or seller
```

---

## Language

| Term | Meaning |
|------|---------|
| Listing | Seller offer under a category |
| Publish | DRAFT → ACTIVE |
| Conversation | Chat for one buyer + listing |
| Soft-delete | Hidden from participants; kept for audit |
| Session | Authenticated device login |

---

## Explicit non-goals

Reviews/ratings · conversation OPEN/CLOSED/ARCHIVED status · per-message `isRead` column (use user-state cursors) · shared listing snapshot table in chat.
