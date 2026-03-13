"use client";
import { atom } from "jotai";
import { atomWithStorage } from "jotai/utils";
import ky from "ky";
import { Tokens, msUntilExpiry } from "@/lib/auth";

export const tokensAtom = atomWithStorage<Tokens | null>(
  "tokens",
  null
);

export const isAuthedAtom = atom((get) => Boolean(get(tokensAtom)?.access));

export const refreshTokensAtom = atom(
  (get) => get(tokensAtom),
  async (get, set) => {
    const t = get(tokensAtom);
    if (!t?.refresh) return null;
    try {
      const data = await ky
        .post("/api/auth/token/refresh/", { json: { refresh: t.refresh } })
        .json<{ access: string }>();
      const next = { access: data.access, refresh: t.refresh };
      set(tokensAtom, next);
      return next;
    } catch (e) {
      set(tokensAtom, null);
      return null;
    }
  }
);

// Eager refresh loop
export const startEagerRefreshAtom = atom(null, async (get, set) => {
  const t = get(tokensAtom);
  if (!t?.access) return;
  const ms = msUntilExpiry(t.access);
  // refresh 30s before expiry, fallback to 4min
  const delay = ms && ms > 60000 ? Math.max(30000, ms - 30000) : 4 * 60 * 1000;
  setTimeout(() => {
    // fire and forget
    set(refreshTokensAtom);
    set(startEagerRefreshAtom);
  }, delay);
});
