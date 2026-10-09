import { isLoggedIn, currentUserId, loadSession, logout as apiLogout } from "./api.js";
import { getTheme, setTheme } from "./store.js";
import { toast, escapeHtml, fmtMoney, statusBadge, el } from "./ui.js";
import * as api from "./api.js";
import { connectChat, disconnectChat, chatRequest, onEvent, uuid } from "./ws.js";

const app = document.getElementById("app");

function requireAuth() {
  if (!isLoggedIn()) {
    location.hash = "#/login";
    return false;
  }
  return true;
}

function shell(content) {
  const logged = isLoggedIn();
  const uid = currentUserId();
  return `
    <header class="topbar">
      <a class="brand" href="#/"><span>K</span> Kologram</a>
      <nav class="nav">
        <a href="#/" data-nav="home">Browse</a>
        ${logged ? `<a href="#/sell" data-nav="sell">Sell</a>` : ""}
        ${logged ? `<a href="#/my-listings" data-nav="my">My listings</a>` : ""}
        ${logged ? `<a href="#/chat" data-nav="chat">Messages</a>` : ""}
        ${logged ? `<a href="#/account" data-nav="account">Account</a>` : ""}
      </nav>
      <div class="topbar-actions">
        <button type="button" class="icon-btn" id="themeBtn" title="Toggle theme">◐</button>
        ${
          logged
            ? `<span class="user-chip" title="${escapeHtml(uid)}">${escapeHtml(loadSession()?.email || uid?.slice(0, 8) || "user")}</span>
               <button type="button" class="btn btn-ghost btn-sm" id="logoutBtn">Log out</button>`
            : `<a class="btn btn-sm" href="#/login">Log in</a>`
        }
      </div>
    </header>
    <main class="main">${content}</main>
    <div class="toast-host" id="toasts"></div>
  `;
}

function bindChrome() {
  setTheme(getTheme());
  $("#themeBtn")?.addEventListener("click", () => {
    const next = getTheme() === "dark" ? "light" : "dark";
    setTheme(next);
  });
  $("#logoutBtn")?.addEventListener("click", async () => {
    try {
      disconnectChat();
      await apiLogout();
      toast("Signed out", "ok");
    } catch (e) {
      toast(e.message, "error");
    }
    location.hash = "#/login";
    route();
  });
  const path = location.hash.slice(2).split("?")[0] || "home";
  document.querySelectorAll("[data-nav]").forEach((a) => {
    const key = a.getAttribute("data-nav");
    if (
      (key === "home" && (path === "" || path === "home" || path.startsWith("listing"))) ||
      (key === "sell" && path === "sell") ||
      (key === "my" && path === "my-listings") ||
      (key === "chat" && path.startsWith("chat")) ||
      (key === "account" && path === "account")
    ) {
      a.classList.add("active");
    }
  });
}

function $(sel) {
  return document.querySelector(sel);
}

/* ---------- Auth pages ---------- */

function pageLogin() {
  app.innerHTML = shell(`
    <div class="auth-shell card">
      <h1 class="card-title">Welcome back</h1>
      <p class="card-sub">Sign in to buy, sell, and message.</p>
      <form class="form" id="loginForm">
        <label>Email<input name="email" type="email" required autocomplete="username" /></label>
        <label>Password<input name="password" type="password" required minlength="1" autocomplete="current-password" /></label>
        <button class="btn" type="submit">Log in</button>
      </form>
      <p class="muted" style="margin-top:1rem">
        <a href="#/register">Create account</a> · <a href="#/forgot">Forgot password</a>
      </p>
    </div>
  `);
  bindChrome();
  $("#loginForm").onsubmit = async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    try {
      await api.login(fd.get("email"), fd.get("password"));
      toast("Logged in", "ok");
      location.hash = "#/";
      route();
    } catch (err) {
      toast(err.message, "error");
    }
  };
}

