"use client";

import Link from "next/link";
import {useQuery} from "@tanstack/react-query";
import {api} from "@/lib/api";

export function SearchResults({query}: {query: string}) {
  const {data, isLoading, isError} = useQuery({
    queryKey: ["search", query],
    queryFn: () => api.search(query),
    enabled: query.length > 0,
  });

  if (!query) return <p className="text-sm text-zinc-500">Type a query to search.</p>;
  if (isLoading) return <p className="text-sm text-zinc-500">Searching…</p>;
  if (isError) return <p className="text-sm text-rose-600">Search failed.</p>;
  if (!data?.results.length) return <p className="text-sm text-zinc-500">No results.</p>;

  return (
    <ul className="flex flex-col divide-y divide-zinc-100">
      {data.results.map((r) => (
        <li key={r.page_id} className="py-3">
          <Link
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            href={`/s/${r.space_slug}/${r.page_slug}` as any}
            className="block hover:bg-zinc-50"
          >
            <div className="text-sm font-medium text-zinc-900">{r.title}</div>
            <div className="mt-0.5 text-xs uppercase tracking-wide text-zinc-500">{r.space_slug}</div>
            <p
              className="mt-1 text-sm text-zinc-600"
              dangerouslySetInnerHTML={{__html: r.snippet_html}}
            />
          </Link>
        </li>
      ))}
    </ul>
  );
}
