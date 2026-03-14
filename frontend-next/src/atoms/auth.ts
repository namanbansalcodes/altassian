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

// Deduplication: only one refresh request can be in-flight at a time
let inflightRefresh: Promise<Tokens | null> | null = null;

export const refreshTokensAtom = atom(
  (get) => get(tokensAtom),
  async (get, set) => {
    if (inflightRefresh) return inflightRefresh;

    const t = get(tokensAtom);
    if (!t?.refresh) return null;

    inflightRefresh = ky
      .post("/api/auth/token/refresh/", { json: { refresh: t.refresh } })
      .json<{ access: string }>()
      .then((data) => {
        const next: Tokens = { access: data.access, refresh: t.refresh };
        set(tokensAtom, next);
        return next;
      })
      .catch(() => {
        set(tokensAtom, null);
        return null;
      })
      .finally(() => {
        inflightRefresh = null;
      });

    return inflightRefresh;
  }
);

// Eager refresh loop — schedules the next refresh based on token expiry
let refreshTimer: ReturnType<typeof setTimeout> | null = null;

export const startEagerRefreshAtom = atom(null, async (get, set) => {
  if (refreshTimer) clearTimeout(refreshTimer);

  const t = get(tokensAtom);
  if (!t?.access) return;
  const ms = msUntilExpiry(t.access);
  // refresh 30s before expiry, fallback to 4min
  const delay = ms && ms > 60000 ? Math.max(30000, ms - 30000) : 4 * 60 * 1000;
  refreshTimer = setTimeout(() => {
    refreshTimer = null;
    set(refreshTokensAtom);
    set(startEagerRefreshAtom);
  }, delay);
});
