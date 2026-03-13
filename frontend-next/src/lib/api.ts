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
