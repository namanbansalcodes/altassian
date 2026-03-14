"use client";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function SpacesPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["spaces"],
    queryFn: () => api.get("spaces/").json<any[]>(),
  });

  if (isLoading) return <main className="p-4 sm:p-6">Loading...</main>;
  if (error) return <main className="p-4 sm:p-6">Failed to load spaces</main>;

  return (
    <main className="p-4 sm:p-6 max-w-4xl mx-auto">
      <h1 className="text-lg sm:text-xl font-semibold mb-4">Spaces</h1>
      <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
        {data?.map((s) => (
          <li key={s.key}>
            <Link href={`/spaces/${s.key}`} className="block border border-neutral-200 dark:border-neutral-700 rounded-xl p-4 sm:p-5 hover:border-blue-300 dark:hover:border-blue-600 hover:shadow-sm transition-all">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-400 flex items-center justify-center text-sm font-bold shrink-0">
                  {s.key.slice(0, 2)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-medium truncate">{s.name}</div>
                  <div className="text-sm text-neutral-500 line-clamp-2 mt-0.5">{s.description || "No description"}</div>
                  <div className="text-xs text-neutral-400 mt-1.5">{s.key}</div>
                </div>
              </div>
            </Link>
          </li>
        ))}
      </ul>
      {(!data || data.length === 0) && (
        <div className="text-center py-12 text-neutral-400">No spaces yet</div>
      )}
    </main>
  );
}
