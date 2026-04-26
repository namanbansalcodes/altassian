import {cookies} from "next/headers";
import {ssrApi} from "@/lib/api";
import {Editor} from "@/components/Editor";
import type {PageNode} from "@/lib/types";

function findNodeBySlug(nodes: PageNode[], slug: string): PageNode | null {
  for (const n of nodes) {
    if (n.slug === slug) return n;
    const child = findNodeBySlug(n.children, slug);
    if (child) return child;
  }
  return null;
}

export default async function EditPage({params}: {params: Promise<{slug: string; pageSlug: string}>}) {
  const {slug, pageSlug} = await params;
  const cookieHeader = (await cookies()).toString();
  const space = await ssrApi.getSpace(cookieHeader, slug);
  const node = findNodeBySlug(space.pages, pageSlug);
  if (!node) {
    return <div className="px-6 py-10">Page not found.</div>;
  }
  const page = await ssrApi.getPage(cookieHeader, node.id);
  return <Editor initial={page} spaceSlug={slug} />;
}
