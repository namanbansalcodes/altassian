"use client";
import { useState } from "react";
import Link from "next/link";
import { useQuery, keepPreviousData } from "@tanstack/react-query";
import { api, PaginatedResponse } from "@/lib/api";
import Pagination from "@/components/Pagination";

const PAGE_SIZE = 20;

export default function SpacesPage() {
  const [page, setPage] = useState(1);

  const { data, isLoading, error } = useQuery({
    queryKey: ["spaces", page],
    queryFn: () =>
      api.get("spaces/", { searchParams: { page, page_size: PAGE_SIZE } }).json<PaginatedResponse<any>>(),
    placeholderData: keepPreviousData,
  });

  if (isLoading && !data) return <main className="p-4 sm:p-6">Loading...</main>;
  if (error) return <main className="p-4 sm:p-6">Failed to load spaces</main>;

  const spaces = data?.results ?? [];

  return (
    <main className="p-4 sm:p-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-lg sm:text-xl font-semibold">Spaces</h1>
        {data && (
          <span className="text-xs text-neutral-400">
            {data.count} space{data.count !== 1 ? "s" : ""}
          </span>
        )}
      </div>
      <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
        {spaces.map((s: any) => (
          <li key={s.key}>
            <Link
              href={`/spaces/${s.key}`}
              className="block border border-neutral-200 dark:border-neutral-700 rounded-xl p-4 sm:p-5 hover:border-blue-300 dark:hover:border-blue-600 hover:shadow-sm transition-all"
            >
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-400 flex items-center justify-center text-sm font-bold shrink-0">
                  {s.key.slice(0, 2)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-medium truncate">{s.name}</div>
                  <div className="text-sm text-neutral-500 line-clamp-2 mt-0.5">
                    {s.description || "No description"}
                  </div>
                  <div className="text-xs text-neutral-400 mt-1.5">{s.key}</div>
                </div>
              </div>
            </Link>
          </li>
        ))}
      </ul>
      {!isLoading && spaces.length === 0 && (
        <div className="text-center py-12 text-neutral-400">No spaces yet</div>
      )}

      {data && (
        <Pagination
          currentPage={data.current_page}
          totalPages={data.total_pages}
          onPageChange={setPage}
        />
      )}
    </main>
  );
}
