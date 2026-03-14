"use client";
import kyBase from "ky";
import { getDefaultStore } from "jotai"
import { tokensAtom } from "@/atoms/auth";

const store = getDefaultStore();

export const api = kyBase.create({
  prefixUrl: "/api",
  hooks: {
    beforeRequest: [async (req) => {
      const t = store.get(tokensAtom);
      if (t?.access) {
        req.headers.set("Authorization", `Bearer ${t.access}`);
      }
    }],
  },
});

/** Shape returned by Django REST Framework's StandardPagination. */
export interface PaginatedResponse<T> {
  count: number;
  total_pages: number;
  current_page: number;
  page_size: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
