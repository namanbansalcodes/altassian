"use client";
import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type Props = {
  value?: string;
  onChange?: (v: string) => void;
};

export default function MarkdownEditor({ value = "", onChange }: Props) {
  const [tab, setTab] = useState<"edit" | "preview">("edit");
  return (
    <div className="border rounded-md">
      <div className="flex gap-2 border-b px-3 sm:px-4 py-1.5 sm:py-2 text-sm" role="tablist" aria-label="Editor mode">
        <button
          role="tab"
          aria-selected={tab === "edit"}
          aria-controls="editor-tabpanel"
          id="editor-tab-edit"
          className={`px-3 py-2 rounded min-h-[44px] ${tab === "edit" ? "bg-gray-200 dark:bg-gray-700" : ""}`}
          onClick={() => setTab("edit")}
        >
          Edit
        </button>
        <button
          role="tab"
          aria-selected={tab === "preview"}
          aria-controls="editor-tabpanel"
          id="editor-tab-preview"
          className={`px-3 py-2 rounded min-h-[44px] ${tab === "preview" ? "bg-gray-200 dark:bg-gray-700" : ""}`}
          onClick={() => setTab("preview")}
        >
          Preview
        </button>
      </div>
      <div id="editor-tabpanel" role="tabpanel" aria-labelledby={`editor-tab-${tab}`}>
        {tab === "edit" ? (
          <textarea
            className="w-full min-h-[12rem] sm:min-h-[14rem] md:min-h-[16rem] p-3 outline-none text-base resize-y"
            value={value}
            onChange={(e) => onChange?.(e.target.value)}
            placeholder="Write markdown..."
            aria-label="Markdown content"
          />
        ) : (
          <div className="prose max-w-none p-3 overflow-x-auto break-words">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{value}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}
