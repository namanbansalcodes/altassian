"use client";
import { useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery, keepPreviousData } from "@tanstack/react-query";
import { api, PaginatedResponse } from "@/lib/api";
import Pagination from "@/components/Pagination";

const PAGE_SIZE = 20;

export default function SpaceDetailPage() {
  const { key } = useParams<{ key: string }>();
  const [page, setPage] = useState(1);

  const { data: space } = useQuery({
    queryKey: ["space", key],
    queryFn: () => api.get(`spaces/${key}/`).json<any>(),
    enabled: !!key,
  });

  const { data: pagesData, isLoading } = useQuery({
    queryKey: ["pages", key, page],
    queryFn: () =>
      api
        .get("pages/", { searchParams: { space_key: key, page, page_size: PAGE_SIZE } })
        .json<PaginatedResponse<any>>(),
    enabled: !!key,
    placeholderData: keepPreviousData,
  });

  if (!space) return <main className="p-4 sm:p-6">Loading...</main>;

  const pages = pagesData?.results ?? [];

  return (
    <main className="p-4 sm:p-6 max-w-4xl mx-auto space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <h1 className="text-lg sm:text-xl font-semibold break-words max-w-full">
          {space.name}{" "}
          <span className="text-neutral-500 text-xs sm:text-sm truncate">({space.key})</span>
        </h1>
        {pagesData && (
          <span className="text-xs text-neutral-400">
            {pagesData.count} page{pagesData.count !== 1 ? "s" : ""}
          </span>
        )}
      </div>

      <div className="bg-white dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-700 overflow-hidden">
        <div className="divide-y divide-neutral-100 dark:divide-neutral-800">
          {isLoading && pages.length === 0 && (
            <div className="p-8 text-center text-neutral-400">Loading pages...</div>
          )}
          {pages.map((p: any) => (
            <Link
              key={p.id}
              className="flex items-center gap-3 px-4 py-3.5 hover:bg-neutral-50 dark:hover:bg-neutral-800 min-w-0 min-h-[48px] active:bg-neutral-100 dark:active:bg-neutral-700"
              href={`/spaces/${space.key}/pages/${p.slug}`}
            >
              <span className="text-sm font-medium truncate flex-1 min-w-0">{p.title}</span>
            </Link>
          ))}
          {!isLoading && pages.length === 0 && (
            <div className="p-8 text-center text-neutral-400 dark:text-neutral-500">
              <p>No pages yet</p>
            </div>
          )}
        </div>
      </div>

      {pagesData && (
        <Pagination
          currentPage={pagesData.current_page}
          totalPages={pagesData.total_pages}
          onPageChange={setPage}
        />
      )}
    </main>
  );
}
