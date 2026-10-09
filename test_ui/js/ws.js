import { WS_URL } from "./config.js";
import { loadSession } from "./store.js";

let socket = null;
let pending = new Map();
let seq = 0;
const listeners = new Set();

export function onEvent(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

function emit(msg) {
  listeners.forEach((fn) => {
    try {
      fn(msg);
    } catch (_) {}
  });
}

export function connectChat() {
  const s = loadSession();
  if (!s?.access_token) return Promise.reject(new Error("Not logged in"));
  if (socket && socket.readyState <= 1) return Promise.resolve();

  return new Promise((resolve, reject) => {
    const url = `${WS_URL}?access_token=${encodeURIComponent(s.access_token)}`;
    socket = new WebSocket(url);
    socket.onopen = () => resolve();
    socket.onerror = () => reject(new Error("WebSocket failed"));
    socket.onclose = () => {
      socket = null;
      pending.forEach(({ reject: rej }) => rej(new Error("Connection closed")));
      pending.clear();
    };
    socket.onmessage = (ev) => {
      let msg;
      try {
        msg = JSON.parse(ev.data);
      } catch {
        return;
      }
      if (msg.id && pending.has(msg.id)) {
        const { resolve: res, reject: rej } = pending.get(msg.id);
        pending.delete(msg.id);
        if (msg.ok) res(msg.payload);
        else rej(new Error(msg.error?.message || msg.error?.code || "Chat error"));
      } else {
        emit(msg);
      }
    };
  });
}

export function disconnectChat() {
  if (socket) {
    socket.close();
    socket = null;
  }
}

export function chatRequest(type, payload = {}) {
  if (!socket || socket.readyState !== 1) {
    return Promise.reject(new Error("Chat not connected"));
  }
  const id = `req-${++seq}-${Date.now()}`;
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject });
    socket.send(JSON.stringify({ id, type, payload }));
    setTimeout(() => {
      if (pending.has(id)) {
        pending.delete(id);
        reject(new Error("Chat request timeout"));
      }
    }, 20000);
  });
}

export function uuid() {
  if (crypto.randomUUID) return crypto.randomUUID();
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}
