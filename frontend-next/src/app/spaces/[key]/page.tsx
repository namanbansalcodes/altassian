"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function SpaceDetailPage() {
  const { key } = useParams<{ key: string }>();
  const { data: space } = useQuery({
    queryKey: ["space", key],
    queryFn: () => api.get(`spaces/${key}/`).json<any>(),
    enabled: !!key,
  });
  const { data: pages } = useQuery({
    queryKey: ["pages", key],
    queryFn: () => api.get("pages/", { searchParams: { space_key: key } }).json<any[]>(),
    enabled: !!key,
  });

  if (!space) return <main className="p-4 sm:p-6">Loading...</main>;

  return (
    <main className="p-4 sm:p-6 max-w-4xl mx-auto space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <h1 className="text-lg sm:text-xl font-semibold break-words">{space.name} <span className="text-zinc-500 text-sm">({space.key})</span></h1>
      </div>
      <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-700 overflow-hidden">
        <div className="divide-y divide-zinc-100 dark:divide-zinc-800">
          {pages?.map((p) => (
            <Link key={p.id} className="flex items-center gap-3 px-4 py-3 hover:bg-zinc-50 dark:hover:bg-zinc-800 min-w-0" href={`/spaces/${space.key}/pages/${p.slug}`}>
              <span className="text-sm font-medium truncate flex-1 min-w-0">{p.title}</span>
            </Link>
          ))}
          {(!pages || pages.length === 0) && (
            <div className="p-8 text-center text-zinc-400 dark:text-zinc-500">
              <p>No pages yet</p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