function pageRegister() {
  app.innerHTML = shell(`
    <div class="auth-shell stack">
      <div class="card">
        <h1 class="card-title">Create account</h1>
        <p class="card-sub">Step 1 — request a verification email, then complete signup with the token you receive.</p>
        <form class="form" id="verifyForm">
          <label>Email<input name="email" type="email" required /></label>
          <button class="btn" type="submit">Send verification</button>
        </form>
      </div>
      <div class="card">
        <h2 class="card-title">Complete signup</h2>
        <p class="card-sub">Paste the verification token from your email (or MailHog / logs).</p>
        <form class="form" id="signupForm">
          <label>Verification token<input name="token" required minlength="36" maxlength="36" class="mono" /></label>
          <label>Password<input name="password" type="password" required minlength="8" /></label>
          <button class="btn" type="submit">Sign up</button>
        </form>
        <p class="muted" style="margin-top:1rem"><a href="#/login">Already have an account?</a></p>
      </div>
    </div>
  `);
  bindChrome();
  $("#verifyForm").onsubmit = async (e) => {
    e.preventDefault();
    const email = new FormData(e.target).get("email");
    try {
      await api.sendVerification(email);
      toast("Verification requested — check email / MailHog", "ok");
    } catch (err) {
      toast(err.message, "error");
    }
  };
  $("#signupForm").onsubmit = async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    try {
      await api.signup(fd.get("token"), fd.get("password"));
      toast("Account created", "ok");
      location.hash = "#/";
      route();
    } catch (err) {
      toast(err.message, "error");
    }
  };
}

function pageForgot() {
  app.innerHTML = shell(`
    <div class="auth-shell stack">
      <div class="card">
        <h1 class="card-title">Forgot password</h1>
        <p class="card-sub">We send a reset token if the email is registered (no account enumeration).</p>
        <form class="form" id="forgotForm">
          <label>Email<input name="email" type="email" required /></label>
          <button class="btn" type="submit">Request reset</button>
        </form>
      </div>
      <div class="card">
        <h2 class="card-title">Reset with token</h2>
        <form class="form" id="resetForm">
          <label>Reset token<input name="token" required minlength="36" maxlength="36" class="mono" /></label>
          <label>New password<input name="password" type="password" required minlength="8" /></label>
          <button class="btn" type="submit">Set new password</button>
        </form>
        <p class="muted" style="margin-top:1rem"><a href="#/login">Back to login</a></p>
      </div>
    </div>
  `);
  bindChrome();
  $("#forgotForm").onsubmit = async (e) => {
    e.preventDefault();
    try {
      await api.forgotPassword(new FormData(e.target).get("email"));
      toast("If that email exists, a reset token was sent", "ok");
    } catch (err) {
      toast(err.message, "error");
    }
  };
  $("#resetForm").onsubmit = async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    try {
      await api.resetPassword(fd.get("token"), fd.get("password"));
      toast("Password updated — log in", "ok");
      location.hash = "#/login";
    } catch (err) {
      toast(err.message, "error");
    }
  };
}

function pageAccount() {
  if (!requireAuth()) return;
  const uid = currentUserId();
  app.innerHTML = shell(`
    <div class="hero">
      <h1>Account</h1>
      <p>Manage password and session.</p>
    </div>
    <div class="grid-2">
      <div class="card">
        <h2 class="card-title">Profile</h2>
        <p class="muted">User ID</p>
        <p class="mono">${escapeHtml(uid)}</p>
        <p class="muted" style="margin-top:0.75rem">Email</p>
        <p>${escapeHtml(loadSession()?.email || "—")}</p>
      </div>
      <div class="card">
        <h2 class="card-title">Change password</h2>
        <form class="form" id="pwForm">
          <label>New password<input name="password" type="password" required minlength="8" /></label>
          <button class="btn" type="submit">Update password</button>
        </form>
      </div>
      <div class="card">
        <h2 class="card-title">Danger zone</h2>
        <p class="card-sub">Permanently delete your account.</p>
        <button class="btn btn-danger" type="button" id="delBtn">Delete account</button>
      </div>
    </div>
  `);
  bindChrome();
  $("#pwForm").onsubmit = async (e) => {
    e.preventDefault();
    try {
      await api.changePassword(new FormData(e.target).get("password"));
      toast("Password changed", "ok");
    } catch (err) {
      toast(err.message, "error");
    }
  };
  $("#delBtn").onclick = async () => {
    if (!confirm("Delete account permanently?")) return;
    try {
      disconnectChat();
      await api.deleteAccount();
      toast("Account deleted", "ok");
      location.hash = "#/register";
      route();
    } catch (err) {
      toast(err.message, "error");
    }
  };
}

