export function MarkdownView({html}: {html: string}) {
  return (
    <article
      className="prose prose-zinc max-w-none prose-headings:font-semibold prose-headings:tracking-tight prose-pre:rounded-md prose-pre:bg-zinc-900 prose-pre:text-zinc-50"
      dangerouslySetInnerHTML={{__html: html}}
    />
  );
}
