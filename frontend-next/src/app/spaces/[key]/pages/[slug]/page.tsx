"use client";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function PageDetail() {
  const { key, slug } = useParams<{ key: string; slug: string }>();
  const { data, isLoading, error } = useQuery({
    queryKey: ["page", key, slug],
    queryFn: () =>
      api
        .get("pages/by-slug/", { searchParams: { space_key: key, slug } })
        .json<any>(),
    enabled: !!key && !!slug,
  });

  if (isLoading) return <main className="p-4 sm:p-6">Loading...</main>;
  if (error || !data) return <main className="p-4 sm:p-6">Not found</main>;

  return (
    <main className="p-4 sm:p-6 space-y-4">
      <h1 className="text-xl sm:text-2xl font-semibold">{data.title}</h1>
      <div className="prose max-w-none overflow-x-auto">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {data.body_markdown || ""}
        </ReactMarkdown>
      </div>
    </main>
  );
}