/* ---------- Market ---------- */

const SEARCH_Q = `
query Search($q: String, $limit: Int) {
  searchListings(input: { query: $q, limit: $limit }) {
    items {
      listingId title status location sellerId categoryId
      priceAmount currency
    }
  }
}`;

const CATEGORIES_Q = `
query { categories(activeOnly: true) { categoryId name isActive parentId } }`;

const LISTING_Q = `
query One($id: String!) {
  listing(listingId: $id) {
    listingId title description status location quantity sellerId categoryId
    priceAmount currency
    images { url sortOrder }
  }
}`;

const CREATE_M = `
mutation Create($input: CreateListingInput!) {
  createListing(input: $input) { listingId status }
}`;

const PUBLISH_M = `
mutation Pub($input: PublishListingInput!) {
  publishListing(input: $input) { listingId status }
}`;

const STATUS_M = `
mutation St($input: ChangeListingStatusInput!) {
  changeListingStatus(input: $input) { listingId status }
}`;

const DELETE_M = `
mutation Del($input: DeleteListingInput!) {
  deleteListing(input: $input) { listingId deleted }
}`;

const SELLER_Q = `
query Mine($sellerId: String!) {
  sellerListings(sellerId: $sellerId) {
    listingId title status location priceAmount currency
  }
}`;

async function pageHome() {
  app.innerHTML = shell(`
    <div class="hero">
      <h1>Discover listings</h1>
      <p>Search the marketplace catalog.</p>
    </div>
    <form class="row" id="searchForm" style="margin-bottom:1rem">
      <input name="q" placeholder="Search titles…" style="flex:1;min-width:200px" />
      <button class="btn" type="submit">Search</button>
    </form>
    <div id="results" class="stack"><p class="muted">Loading…</p></div>
  `);
  bindChrome();
  const render = async (q = "") => {
    const box = $("#results");
    if (!isLoggedIn()) {
      box.innerHTML = `<div class="empty">Log in to search the catalog (gateway requires auth for GraphQL).</div>`;
      return;
    }
    try {
      const data = await api.graphql(SEARCH_Q, { q: q || null, limit: 40 });
      const items = data.searchListings?.items || [];
      if (!items.length) {
        box.innerHTML = `<div class="empty">No listings found.</div>`;
        return;
      }
      box.innerHTML = `<div class="grid-2">${items
        .map(
          (it) => `
        <article class="listing-card" data-id="${escapeHtml(it.listingId)}">
          <div class="row" style="justify-content:space-between">
            <h3>${escapeHtml(it.title)}</h3>
            ${statusBadge(it.status)}
          </div>
          <div class="price">${fmtMoney(it.priceAmount, it.currency)}</div>
          <div class="muted">${escapeHtml(it.location || "")}</div>
        </article>`
        )
        .join("")}</div>`;
      box.querySelectorAll(".listing-card").forEach((c) => {
        c.onclick = () => {
          location.hash = `#/listing/${c.dataset.id}`;
        };
      });
    } catch (err) {
      box.innerHTML = `<div class="empty">${escapeHtml(err.message)}</div>`;
    }
  };
  $("#searchForm").onsubmit = (e) => {
    e.preventDefault();
    render(new FormData(e.target).get("q"));
  };
  render();
}

