"use client";
import { useEffect, useMemo } from "react";
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

  useEffect(() => {
    if (data?.title) {
      document.title = `${data.title} — Altassian`;
    }
    return () => {
      document.title = "Altassian — Git-Powered Team Knowledge Base";
    };
  }, [data?.title]);

  const schema = useMemo(() => {
    if (!data) return null;
    return {
      "@context": "https://schema.org",
      "@type": "Article",
      headline: data.title,
      description: data.meta_description || data.title,
      datePublished: data.created_at,
      dateModified: data.updated_at,
      publisher: { "@type": "Organization", name: "Altassian" },
      mainEntityOfPage: {
        "@type": "WebPage",
        "@id": `${typeof window !== "undefined" ? window.location.origin : ""}/spaces/${key}/pages/${slug}`,
      },
    };
  }, [data, key, slug]);

  if (isLoading) return <main className="p-4 sm:p-6">Loading...</main>;
  if (error || !data) return <main className="p-4 sm:p-6">Not found</main>;

  return (
    <main className="p-4 sm:p-6 max-w-4xl mx-auto space-y-4">
      {schema && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
        />
      )}
      <h1 className="text-xl sm:text-2xl font-semibold break-words">{data.title}</h1>
      <article className="bg-white dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-700 px-4 py-5 sm:p-6 md:p-8 prose max-w-none break-words">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {data.body_markdown || ""}
        </ReactMarkdown>
      </article>
    </main>
  );
}
