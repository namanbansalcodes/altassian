"use client";

import {useState, useTransition} from "react";
import {useRouter} from "next/navigation";
import CodeMirror from "@uiw/react-codemirror";
import {markdown} from "@codemirror/lang-markdown";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {api} from "@/lib/api";
import type {PageDetail} from "@/lib/types";
import {Save, Eye} from "lucide-react";

export function Editor({initial, spaceSlug}: {initial: PageDetail; spaceSlug: string}) {
  const router = useRouter();
  const [title, setTitle] = useState(initial.title);
  const [body, setBody] = useState(initial.body_md);
  const [busy, setBusy] = useState(false);
  const [, startTransition] = useTransition();

  async function save() {
    setBusy(true);
    try {
      const updated = await api.updatePage(initial.id, {title, body_md: body});
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      startTransition(() => router.push(`/s/${spaceSlug}/${updated.slug}` as any));
      router.refresh();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-full flex-col">
      <div className="flex items-center gap-3 border-b border-zinc-200 px-4 py-2">
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="flex-1 bg-transparent text-2xl font-semibold tracking-tight focus:outline-none"
          placeholder="Untitled"
        />
        <button
          onClick={save}
          disabled={busy}
          className="flex items-center gap-1 rounded-md bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-zinc-700 disabled:opacity-50"
        >
          <Save size={14} /> {busy ? "Saving…" : "Save"}
        </button>
      </div>
      <div className="grid min-h-0 flex-1 grid-cols-2 divide-x divide-zinc-200">
        <div className="overflow-auto">
          <CodeMirror
            value={body}
            onChange={setBody}
            extensions={[markdown()]}
            basicSetup={{lineNumbers: false, foldGutter: false}}
            theme="light"
            className="text-sm"
          />
        </div>
        <div className="overflow-auto px-6 py-4">
          <div className="mb-3 flex items-center gap-1 text-xs uppercase tracking-wide text-zinc-500">
            <Eye size={12} /> Preview
          </div>
          <article className="prose prose-zinc max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{body || "_Nothing yet._"}</ReactMarkdown>
          </article>
        </div>
      </div>
    </div>
  );
}
