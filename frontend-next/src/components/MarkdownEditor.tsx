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
      <div className="flex gap-2 border-b px-2 py-1 text-sm">
        <button
          className={`px-2 py-1 rounded ${tab === "edit" ? "bg-gray-200" : ""}`}
          onClick={() => setTab("edit")}
        >
          Edit
        </button>
        <button
          className={`px-2 py-1 rounded ${tab === "preview" ? "bg-gray-200" : ""}`}
          onClick={() => setTab("preview")}
        >
          Preview
        </button>
      </div>
      {tab === "edit" ? (
        <textarea
          className="w-full h-64 p-3 outline-none"
          value={value}
          onChange={(e) => onChange?.(e.target.value)}
          placeholder="Write markdown..."
        />
      ) : (
        <div className="prose max-w-none p-3">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{value}</ReactMarkdown>
        </div>
      )}
    </div>
  );
}
