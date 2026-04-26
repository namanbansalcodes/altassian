import Link from "next/link";
import {cookies} from "next/headers";
import {ssrApi} from "@/lib/api";
import {PageTree} from "@/components/PageTree";
import {MarkdownView} from "@/components/MarkdownView";
import {Pencil} from "lucide-react";
import type {PageNode} from "@/lib/types";
import type {Route} from "next";

function findNodeBySlug(nodes: PageNode[], slug: string): PageNode | null {
  for (const n of nodes) {
    if (n.slug === slug) return n;
    const child = findNodeBySlug(n.children, slug);
    if (child) return child;
  }
  return null;
}

export default async function PageView({params}: {params: Promise<{slug: string; pageSlug: string}>}) {
  const {slug, pageSlug} = await params;
  const cookieHeader = (await cookies()).toString();

  const space = await ssrApi.getSpace(cookieHeader, slug).catch(() => null);
  if (!space) {
    return <div className="px-6 py-10">Space not found.</div>;
  }

  const node = findNodeBySlug(space.pages, pageSlug);
  if (!node) {
    return (
      <div className="px-6 py-10">
        <p>Page not found.</p>
        {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
        <Link href={`/s/${slug}` as any} className="text-sm text-zinc-600 underline">Back to {space.name}</Link>
      </div>
    );
  }

  const page = await ssrApi.getPage(cookieHeader, node.id);

  return (
    <div className="flex min-h-full">
      <aside className="hidden w-64 shrink-0 border-r border-zinc-200 bg-zinc-50 lg:block">
        <div className="border-b border-zinc-200 px-4 py-3 text-sm font-medium text-zinc-900">
          {space.icon} {space.name}
        </div>
        <div className="p-2">
          <PageTree nodes={space.pages} spaceSlug={space.slug} />
        </div>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col px-6 py-8">
        <div className="mb-4 flex items-center justify-between">
          <h1 className="text-3xl font-semibold tracking-tight">{page.title}</h1>
          <Link
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            href={`/s/${slug}/${pageSlug}/edit` as any}
            className="flex items-center gap-1 rounded-md border border-zinc-200 px-3 py-1.5 text-sm text-zinc-700 hover:bg-zinc-50"
          >
            <Pencil size={14} /> Edit
          </Link>
        </div>
        <MarkdownView html={page.body_html} />
      </div>
    </div>
  );
}
