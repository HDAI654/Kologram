-- Chat service schema (manual apply; no migration runner in this phase).
-- PostgreSQL 14+.
-- Apply: psql "$DATABASE_URL" -f internal/infrastructure/persistence/postgres/schema.sql

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ---------------------------------------------------------------------------
-- conversations — shared shell (one thread per buyer + listing)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS conversations (
    id                   UUID PRIMARY KEY,
    buyer_id             UUID        NOT NULL,
    seller_id            UUID        NOT NULL,
    listing_id           UUID        NOT NULL,
    is_read_only         BOOLEAN     NOT NULL DEFAULT FALSE,
    last_message_id      UUID        NULL,
    last_message_preview TEXT        NOT NULL DEFAULT '',
    last_message_at      TIMESTAMPTZ NOT NULL,
    created_at           TIMESTAMPTZ NOT NULL,
    updated_at           TIMESTAMPTZ NOT NULL,

    CONSTRAINT conversations_buyer_seller_distinct CHECK (buyer_id <> seller_id),
    CONSTRAINT conversations_buyer_listing_unique UNIQUE (buyer_id, listing_id)
);

CREATE INDEX IF NOT EXISTS conversations_listing_id_idx
    ON conversations (listing_id);

-- ListForUser sort support (joined with conversation_user_states).
CREATE INDEX IF NOT EXISTS conversations_last_message_at_id_idx
    ON conversations (last_message_at DESC, id DESC);

-- ---------------------------------------------------------------------------
-- conversation_user_states — per-user UI/read state (not shared)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS conversation_user_states (
    conversation_id       UUID        NOT NULL REFERENCES conversations (id),
    user_id               UUID        NOT NULL,
    last_read_message_id  UUID        NULL,
    unread_count          INTEGER     NOT NULL DEFAULT 0,
    is_archived           BOOLEAN     NOT NULL DEFAULT FALSE,
    is_hidden             BOOLEAN     NOT NULL DEFAULT FALSE,
    is_pinned             BOOLEAN     NOT NULL DEFAULT FALSE,
    muted_until           TIMESTAMPTZ NULL,
    updated_at            TIMESTAMPTZ NOT NULL,

    CONSTRAINT conversation_user_states_pk PRIMARY KEY (conversation_id, user_id),
    CONSTRAINT conversation_user_states_unread_non_negative CHECK (unread_count >= 0)
);

-- Inbox query: filter by user + hidden/archived, order pinned then activity.
CREATE INDEX IF NOT EXISTS conversation_user_states_inbox_idx
    ON conversation_user_states (user_id, is_hidden, is_archived, is_pinned DESC);

-- ---------------------------------------------------------------------------
-- messages — independent of conversation aggregate; soft-delete for everyone
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS messages (
    id                    UUID PRIMARY KEY,
    conversation_id       UUID        NOT NULL REFERENCES conversations (id),
    sender_id             UUID        NOT NULL,
    content               TEXT        NOT NULL,
    sent_at               TIMESTAMPTZ NOT NULL,
    client_message_id     UUID        NOT NULL,
    deleted_for_everyone  BOOLEAN     NOT NULL DEFAULT FALSE,
    deleted_at            TIMESTAMPTZ NULL,

    CONSTRAINT messages_sender_conversation_client_unique
        UNIQUE (sender_id, conversation_id, client_message_id)
);

-- Participant history (visible rows only).
CREATE INDEX IF NOT EXISTS messages_conversation_visible_sent_at_id_idx
    ON messages (conversation_id, sent_at DESC, id DESC)
    WHERE deleted_for_everyone = FALSE;

-- Admin / GetByID / idempotency paths may include soft-deleted rows.
CREATE INDEX IF NOT EXISTS messages_conversation_sent_at_id_idx
    ON messages (conversation_id, sent_at DESC, id DESC);

-- ---------------------------------------------------------------------------
-- user_blocks — global pair block (not conversation-scoped)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_blocks (
    blocker_id  UUID        NOT NULL,
    blocked_id  UUID        NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL,

    CONSTRAINT user_blocks_pk PRIMARY KEY (blocker_id, blocked_id),
    CONSTRAINT user_blocks_not_self CHECK (blocker_id <> blocked_id)
);

CREATE INDEX IF NOT EXISTS user_blocks_blocked_id_idx
    ON user_blocks (blocked_id);
