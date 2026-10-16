/* Kologram — vanilla HTML/CSS/JS frontend
   API contract source: AI_ENDPOINT_GUID.md. No framework or build step required. */
(() => {
  'use strict';
  const API_BASE = (window.KOLOGRAM_API_BASE || 'http://localhost:8000').replace(/\/$/, '');
  const WS_URL = (window.KOLOGRAM_WS_URL || API_BASE.replace(/^http/, 'ws') + '/ws');
  const DEVICE = 'web';
  const ACCESS_KEY = 'kologram.access_token';
  const REFRESH_KEY = 'kologram.refresh_token';
  const SAVED_KEY = 'kologram.saved_listings';
  const SAVED_ITEMS_KEY = 'kologram.saved_items';
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const app = $('#app');

  const PHOTOS = {
    camera: 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=900&q=85',
    chair: 'https://images.unsplash.com/photo-1503602642458-232111445657?auto=format&fit=crop&w=900&q=85',
    bag: 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=900&q=85',
    lamp: 'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=900&q=85',
    record: 'https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=900&q=85',
    bike: 'https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=900&q=85',
    watch: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=85',
    plant: 'https://images.unsplash.com/photo-1485955900006-10f4d324d411?auto=format&fit=crop&w=900&q=85',
    headphones: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=85',
    ceramics: 'https://images.unsplash.com/photo-1578749556568-bc2c40e68b61?auto=format&fit=crop&w=900&q=85',
    hero: 'https://images.unsplash.com/photo-1607082349566-187342175e2f?auto=format&fit=crop&w=1400&q=85',
    auth: 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=1000&q=85'
  };
  const DEMO_ITEMS = [
    { listingId: 'demo-camera', title: 'Vintage film camera', priceAmount: '185.00', currency: 'USD', categoryLabel: 'Tech & gadgets', location: 'Brooklyn, NY', status: 'ACTIVE', cover: PHOTOS.camera, description: 'A beautifully kept 35mm film camera with a classic feel. Carefully stored and ready for its next chapter.', sellerId: 'preview-seller', quantity: 1, createdAt: '2026-10-08T10:00:00Z', quality: 'Editor’s pick' },
    { listingId: 'demo-chair', title: 'Mid-century accent chair', priceAmount: '240.00', currency: 'USD', categoryLabel: 'Home & living', location: 'Queens, NY', status: 'ACTIVE', cover: PHOTOS.chair, description: 'A sculptural accent chair with warm wood and a clean silhouette. A great statement piece for a thoughtful home.', sellerId: 'preview-seller', quantity: 1, createdAt: '2026-10-07T10:00:00Z', quality: 'Good find' },
    { listingId: 'demo-bag', title: 'Everyday leather tote', priceAmount: '78.00', currency: 'USD', categoryLabel: 'Style', location: 'Jersey City, NJ', status: 'ACTIVE', cover: PHOTOS.bag, description: 'A versatile everyday tote with plenty of room and a timeless shape.', sellerId: 'preview-seller', quantity: 1, createdAt: '2026-10-09T10:00:00Z', quality: 'Like new' },
    { listingId: 'demo-lamp', title: 'Soft-glow table lamp', priceAmount: '64.00', currency: 'USD', categoryLabel: 'Home & living', location: 'Brooklyn, NY', status: 'ACTIVE', cover: PHOTOS.lamp, description: 'Warm light, quiet lines, and a minimal shape that fits almost anywhere.', sellerId: 'preview-seller', quantity: 1, createdAt: '2026-10-02T10:00:00Z', quality: 'Good find' },
    { listingId: 'demo-record', title: 'Record player & vinyl set', priceAmount: '129.00', currency: 'USD', categoryLabel: 'Collectibles', location: 'Manhattan, NY', status: 'ACTIVE', cover: PHOTOS.record, description: 'A starter set for listening to records slowly. Ask the seller for a list of included albums.', sellerId: 'preview-seller', quantity: 1, createdAt: '2026-10-01T10:00:00Z', quality: 'Editor’s pick' },
    { listingId: 'demo-bike', title: 'City commuter bicycle', priceAmount: '310.00', currency: 'USD', categoryLabel: 'Outdoors', location: 'Hoboken, NJ', status: 'ACTIVE', cover: PHOTOS.bike, description: 'A practical city bike that makes everyday journeys feel a little more special.', sellerId: 'preview-seller', quantity: 1, createdAt: '2026-10-05T10:00:00Z', quality: 'Good find' },
    { listingId: 'demo-watch', title: 'Minimal steel wristwatch', priceAmount: '92.00', currency: 'USD', categoryLabel: 'Style', location: 'Brooklyn, NY', status: 'ACTIVE', cover: PHOTOS.watch, description: 'An understated stainless-steel watch with a clean dial and easy-to-style profile.', sellerId: 'preview-seller', quantity: 1, createdAt: '2026-10-04T10:00:00Z', quality: 'Like new' },
    { listingId: 'demo-plant', title: 'Ceramic planter with plant', priceAmount: '38.00', currency: 'USD', categoryLabel: 'Home & living', location: 'Astoria, NY', status: 'ACTIVE', cover: PHOTOS.plant, description: 'A healthy houseplant in a textured ceramic planter. A simple way to bring a little green indoors.', sellerId: 'preview-seller', quantity: 1, createdAt: '2026-10-03T10:00:00Z', quality: 'Good find' },
    { listingId: 'demo-headphones', title: 'Studio over-ear headphones', priceAmount: '115.00', currency: 'USD', categoryLabel: 'Tech & gadgets', location: 'Brooklyn, NY', status: 'ACTIVE', cover: PHOTOS.headphones, description: 'Comfortable over-ear headphones for focused listening, work, or long journeys.', sellerId: 'preview-seller', quantity: 1, createdAt: '2026-10-06T10:00:00Z', quality: 'Like new' }
  ];
  const STATIC_CATEGORIES = [
    { name: 'All finds', slug: 'all', icon: 'sparkles' },
    { name: 'Tech & gadgets', slug: 'tech', icon: 'device' },
    { name: 'Home & living', slug: 'home', icon: 'home' },
    { name: 'Style', slug: 'style', icon: 'bag' },
    { name: 'Outdoors', slug: 'outdoors', icon: 'sun' },
    { name: 'Collectibles', slug: 'collectibles', icon: 'disc' }
  ];
  const state = {
    page: 'discover', modal: null, authMode: 'login', authEmail: '',
    userId: getUserId(), token: localStorage.getItem(ACCESS_KEY),
    categories: [], items: DEMO_ITEMS.map(x => ({ ...x })), myItems: [],
    live: false, apiUnavailable: false, loadingItems: false, loadingMine: false, mineUnavailable: false,
    search: '', selectedCategory: 'all', minPrice: '', maxPrice: '', location: '', sort: 'recommended',
    filtersOpen: false, saved: new Set(readSaved()), savedItems: new Map(readSavedItems().map(item => [item.listingId, item])), detail: null, detailLoading: false, offset: 0, pageSize: 24, hasMore: false, loadingMore: false,
    editing: null, toastId: 0, toasts: [],
    chat: { socket: null, connectPromise: null, pending: new Map(), counter: 0, status: 'disconnected', conversations: [], activeId: null, active: null, messages: [], filter: 'active', loading: false, error: '', unsubscribed: false },
    confirm: null, accountTab: 'security', mobileThread: false
  };

  function icon(name, size = 18, cls = '') {
    const paths = {
      search: '<circle cx="11" cy="11" r="7.5"/><path d="m16.5 16.5 4 4"/>',
      arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>', back: '<path d="m15 18-6-6 6-6"/>',
      close: '<path d="m18 6-12 12M6 6l12 12"/>', check: '<path d="m5 12 4 4L19 6"/>',
      heart: '<path d="M20.8 8.8c0 5.2-8.8 10.1-8.8 10.1S3.2 14 3.2 8.8A4.7 4.7 0 0 1 12 6.1a4.7 4.7 0 0 1 8.8 2.7Z"/>',
      pin: '<path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
      chevron: '<path d="m6 9 6 6 6-6"/>', filter: '<path d="M4 7h16M7 12h10m-7 5h4"/><circle cx="8" cy="7" r="1.6"/><circle cx="15" cy="12" r="1.6"/>',
      sliders: '<path d="M4 7h8m4 0h4M4 17h4m4 0h8"/><circle cx="14" cy="7" r="2"/><circle cx="10" cy="17" r="2"/>',
      sparkles: '<path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3Z"/><path d="m19 14 .9 2.2L22 17l-2.1.8L19 20l-.8-2.2L16 17l2.2-.8L19 14Z"/>',
      device: '<rect x="4" y="3" width="16" height="18" rx="2.5"/><path d="M9 7h6M10 17h4"/>', home: '<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1Z"/><path d="M9 21v-7h6v7"/>',
      bag: '<path d="M5 8h14l1 13H4L5 8Z"/><path d="M9 8a3 3 0 0 1 6 0"/>', sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
      disc: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="2.5"/><path d="m18.3 5.7-4.5 4.5"/>',
      message: '<path d="M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7a8.4 8.4 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.4 8.4 0 0 1 3.8-.9h.5a8.5 8.5 0 0 1 8 8v.5Z"/>',
      plus: '<path d="M12 5v14M5 12h14"/>', menu: '<path d="M4 6h16M4 12h16M4 18h16"/>', user: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
      logout: '<path d="M10 17l5-5-5-5M15 12H3"/><path d="M12 3h7a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-7"/>',
      shield: '<path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11Z"/><path d="m9 12 2 2 4-4"/>',
      trash: '<path d="M3 6h18M8 6V4h8v2m3 0-1 14H6L5 6m4 4v6m6-6v6"/>', clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
      box: '<path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="M3 8v9l9 5 9-5V8M12 13v9"/>',
      refresh: '<path d="M20 7v5h-5M4 17v-5h5"/><path d="M5.6 9A7 7 0 0 1 17 6.5L20 12M4 12l3 5.5A7 7 0 0 0 18.4 15"/>',
      lock: '<rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V6a4 4 0 0 1 8 0v4"/>', eye: '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
      checkCircle: '<circle cx="12" cy="12" r="9"/><path d="m8 12 2.5 2.5L16 9"/>', alert: '<path d="m10.3 3.9-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.7-3.1l-8-14a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4m0 4h.01"/>',
      pinOff: '<path d="M12 17v5m7-12c0 1.8-2 4.4-4.2 6.4M5 7a7 7 0 0 1 13.8 0M4 4l16 16"/>',
      archive: '<rect x="3" y="4" width="18" height="5" rx="1"/><path d="M5 9v11h14V9m-8 4h2"/>',
      more: '<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>',
      send: '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>',
      chevrons: '<path d="m8 9 4-4 4 4M8 15l4 4 4-4"/>',
      info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v5m0-8h.01"/>',
      star: '<path d="m12 3 2.7 5.5 6.1.9-4.4 4.3 1 6.1-5.4-2.9-5.4 2.9 1-6.1-4.4-4.3 6.1-.9L12 3Z"/>',
      grid: '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
      edit: '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L8 18l-4 1 1-4Z"/>',
      external: '<path d="M14 3h7v7m-1-6-9 9"/><path d="M19 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h6"/>',
      sparkleSmall: '<path d="m12 2 1.2 7.1L20 12l-6.8 2.9L12 22l-2.9-7.1L2 12l7.1-2.9L12 2Z"/>',
      mail: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
      tag: '<path d="M20 13 11 22l-9-9V2h11l7 7a3 3 0 0 1 0 4Z"/><circle cx="7" cy="7" r="1"/>',
      sliders2: '<path d="M4 21v-7m0-4V3m8 18v-9m0-4V3m8 18v-5m0-4V3M1 14h6m2-6h6m2 8h6"/>'
    };
    return `<svg class="${cls}" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[name] || paths.sparkles}</svg>`;
  }
  function esc(value = '') {
    return String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }
  function getTokens() { return { access_token: localStorage.getItem(ACCESS_KEY), refresh_token: localStorage.getItem(REFRESH_KEY) }; }
  function getUserId() {
    const token = localStorage.getItem(ACCESS_KEY);
    if (!token) return null;
    try { return decodeJwt(token).sub || null; } catch { return null; }
  }
  function decodeJwt(token) {
    const segment = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    const padded = segment + '='.repeat((4 - segment.length % 4) % 4);
    const binary = atob(padded);
    const utf8 = decodeURIComponent([...binary].map(ch => '%' + ch.charCodeAt(0).toString(16).padStart(2, '0')).join(''));
    return JSON.parse(utf8);
  }
  function isAdmin() { try { return decodeJwt(getTokens().access_token).admin === true; } catch { return false; } }
  function readSaved() { try { return JSON.parse(localStorage.getItem(SAVED_KEY) || '[]'); } catch { return []; } }
  function readSavedItems() { try { const rows = JSON.parse(localStorage.getItem(SAVED_ITEMS_KEY) || '[]'); return Array.isArray(rows) ? rows.filter(item => item && item.listingId) : []; } catch { return []; } }
  function saveSaved() { localStorage.setItem(SAVED_KEY, JSON.stringify([...state.saved])); localStorage.setItem(SAVED_ITEMS_KEY, JSON.stringify([...state.savedItems.values()])); }
  function usd(amount, currency = 'USD') {
    const n = Number(amount);
    if (!Number.isFinite(n)) return esc(`${amount || ''} ${currency || ''}`.trim());
    try { return new Intl.NumberFormat('en-US', { style: 'currency', currency: currency || 'USD', maximumFractionDigits: 2 }).format(n); }
    catch { return `${currency || 'USD'} ${n.toFixed(2)}`; }
  }
  function relativeDate(value) {
    if (!value) return 'Recently';
    const date = new Date(value); if (Number.isNaN(date.getTime())) return 'Recently';
    const days = Math.max(0, Math.floor((Date.now() - date.getTime()) / 86400000));
    if (days === 0) return 'Today'; if (days === 1) return 'Yesterday'; if (days < 7) return `${days} days ago`;
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  }
  function shortTime(value) {
    if (!value) return '';
    const d = new Date(value); if (Number.isNaN(d.getTime())) return '';
    return d.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
  }
  function randomId() {
    if (crypto && crypto.randomUUID) return crypto.randomUUID();
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => { const r = Math.random() * 16 | 0; return (c === 'x' ? r : (r & 3 | 8)).toString(16); });
  }
  function showToast(message, kind = 'success', duration = 3600) {
    const id = ++state.toastId;
    state.toasts.push({ id, message, kind }); state.toasts = state.toasts.slice(-4);
    renderToasts();
    window.setTimeout(() => { state.toasts = state.toasts.filter(t => t.id !== id); renderToasts(); }, duration);
  }
  function renderToasts() {
    const region = $('#toast-region'); if (!region) return;
    region.innerHTML = state.toasts.map(t => `<div class="toast ${t.kind === 'error' ? 'error' : t.kind === 'info' ? 'info' : ''}" role="status">${icon(t.kind === 'error' ? 'alert' : t.kind === 'info' ? 'info' : 'checkCircle', 17)}<span>${esc(t.message)}</span><button data-action="dismiss-toast" data-id="${t.id}" aria-label="Dismiss">${icon('close', 14)}</button></div>`).join('');
  }
  function friendlyError(error, fallback = 'Something went wrong. Please try again.') {
    if (error?.status === 429) return 'You’re moving a little fast. Please wait a moment and retry.';
    if (error?.status === 403) return 'This action isn’t available for your account.';
    if (error?.status >= 500) return 'The service is having trouble. Please try again shortly.';
    return error?.message || fallback;
  }
  class ApiError extends Error {
    constructor(message, status, code) { super(message); this.name = 'ApiError'; this.status = status; this.code = code; }
  }
  async function readBody(response) {
    if (response.status === 204) return undefined;
    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) return response.json().catch(() => null);
    return response.text().then(t => t ? { detail: t } : null).catch(() => null);
  }
  function extractError(body, fallback = 'Request failed.') {
    if (body && typeof body.detail === 'string') return body.detail;
    if (body && Array.isArray(body.detail)) return body.detail.map(e => e?.msg || 'Invalid value').join(', ');
    if (body && typeof body.message === 'string') return body.message;
    return fallback;
  }
  async function refreshTokens() {
    const tokens = getTokens(); if (!tokens.refresh_token) return false;
    try {
      const response = await fetch(`${API_BASE}/api/v1/auth/token/refresh`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ refresh_token: tokens.refresh_token, device: DEVICE }) });
      const data = await readBody(response);
      if (!response.ok || !data?.access_token || !data?.refresh_token) { clearTokens(); return false; }
      localStorage.setItem(ACCESS_KEY, data.access_token); localStorage.setItem(REFRESH_KEY, data.refresh_token);
      state.token = data.access_token; state.userId = getUserId(); return true;
    } catch { return false; }
  }
  function clearTokens() {
    localStorage.removeItem(ACCESS_KEY); localStorage.removeItem(REFRESH_KEY);
    state.token = null; state.userId = null;
    closeChat(); state.chat.conversations = []; state.chat.active = null; state.chat.activeId = null; state.chat.messages = [];
  }
  async function apiRequest(path, options = {}, requiresAuth = true, retry = true) {
    const headers = new Headers(options.headers || {});
    if (options.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
    if (requiresAuth && getTokens().access_token) headers.set('Authorization', `Bearer ${getTokens().access_token}`);
    let response = await fetch(`${API_BASE}${path}`, { ...options, headers });
    if (response.status === 401 && requiresAuth && retry) {
      if (await refreshTokens()) return apiRequest(path, options, requiresAuth, false);
      clearTokens(); render();
    }
    const data = await readBody(response);
    if (!response.ok) throw new ApiError(extractError(data, response.status === 401 ? 'Invalid email or password.' : `Request failed (${response.status}).`), response.status);
    return data;
  }
  const publicRequest = (path, body, method = 'POST') => apiRequest(path, { method, ...(body === undefined ? {} : { body: JSON.stringify(body) }) }, false);
  async function graphql(query, variables = {}) {
    const result = await apiRequest('/graphql', { method: 'POST', body: JSON.stringify({ query, variables }) }, true);
    if (result?.errors?.length) { const first = result.errors[0]; throw new ApiError(first.message || 'The request could not be completed.', 200, first.extensions?.code); }
    if (!result || result.data === undefined) throw new ApiError('The server returned an empty GraphQL response.');
    return result.data;
  }
  const QUERIES = {
    categories: `query { categories(activeOnly: true) { categoryId name parentId isActive createdAt } }`,
    search: `query ($input: SearchListingsInput) { searchListings(input: $input) { items { listingId sellerId categoryId title priceAmount currency status location createdAt } limit offset } }`,
    listing: `query ($id: String!) { listing(listingId: $id) { listingId sellerId categoryId title description priceAmount currency quantity status location images { url sortOrder } createdAt updatedAt } }`,
    seller: `query ($sellerId: String!, $limit: Int, $offset: Int) { sellerListings(sellerId: $sellerId, limit: $limit, offset: $offset) { listingId title status priceAmount currency location createdAt } }`,
    create: `mutation ($input: CreateListingInput!) { createListing(input: $input) { listingId status } }`,
    update: `mutation ($input: UpdateListingInput!) { updateListing(input: $input) { listingId status } }`,
    publish: `mutation ($input: PublishListingInput!) { publishListing(input: $input) { listingId status } }`,
    status: `mutation ($input: ChangeListingStatusInput!) { changeListingStatus(input: $input) { listingId status } }`,
    delete: `mutation ($input: DeleteListingInput!) { deleteListing(input: $input) { listingId deleted } }`
  };
  function fallbackCover(item, index = 0) {
    if (item?.cover) return item.cover;
    const category = String(item?.categoryLabel || item?.categoryName || item?.categoryId || '').toLowerCase();
    if (category.includes('tech') || category.includes('electronic')) return [PHOTOS.headphones, PHOTOS.camera, PHOTOS.watch][index % 3];
    if (category.includes('home') || category.includes('furniture')) return [PHOTOS.chair, PHOTOS.lamp, PHOTOS.plant, PHOTOS.ceramics][index % 4];
    if (category.includes('style') || category.includes('fashion')) return [PHOTOS.bag, PHOTOS.watch][index % 2];
    if (category.includes('outdoor') || category.includes('sport')) return [PHOTOS.bike, PHOTOS.plant][index % 2];
    if (category.includes('collect')) return [PHOTOS.record, PHOTOS.ceramics][index % 2];
    return [PHOTOS.camera, PHOTOS.chair, PHOTOS.bag, PHOTOS.lamp, PHOTOS.record, PHOTOS.bike, PHOTOS.watch, PHOTOS.plant, PHOTOS.headphones][index % 9];
  }
  function normalizeListing(item, index = 0) {
    const imageList = Array.isArray(item?.images) ? [...item.images].sort((a, b) => (a.sortOrder || 0) - (b.sortOrder || 0)) : [];
    const cover = imageList.find(x => x?.url)?.url || item?.cover || fallbackCover(item, index);
    const cat = state.categories.find(c => c.categoryId === item?.categoryId);
    return { ...item, listingId: item?.listingId || item?.id || `unknown-${index}`, title: item?.title || 'Untitled listing', priceAmount: item?.priceAmount ?? '—', currency: item?.currency || 'USD', location: item?.location || 'Location not listed', categoryLabel: item?.categoryLabel || cat?.name || 'Marketplace find', cover, description: item?.description || 'Ask the seller for more details about this item.', status: item?.status || 'ACTIVE', sellerId: item?.sellerId || '', quantity: item?.quantity ?? 1 };
  }
  function categoryIdFromSelection() {
    if (state.selectedCategory === 'all') return null;
    return state.categories.find(c => c.categoryId === state.selectedCategory)?.categoryId || null;
  }
  function previewFilter() {
    let items = [...DEMO_ITEMS].map(x => ({ ...x }));
    const q = state.search.toLowerCase().trim();
    if (q) items = items.filter(x => `${x.title} ${x.description} ${x.categoryLabel} ${x.location}`.toLowerCase().includes(q));
    if (state.selectedCategory !== 'all' && !state.categories.some(c => c.categoryId === state.selectedCategory)) {
      const cat = STATIC_CATEGORIES.find(c => c.slug === state.selectedCategory);
      if (cat) items = items.filter(x => x.categoryLabel === cat.name);
    }
    if (state.minPrice !== '') items = items.filter(x => Number(x.priceAmount) >= Number(state.minPrice));
    if (state.maxPrice !== '') items = items.filter(x => Number(x.priceAmount) <= Number(state.maxPrice));
    if (state.location) items = items.filter(x => x.location.toLowerCase().includes(state.location.toLowerCase()));
    if (state.sort === 'price-low') items.sort((a, b) => Number(a.priceAmount) - Number(b.priceAmount));
    if (state.sort === 'price-high') items.sort((a, b) => Number(b.priceAmount) - Number(a.priceAmount));
    if (state.sort === 'newest') items.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    return items;
  }
  async function loadCategories() {
    if (!state.userId) return;
    try { const data = await graphql(QUERIES.categories); state.categories = (data.categories || []).filter(c => c.isActive !== false); }
    catch (e) { console.warn('Categories could not be loaded:', e); state.categories = []; }
  }
  async function loadExplore() {
    if (!state.userId) { state.live = false; state.apiUnavailable = false; state.hasMore = false; state.offset = 0; state.items = previewFilter(); render(); return; }
    state.loadingItems = true; state.loadingMore = false; state.hasMore = false; state.offset = 0; state.apiUnavailable = false; render();
    try {
      if (!state.categories.length) await loadCategories();
      const variables = { input: { query: state.search || null, categoryId: categoryIdFromSelection(), minPrice: state.minPrice ? Number(state.minPrice).toFixed(2) : null, maxPrice: state.maxPrice ? Number(state.maxPrice).toFixed(2) : null, location: state.location || null, status: 'ACTIVE', limit: state.pageSize, offset: 0 } };
      const data = await graphql(QUERIES.search, variables);
      const result = data.searchListings || {};
      state.items = (result.items || []).map(normalizeListing); state.offset = 0; state.hasMore = (result.items || []).length >= state.pageSize;
      if (state.sort === 'price-low') state.items.sort((a,b) => Number(a.priceAmount) - Number(b.priceAmount));
      if (state.sort === 'price-high') state.items.sort((a,b) => Number(b.priceAmount) - Number(a.priceAmount));
      state.live = true; state.apiUnavailable = false;
    } catch (e) {
      state.live = false; state.apiUnavailable = true; state.hasMore = false; state.items = previewFilter();
      console.error('Marketplace query failed:', e);
    } finally { state.loadingItems = false; render(); }
  }
  async function loadMoreListings() {
    if (!state.userId || !state.live || !state.hasMore || state.loadingMore) return;
    state.loadingMore = true; render();
    try {
      const nextOffset = state.offset + state.pageSize;
      const variables = { input: { query: state.search || null, categoryId: categoryIdFromSelection(), minPrice: state.minPrice ? Number(state.minPrice).toFixed(2) : null, maxPrice: state.maxPrice ? Number(state.maxPrice).toFixed(2) : null, location: state.location || null, status: 'ACTIVE', limit: state.pageSize, offset: nextOffset } };
      const data = await graphql(QUERIES.search, variables);
      const result = data.searchListings || {}; const rows = result.items || [];
      state.items = state.items.concat(rows.map((item, i) => normalizeListing(item, state.items.length + i)));
      state.offset = nextOffset; state.hasMore = rows.length >= state.pageSize;
      if (state.sort === 'price-low') state.items.sort((a,b) => Number(a.priceAmount)-Number(b.priceAmount));
      else if (state.sort === 'price-high') state.items.sort((a,b) => Number(b.priceAmount)-Number(a.priceAmount));
      else if (state.sort === 'newest') state.items.sort((a,b) => new Date(b.createdAt)-new Date(a.createdAt));
    } catch (e) { showToast(friendlyError(e, 'Could not load more listings.'), 'error'); }
    finally { state.loadingMore = false; render(); }
  }

  async function loadMyListings() {
    if (!state.userId) { openAuth('login'); return; }
    state.loadingMine = true; state.mineUnavailable = false; render();
    try {
      const data = await graphql(QUERIES.seller, { sellerId: state.userId, limit: 100, offset: 0 });
      state.myItems = (data.sellerListings || []).map(normalizeListing); state.loadingMine = false; state.mineUnavailable = false; render();
    } catch (e) { state.loadingMine = false; state.mineUnavailable = true; render(); showToast(friendlyError(e, 'Could not load your listings.'), 'error'); }
  }

  function renderHeader() {
    const nav = [
      ['discover', 'Explore', 'grid'], ['messages', 'Messages', 'message'], ['my-listings', 'My listings', 'box'], ['account', 'Account', 'user']
    ];
    return `<header class="topbar">
      <a href="#discover" class="brand" data-action="navigate" data-page="discover" aria-label="Kologram home"><span class="brand-mark">k<span>.</span></span><span><span class="brand-word">kologram<span>.</span></span><span class="brand-mini">A marketplace with a point of view</span></span></a>
      <form class="head-search" data-form="header-search" role="search">${icon('search', 18)}<label class="sr-only" for="global-search">Search listings</label><input id="global-search" type="search" name="query" placeholder="Find something worth keeping…" value="${esc(state.search)}" autocomplete="off"><span class="search-shortcut">↵</span></form>
      <nav class="nav-links" aria-label="Main navigation">${nav.map(([page,label,ic]) => `<button class="nav-link ${state.page === page ? 'active' : ''}" data-action="navigate" data-page="${page}" aria-label="${label}" ${state.page === page ? 'aria-current="page"' : ''}>${icon(ic,19,'nav-icon')}<span>${label}</span></button>`).join('')}</nav>
      <div class="top-actions"><button class="btn-icon" data-action="saved-view" aria-label="Saved finds">${icon('heart',18)}${state.saved.size ? `<i class="saved-dot"></i>` : ''}</button>${state.userId ? `<button class="btn btn-primary desktop-sell" data-action="navigate" data-page="sell">${icon('plus',17)} Sell something</button><button class="avatar" data-action="navigate" data-page="account" aria-label="Open account">${esc((state.userId || 'U').slice(0,1).toUpperCase())}</button>` : `<button class="btn btn-quiet" data-action="open-auth" data-mode="login">Log in</button><button class="btn btn-primary" data-action="open-auth" data-mode="login">Get started ${icon('arrow',15)}</button>`}</div>
    </header>`;
  }
  function renderHero() {
    return `<section class="hero"><div class="hero-copy"><div class="eyebrow">A little less ordinary</div><h1 class="display">Good things find <em>good people.</em></h1><p>Discover pre-loved pieces, thoughtful finds, and things with a story. Buy and sell with people who get it.</p><div class="hero-actions"><button class="btn btn-primary" data-action="scroll-market">Explore the marketplace ${icon('arrow',16)}</button><button class="btn btn-secondary" data-action="navigate" data-page="sell">${icon('plus',16)} List an item</button></div><div class="hero-note"><div class="avatar-stack"><span>J</span><span>M</span><span>A</span></div><span>Made for finding your next favorite thing.</span></div></div><div class="hero-visual"><img class="hero-image" src="${PHOTOS.hero}" alt="Carefully chosen objects ready for a new home" loading="eager" onerror="this.onerror=null;this.src='${PHOTOS.chair}'"><span class="hero-orb"></span><div class="floating-note note-top"><span class="note-icon">${icon('sparkles',18)}</span><span><b>Finds with a story</b><small>Discover something different</small></span></div><div class="floating-note note-bottom"><span class="note-icon">${icon('checkCircle',18)}</span><span><b>A more thoughtful marketplace</b><small>Buy well. Pass good things on.</small></span></div></div></section>
    <div class="trust-row"><span class="trust-item">${icon('shield',16)} People-first marketplace</span><span class="trust-item">${icon('refresh',16)} Give great things another life</span><span class="trust-item">${icon('heart',16)} Find pieces you'll keep</span></div>`;
  }
  function renderCategories() {
    let cats;
    if (state.userId && !state.apiUnavailable) cats = [{ categoryId: 'all', name: 'All finds' }, ...state.categories];
    else cats = STATIC_CATEGORIES.map(c => ({ ...c, categoryId: c.slug }));
    return `<div class="category-strip" role="group" aria-label="Filter by category">${cats.map((cat, i) => {
      const selected = state.selectedCategory === cat.categoryId || (state.selectedCategory === 'all' && cat.categoryId === 'all');
      return `<button class="category-pill ${selected ? 'active' : ''}" data-action="category" data-category="${esc(cat.categoryId)}">${i === 0 ? `<span class="cat-dot"></span>` : ''}${esc(cat.name)}</button>`;
    }).join('')}</div>`;
  }
  function renderFilters() {
    let categoryChoices = state.categories.length ? state.categories.map(c => `<option value="${esc(c.categoryId)}" ${state.selectedCategory === c.categoryId ? 'selected' : ''}>${esc(c.name)}</option>`).join('') : '';
    return `<aside class="filter-panel ${state.filtersOpen ? 'open' : ''}" aria-label="Search filters"><div class="filter-head"><h3>Refine your search</h3><button class="btn btn-quiet btn-small" data-action="reset-filters">Reset</button></div><form data-form="filters"><div class="filter-layout"><div class="filter-group"><label class="filter-label" for="filter-location">Location</label><input class="filter-input" id="filter-location" name="location" placeholder="City or area" value="${esc(state.location)}" maxlength="100"></div><div class="filter-group"><span class="filter-label">Price range</span><div class="filter-range"><label class="sr-only" for="min-price">Minimum price</label><input class="filter-input" id="min-price" name="minPrice" type="number" min="0" step="0.01" placeholder="Min $" value="${esc(state.minPrice)}"><label class="sr-only" for="max-price">Maximum price</label><input class="filter-input" id="max-price" name="maxPrice" type="number" min="0" step="0.01" placeholder="Max $" value="${esc(state.maxPrice)}"></div></div>${state.categories.length ? `<div class="filter-group"><label class="filter-label" for="filter-category">Category</label><select class="filter-input" id="filter-category" name="categoryId"><option value="all">All categories</option>${categoryChoices}</select></div>` : ''}</div><div class="filter-actions" style="margin-top:17px"><button class="btn btn-primary" type="submit">Apply filters</button><button class="btn btn-secondary" type="button" data-action="filter-toggle">Done</button></div></form></aside>`;
  }
  function renderCard(item, i) {
    const liveId = !String(item.listingId).startsWith('demo-');
    const saved = state.saved.has(item.listingId);
    const badge = item.quality || (item.status === 'ACTIVE' ? 'Available now' : item.status);
    return `<article class="product-card" tabindex="0" role="group" aria-label="View ${esc(item.title)}" data-card-id="${esc(item.listingId)}" data-live="${liveId ? '1' : '0'}">
      <div class="product-photo"><img src="${esc(item.cover || fallbackCover(item,i))}" alt="${esc(item.title)}" loading="lazy" onerror="this.onerror=null;this.src='${PHOTOS.camera}'"><span class="product-badge">${esc(badge)}</span><button class="heart-btn ${saved ? 'saved' : ''}" data-action="toggle-save" data-id="${esc(item.listingId)}" aria-label="${saved ? 'Remove saved item' : 'Save item'}" aria-pressed="${saved}">${icon('heart',17)}</button></div>
      <div class="product-info"><div class="product-kicker">${esc(item.categoryLabel || 'Marketplace find')}</div><div class="product-title-row"><h3 class="product-title">${esc(item.title)}</h3><span class="product-price">${usd(item.priceAmount,item.currency)}</span></div><div class="product-meta">${icon('pin',13)}<span>${esc(item.location || 'Location not listed')}</span><span class="dot-sep"></span><span>${esc(relativeDate(item.createdAt))}</span></div></div>
    </article>`;
  }
  function renderDiscover() {
    const items = state.loadingItems ? `<div class="listing-skeleton"></div><div class="listing-skeleton"></div><div class="listing-skeleton"></div>` : state.items.length ? state.items.map(renderCard).join('') : `<div class="empty-state"> <div class="empty-illustration">${icon('search',24)}</div><h3>No finds just yet</h3><p>Try a different search or loosen your filters. Your next good find might be one word away.</p><button class="btn btn-secondary" data-action="reset-filters">Clear all filters</button></div>`;
    const listingCount = state.loadingItems ? 'Finding good things…' : `${state.items.length} ${state.live ? 'listings' : 'curated finds'}${state.search ? ` for “${esc(state.search)}”` : ''}`;
    return `<main class="page-wrap">${renderHero()}<section id="marketplace"><div class="section-head"><div><div class="eyebrow">The good stuff</div><h2>Finds worth finding.</h2><p>One-of-a-kind pieces, ready for their next chapter.</p></div><button class="btn btn-secondary" data-action="navigate" data-page="my-listings">${icon('box',16)} Manage your listings</button></div>
      ${!state.userId ? `<div class="preview-note">${icon('info',16)} <span><b>Preview mode.</b> These are sample listings so you can explore the design. Log in to browse live items from your marketplace API.</span></div>` : state.apiUnavailable ? `<div class="preview-note">${icon('alert',16)} <span><b>Live inventory is unavailable.</b> Showing sample listings for now—not real marketplace results. Check that the gateway at <code>${esc(API_BASE)}</code> is running, then retry.</span><button class="text-link" data-action="retry-explore">Retry</button></div>` : ''}
      ${renderCategories()}<div class="browse-toolbar"><span class="results-count" id="result-count">${listingCount}</span><div class="toolbar-right"><button class="btn btn-secondary btn-small" data-action="filter-toggle">${icon('sliders',15)} Filters</button><label class="sr-only" for="sort-listings">Sort listings</label><select class="select-control" id="sort-listings" name="sort"><option value="recommended" ${state.sort==='recommended'?'selected':''}>Recommended</option><option value="newest" ${state.sort==='newest'?'selected':''}>Newest first</option><option value="price-low" ${state.sort==='price-low'?'selected':''}>Price: low to high</option><option value="price-high" ${state.sort==='price-high'?'selected':''}>Price: high to low</option></select></div></div>
      <div class="content-layout">${renderFilters()}<div><div class="product-grid" id="product-grid">${items}</div>${!state.loadingItems && state.live && state.hasMore ? `<div class="pagination"><button class="btn btn-secondary" data-action="load-more" ${state.loadingMore ? 'disabled' : ''}>${state.loadingMore ? '<span class="spinner"></span> Loading…' : `Explore more finds ${icon('arrow',15)}`}</button></div>` : ''}</div></div></section></main>`;
  }
  function renderAuthRequired(title, detail, action = 'open-auth') {
    return `<div class="empty-state"><div class="empty-illustration">${icon('lock',26)}</div><h3>${esc(title)}</h3><p>${esc(detail)}</p><button class="btn btn-primary" data-action="${action}" data-mode="login">Log in to continue ${icon('arrow',15)}</button></div>`;
  }
  function renderSell() {
    if (!state.userId) return `<main class="page-wrap"><div class="page-heading"><div><div class="eyebrow">Pass it on</div><h1>Give a good thing<br>its next chapter.</h1><p>Thoughtfully describe what you're selling. The right person will find it.</p></div></div>${renderAuthRequired('Ready to sell something?','Log in to create a listing, manage offers, and talk to interested buyers.')}</main>`;
    const item = state.editing || {};
    const categoryOptions = state.categories.map(c => `<option value="${esc(c.categoryId)}" ${item.categoryId === c.categoryId ? 'selected' : ''}>${esc(c.name)}</option>`).join('');
    return `<main class="page-wrap"><div class="page-heading"><div><div class="eyebrow">Your little corner of the marketplace</div><h1>${state.editing ? 'Polish your listing.' : 'List something good.'}</h1><p>${state.editing ? 'Make a few changes and keep the details fresh.' : 'A few thoughtful details help the right person find your item.'}</p></div><button class="btn btn-secondary" data-action="navigate" data-page="my-listings">${icon('box',16)} My listings</button></div>
    <div class="form-card"><div class="inline-help">${icon('sparkles',17)} <span>Be clear, honest, and specific. A helpful description builds trust before the first message.</span></div><div class="form-error" id="listing-form-error" role="alert"></div><form data-form="listing"><div class="form-grid">
      <div class="field full"><label for="listing-title">What are you selling? *</label><input class="text-control" id="listing-title" name="title" required minlength="3" maxlength="160" placeholder="e.g. Vintage film camera in great condition" value="${esc(item.title || '')}"><span class="hint">Give your item a clear, descriptive title.</span></div>
      <div class="field"><label for="listing-category">Category *</label><select class="text-control" id="listing-category" name="categoryId" required><option value="">${state.categories.length ? 'Choose a category' : 'Loading categories…'}</option>${categoryOptions}</select>${!state.categories.length ? `<span class="hint">Active categories load from the backend. If this stays empty, retry after checking your gateway.</span>` : ''}</div>
      <div class="field"><label for="listing-price">Price *</label><div style="display:flex;gap:8px"><input class="text-control" id="listing-price" name="priceAmount" type="number" min="0.01" max="999999999" step="0.01" required placeholder="0.00" value="${esc(item.priceAmount || '')}"><select class="text-control" name="currency" aria-label="Currency" style="max-width:125px"><option value="USD" ${(item.currency||'USD')==='USD'?'selected':''}>USD · $</option><option value="EUR" ${item.currency==='EUR'?'selected':''}>EUR · €</option><option value="GBP" ${item.currency==='GBP'?'selected':''}>GBP · £</option><option value="CAD" ${item.currency==='CAD'?'selected':''}>CAD · $</option></select></div><span class="hint">Use a fair price and specify the currency.</span></div>
      <div class="field full"><label for="listing-description">Description *</label><textarea class="text-control" id="listing-description" name="description" minlength="10" maxlength="10000" required placeholder="Condition, dimensions, what's included, and anything a buyer should know…">${esc(item.description || '')}</textarea><span class="hint">Specific details help buyers make confident decisions.</span></div>
      <div class="field"><label for="listing-location">Location *</label><input class="text-control" id="listing-location" name="location" required maxlength="160" placeholder="City, neighborhood, or area" value="${esc(item.location === 'Location not listed' ? '' : item.location || '')}"></div>
      <div class="field"><label for="listing-quantity">Quantity *</label><input class="text-control" id="listing-quantity" name="quantity" type="number" required min="1" max="9999" step="1" value="${esc(item.quantity || 1)}"></div>
      ${!state.editing ? `<div class="field full"><label for="listing-images">Image URLs</label><textarea class="text-control" id="listing-images" name="imageUrls" placeholder="https://example.com/item-photo.jpg&#10;https://example.com/another-angle.jpg" style="min-height:82px"></textarea><span class="hint">Paste one image URL per line. The current API guide doesn't document direct file uploads.</span></div>` : `<div class="field full"><div class="inline-help" style="margin:0">${icon('info',16)} <span>The documented update mutation doesn't include image updates. To change photos, use the image URLs when creating a new listing.</span></div></div>`}
      ${state.editing ? `<input type="hidden" name="listingId" value="${esc(item.listingId)}">` : ''}
    </div><div class="form-actions"><button type="button" class="btn btn-secondary" data-action="cancel-listing-form">Cancel</button><button type="submit" class="btn btn-secondary" name="submitIntent" value="draft">${icon('box',16)} ${state.editing ? 'Save changes' : 'Save as draft'}</button>${!state.editing ? `<button type="submit" class="btn btn-primary" name="submitIntent" value="publish">Publish listing ${icon('arrow',15)}</button>` : ''}</div></form></div></main>`;
  }
  function statusClass(status) { return `status-${String(status || '').toLowerCase()}`; }
  function renderMine() {
    if (!state.userId) return `<main class="page-wrap"><div class="page-heading"><div><div class="eyebrow">Your activity</div><h1>Your listings.</h1><p>Everything you've shared with the marketplace, all in one place.</p></div></div>${renderAuthRequired('Your listings are waiting','Log in to see drafts, active listings, and items you have sold.')}</main>`;
    let body;
    if (state.loadingMine) body = `<div class="listing-skeleton"></div><div class="listing-skeleton" style="margin-top:12px"></div>`;
    else if (state.mineUnavailable) body = `<div class="empty-state"><div class="empty-illustration">${icon('alert',24)}</div><h3>We couldn't load your listings.</h3><p>Your items haven't been replaced with sample data. Check your gateway connection and try again.</p><button class="btn btn-secondary" data-action="reload-mine">${icon('refresh',15)} Retry</button></div>`;
    else if (!state.myItems.length) body = `<div class="empty-state"><div class="empty-illustration">${icon('box',25)}</div><h3>A fresh start looks good on you.</h3><p>You don't have any listings yet. Share something useful, lovely, or simply ready for a new home.</p><button class="btn btn-primary" data-action="navigate" data-page="sell">${icon('plus',16)} Create your first listing</button></div>`;
    else body = `<div class="listing-list">${state.myItems.map((item,i) => `<div class="my-listing"><img src="${esc(item.cover || fallbackCover(item,i))}" alt="" loading="lazy"><div><h3>${esc(item.title)}</h3><p>${usd(item.priceAmount,item.currency)} · ${esc(item.location)} · ${esc(relativeDate(item.createdAt))}</p><span class="status-pill ${statusClass(item.status)}">${esc(String(item.status).toLowerCase())}</span></div><div class="row-actions"><button class="btn btn-secondary btn-small" data-action="edit-listing" data-id="${esc(item.listingId)}">${icon('edit',13)} Edit</button>${item.status === 'DRAFT' ? `<button class="btn btn-primary btn-small" data-action="publish-listing" data-id="${esc(item.listingId)}">Publish</button>` : item.status === 'ACTIVE' ? `<button class="btn btn-secondary btn-small" data-action="mark-sold" data-id="${esc(item.listingId)}">Mark sold</button>` : ''}<button class="btn btn-icon btn-small" data-action="delete-listing" data-id="${esc(item.listingId)}" aria-label="Delete ${esc(item.title)}">${icon('trash',14)}</button></div></div>`).join('')}</div>`;
    return `<main class="page-wrap"><div class="page-heading"><div><div class="eyebrow">Your activity</div><h1>Your listings.</h1><p>Everything you've shared with the marketplace, all in one place.</p></div><button class="btn btn-primary" data-action="navigate" data-page="sell">${icon('plus',16)} Create a listing</button></div><div class="table-card"><div class="section-head"><div><h2>Manage your items</h2><p>Keep your listings up to date.</p></div><span class="status-pill">${state.myItems.length} total</span></div>${body}</div></main>`;
  }
  function getConversationId(c) { return c?.conversation_id || c?.conversationId || c?.id || ''; }
  function getConversationListingId(c) { return c?.listing_id || c?.listingId || ''; }
  function getMessagesFromPayload(data) {
    const p = data?.payload ?? data ?? {};
    if (Array.isArray(p)) return p;
    return p.messages || p.items || p.results || [];
  }
  function renderConversationItem(c) {
    const id = getConversationId(c);
    const title = c?.listing_title || c?.listingTitle || c?.last_message_preview || c?.lastMessagePreview || 'Marketplace conversation';
    const preview = c?.last_message_preview || c?.lastMessagePreview || 'Open to view messages';
    const date = c?.last_message_at || c?.lastMessageAt || c?.updated_at;
    return `<button class="conversation-item ${state.chat.activeId === id ? 'active' : ''}" data-action="open-conversation" data-id="${esc(id)}"><span class="conversation-avatar">${esc(String(title).slice(0,1).toUpperCase())}</span><span class="conversation-main"><span class="conversation-title-row"><span class="conversation-title">${esc(title)}${Number(c?.unread_count || 0) > 0 ? '<i class="unread-dot"></i>' : ''}</span><time class="conversation-date">${esc(shortTime(date))}</time></span><p class="conversation-preview">${esc(preview)}</p></span></button>`;
  }
  function renderMessage(m) {
    const isMine = m?.sender_id === state.userId || m?.senderId === state.userId;
    return `<div class="message-bubble ${isMine ? 'mine' : 'theirs'}">${esc(m?.content || '')}${m?.is_deleted ? '<em>Message removed</em>' : ''}<div class="message-time">${esc(shortTime(m?.sent_at || m?.sentAt))}</div></div>`;
  }
  function renderThread() {
    const selected = state.chat.active;
    if (!selected) return `<div class="thread-empty"><div class="empty-illustration">${icon('message',26)}</div><h3>A good conversation starts here.</h3><p>Choose a message on the left to pick up where you left off, or contact a seller from a listing.</p></div>`;
    const title = selected?.listing_title || selected?.listingTitle || selected?.last_message_preview || 'Marketplace conversation';
    const readOnly = selected?.is_read_only || selected?.isReadOnly;
    const messages = state.chat.messages;
    return `<div class="thread-header"><button class="btn-icon mobile-back" data-action="back-to-inbox" aria-label="Back to inbox">${icon('back',17)}</button><span class="conversation-avatar">${esc(String(title).slice(0,1).toUpperCase())}</span><div class="thread-person"><h3>${esc(title)}</h3><p>${readOnly ? 'This conversation is read-only' : 'Keep it kind. Keep it clear.'}</p></div><div class="thread-header-actions"><button class="btn-icon" data-action="toggle-pin" title="${selected.is_pinned ? 'Unpin conversation' : 'Pin conversation'}" aria-label="Pin conversation">${icon('star',16)}</button><button class="btn-icon" data-action="toggle-mute" title="${selected.is_muted ? 'Unmute conversation' : 'Mute conversation'}" aria-label="Mute conversation">${icon('more',16)}</button><button class="btn-icon" data-action="conversation-actions" aria-label="More conversation actions">${icon('chevron',16)}</button></div></div>
      ${state.chat.error ? `<div class="chat-banner">${esc(state.chat.error)}</div>` : ''}
      <div class="thread-messages" id="thread-messages">${messages.length ? `<div class="message-day">Messages</div>${messages.map(renderMessage).join('')}` : `<div class="thread-empty"><div class="empty-illustration">${icon('message',24)}</div><h3>Say hello.</h3><p>A friendly note is a good place to start.</p></div>`}</div>
      <form class="message-composer" data-form="send-message"><label class="sr-only" for="message-text">Your message</label><textarea id="message-text" name="content" placeholder="Write a thoughtful message…" rows="1" maxlength="5000" ${readOnly ? 'disabled' : ''} required></textarea><button class="btn btn-primary" type="submit" ${readOnly ? 'disabled' : ''} aria-label="Send message">${icon('send',17)}</button></form>`;
  }
  function renderMessages() {
    if (!state.userId) return `<main class="page-wrap"><div class="page-heading"><div><div class="eyebrow">Make it personal</div><h1>Your conversations.</h1><p>Ask a question, arrange a pickup, or just say hello.</p></div></div>${renderAuthRequired('Good finds start with good conversations','Log in to message sellers and keep your conversations in one place.')}</main>`;
    const conversations = state.chat.conversations.filter(c => !c?.is_hidden && !c?.isHidden);
    return `<main class="page-wrap"><div class="page-heading"><div><div class="eyebrow">A little human connection</div><h1>Messages.</h1><p>Good communication makes every exchange better.</p></div><div class="connection-indicator ${state.chat.status === 'connected' ? 'online' : ''}">${state.chat.status === 'connected' ? 'Connected' : state.chat.status === 'connecting' ? 'Connecting…' : 'Reconnecting if needed'}</div></div><section class="inbox-layout"><aside class="inbox-sidebar ${state.mobileThread ? 'thread-open' : ''}"><div class="inbox-top"><h2>Your inbox</h2><p>Pick up a conversation.</p><div class="inbox-tabs"><button class="${state.chat.filter==='active'?'active':''}" data-action="conversation-filter" data-filter="active">Active</button><button class="${state.chat.filter==='archived'?'active':''}" data-action="conversation-filter" data-filter="archived">Archived</button></div></div><div class="conversation-list">${state.chat.loading && !conversations.length ? `<div style="padding:20px;color:var(--muted);font-size:12px">Loading your conversations…</div>` : conversations.length ? conversations.map(renderConversationItem).join('') : `<div style="padding:30px 22px;text-align:center"><div class="empty-illustration" style="margin:0 auto 12px">${icon('message',22)}</div><b style="font-size:13px">A quiet inbox.</b><p class="muted tiny">When you message a seller, your conversation will appear here.</p><button class="btn btn-secondary btn-small" data-action="navigate" data-page="discover">Explore finds</button></div>`}</div></aside><section class="thread-panel ${state.mobileThread ? 'thread-visible' : ''}" aria-label="Conversation">${renderThread()}</section></section></main>`;
  }
  function renderAccount() {
    if (!state.userId) return `<main class="page-wrap"><div class="page-heading"><div><div class="eyebrow">Your corner</div><h1>Your account.</h1><p>A few details help keep your account yours.</p></div></div>${renderAuthRequired('Make yourself at home','Log in to manage your password, sessions, and account settings.')}</main>`;
    return `<main class="page-wrap"><div class="page-heading"><div><div class="eyebrow">Your corner</div><h1>Account settings.</h1><p>Your security, under your control.</p></div></div><div class="settings-layout"><aside class="settings-nav"><button class="${state.accountTab==='security'?'active':''}" data-action="account-tab" data-tab="security">${icon('shield',16)} Security</button><button class="${state.accountTab==='sessions'?'active':''}" data-action="account-tab" data-tab="sessions">${icon('device',16)} Sessions</button><button class="${state.accountTab==='privacy'?'active':''}" data-action="account-tab" data-tab="privacy">${icon('lock',16)} Account</button></aside><div><section class="settings-card"><div class="account-identity"><span class="account-big-avatar">${esc(String(state.userId).slice(0,1).toUpperCase())}</span><div><h3 style="margin:0 0 4px">Your Kologram account</h3><div class="account-id">ID · ${esc(state.userId)}</div></div></div><h3>${state.accountTab === 'sessions' ? 'Session management' : state.accountTab === 'privacy' ? 'Account controls' : 'Keep your account secure'}</h3><p>${state.accountTab === 'sessions' ? 'Sign out of other active sessions when you need a fresh start.' : state.accountTab === 'privacy' ? 'You can permanently delete your account and its associated access.' : 'Use a strong password and revoke sessions you no longer recognize.'}</p>
      ${state.accountTab === 'sessions' ? `<button class="btn btn-secondary" data-action="revoke-others">${icon('refresh',16)} Revoke other sessions</button><div class="section-divider"></div><p>Session identifiers aren't returned by a documented “list sessions” endpoint, so this screen only offers the supported revoke-others action.</p>` : state.accountTab === 'privacy' ? `<div class="settings-card danger-zone" style="padding:18px;margin:0"><h3>Delete account</h3><p>This action cannot be undone. You’ll be asked to confirm before your account is removed.</p><button class="btn btn-danger" data-action="confirm-delete-account">${icon('trash',15)} Delete account</button></div>` : `<form data-form="change-password"><div class="form-error" id="password-error" role="alert"></div><div class="field" style="max-width:480px"><label for="new-password">New password</label><input class="text-control" id="new-password" name="newPassword" type="password" minlength="8" maxlength="128" autocomplete="new-password" required placeholder="At least 8 characters"><span class="hint">Use 8–128 characters and avoid reusing a password.</span></div><div class="form-actions" style="justify-content:flex-start;border:0;margin-top:16px;padding-top:0"><button class="btn btn-primary" type="submit">Update password ${icon('arrow',15)}</button></div></form>`}</section><section class="settings-card"><h3>Signing out?</h3><p>This device will be logged out. You can sign in again at any time.</p><button class="btn btn-secondary" data-action="logout">${icon('logout',16)} Log out of Kologram</button></section></div></div></main>`;
  }
  function renderFooter() {
    return `<footer class="footer"><div class="footer-brand"><span class="brand-mark">k<span>.</span></span> kologram.</div><span>A more thoughtful way to pass good things on.</span><span>© ${new Date().getFullYear()} Kologram</span></footer>`;
  }

  function openAuth(mode = 'login') { state.modal = { type: 'auth' }; state.authMode = mode; state.authEmail = state.authEmail || ''; render(); }
  function renderAuthModal() {
    let title = 'Welcome back.'; let lead = 'Log in to pick up where you left off.'; let form = '';
    if (state.authMode === 'login') {
      form = `<form class="auth-form" data-form="login"><div class="form-error" id="auth-error" role="alert"></div><div class="field"><label for="auth-email">Email address</label><input class="text-control" id="auth-email" name="email" type="email" autocomplete="email" required minlength="3" maxlength="254" placeholder="you@example.com" value="${esc(state.authEmail)}"></div><div class="field"><label for="auth-password">Password</label><div class="password-wrap"><input class="text-control" id="auth-password" name="password" type="password" autocomplete="current-password" minlength="8" maxlength="128" required placeholder="Your password"><button type="button" class="password-toggle" data-action="toggle-password" data-target="auth-password">Show</button></div></div><div style="display:flex;justify-content:flex-end;margin-top:-5px"><button class="text-link" type="button" data-action="auth-mode" data-mode="forgot">Forgot password?</button></div><button class="btn btn-primary" type="submit">Log in ${icon('arrow',15)}</button></form><p class="auth-footer">New around here? <button class="text-link" data-action="auth-mode" data-mode="register-email">Create an account</button></p>`;
    } else if (state.authMode === 'register-email') {
      title = 'Find your people.'; lead = 'Start with your email. We’ll send you a verification token to finish creating your account.';
      form = `<form class="auth-form" data-form="request-verification"><div class="form-error" id="auth-error" role="alert"></div><div class="field"><label for="auth-email">Email address</label><input class="text-control" id="auth-email" name="email" type="email" autocomplete="email" required minlength="3" maxlength="254" placeholder="you@example.com" value="${esc(state.authEmail)}"></div><button class="btn btn-primary" type="submit">Send verification email ${icon('arrow',15)}</button></form><p class="auth-footer">Already a member? <button class="text-link" data-action="auth-mode" data-mode="login">Log in</button></p>`;
    } else if (state.authMode === 'register-token') {
      title = 'One last step.'; lead = `Paste the 36-character verification token sent to <b>${esc(state.authEmail)}</b>, then choose a password.`;
      form = `<form class="auth-form" data-form="signup"><div class="form-error" id="auth-error" role="alert"></div><div class="field"><label for="verify-token">Verification token</label><input class="text-control" id="verify-token" name="verifyToken" required minlength="36" maxlength="36" pattern="[0-9a-fA-F-]{36}" placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" autocomplete="one-time-code"></div><div class="field"><label for="new-auth-password">Create password</label><div class="password-wrap"><input class="text-control" id="new-auth-password" name="password" type="password" autocomplete="new-password" minlength="8" maxlength="128" required placeholder="At least 8 characters"><button class="password-toggle" type="button" data-action="toggle-password" data-target="new-auth-password">Show</button></div></div><button class="btn btn-primary" type="submit">Create my account ${icon('arrow',15)}</button></form><p class="auth-footer">Token didn’t arrive? <button class="text-link" data-action="auth-mode" data-mode="register-email">Try another email</button></p>`;
    } else if (state.authMode === 'forgot') {
      title = 'Let’s get you back in.'; lead = 'Enter your email and, if an account matches, you’ll receive instructions to reset your password.';
      form = `<form class="auth-form" data-form="forgot-password"><div class="form-error" id="auth-error" role="alert"></div><div class="field"><label for="auth-email">Email address</label><input class="text-control" id="auth-email" name="email" type="email" required minlength="3" maxlength="254" autocomplete="email" placeholder="you@example.com" value="${esc(state.authEmail)}"></div><button class="btn btn-primary" type="submit">Send reset instructions ${icon('arrow',15)}</button></form><p class="auth-footer"><button class="text-link" data-action="auth-mode" data-mode="login">Back to log in</button></p>`;
    } else if (state.authMode === 'forgot-sent') {
      title = 'Check your inbox.'; lead = 'If there’s an account associated with that email, reset instructions will be on their way. For local development, check your email testing inbox.';
      form = `<div class="empty-illustration">${icon('mail',25)}</div><button class="btn btn-primary" data-action="auth-mode" data-mode="reset">I have a reset token</button><p class="auth-footer"><button class="text-link" data-action="auth-mode" data-mode="login">Back to log in</button></p>`;
    } else if (state.authMode === 'reset') {
      title = 'Choose a new password.'; lead = 'Paste your verification token and set a new password.';
      form = `<form class="auth-form" data-form="reset-password"><div class="form-error" id="auth-error" role="alert"></div><div class="field"><label for="reset-token">Verification token</label><input class="text-control" id="reset-token" name="verifyToken" required minlength="36" maxlength="36" pattern="[0-9a-fA-F-]{36}" placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"></div><div class="field"><label for="reset-password">New password</label><div class="password-wrap"><input class="text-control" id="reset-password" name="newPassword" type="password" required minlength="8" maxlength="128" autocomplete="new-password"><button class="password-toggle" type="button" data-action="toggle-password" data-target="reset-password">Show</button></div></div><button class="btn btn-primary" type="submit">Reset password ${icon('arrow',15)}</button></form><p class="auth-footer"><button class="text-link" data-action="auth-mode" data-mode="login">Back to log in</button></p>`;
    }
    return `<div class="modal-backdrop" data-action="modal-backdrop"><section class="modal" role="dialog" aria-modal="true" aria-labelledby="auth-title"><button class="modal-close" data-action="close-modal" aria-label="Close dialog">${icon('close',17)}</button><div class="auth-split"><div class="modal-content"><div class="brand" style="margin-bottom:28px"><span class="brand-mark">k<span>.</span></span><span class="brand-word">kologram<span>.</span></span></div><div class="modal-eyebrow">A better kind of marketplace</div><h2 id="auth-title">${title}</h2><p class="modal-lead">${lead}</p>${form}</div><aside class="auth-side-art"><img src="${PHOTOS.auth}" alt="A person shopping thoughtfully"><div class="auth-side-copy"><h3>Good things should find good people.</h3><p>Find something you love. Pass along something great. Make the exchange feel human.</p></div></aside></div></section></div>`;
  }
  function renderDetailModal() {
    const item = state.detail; if (!item) return '';
    const isDemo = String(item.listingId).startsWith('demo-');
    const owner = state.userId && item.sellerId && state.userId === item.sellerId;
    return `<div class="modal-backdrop" data-action="modal-backdrop"><section class="modal modal-wide" role="dialog" aria-modal="true" aria-label="Listing details"><button class="modal-close" data-action="close-modal" aria-label="Close listing details">${icon('close',17)}</button><div class="detail-layout"><div class="detail-media"><img src="${esc(item.cover || fallbackCover(item))}" alt="${esc(item.title)}" onerror="this.onerror=null;this.src='${PHOTOS.camera}'"></div><div class="detail-copy"><div class="modal-eyebrow">${esc(item.categoryLabel || 'A good find')}</div><h2>${esc(item.title)}</h2><div class="detail-price">${usd(item.priceAmount,item.currency)}</div><div class="detail-meta"><span>${icon('pin',14)} ${esc(item.location)}</span><span>${icon('clock',14)} ${esc(relativeDate(item.createdAt))}</span></div><p class="detail-description">${esc(item.description || 'No description has been added yet. Ask the seller for details.')}</p><div class="seller-card"><span class="conversation-avatar">${esc(String(item.sellerId || 'S').slice(0,1).toUpperCase())}</span><div><b>${owner ? 'This is your listing' : 'The person behind the find'}</b><p>${owner ? 'Manage your item from My listings.' : 'Ask a question before you make it yours.'}</p></div></div><div class="detail-actions">${owner ? `<button class="btn btn-primary" data-action="edit-listing" data-id="${esc(item.listingId)}">${icon('edit',16)} Edit your listing</button>` : `<button class="btn btn-primary" data-action="contact-seller" data-id="${esc(item.listingId)}" ${isDemo ? 'data-demo="1"' : ''}>${icon('message',16)} Message the seller</button>`}<button class="btn btn-secondary" data-action="toggle-save" data-id="${esc(item.listingId)}">${icon('heart',16)} ${state.saved.has(item.listingId) ? 'Saved to your finds' : 'Save this find'}</button>${isDemo ? `<div class="tiny muted" style="text-align:center">Preview listing · sample content only</div>` : ''}</div></div></div></section></div>`;
  }
  function renderConfirmModal() {
    if (!state.confirm) return '';
    const c = state.confirm;
    return `<div class="modal-backdrop" data-action="modal-backdrop"><section class="modal" role="dialog" aria-modal="true" aria-labelledby="confirm-title"><button class="modal-close" data-action="close-modal" aria-label="Close dialog">${icon('close',16)}</button><div class="confirm-content"><div class="empty-illustration" style="background:#fff0ee;color:#b34b45">${icon(c.danger ? 'trash' : 'alert',25)}</div><h2 id="confirm-title">${esc(c.title)}</h2><p>${esc(c.message)}</p><div class="confirm-actions"><button class="btn btn-secondary" data-action="cancel-confirm">Cancel</button><button class="btn ${c.danger ? 'btn-danger' : 'btn-primary'}" data-action="execute-confirm">${esc(c.confirmLabel || 'Confirm')}</button></div></div></section></div>`;
  }
  function renderModal() {
    if (state.confirm) return renderConfirmModal();
    if (state.modal?.type === 'auth') return renderAuthModal();
    if (state.detail) return renderDetailModal();
    if (state.modal?.type === 'conversation-actions') return `<div class="modal-backdrop" data-action="modal-backdrop"><section class="modal" role="dialog" aria-modal="true" aria-label="Conversation actions"><button class="modal-close" data-action="close-modal" aria-label="Close">${icon('close',16)}</button><div class="modal-content"><div class="modal-eyebrow">Conversation</div><h2>Make space for a better chat.</h2><p class="modal-lead">Manage what happens with this conversation.</p><div style="display:grid;gap:9px"><button class="btn btn-secondary" data-action="toggle-archive">${icon('archive',16)} ${state.chat.active?.is_archived ? 'Unarchive conversation' : 'Archive conversation'}</button><button class="btn btn-secondary" data-action="toggle-hide">${icon('eye',16)} Hide from your inbox</button><button class="btn btn-secondary" data-action="block-user">${icon('lock',16)} Block this user</button></div></div></section></div>`;
    return '';
  }
  function render() {
    const wasOverlayOpen = document.body.classList.contains('modal-open');
    let page = '';
    if (state.page === 'discover') page = renderDiscover();
    else if (state.page === 'sell') page = renderSell();
    else if (state.page === 'my-listings') page = renderMine();
    else if (state.page === 'messages') page = renderMessages();
    else if (state.page === 'account') page = renderAccount();
    else if (state.page === 'saved') page = renderSaved();
    app.innerHTML = `${renderHeader()}${page}${renderFooter()}${renderModal()}<div class="toast-region" id="toast-region" aria-live="polite" aria-atomic="false"></div>`;
    renderToasts();
    const overlayOpen = Boolean(state.modal || state.detail || state.confirm);
    document.body.classList.toggle('modal-open', overlayOpen);
    if (overlayOpen && !wasOverlayOpen) requestAnimationFrame(() => { const dialog = app.querySelector('[role="dialog"]'); const first = dialog?.querySelector('input:not([disabled]), textarea:not([disabled]), select:not([disabled]), button:not([disabled])'); first?.focus(); });
    if (state.page === 'messages') scrollMessagesToBottom();
  }
  function renderSaved() {
    const catalog = new Map([...state.savedItems.entries()]);
    [...state.items, ...DEMO_ITEMS, ...state.myItems].forEach(item => { if (state.saved.has(item.listingId)) catalog.set(item.listingId, item); });
    const items = [...state.saved].map(id => catalog.get(id)).filter(Boolean);
    return `<main class="page-wrap"><div class="page-heading"><div><div class="eyebrow">Keep the good ones close</div><h1>Your saved finds.</h1><p>A shortlist of things that caught your eye. Saves are stored in this browser.</p></div><button class="btn btn-secondary" data-action="navigate" data-page="discover">${icon('arrow',15)} Explore more</button></div>${items.length ? `<div class="product-grid">${items.map(renderCard).join('')}</div>` : `<div class="empty-state"><div class="empty-illustration">${icon('heart',25)}</div><h3>Nothing saved just yet.</h3><p>Tap the heart on any listing to keep it here while you think it over.</p><button class="btn btn-primary" data-action="navigate" data-page="discover">Find something lovely ${icon('arrow',15)}</button></div>`}</main>`;
  }
  function scrollMessagesToBottom() {
    requestAnimationFrame(() => { const el = $('#thread-messages'); if (el) el.scrollTop = el.scrollHeight; });
  }
  function setPage(page) {
    if (['messages','my-listings','account','sell'].includes(page) && !state.userId && page !== 'sell') { state.page = page; state.modal = { type: 'auth' }; state.authMode = 'login'; render(); return; }
    state.page = page; state.modal = null; state.detail = null; state.confirm = null;
    if (page !== 'sell') state.editing = null;
    if (page === 'discover') loadExplore(); else if (page === 'my-listings') loadMyListings(); else { render(); if (page === 'messages' && state.userId) refreshInbox().catch(e => showToast(friendlyError(e, 'Could not load messages.'), 'error')); }
  }

  // --- Auth and listing flows ---
  function setFormError(id, message) { const el = document.getElementById(id); if (el) { el.textContent = message; el.classList.add('visible'); } }
  function clearFormError(id) { const el = document.getElementById(id); if (el) { el.textContent = ''; el.classList.remove('visible'); } }
  async function handleLogin(form) {
    clearFormError('auth-error'); const fd = new FormData(form); const email = String(fd.get('email') || '').trim(); const password = String(fd.get('password') || '');
    const button = form.querySelector('[type="submit"]'); setButtonBusy(button, true, 'Logging in…');
    try {
      const data = await publicRequest('/api/v1/auth/login', { email, password, device: DEVICE });
      if (!data?.access_token || !data?.refresh_token) throw new Error('The server did not return the expected tokens.');
      storeTokens(data); state.modal = null; state.page = 'discover'; state.userId = getUserId(); state.token = data.access_token; state.categories = []; state.live = false; state.apiUnavailable = false;
      render(); showToast('Welcome back. Good to see you.'); await loadExplore();
    } catch (e) { setFormError('auth-error', e.status === 401 ? 'Invalid email or password.' : friendlyError(e, 'We couldn’t log you in. Please try again.')); }
    finally { if (button) setButtonBusy(button, false); }
  }
  function storeTokens(data) { localStorage.setItem(ACCESS_KEY, data.access_token); localStorage.setItem(REFRESH_KEY, data.refresh_token); state.userId = getUserId(); state.token = data.access_token; }
  function setButtonBusy(button, busy, label = 'Working…') {
    if (!button) return;
    if (busy) { button.dataset.originalText = button.innerHTML; button.innerHTML = `<span class="spinner" aria-hidden="true"></span>${esc(label)}`; button.disabled = true; }
    else { button.innerHTML = button.dataset.originalText || button.innerHTML; button.disabled = false; }
  }
  async function handleRequestVerification(form) {
    clearFormError('auth-error'); const fd = new FormData(form); const email = String(fd.get('email') || '').trim();
    const button = form.querySelector('[type="submit"]'); setButtonBusy(button, true, 'Sending…');
    try { await publicRequest('/api/v1/auth/verification', { email }); state.authEmail = email; state.authMode = 'register-token'; render(); showToast('Verification email requested. Check your inbox or local mail catcher.'); }
    catch (e) { setFormError('auth-error', friendlyError(e, 'Could not request a verification email.')); }
    finally { if (button) setButtonBusy(button, false); }
  }
  async function handleSignup(form) {
    clearFormError('auth-error'); const fd = new FormData(form); const verify_token = String(fd.get('verifyToken') || '').trim(); const password = String(fd.get('password') || '');
    const button = form.querySelector('[type="submit"]'); setButtonBusy(button, true, 'Creating account…');
    try { const data = await publicRequest('/api/v1/auth/signup', { verify_token, password, device: DEVICE }); if (!data?.access_token || !data?.refresh_token) throw new Error('The server did not return the expected tokens.'); storeTokens(data); state.modal = null; state.page = 'discover'; state.categories = []; render(); showToast('Your account is ready. Welcome to Kologram.'); await loadExplore(); }
    catch (e) { setFormError('auth-error', friendlyError(e, 'Could not create your account. Check the token and try again.')); }
    finally { if (button) setButtonBusy(button, false); }
  }
  async function handleForgot(form) {
    clearFormError('auth-error'); const email = String(new FormData(form).get('email') || '').trim(); const button = form.querySelector('[type="submit"]'); setButtonBusy(button, true, 'Sending…');
    try { await publicRequest('/api/v1/auth/password/forgot', { email }); state.authEmail = email; state.authMode = 'forgot-sent'; render(); }
    catch (e) { // The UI should avoid disclosing whether an account exists; network errors are still surfaced.
      setFormError('auth-error', friendlyError(e, 'The request could not be sent. Please try again.'));
    } finally { if (button) setButtonBusy(button, false); }
  }
  async function handleReset(form) {
    clearFormError('auth-error'); const fd = new FormData(form); const verify_token = String(fd.get('verifyToken') || '').trim(); const new_password = String(fd.get('newPassword') || ''); const button = form.querySelector('[type="submit"]'); setButtonBusy(button, true, 'Resetting…');
    try { await publicRequest('/api/v1/auth/password/reset', { verify_token, new_password }); state.authMode = 'login'; render(); showToast('Password reset. You can now log in with your new password.'); }
    catch (e) { setFormError('auth-error', friendlyError(e, 'Could not reset the password.')); }
    finally { if (button) setButtonBusy(button, false); }
  }
  async function handleListing(form, submitter) {
    const errorId = 'listing-form-error'; clearFormError(errorId);
    if (!state.userId) { openAuth('login'); return; }
    const fd = new FormData(form); const title = String(fd.get('title') || '').trim(); const description = String(fd.get('description') || '').trim(); const categoryId = String(fd.get('categoryId') || '').trim(); const priceRaw = String(fd.get('priceAmount') || '').trim(); const price = Number(priceRaw); const currency = String(fd.get('currency') || 'USD'); const location = String(fd.get('location') || '').trim(); const quantity = Number(fd.get('quantity') || 1);
    if (!categoryId) { setFormError(errorId, 'Choose a category. Categories must be available from your backend to create a listing.'); return; }
    if (!Number.isFinite(price) || price <= 0) { setFormError(errorId, 'Enter a price greater than zero.'); return; }
    const isEdit = Boolean(state.editing); const wantsPublish = submitter?.value === 'publish';
    const button = submitter; setButtonBusy(button, true, isEdit ? 'Saving…' : wantsPublish ? 'Publishing…' : 'Saving draft…');
    try {
      let listingId;
      if (isEdit) {
        listingId = state.editing.listingId;
        await graphql(QUERIES.update, { input: { listingId, sellerId: state.userId, title, description, priceAmount: price.toFixed(2), currency, quantity, location, categoryId } });
        showToast('Listing details updated.');
      } else {
        const imageUrls = String(fd.get('imageUrls') || '').split(/[\n,]+/).map(x => x.trim()).filter(Boolean);
        const result = await graphql(QUERIES.create, { input: { sellerId: state.userId, categoryId, title, description, priceAmount: price.toFixed(2), currency, quantity, location, imageUrls } });
        listingId = result.createListing?.listingId;
        if (!listingId) throw new Error('The API did not return a listing ID.');
        if (wantsPublish) { await graphql(QUERIES.publish, { input: { listingId, sellerId: state.userId } }); showToast('Your listing is now published.'); }
        else showToast('Draft saved. Publish it whenever you’re ready.');
      }
      state.editing = null; state.page = 'my-listings'; await loadMyListings();
    } catch (e) { setFormError(errorId, friendlyError(e, 'Could not save your listing.')); }
    finally { if (button) setButtonBusy(button, false); }
  }
  async function performListingMutation(action, id) {
    const item = state.myItems.find(x => x.listingId === id) || state.detail;
    try {
      if (action === 'publish') { await graphql(QUERIES.publish, { input: { listingId: id, sellerId: state.userId } }); showToast('Listing published.'); }
      if (action === 'sold') { await graphql(QUERIES.status, { input: { listingId: id, sellerId: state.userId, newStatus: 'SOLD' } }); showToast('Listing marked as sold.'); }
      if (action === 'cancel') { await graphql(QUERIES.status, { input: { listingId: id, sellerId: state.userId, newStatus: 'CANCELLED' } }); showToast('Listing cancelled.'); }
      if (action === 'delete') { await graphql(QUERIES.delete, { input: { listingId: id, sellerId: state.userId } }); showToast('Listing deleted.'); }
      state.confirm = null; state.detail = null; await loadMyListings();
    } catch (e) { showToast(friendlyError(e, `Could not ${action} this listing.`), 'error'); }
  }
  async function beginEdit(id) {
    let item = state.myItems.find(x => x.listingId === id);
    if (!item) { showToast('That listing could not be found in your list.', 'error'); return; }
    try { const data = await graphql(QUERIES.listing, { id }); item = normalizeListing(data.listing || item); }
    catch (e) { showToast('Some listing details could not be loaded. You can still edit available fields.', 'info'); }
    state.editing = item; state.detail = null; state.modal = null; state.page = 'sell'; render(); window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // --- WebSocket chat client, based on the documented request/reply envelope ---
  function closeChat() {
    const chat = state.chat; chat.unsubscribed = true;
    if (chat.socket) { try { chat.socket.close(); } catch {} }
    chat.socket = null; chat.connectPromise = null; chat.status = 'disconnected';
    for (const [id, entry] of chat.pending) { clearTimeout(entry.timer); entry.reject(new Error('Disconnected.')); }
    chat.pending.clear();
  }
  function handleChatPush(message) {
    if (!message?.type) return;
    if (message.type === 'message_sent' || message.type === 'message_deleted') {
      if (state.page === 'messages') {
        refreshInbox(true).catch(() => {});
        if (state.chat.activeId && message.conversation_id === state.chat.activeId) loadThread(state.chat.activeId).catch(() => {});
      }
    }
  }
  function connectChat() {
    const chat = state.chat;
    if (!state.userId || !getTokens().access_token) return Promise.reject(new Error('Sign in to use messages.'));
    if (chat.socket?.readyState === WebSocket.OPEN) return Promise.resolve();
    if (chat.connectPromise) return chat.connectPromise;
    chat.status = 'connecting'; chat.unsubscribed = false;
    chat.connectPromise = new Promise((resolve, reject) => {
      let socket;
      try { const joiner = WS_URL.includes('?') ? '&' : '?'; socket = new WebSocket(`${WS_URL}${joiner}access_token=${encodeURIComponent(getTokens().access_token)}`); }
      catch (e) { chat.status = 'disconnected'; chat.connectPromise = null; reject(e); return; }
      chat.socket = socket;
      const connectTimer = setTimeout(() => { if (socket.readyState !== WebSocket.OPEN) { try { socket.close(); } catch {} chat.status = 'disconnected'; chat.connectPromise = null; reject(new Error('Chat connection timed out. Check that the gateway is running.')); } }, 12000);
      socket.onopen = () => { clearTimeout(connectTimer); chat.status = 'connected'; chat.connectPromise = null; render(); resolve(); };
      socket.onmessage = event => {
        let message; try { message = JSON.parse(event.data); } catch { return; }
        if (message.id && chat.pending.has(message.id)) {
          const pending = chat.pending.get(message.id); clearTimeout(pending.timer); chat.pending.delete(message.id);
          if (message.ok === false) pending.reject(new ApiError(message.error?.message || 'Chat request failed.', undefined, message.error?.code)); else pending.resolve(message);
        }
        handleChatPush(message);
      };
      socket.onerror = () => { /* The close handler contains the user-facing recovery. */ };
      socket.onclose = () => {
        clearTimeout(connectTimer); chat.status = 'disconnected'; chat.socket = null; chat.connectPromise = null;
        for (const [id, pending] of chat.pending) { clearTimeout(pending.timer); pending.reject(new Error('Connection closed. Please retry.')); }
        chat.pending.clear();
        if (!chat.unsubscribed && state.userId) {
          setTimeout(() => { if (state.userId && !chat.unsubscribed && state.page === 'messages') connectChat().then(() => refreshInbox(true)).catch(() => {}); }, 1900);
        }
        if (state.page === 'messages') render();
      };
    });
    return chat.connectPromise;
  }
  async function chatRequest(type, payload = {}, timeoutMs = 12000) {
    await connectChat(); const chat = state.chat;
    if (!chat.socket || chat.socket.readyState !== WebSocket.OPEN) throw new Error('Chat is reconnecting. Please retry in a moment.');
    const id = `web-${Date.now()}-${++chat.counter}`;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => { chat.pending.delete(id); reject(new Error('The chat request timed out. Please retry.')); }, timeoutMs);
      chat.pending.set(id, { resolve, reject, timer });
      chat.socket.send(JSON.stringify({ id, type, payload }));
    });
  }
  async function refreshInbox(silent = false) {
    if (!state.userId) return;
    state.chat.loading = true; if (!silent) render();
    try {
      await connectChat();
      const response = await chatRequest('list_conversations', { filter: state.chat.filter, limit: 50 });
      const payload = response.payload || {};
      state.chat.conversations = Array.isArray(payload) ? payload : payload.conversations || payload.items || payload.results || [];
      state.chat.loading = false; state.chat.error = '';
    } catch (e) {
      state.chat.loading = false; state.chat.error = friendlyError(e, 'Could not load your conversations.');
      if (!silent) showToast(state.chat.error, 'error');
    }
    if (state.page === 'messages') render();
  }
  async function loadThread(conversationId) {
    state.chat.activeId = conversationId; state.chat.mobileThread = true; state.chat.active = state.chat.conversations.find(c => getConversationId(c) === conversationId) || null; state.chat.messages = []; state.chat.error = ''; render();
    try {
      await connectChat();
      const convRes = await chatRequest('get_conversation', { conversation_id: conversationId });
      state.chat.active = convRes.payload?.conversation || convRes.payload || state.chat.active;
      const msgRes = await chatRequest('list_messages', { conversation_id: conversationId, limit: 100 });
      state.chat.messages = getMessagesFromPayload(msgRes).sort((a,b) => new Date(a.sent_at || a.sentAt || 0) - new Date(b.sent_at || b.sentAt || 0));
      const last = state.chat.messages[state.chat.messages.length - 1];
      if (last?.message_id || last?.messageId) await chatRequest('mark_conversation_read', { conversation_id: conversationId, last_read_message_id: last.message_id || last.messageId }).catch(() => {});
      state.chat.error = '';
    } catch (e) { state.chat.error = friendlyError(e, 'Could not open this conversation.'); }
    render();
  }
  async function startConversation(listingId) {
    if (!state.userId) { state.detail = null; openAuth('login'); return; }
    if (String(listingId).startsWith('demo-')) { showToast('This is a sample listing. Log in to contact sellers on live listings.', 'info'); return; }
    try {
      state.detail = null; render(); showToast('Opening conversation…', 'info', 1800);
      const result = await chatRequest('start_conversation', { listing_id: listingId });
      const payload = result.payload || {};
      let id = payload.conversation_id || payload.conversationId || payload.conversation?.conversation_id || payload.conversation?.conversationId;
      await refreshInbox(true);
      if (!id) { const match = state.chat.conversations.find(c => getConversationListingId(c) === listingId); id = match && getConversationId(match); }
      state.page = 'messages'; state.mobileThread = true; render();
      if (id) await loadThread(id); else showToast('Conversation created, but the response did not include its ID. Refresh the inbox to find it.', 'info');
    } catch (e) { showToast(friendlyError(e, 'Could not start a conversation.'), 'error'); }
  }
  async function handleSendMessage(form) {
    const content = String(new FormData(form).get('content') || '').trim(); if (!content || !state.chat.activeId) return;
    const textarea = $('#message-text'); if (textarea) textarea.disabled = true;
    try {
      const client_message_id = randomId();
      await chatRequest('send_message', { conversation_id: state.chat.activeId, client_message_id, content });
      await loadThread(state.chat.activeId);
    } catch (e) { showToast(friendlyError(e, 'Message could not be sent.'), 'error'); }
    finally { const current = $('#message-text'); if (current) { current.disabled = false; current.focus(); } }
  }
  async function conversationAction(type, payload, success) {
    const active = state.chat.active; if (!active) return;
    try { await chatRequest(type, { conversation_id: state.chat.activeId, ...payload }); showToast(success); await refreshInbox(true); if (type === 'hide_conversation') { state.chat.active = null; state.chat.activeId = null; state.chat.messages = []; state.chat.mobileThread = false; } else if (state.chat.activeId) await loadThread(state.chat.activeId); }
    catch (e) { showToast(friendlyError(e, 'Could not update this conversation.'), 'error'); }
    state.modal = null; render();
  }

  async function handleChangePassword(form) {
    clearFormError('password-error'); const new_password = String(new FormData(form).get('newPassword') || ''); const button = form.querySelector('[type="submit"]'); setButtonBusy(button, true, 'Updating…');
    try { await apiRequest('/api/v1/auth/password', { method: 'POST', body: JSON.stringify({ new_password, device: DEVICE }) }); form.reset(); showToast('Password updated successfully.'); }
    catch (e) { setFormError('password-error', friendlyError(e, 'Could not change your password.')); }
    finally { if (button) setButtonBusy(button, false); }
  }
  async function logout() {
    try { await apiRequest('/api/v1/auth/logout', { method: 'POST', body: JSON.stringify({ device: DEVICE }) }); }
    catch (e) { console.warn('Logout endpoint error; clearing local credentials anyway.', e); }
    clearTokens(); state.page = 'discover'; state.modal = null; state.categories = []; state.myItems = []; state.items = previewFilter(); state.live = false; state.apiUnavailable = false; state.detail = null; render(); showToast('You’re logged out. See you next time.');
  }
  async function deleteAccount() {
    try { await apiRequest('/api/v1/auth/account', { method: 'DELETE', body: JSON.stringify({ device: DEVICE }) }); clearTokens(); state.confirm = null; state.page = 'discover'; state.items = previewFilter(); render(); showToast('Your account has been deleted.'); }
    catch (e) { state.confirm = null; render(); showToast(friendlyError(e, 'Could not delete your account.'), 'error'); }
  }

  // --- Event delegation: forms and buttons are deliberately plain HTML. ---
  app.addEventListener('click', async event => {
    const actionEl = event.target.closest('[data-action]');
    if (actionEl) {
      const action = actionEl.dataset.action;
      if (action === 'modal-backdrop' && event.target === actionEl) { state.modal = null; state.detail = null; state.confirm = null; render(); return; }
      if (action === 'close-modal') { state.modal = null; state.detail = null; state.confirm = null; render(); return; }
      if (action === 'dismiss-toast') { state.toasts = state.toasts.filter(t => String(t.id) !== actionEl.dataset.id); renderToasts(); return; }
      if (action === 'navigate') { setPage(actionEl.dataset.page); return; }
      if (action === 'open-auth') { openAuth(actionEl.dataset.mode || 'login'); return; }
      if (action === 'auth-mode') { state.authMode = actionEl.dataset.mode; render(); return; }
      if (action === 'toggle-password') { const input = document.getElementById(actionEl.dataset.target); if (input) { input.type = input.type === 'password' ? 'text' : 'password'; actionEl.textContent = input.type === 'password' ? 'Show' : 'Hide'; } return; }
      if (action === 'scroll-market') { $('#marketplace')?.scrollIntoView({ behavior: 'smooth', block: 'start' }); return; }
      if (action === 'category') { state.selectedCategory = actionEl.dataset.category || 'all'; if (state.userId) loadExplore(); else { state.items = previewFilter(); render(); } return; }
      if (action === 'filter-toggle') { state.filtersOpen = !state.filtersOpen; render(); return; }
      if (action === 'reset-filters') { state.search = ''; state.selectedCategory = 'all'; state.minPrice = ''; state.maxPrice = ''; state.location = ''; state.sort = 'recommended'; const input = $('#global-search'); if (input) input.value = ''; state.filtersOpen = false; if (state.userId) loadExplore(); else { state.items = previewFilter(); render(); } return; }
      if (action === 'retry-explore') { loadExplore(); return; }
      if (action === 'reload-mine') { loadMyListings(); return; }
      if (action === 'load-more') { await loadMoreListings(); return; }
      if (action === 'toggle-save') { const id = actionEl.dataset.id; if (!id) return; if (state.saved.has(id)) { state.saved.delete(id); state.savedItems.delete(id); } else { state.saved.add(id); const found = [state.detail, ...state.items, ...state.myItems, ...DEMO_ITEMS].find(x => x && x.listingId === id); if (found) state.savedItems.set(id, found); } saveSaved(); render(); return; }
      if (action === 'saved-view') { state.page = 'saved'; state.modal = null; render(); return; }
      if (action === 'edit-listing') { beginEdit(actionEl.dataset.id); return; }
      if (action === 'cancel-listing-form') { state.editing = null; setPage('my-listings'); return; }
      if (action === 'publish-listing') { const id = actionEl.dataset.id; state.confirm = { title: 'Publish this listing?', message: 'Your item will become visible to people browsing the marketplace.', confirmLabel: 'Publish item', run: () => performListingMutation('publish', id) }; render(); return; }
      if (action === 'mark-sold') { const id = actionEl.dataset.id; state.confirm = { title: 'Mark this item as sold?', message: 'This updates the listing status to sold. You can continue to refer to it in your own listing history.', confirmLabel: 'Mark as sold', run: () => performListingMutation('sold', id) }; render(); return; }
      if (action === 'delete-listing') { const id = actionEl.dataset.id; state.confirm = { title: 'Delete this listing?', message: 'This action removes the listing and cannot be undone.', confirmLabel: 'Delete listing', danger: true, run: () => performListingMutation('delete', id) }; render(); return; }
      if (action === 'contact-seller') { startConversation(actionEl.dataset.id); return; }
      if (action === 'conversation-filter') { state.chat.filter = actionEl.dataset.filter; refreshInbox(); return; }
      if (action === 'open-conversation') { loadThread(actionEl.dataset.id); return; }
      if (action === 'back-to-inbox') { state.chat.mobileThread = false; render(); return; }
      if (action === 'toggle-pin') { const c = state.chat.active; if (c) conversationAction('pin_conversation', { pin: !c.is_pinned }, c.is_pinned ? 'Conversation unpinned.' : 'Conversation pinned.'); return; }
      if (action === 'toggle-mute') { const c = state.chat.active; if (c) { const mute = !c.is_muted; conversationAction('mute_conversation', mute ? { mute: true, until: new Date(Date.now()+86400000).toISOString() } : { mute: false }, mute ? 'Conversation muted for 24 hours.' : 'Conversation unmuted.'); } return; }
      if (action === 'conversation-actions') { state.modal = { type: 'conversation-actions' }; render(); return; }
      if (action === 'toggle-archive') { const c = state.chat.active; if (c) conversationAction('archive_conversation', { archive: !c.is_archived }, c.is_archived ? 'Conversation unarchived.' : 'Conversation archived.'); return; }
      if (action === 'toggle-hide') { conversationAction('hide_conversation', { hide: true }, 'Conversation hidden from your inbox.'); return; }
      if (action === 'block-user') { const c = state.chat.active || {}; const other = c.buyer_id === state.userId ? c.seller_id : c.buyer_id; if (!other) { showToast('The other participant ID was not provided by the conversation.', 'error'); return; } state.confirm = { title: 'Block this person?', message: 'They will no longer be able to interact with you through the supported messaging flow.', confirmLabel: 'Block person', danger: true, run: async () => { try { await chatRequest('block_user', { blocked_id: other }); showToast('Person blocked.'); } catch(e) { showToast(friendlyError(e), 'error'); } state.confirm = null; state.modal = null; render(); } }; state.modal = null; render(); return; }
      if (action === 'account-tab') { state.accountTab = actionEl.dataset.tab; render(); return; }
      if (action === 'revoke-others') { try { await apiRequest('/api/v1/auth/sessions/revoke-others', { method: 'POST', body: JSON.stringify({ device: DEVICE }) }); showToast('Other sessions have been revoked.'); } catch (e) { showToast(friendlyError(e, 'Could not revoke sessions.'), 'error'); } return; }
      if (action === 'logout') { state.confirm = { title: 'Log out of Kologram?', message: 'You can sign in again whenever you want to pick things back up.', confirmLabel: 'Log out', run: logout }; render(); return; }
      if (action === 'confirm-delete-account') { state.confirm = { title: 'Delete your account permanently?', message: 'This action cannot be undone. Your current account credentials will be cleared if the server confirms deletion.', confirmLabel: 'Delete account', danger: true, run: deleteAccount }; render(); return; }
      if (action === 'cancel-confirm') { state.confirm = null; render(); return; }
      if (action === 'execute-confirm') { const run = state.confirm?.run; if (run) await run(); else { state.confirm = null; render(); } return; }
    }
    const card = event.target.closest('[data-card-id]');
    if (card && !event.target.closest('[data-action]')) { await openListingDetail(card.dataset.cardId, card.dataset.live === '1'); return; }
  });

  app.addEventListener('keydown', async event => {
    const card = event.target.closest('[data-card-id]');
    if (card && event.target === card && (event.key === 'Enter' || event.key === ' ')) { event.preventDefault(); await openListingDetail(card.dataset.cardId, card.dataset.live === '1'); }
    if (event.key === 'Escape') { if (state.confirm || state.modal || state.detail) { state.confirm = null; state.modal = null; state.detail = null; render(); } }
  });
  async function openListingDetail(id, live) {
    let item = [...state.items, ...DEMO_ITEMS, ...state.myItems].find(x => x.listingId === id);
    if (item) item = normalizeListing(item);
    state.detail = item || { listingId: id, title: 'Loading listing…', priceAmount: '—', currency: 'USD', location: 'Location not listed', cover: fallbackCover({}, 0), description: '' };
    state.modal = null; state.detailLoading = Boolean(live); render();
    if (live && state.userId) {
      try { const data = await graphql(QUERIES.listing, { id }); if (data.listing) state.detail = normalizeListing(data.listing); }
      catch (e) { showToast(friendlyError(e, 'Could not load full listing details.'), 'error'); }
      finally { state.detailLoading = false; render(); }
    }
  }
  app.addEventListener('submit', async event => {
    const form = event.target.closest('form[data-form]'); if (!form) return;
    event.preventDefault();
    const type = form.dataset.form;
    if (type === 'header-search') { const query = String(new FormData(form).get('query') || '').trim(); state.search = query; state.page = 'discover'; state.filtersOpen = false; if (state.userId) loadExplore(); else { state.items = previewFilter(); render(); $('#global-search')?.focus(); } }
    else if (type === 'filters') { const fd = new FormData(form); state.location = String(fd.get('location') || '').trim(); state.minPrice = String(fd.get('minPrice') || '').trim(); state.maxPrice = String(fd.get('maxPrice') || '').trim(); if (fd.has('categoryId')) state.selectedCategory = String(fd.get('categoryId') || 'all'); if (state.minPrice && state.maxPrice && Number(state.minPrice) > Number(state.maxPrice)) { showToast('Minimum price must be lower than maximum price.', 'error'); return; } state.filtersOpen = false; if (state.userId) loadExplore(); else { state.items = previewFilter(); render(); } }
    else if (type === 'login') await handleLogin(form);
    else if (type === 'request-verification') await handleRequestVerification(form);
    else if (type === 'signup') await handleSignup(form);
    else if (type === 'forgot-password') await handleForgot(form);
    else if (type === 'reset-password') await handleReset(form);
    else if (type === 'listing') await handleListing(form, event.submitter);
    else if (type === 'send-message') await handleSendMessage(form);
    else if (type === 'change-password') await handleChangePassword(form);
  });
  app.addEventListener('change', event => {
    if (event.target.id === 'sort-listings') { state.sort = event.target.value; if (state.userId) { if (state.live) { if (state.sort === 'price-low') state.items.sort((a,b) => Number(a.priceAmount)-Number(b.priceAmount)); else if (state.sort === 'price-high') state.items.sort((a,b) => Number(b.priceAmount)-Number(a.priceAmount)); else if (state.sort === 'newest') state.items.sort((a,b) => new Date(b.createdAt)-new Date(a.createdAt)); render(); } else loadExplore(); } else { state.items = previewFilter(); render(); } }
  });

  function initialRender() {
    state.userId = getUserId(); state.token = getTokens().access_token;
    if (state.userId) { state.page = 'discover'; render(); loadExplore(); }
    else { state.items = previewFilter(); render(); }
    // If a user opens a shared listing link, use the documented listing detail query after login.
    const sharedId = new URLSearchParams(location.search).get('listing');
    if (sharedId && state.userId) openListingDetail(sharedId, true);
  }
  window.Kologram = { API_BASE, WS_URL, version: 'vanilla-1.0', reload: () => { if (state.page === 'discover') loadExplore(); else render(); } };
  initialRender();
})();