async function pageListing(id) {
  if (!requireAuth()) return;
  app.innerHTML = shell(`<p class="muted">Loading listing…</p>`);
  bindChrome();
  try {
    const data = await api.graphql(LISTING_Q, { id });
    const L = data.listing;
    if (!L) throw new Error("Listing not found");
    const mine = L.sellerId === currentUserId();
    app.innerHTML = shell(`
      <div class="card stack">
        <div class="row" style="justify-content:space-between">
          <h1 class="card-title" style="margin:0">${escapeHtml(L.title)}</h1>
          ${statusBadge(L.status)}
        </div>
        <div class="price">${fmtMoney(L.priceAmount, L.currency)}</div>
        <p>${escapeHtml(L.description || "")}</p>
        <p class="muted">Location: ${escapeHtml(L.location || "—")} · Qty: ${escapeHtml(L.quantity ?? "—")}</p>
        <p class="mono muted">Seller: ${escapeHtml(L.sellerId)}</p>
        <div class="row">
          ${
            !mine && String(L.status).toUpperCase() === "ACTIVE"
              ? `<button class="btn" type="button" id="msgBtn">Message seller</button>`
              : ""
          }
          <a class="btn btn-ghost" href="#/">Back</a>
        </div>
      </div>
    `);
    bindChrome();
    $("#msgBtn")?.addEventListener("click", async () => {
      try {
        await connectChat();
        const r = await chatRequest("start_conversation", { listing_id: id });
        const cid = r.conversation_id || r.ConversationID || r.id;
        toast("Conversation ready", "ok");
        location.hash = `#/chat/${cid}`;
        route();
      } catch (err) {
        toast(err.message, "error");
      }
    });
  } catch (err) {
    app.innerHTML = shell(`<div class="empty">${escapeHtml(err.message)}</div>`);
    bindChrome();
  }
}

async function pageSell() {
  if (!requireAuth()) return;
  let categories = [];
  try {
    const d = await api.graphql(CATEGORIES_Q);
    categories = d.categories || [];
  } catch (_) {}
  app.innerHTML = shell(`
    <div class="hero"><h1>New listing</h1><p>Creates a DRAFT — publish from My listings.</p></div>
    <div class="card">
      <form class="form" id="createForm">
        <label>Title<input name="title" required maxlength="200" /></label>
        <label>Description<textarea name="description" required></textarea></label>
        <div class="grid-2">
          <label>Price<input name="price" type="number" step="0.01" min="0" required /></label>
          <label>Currency
            <select name="currency">
              <option>USD</option><option>EUR</option><option>GBP</option><option>TRY</option><option>AED</option>
            </select>
          </label>
        </div>
        <div class="grid-2">
          <label>Quantity<input name="quantity" type="number" min="1" value="1" required /></label>
          <label>Location<input name="location" required /></label>
        </div>
        <label>Category
          <select name="category_id" required>
            <option value="">Select…</option>
            ${categories
              .filter((c) => c.isActive !== false)
              .map((c) => `<option value="${escapeHtml(c.categoryId)}">${escapeHtml(c.name)}</option>`)
              .join("")}
          </select>
        </label>
        <label>Image URLs (optional, comma-separated)<input name="images" placeholder="https://..." /></label>
        <button class="btn" type="submit">Create draft</button>
      </form>
    </div>
  `);
  bindChrome();
  $("#createForm").onsubmit = async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const sellerId = currentUserId();
    const images = String(fd.get("images") || "")
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    try {
      const data = await api.graphql(CREATE_M, {
        input: {
          sellerId,
          categoryId: fd.get("category_id"),
          title: fd.get("title"),
          description: fd.get("description"),
          priceAmount: String(fd.get("price")),
          currency: fd.get("currency"),
          quantity: Number(fd.get("quantity")),
          location: fd.get("location"),
          imageUrls: images.length ? images : null,
        },
      });
      const id = data.createListing?.listingId;
      toast("Draft created", "ok");
      location.hash = `#/my-listings`;
      route();
    } catch (err) {
      toast(err.message, "error");
    }
  };
}

