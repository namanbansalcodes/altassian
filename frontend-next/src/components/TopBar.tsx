"use client";

import {useRouter} from "next/navigation";
import {useState} from "react";
import {Search, LogOut} from "lucide-react";
import type {Route} from "next";
import {api} from "@/lib/api";
import type {User} from "@/lib/types";

export function TopBar({user}: {user: User}) {
  const router = useRouter();
  const [q, setQ] = useState("");

  function onSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!q.trim()) return;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    router.push(`/search?q=${encodeURIComponent(q.trim())}` as any);
  }

  async function logout() {
    await api.logout();
    router.push("/login" as Route<"/login">);
    router.refresh();
  }

  return (
    <header className="flex h-14 items-center justify-between border-b border-zinc-200 bg-white px-4">
      <form onSubmit={onSearch} className="relative w-full max-w-md">
        <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400" size={16} />
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search…"
          className="w-full rounded-md border border-zinc-200 bg-zinc-50 py-1.5 pl-9 pr-3 text-sm focus:border-zinc-900 focus:bg-white focus:outline-none"
        />
      </form>
      <div className="flex items-center gap-3 pl-4 text-sm">
        <span className="text-zinc-600" title={user.email}>{user.display_name || user.email}</span>
        <button
          onClick={logout}
          className="flex items-center gap-1 rounded-md border border-zinc-200 px-2 py-1 text-zinc-700 hover:bg-zinc-100"
          title="Log out"
        >
          <LogOut size={14} /> Log out
        </button>
      </div>
    </header>
  );
}
