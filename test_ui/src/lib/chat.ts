import { getAccessToken, WS_URL } from './api';

type Envelope = { id?: string; type: string; ok?: boolean; payload?: any; error?: { code?: string; message?: string; field?: string }; [key: string]: any };
type Pending = { resolve: (value: any) => void; reject: (reason: Error) => void; timer: number };
let socket: WebSocket | null = null;
let connecting: Promise<void> | null = null;
let sequence = 0;
const pending = new Map<string, Pending>();
const listeners = new Set<(event: Envelope) => void>();
const statusListeners = new Set<(status: 'connecting' | 'connected' | 'disconnected') => void>();
let currentStatus: 'connecting' | 'connected' | 'disconnected' = 'disconnected';
function setStatus(status: typeof currentStatus) { currentStatus = status; statusListeners.forEach(fn => fn(status)); }
export function getChatStatus() { return currentStatus; }
export function onChatEvent(listener: (event: Envelope) => void) { listeners.add(listener); return () => { listeners.delete(listener); }; }
export function onChatStatus(listener: (status: typeof currentStatus) => void) { statusListeners.add(listener); listener(currentStatus); return () => { statusListeners.delete(listener); }; }

export function connectChat(): Promise<void> {
  if (socket?.readyState === WebSocket.OPEN) return Promise.resolve();
  if (connecting) return connecting;
  const token = getAccessToken();
  if (!token) return Promise.reject(new Error('Sign in to use messages.'));
  setStatus('connecting');
  connecting = new Promise<void>((resolve, reject) => {
    try {
      const url = `${WS_URL}${WS_URL.includes('?') ? '&' : '?'}access_token=${encodeURIComponent(token)}`;
      const ws = new WebSocket(url); socket = ws;
      const timeout = window.setTimeout(() => {
        if (ws.readyState !== WebSocket.OPEN) { ws.close(); reject(new Error('Chat connection timed out.')); }
      }, 12000);
      ws.onopen = () => { window.clearTimeout(timeout); setStatus('connected'); resolve(); };
      ws.onmessage = (message) => {
        try {
          const event = JSON.parse(message.data) as Envelope;
          if (event.id && pending.has(event.id)) {
            const item = pending.get(event.id)!; pending.delete(event.id); window.clearTimeout(item.timer);
            if (event.ok === false) item.reject(new Error(event.error?.message || 'The chat action failed.'));
            else item.resolve(event.payload ?? event);
          }
          listeners.forEach(fn => fn(event));
        } catch { /* Ignore malformed server frames. */ }
      };
      ws.onerror = () => { setStatus('disconnected'); };
      ws.onclose = () => {
        window.clearTimeout(timeout); setStatus('disconnected'); socket = null; connecting = null;
        pending.forEach(item => { window.clearTimeout(item.timer); item.reject(new Error('Chat connection closed.')); }); pending.clear();
      };
    } catch (error) { connecting = null; setStatus('disconnected'); reject(error instanceof Error ? error : new Error('Could not connect to chat.')); }
  }).finally(() => { connecting = null; });
  return connecting!;
}
export async function chatRequest(type: string, payload: Record<string, unknown> = {}) {
  await connectChat();
  if (!socket || socket.readyState !== WebSocket.OPEN) throw new Error('Chat is not connected.');
  const id = globalThis.crypto?.randomUUID?.() || `req-${Date.now()}-${++sequence}`;
  return new Promise<any>((resolve, reject) => {
    const timer = window.setTimeout(() => { pending.delete(id); reject(new Error('Chat server did not respond. Please try again.')); }, 15000);
    pending.set(id, { resolve, reject, timer });
    socket!.send(JSON.stringify({ id, type, payload }));
  });
}
export function closeChat() {
  socket?.close(); socket = null; connecting = null; setStatus('disconnected');
}
export function unwrapArray(value: any, ...keys: string[]): any[] {
  if (Array.isArray(value)) return value;
  for (const key of keys) if (Array.isArray(value?.[key])) return value[key];
  return [];
}
