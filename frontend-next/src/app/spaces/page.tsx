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
    <main className="p-4 sm:p-6">
      <h1 className="text-lg sm:text-xl font-semibold mb-4">Spaces</h1>
      <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
        {data?.map((s) => (
          <li key={s.key} className="border rounded-lg p-3 sm:p-4">
            <div className="font-medium truncate">{s.name} <span className="text-zinc-500 text-sm">({s.key})</span></div>
            <div className="text-sm text-zinc-600 line-clamp-2 mt-1">{s.description}</div>
            <Link className="underline text-sm mt-2 inline-block" href={`/spaces/${s.key}`}>Open</Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
