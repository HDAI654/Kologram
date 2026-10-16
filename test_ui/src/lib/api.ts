export const API_BASE = (import.meta.env.VITE_API_BASE || 'http://localhost:8000').replace(/\/$/, '');
export const WS_URL = import.meta.env.VITE_WS_URL || `${API_BASE.replace(/^http/, 'ws')}/ws`;
export const DEVICE = 'web';
const ACCESS_KEY = 'kologram.access_token';
const REFRESH_KEY = 'kologram.refresh_token';
const SAVED_KEY = 'kologram.saved_items';

export interface Category { categoryId: string; name: string; parentId?: string | null; isActive?: boolean }
export interface Listing {
  listingId: string; sellerId?: string; categoryId?: string; categoryLabel?: string; title: string;
  description?: string; priceAmount: string; currency?: string; quantity?: number; status?: string;
  location?: string; images?: { url: string; sortOrder?: number }[]; cover?: string; createdAt?: string; updatedAt?: string;
}
export interface SearchInput {
  query?: string; categoryId?: string | null; minPrice?: string | null; maxPrice?: string | null;
  location?: string | null; status?: string; limit?: number; offset?: number;
}
export interface Tokens { access_token: string; refresh_token: string }

export class ApiError extends Error {
  status?: number; code?: string;
  constructor(message: string, status?: number, code?: string) { super(message); this.name = 'ApiError'; this.status = status; this.code = code; }
}

export function getAccessToken() { return localStorage.getItem(ACCESS_KEY); }
export function getRefreshToken() { return localStorage.getItem(REFRESH_KEY); }
export function getUserId(): string | null {
  const token = getAccessToken();
  try {
    if (!token) return null;
    const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')));
    return typeof payload.sub === 'string' ? payload.sub : null;
  } catch { return null; }
}
export function persistTokens(tokens: Tokens) {
  localStorage.setItem(ACCESS_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
  window.dispatchEvent(new Event('kologram:auth'));
}
export function clearTokens() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
  window.dispatchEvent(new Event('kologram:auth'));
}

