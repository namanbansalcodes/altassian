"use client";

import Link from "next/link";
import type {PageNode} from "@/lib/types";

export function PageTree({nodes, spaceSlug, depth = 0}: {nodes: PageNode[]; spaceSlug: string; depth?: number}) {
  if (nodes.length === 0) {
    return <p className="px-2 py-1 text-xs text-zinc-500">No pages yet.</p>;
  }
  return (
    <ul className="flex flex-col">
      {nodes.map((n) => (
        <li key={n.id}>
          <Link
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            href={`/s/${spaceSlug}/${n.slug}` as any}
            className="block truncate rounded-md px-2 py-1 text-sm text-zinc-700 hover:bg-zinc-200"
            style={{paddingLeft: `${0.5 + depth * 0.75}rem`}}
          >
            {n.title}{n.is_draft ? <span className="ml-1 text-xs text-zinc-400">(draft)</span> : null}
          </Link>
          {n.children.length > 0 && (
            <PageTree nodes={n.children} spaceSlug={spaceSlug} depth={depth + 1} />
          )}
        </li>
      ))}
    </ul>
  );
}
