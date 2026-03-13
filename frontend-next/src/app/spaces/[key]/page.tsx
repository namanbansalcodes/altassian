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

  if (!space) return <main className="p-6">Loading...</main>;

  return (
    <main className="p-6 space-y-4">
      <h1 className="text-xl font-semibold">{space.name} ({space.key})</h1>
      <ul className="space-y-1">
        {pages?.map((p) => (
          <li key={p.id}>
            <Link className="underline" href={`/spaces/${space.key}/pages/${p.slug}`}>{p.title}</Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