async function pageMyListings() {
  if (!requireAuth()) return;
  app.innerHTML = shell(`
    <div class="hero row" style="justify-content:space-between;align-items:flex-end">
      <div><h1>My listings</h1><p>Publish, update status, or remove.</p></div>
      <a class="btn" href="#/sell">New listing</a>
    </div>
    <div id="mine" class="stack"><p class="muted">Loading…</p></div>
  `);
  bindChrome();
  const box = $("#mine");
  try {
    const data = await api.graphql(SELLER_Q, { sellerId: currentUserId() });
    const items = data.sellerListings || [];
    if (!items.length) {
      box.innerHTML = `<div class="empty">No listings yet. <a href="#/sell">Create one</a></div>`;
      return;
    }
    box.innerHTML = items
      .map((it) => {
        const st = String(it.status || "").toUpperCase();
        return `
        <div class="card row" style="justify-content:space-between;align-items:center" data-id="${escapeHtml(it.listingId)}">
          <div>
            <div class="row"><strong>${escapeHtml(it.title)}</strong> ${statusBadge(it.status)}</div>
            <div class="price">${fmtMoney(it.priceAmount, it.currency)}</div>
          </div>
          <div class="row">
            <a class="btn btn-ghost btn-sm" href="#/listing/${escapeHtml(it.listingId)}">View</a>
            ${st === "DRAFT" ? `<button class="btn btn-sm pub" type="button">Publish</button>` : ""}
            ${st === "ACTIVE" ? `<button class="btn btn-sm btn-ghost sold" type="button">Mark sold</button>` : ""}
            ${st === "ACTIVE" ? `<button class="btn btn-sm btn-ghost cancel" type="button">Cancel</button>` : ""}
            <button class="btn btn-sm btn-danger del" type="button">Delete</button>
          </div>
        </div>`;
      })
      .join("");
    const sellerId = currentUserId();
    box.querySelectorAll(".pub").forEach((btn) => {
      btn.onclick = async () => {
        const id = btn.closest("[data-id]").dataset.id;
        try {
          await api.graphql(PUBLISH_M, { input: { listingId: id, sellerId } });
          toast("Published", "ok");
          pageMyListings();
        } catch (e) {
          toast(e.message, "error");
        }
      };
    });
    box.querySelectorAll(".sold").forEach((btn) => {
      btn.onclick = async () => {
        const id = btn.closest("[data-id]").dataset.id;
        try {
          await api.graphql(STATUS_M, {
            input: { listingId: id, sellerId, newStatus: "SOLD" },
          });
          toast("Marked sold", "ok");
          pageMyListings();
        } catch (e) {
          toast(e.message, "error");
        }
      };
    });
    box.querySelectorAll(".cancel").forEach((btn) => {
      btn.onclick = async () => {
        const id = btn.closest("[data-id]").dataset.id;
        try {
          await api.graphql(STATUS_M, {
            input: { listingId: id, sellerId, newStatus: "CANCELLED" },
          });
          toast("Cancelled", "ok");
          pageMyListings();
        } catch (e) {
          toast(e.message, "error");
        }
      };
    });
    box.querySelectorAll(".del").forEach((btn) => {
      btn.onclick = async () => {
        if (!confirm("Delete listing?")) return;
        const id = btn.closest("[data-id]").dataset.id;
        try {
          await api.graphql(DELETE_M, { input: { listingId: id, sellerId } });
          toast("Deleted", "ok");
          pageMyListings();
        } catch (e) {
          toast(e.message, "error");
        }
      };
    });
  } catch (err) {
    box.innerHTML = `<div class="empty">${escapeHtml(err.message)}</div>`;
  }
}

/* ---------- Chat ---------- */

let chatUnsub = null;

