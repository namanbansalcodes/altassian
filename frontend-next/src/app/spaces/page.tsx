"use client";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function SpacesPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["spaces"],
    queryFn: () => api.get("spaces/").json<any[]>(),
  });

  if (isLoading) return <main className="p-6">Loading...</main>;
  if (error) return <main className="p-6">Failed to load spaces</main>;

  return (
    <main className="p-6">
      <h1 className="text-xl font-semibold mb-4">Spaces</h1>
      <ul className="space-y-2">
        {data?.map((s) => (
          <li key={s.key} className="border rounded p-3">
            <div className="font-medium">{s.name} ({s.key})</div>
            <div className="text-sm text-zinc-600">{s.description}</div>
            <Link className="underline text-sm" href={`/spaces/${s.key}`}>Open</Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
