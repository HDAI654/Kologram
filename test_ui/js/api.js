import { GATEWAY, DEVICE } from "./config.js";
import { loadSession, saveSession, clearSession, parseJwt } from "./store.js";

function authHeaders() {
  const s = loadSession();
  const h = { "Content-Type": "application/json" };
  if (s?.access_token) h.Authorization = `Bearer ${s.access_token}`;
  return h;
}

async function parseError(res) {
  const text = await res.text();
  try {
    const j = JSON.parse(text);
    return j.detail || j.message || j.error || text || res.statusText;
  } catch {
    return text || res.statusText;
  }
}

export async function api(path, { method = "GET", body, auth = true } = {}) {
  const headers = auth ? authHeaders() : { "Content-Type": "application/json" };
  if (!auth) headers["Content-Type"] = "application/json";
  const res = await fetch(`${GATEWAY}${path}`, {
    method,
    headers,
    body: body != null ? JSON.stringify(body) : undefined,
  });
  if (res.status === 204) return null;
  if (!res.ok) throw new Error(await parseError(res));
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) return res.json();
  return res.text();
}

export async function graphql(query, variables = {}) {
  const res = await fetch(`${GATEWAY}/graphql`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ query, variables }),
  });
  const data = await res.json();
  if (data.errors?.length) {
    throw new Error(data.errors.map((e) => e.message).join("; "));
  }
  return data.data;
}

export function currentUserId() {
  const s = loadSession();
  if (!s?.access_token) return null;
  return parseJwt(s.access_token)?.sub || null;
}

export function isLoggedIn() {
  return !!loadSession()?.access_token;
}

export async function login(email, password) {
  const data = await api("/api/v1/auth/login", {
    method: "POST",
    auth: false,
    body: { email, password, device: DEVICE },
  });
  saveSession({ ...data, email });
  return data;
}

export async function signup(verify_token, password) {
  const data = await api("/api/v1/auth/signup", {
    method: "POST",
    auth: false,
    body: { verify_token, password, device: DEVICE },
  });
  saveSession(data);
  return data;
}

export async function sendVerification(email) {
  return api("/api/v1/auth/verification", {
    method: "POST",
    auth: false,
    body: { email },
  });
}

export async function forgotPassword(email) {
  return api("/api/v1/auth/password/forgot", {
    method: "POST",
    auth: false,
    body: { email },
  });
}

export async function resetPassword(verify_token, new_password) {
  return api("/api/v1/auth/password/reset", {
    method: "POST",
    auth: false,
    body: { verify_token, new_password },
  });
}

export async function logout() {
  try {
    await api("/api/v1/auth/logout", { method: "POST", body: { device: DEVICE } });
  } finally {
    clearSession();
  }
}

export async function changePassword(new_password) {
  return api("/api/v1/auth/password", {
    method: "POST",
    body: { new_password, device: DEVICE },
  });
}

export async function deleteAccount() {
  await api("/api/v1/auth/account", {
    method: "DELETE",
    body: { device: DEVICE },
  });
  clearSession();
}

export async function refreshTokens() {
  const s = loadSession();
  if (!s?.refresh_token) throw new Error("No refresh token");
  const data = await api("/api/v1/auth/token/refresh", {
    method: "POST",
    auth: false,
    body: { refresh_token: s.refresh_token, device: DEVICE },
  });
  saveSession({ ...s, ...data });
  return data;
}

export { loadSession, clearSession, DEVICE };