async function pageChat(conversationId) {
  if (!requireAuth()) return;
  app.innerHTML = shell(`
    <div class="chat-layout">
      <aside class="chat-sidebar">
        <div class="chat-sidebar-head">
          <div class="tabs" id="convFilter">
            <button type="button" class="active" data-f="active">Active</button>
            <button type="button" data-f="archived">Archived</button>
          </div>
        </div>
        <div class="conv-list" id="convList"><p class="muted" style="padding:1rem">Connecting…</p></div>
      </aside>
      <section class="chat-thread" id="thread">
        <div class="empty">Select a conversation</div>
      </section>
    </div>
  `);
  bindChrome();

  try {
    await connectChat();
  } catch (e) {
    $("#convList").innerHTML = `<p class="muted" style="padding:1rem">${escapeHtml(e.message)}</p>`;
    return;
  }

  let filter = "active";
  let activeId = conversationId || null;

  const loadConvs = async () => {
    try {
      const r = await chatRequest("list_conversations", { filter, limit: 50 });
      const items = r.conversations || r.items || r.Conversations || [];
      const list = $("#convList");
      if (!items.length) {
        list.innerHTML = `<div class="empty">No conversations</div>`;
        return;
      }
      list.innerHTML = items
        .map((c) => {
          const id = c.conversation_id || c.id;
          const preview = c.last_message_preview || c.preview || "";
          const unread = c.unread_count || 0;
          return `<div class="conv-item ${id === activeId ? "active" : ""}" data-id="${escapeHtml(id)}">
            <div class="row" style="justify-content:space-between">
              <strong class="mono">${escapeHtml(String(id).slice(0, 8))}…</strong>
              ${unread ? `<span class="badge active">${unread}</span>` : ""}
            </div>
            <div class="preview">${escapeHtml(preview || "—")}</div>
          </div>`;
        })
        .join("");
      list.querySelectorAll(".conv-item").forEach((n) => {
        n.onclick = () => {
          activeId = n.dataset.id;
          location.hash = `#/chat/${activeId}`;
          openThread(activeId);
          loadConvs();
        };
      });
    } catch (e) {
      $("#convList").innerHTML = `<p class="muted" style="padding:1rem">${escapeHtml(e.message)}</p>`;
    }
  };

  const openThread = async (cid) => {
    const thread = $("#thread");
    if (!cid) {
      thread.innerHTML = `<div class="empty">Select a conversation</div>`;
      return;
    }
    thread.innerHTML = `<p class="muted" style="padding:1rem">Loading…</p>`;
    try {
      const [meta, msgs] = await Promise.all([
        chatRequest("get_conversation", { conversation_id: cid }),
        chatRequest("list_messages", { conversation_id: cid, limit: 100 }),
      ]);
      const messages = msgs.messages || msgs.items || [];
      const me = currentUserId();
      const other =
        meta.buyer_id === me ? meta.seller_id : meta.buyer_id || meta.peer_id || "";
      const readOnly = meta.is_read_only || meta.isReadOnly;
      thread.innerHTML = `
        <div class="chat-thread-head">
          <div>
            <strong class="mono">${escapeHtml(cid.slice(0, 13))}…</strong>
            ${readOnly ? `<span class="badge sold">read-only</span>` : ""}
            <div class="muted mono">Peer ${escapeHtml(String(other).slice(0, 8))}…</div>
          </div>
          <div class="dropdown" id="chatMenu">
            <button type="button" class="btn btn-ghost btn-sm" id="menuBtn">Actions ▾</button>
            <div class="dropdown-menu">
              <button type="button" data-act="archive">Archive / unarchive</button>
              <button type="button" data-act="hide">Hide</button>
              <button type="button" data-act="pin">Pin / unpin</button>
              <button type="button" data-act="mute">Mute 1h</button>
              <button type="button" data-act="block">Block peer</button>
              <button type="button" data-act="unblock">Unblock peer</button>
            </div>
          </div>
        </div>
        <div class="messages" id="msgs"></div>
        <form class="composer" id="sendForm">
          <input name="text" placeholder="${readOnly ? "Read-only" : "Message…"}" ${readOnly ? "disabled" : ""} required />
          <button class="btn" type="submit" ${readOnly ? "disabled" : ""}>Send</button>
        </form>`;

      const msgsEl = $("#msgs");
      const renderMsgs = (list) => {
        msgsEl.innerHTML = list
          .map((m) => {
            const mid = m.message_id || m.id;
            const sender = m.sender_id || m.senderId;
            const mine = sender === me;
            const content = m.content || m.body || "";
            return `<div class="bubble ${mine ? "mine" : ""}" data-mid="${escapeHtml(mid)}">
              <div>${escapeHtml(content)}</div>
              <div class="meta row" style="justify-content:space-between">
                <span>${escapeHtml(m.sent_at || m.sentAt || "")}</span>
                ${mine ? `<button type="button" class="btn-ghost btn-sm del-msg" data-mid="${escapeHtml(mid)}">Delete</button>` : ""}
              </div>
            </div>`;
          })
          .join("");
        msgsEl.scrollTop = msgsEl.scrollHeight;
        msgsEl.querySelectorAll(".del-msg").forEach((b) => {
          b.onclick = async () => {
            try {
              await chatRequest("delete_message_for_everyone", { message_id: b.dataset.mid });
              toast("Message deleted", "ok");
              openThread(cid);
            } catch (err) {
              toast(err.message, "error");
            }
          };
        });
      };
      renderMsgs(messages);

      if (messages.length) {
        const last = messages[messages.length - 1];
        const lastId = last.message_id || last.id;
        try {
          await chatRequest("mark_conversation_read", {
            conversation_id: cid,
            last_read_message_id: lastId,
          });
        } catch (_) {}
      }

      $("#menuBtn").onclick = (e) => {
        e.stopPropagation();
        $("#chatMenu").classList.toggle("open");
      };
      document.addEventListener(
        "click",
        () => $("#chatMenu")?.classList.remove("open"),
        { once: true }
      );

      $("#chatMenu").querySelectorAll("[data-act]").forEach((b) => {
        b.onclick = async () => {
          const act = b.dataset.act;
          try {
            if (act === "archive") {
              await chatRequest("archive_conversation", {
                conversation_id: cid,
                archive: true,
              });
            } else if (act === "hide") {
              await chatRequest("hide_conversation", { conversation_id: cid, hide: true });
            } else if (act === "pin") {
              await chatRequest("pin_conversation", { conversation_id: cid, pin: true });
            } else if (act === "mute") {
              const until = new Date(Date.now() + 3600e3).toISOString();
              await chatRequest("mute_conversation", {
                conversation_id: cid,
                mute: true,
                until,
              });
            } else if (act === "block" && other) {
              await chatRequest("block_user", { blocked_id: other });
            } else if (act === "unblock" && other) {
              await chatRequest("unblock_user", { blocked_id: other });
            }
            toast("Done", "ok");
            loadConvs();
          } catch (err) {
            toast(err.message, "error");
          }
        };
      });

      $("#sendForm").onsubmit = async (e) => {
        e.preventDefault();
        const text = new FormData(e.target).get("text");
        try {
          await chatRequest("send_message", {
            conversation_id: cid,
            client_message_id: uuid(),
            content: text,
          });
          e.target.reset();
          openThread(cid);
          loadConvs();
        } catch (err) {
          toast(err.message, "error");
        }
      };
    } catch (err) {
      thread.innerHTML = `<div class="empty">${escapeHtml(err.message)}</div>`;
    }
  };

  $("#convFilter").onclick = (e) => {
    const b = e.target.closest("button[data-f]");
    if (!b) return;
    filter = b.dataset.f;
    $("#convFilter").querySelectorAll("button").forEach((x) => x.classList.toggle("active", x === b));
    loadConvs();
  };

  if (chatUnsub) chatUnsub();
  chatUnsub = onEvent((msg) => {
    if (msg.type === "message_sent" || msg.type === "message_deleted") {
      loadConvs();
      if (activeId && (msg.conversation_id === activeId || msg.ConversationID === activeId)) {
        openThread(activeId);
      }
    }
  });

  await loadConvs();
  if (activeId) await openThread(activeId);
}

/* ---------- Router ---------- */

export function route() {
  const raw = location.hash.replace(/^#\/?/, "") || "home";
  const [path, ...rest] = raw.split("/");
  if (path === "login") return pageLogin();
  if (path === "register") return pageRegister();
  if (path === "forgot") return pageForgot();
  if (path === "account") return pageAccount();
  if (path === "sell") return pageSell();
  if (path === "my-listings") return pageMyListings();
  if (path === "listing" && rest[0]) return pageListing(rest[0]);
  if (path === "chat") return pageChat(rest[0] || null);
  return pageHome();
}

window.addEventListener("hashchange", route);
setTheme(getTheme());
route();
