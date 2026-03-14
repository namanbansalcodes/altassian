import { writable, derived, get } from 'svelte/store';
import { browser } from '$app/environment';
import { api } from '../api/client';
import { AuthTokens } from '../api/schemas';

const tokens = writable<{ access: string | null; refresh: string | null }>({ access: null, refresh: null });
let accessExp = 0;

export const isAuthenticated = derived(tokens, ($t) => !!$t.access);

export const currentUser = writable<{ id: number; username: string } | null>(null);

export function initFromStorage() {
  if (!browser) return;
  const raw = localStorage.getItem('auth');
  if (raw) {
    const data = JSON.parse(raw);
    tokens.set({ access: data.access ?? null, refresh: data.refresh ?? null });
    accessExp = data.accessExp ?? 0;
  }
  const userRaw = localStorage.getItem('user');
  if (userRaw) {
    try {
      currentUser.set(JSON.parse(userRaw));
    } catch { /* ignore corrupt data */ }
  }
}

export function getAccessToken() {
  return get(tokens).access;
}

export async function login(username: string, password: string) {
  const res = await api.post('auth/login/', { json: { username, password } }).json();
  const parsed = AuthTokens.parse(res);
  setTokens(parsed.access, parsed.refresh);
  try {
    const me = await api.get('auth/me/').json<{ id: number; username: string }>();
    currentUser.set(me);
    if (browser) localStorage.setItem('user', JSON.stringify(me));
  } catch { /* non-critical */ }
}

export function logout() {
  setTokens(null, null);
  currentUser.set(null);
  if (browser) localStorage.removeItem('user');
}

export function setTokens(access: string | null, refresh: string | null) {
  tokens.set({ access, refresh });
  if (browser) localStorage.setItem('auth', JSON.stringify({ access, refresh, accessExp }));
}

async function refresh() {
  const { refresh: refreshTok } = get(tokens);
  if (!refreshTok) return false;
  try {
    const res = await api.post('auth/refresh/', { json: { refresh: refreshTok } }).json();
    const parsed = AuthTokens.parse(res);
    setTokens(parsed.access, parsed.refresh);
    return true;
  } catch {
    logout();
    return false;
  }
}

export async function refreshIfNeeded() {
  const now = Math.floor(Date.now() / 1000);
  if (now + 30 >= accessExp) return await refresh();
  return true;
}

export const auth = { subscribe: tokens.subscribe };
