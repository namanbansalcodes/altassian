import {SearchResults} from "@/components/SearchResults";

export default async function SearchPage({searchParams}: {searchParams: Promise<{q?: string}>}) {
  const {q} = await searchParams;
  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <h1 className="text-xl font-semibold">Search</h1>
      <p className="mt-1 text-sm text-zinc-600">
        Results for {q ? <span className="font-mono">{q}</span> : <em>(no query)</em>}
      </p>
      <div className="mt-6">
        <SearchResults query={q ?? ""} />
      </div>
    </div>
  );
}