async function responseBody(response: Response): Promise<any> {
  if (response.status === 204) return undefined;
  const type = response.headers.get('content-type') || '';
  if (type.includes('application/json')) return response.json().catch(() => null);
  const text = await response.text().catch(() => '');
  return text ? { detail: text } : null;
}
function errorMessage(body: any, fallback: string) {
  if (typeof body?.detail === 'string') return body.detail;
  if (Array.isArray(body?.detail)) return body.detail.map((item: any) => item?.msg || 'Invalid value').join(', ');
  return body?.message || fallback;
}
let refreshPromise: Promise<boolean> | null = null;
async function refreshTokens(): Promise<boolean> {
  const refresh_token = getRefreshToken();
  if (!refresh_token) return false;
  if (!refreshPromise) refreshPromise = (async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/auth/token/refresh`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token, device: DEVICE }),
      });
      const body = await responseBody(response);
      if (!response.ok || !body?.access_token || !body?.refresh_token) { clearTokens(); return false; }
      localStorage.setItem(ACCESS_KEY, body.access_token);
      localStorage.setItem(REFRESH_KEY, body.refresh_token);
      window.dispatchEvent(new Event('kologram:auth'));
      return true;
    } catch { return false; }
    finally { refreshPromise = null; }
  })();
  return refreshPromise;
}

export async function request<T = any>(path: string, options: RequestInit = {}, auth = true, retry = true): Promise<T> {
  const headers = new Headers(options.headers || {});
  if (options.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
  const token = getAccessToken();
  if (auth && token) headers.set('Authorization', `Bearer ${token}`);
  let response: Response;
  try { response = await fetch(`${API_BASE}${path}`, { ...options, headers }); }
  catch { throw new ApiError(`Cannot reach the API gateway at ${API_BASE}. Check that your backend is running and CORS allows this frontend origin.`); }
  if (response.status === 401 && auth && retry) {
    if (await refreshTokens()) return request<T>(path, options, auth, false);
    clearTokens();
  }
  const body = await responseBody(response);
  if (!response.ok) throw new ApiError(errorMessage(body, response.status === 401 ? 'Invalid email or password.' : `Request failed (${response.status}).`), response.status);
  return body as T;
}
export function publicPost<T = any>(path: string, body: unknown) {
  return request<T>(path, { method: 'POST', body: JSON.stringify(body) }, false);
}
export async function graphql<T = any>(query: string, variables: Record<string, unknown> = {}): Promise<T> {
  const result = await request<any>('/graphql', { method: 'POST', body: JSON.stringify({ query, variables }) }, true);
  if (result?.errors?.length) {
    const error = result.errors[0];
    throw new ApiError(error.message || 'The request could not be completed.', 200, error.extensions?.code);
  }
  if (!result || result.data === undefined) throw new ApiError('The server returned an empty GraphQL response.');
  return result.data as T;
}

export const GQL = {
  categories: `query { categories(activeOnly: true) { categoryId name parentId isActive createdAt } }`,
  search: `query ($input: SearchListingsInput) { searchListings(input: $input) { items { listingId sellerId categoryId title priceAmount currency status location createdAt } limit offset } }`,
  listing: `query ($id: String!) { listing(listingId: $id) { listingId sellerId categoryId title description priceAmount currency quantity status location images { url sortOrder } createdAt updatedAt } }`,
  seller: `query ($sellerId: String!, $limit: Int, $offset: Int) { sellerListings(sellerId: $sellerId, limit: $limit, offset: $offset) { listingId title status priceAmount currency location createdAt } }`,
  create: `mutation ($input: CreateListingInput!) { createListing(input: $input) { listingId status } }`,
  update: `mutation ($input: UpdateListingInput!) { updateListing(input: $input) { listingId status } }`,
  publish: `mutation ($input: PublishListingInput!) { publishListing(input: $input) { listingId status } }`,
  status: `mutation ($input: ChangeListingStatusInput!) { changeListingStatus(input: $input) { listingId status } }`,
  delete: `mutation ($input: DeleteListingInput!) { deleteListing(input: $input) { listingId deleted } }`,
};
export const fetchCategories = () => graphql<{ categories: Category[] }>(GQL.categories).then(x => x.categories || []);
export const searchListings = (input: SearchInput) => graphql<{ searchListings: { items: Listing[]; limit: number; offset: number } }>(GQL.search, { input }).then(x => x.searchListings);
export const fetchListing = (id: string) => graphql<{ listing: Listing }>(GQL.listing, { id }).then(x => x.listing);
export const fetchSellerListings = (sellerId: string, limit = 50, offset = 0) => graphql<{ sellerListings: Listing[] }>(GQL.seller, { sellerId, limit, offset }).then(x => x.sellerListings || []);

export const DEMO_ITEMS: Listing[] = [
  { listingId: 'demo-camera', title: 'Vintage film camera', priceAmount: '185.00', currency: 'USD', categoryLabel: 'Tech & gadgets', location: 'Brooklyn, NY', status: 'ACTIVE', cover: 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=900&q=85', description: 'A beautifully kept 35mm film camera with a classic feel. Carefully stored and ready for its next chapter.', quantity: 1, createdAt: '2026-10-08T10:00:00Z' },
  { listingId: 'demo-chair', title: 'Mid-century accent chair', priceAmount: '240.00', currency: 'USD', categoryLabel: 'Home & living', location: 'Queens, NY', status: 'ACTIVE', cover: 'https://images.unsplash.com/photo-1503602642458-232111445657?auto=format&fit=crop&w=900&q=85', description: 'A sculptural accent chair with warm wood and a clean silhouette. A timeless piece for a thoughtful home.', quantity: 1, createdAt: '2026-10-07T10:00:00Z' },
  { listingId: 'demo-bag', title: 'Everyday leather tote', priceAmount: '78.00', currency: 'USD', categoryLabel: 'Style', location: 'Jersey City, NJ', status: 'ACTIVE', cover: 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=900&q=85', description: 'A versatile everyday tote with plenty of room and a timeless shape.', quantity: 1, createdAt: '2026-10-09T10:00:00Z' },
  { listingId: 'demo-lamp', title: 'Soft-glow table lamp', priceAmount: '64.00', currency: 'USD', categoryLabel: 'Home & living', location: 'Brooklyn, NY', status: 'ACTIVE', cover: 'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=900&q=85', description: 'Warm light, quiet lines, and a minimal shape that fits almost anywhere.', quantity: 1, createdAt: '2026-10-02T10:00:00Z' },
  { listingId: 'demo-record', title: 'Record player & vinyl set', priceAmount: '129.00', currency: 'USD', categoryLabel: 'Collectibles', location: 'Manhattan, NY', status: 'ACTIVE', cover: 'https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=900&q=85', description: 'A starter set for listening to records slowly. Ask about the included albums.', quantity: 1, createdAt: '2026-10-01T10:00:00Z' },
  { listingId: 'demo-bike', title: 'City commuter bicycle', priceAmount: '310.00', currency: 'USD', categoryLabel: 'Outdoors', location: 'Hoboken, NJ', status: 'ACTIVE', cover: 'https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=900&q=85', description: 'A practical city bike that makes everyday journeys feel a little more special.', quantity: 1, createdAt: '2026-10-05T10:00:00Z' },
  { listingId: 'demo-watch', title: 'Minimal steel wristwatch', priceAmount: '92.00', currency: 'USD', categoryLabel: 'Style', location: 'Brooklyn, NY', status: 'ACTIVE', cover: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=85', description: 'An understated stainless-steel watch with a clean dial and easy-to-style profile.', quantity: 1, createdAt: '2026-10-04T10:00:00Z' },
  { listingId: 'demo-plant', title: 'Ceramic planter with plant', priceAmount: '38.00', currency: 'USD', categoryLabel: 'Home & living', location: 'Astoria, NY', status: 'ACTIVE', cover: 'https://images.unsplash.com/photo-1485955900006-10f4d324d411?auto=format&fit=crop&w=900&q=85', description: 'A healthy houseplant in a textured ceramic planter. A little green for indoors.', quantity: 1, createdAt: '2026-10-03T10:00:00Z' },
  { listingId: 'demo-headphones', title: 'Studio over-ear headphones', priceAmount: '115.00', currency: 'USD', categoryLabel: 'Tech & gadgets', location: 'Brooklyn, NY', status: 'ACTIVE', cover: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=85', description: 'Comfortable over-ear headphones for focused listening, work, or long journeys.', quantity: 1, createdAt: '2026-10-06T10:00:00Z' },
  { listingId: 'demo-ceramics', title: 'Handmade ceramic vessels', priceAmount: '56.00', currency: 'USD', categoryLabel: 'Home & living', location: 'Brooklyn, NY', status: 'ACTIVE', cover: 'https://images.unsplash.com/photo-1578749556568-bc2c40e68b61?auto=format&fit=crop&w=900&q=85', description: 'A small set of tactile, handmade ceramic vessels in soft natural tones.', quantity: 1, createdAt: '2026-10-10T10:00:00Z' },
  { listingId: 'demo-desk', title: 'Oak writing desk', priceAmount: '325.00', currency: 'USD', categoryLabel: 'Home & living', location: 'Park Slope, NY', status: 'ACTIVE', cover: 'https://images.unsplash.com/photo-1499933374294-4584851497cc?auto=format&fit=crop&w=900&q=85', description: 'A considered workspace piece with a light oak finish and simple lines.', quantity: 1, createdAt: '2026-10-09T10:00:00Z' },
  { listingId: 'demo-speaker', title: 'Compact wireless speaker', priceAmount: '89.00', currency: 'USD', categoryLabel: 'Tech & gadgets', location: 'Greenpoint, NY', status: 'ACTIVE', cover: 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=900&q=85', description: 'A compact speaker with a warm sound and understated design.', quantity: 1, createdAt: '2026-10-11T10:00:00Z' },
];
export const STATIC_CATEGORIES = [
  { name: 'All finds', slug: 'all', icon: '✨' }, { name: 'Tech & gadgets', slug: 'tech', icon: '⌘' },
  { name: 'Home & living', slug: 'home', icon: '⌂' }, { name: 'Style', slug: 'style', icon: '◇' },
  { name: 'Outdoors', slug: 'outdoors', icon: '↗' }, { name: 'Collectibles', slug: 'collectibles', icon: '◎' },
];

export function getSavedItems(): Listing[] {
  try { return JSON.parse(localStorage.getItem(SAVED_KEY) || '[]') as Listing[]; } catch { return []; }
}
export function saveListing(item: Listing): boolean {
  const items = getSavedItems();
  const exists = items.some(x => x.listingId === item.listingId);
  localStorage.setItem(SAVED_KEY, JSON.stringify(exists ? items.filter(x => x.listingId !== item.listingId) : [...items, item]));
  window.dispatchEvent(new Event('kologram:saved'));
  return !exists;
}
export function isSaved(id: string) { return getSavedItems().some(x => x.listingId === id); }
export function money(item: Pick<Listing, 'priceAmount' | 'currency'>) {
  const currency = item.currency || 'USD';
  const amount = Number(item.priceAmount);
  if (!Number.isFinite(amount)) return `${item.priceAmount} ${currency}`;
  try { return new Intl.NumberFormat(undefined, { style: 'currency', currency, maximumFractionDigits: 2 }).format(amount); }
  catch { return `${currency} ${amount.toFixed(2)}`; }
}
export function normalizeListing(item: Listing, categories: Category[] = [], index = 0): Listing {
  const images = Array.isArray(item.images) ? [...item.images].sort((a, b) => (a.sortOrder || 0) - (b.sortOrder || 0)) : [];
  return { ...item, cover: images.find(i => i.url)?.url || item.cover || DEMO_ITEMS[index % DEMO_ITEMS.length].cover || DEMO_ITEMS[0].cover, categoryLabel: item.categoryLabel || categories.find(c => c.categoryId === item.categoryId)?.name || 'Marketplace find', location: item.location || 'Location not listed', description: item.description || 'Ask the seller for more details about this item.', currency: item.currency || 'USD' };
}
