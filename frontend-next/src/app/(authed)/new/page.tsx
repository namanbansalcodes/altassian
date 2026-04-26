"use client";

import {useEffect, useState} from "react";
import {useRouter, useSearchParams} from "next/navigation";
import {useQuery, useMutation} from "@tanstack/react-query";
import {api} from "@/lib/api";

export default function NewPagePage() {
  const router = useRouter();
  const params = useSearchParams();
  const presetSpace = params.get("space");

  const {data: spaces} = useQuery({queryKey: ["spaces"], queryFn: () => api.listSpaces()});
  const [spaceSlug, setSpaceSlug] = useState<string>("");
  const [title, setTitle] = useState("");

  useEffect(() => {
    if (!spaceSlug && spaces?.results.length) {
      setSpaceSlug(presetSpace || spaces.results[0].slug);
    }
  }, [spaces, spaceSlug, presetSpace]);

  const createMutation = useMutation({
    mutationFn: async () => {
      const space = spaces!.results.find((s) => s.slug === spaceSlug)!;
      return api.createPage({space: space.id, title, body_md: `# ${title}\n\n`});
    },
    onSuccess: (page) => {
      const slug = spaces!.results.find((s) => s.id === page.space)!.slug;
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      router.push(`/s/${slug}/${page.slug}/edit` as any);
      router.refresh();
    },
  });

  return (
    <div className="mx-auto max-w-md px-6 py-12">
      <h1 className="text-xl font-semibold">New page</h1>
      <form
        className="mt-6 flex flex-col gap-3"
        onSubmit={(e) => {
          e.preventDefault();
          if (title && spaceSlug) createMutation.mutate();
        }}
      >
        <label className="flex flex-col gap-1">
          <span className="text-sm text-zinc-700">Space</span>
          <select
            value={spaceSlug}
            onChange={(e) => setSpaceSlug(e.target.value)}
            className="rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm"
          >
            {spaces?.results.map((s) => (
              <option key={s.id} value={s.slug}>{s.name}</option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1">
          <span className="text-sm text-zinc-700">Title</span>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            autoFocus
            className="rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm"
          />
        </label>
        <button
          type="submit"
          disabled={!title || !spaceSlug || createMutation.isPending}
          className="mt-2 rounded-md bg-zinc-900 px-3 py-2 text-sm font-medium text-white hover:bg-zinc-700 disabled:opacity-50"
        >
          {createMutation.isPending ? "Creating…" : "Create page"}
        </button>
      </form>
    </div>
  );
}
