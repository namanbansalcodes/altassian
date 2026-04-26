import Link from "next/link";
import {cookies} from "next/headers";
import {ssrApi} from "@/lib/api";

export default async function HomePage() {
  const cookieHeader = (await cookies()).toString();
  const spaces = await ssrApi.listSpaces(cookieHeader).catch(() => ({results: []}));

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <h1 className="text-2xl font-semibold tracking-tight">Welcome back</h1>
      <p className="mt-1 text-sm text-zinc-600">Pick a space to dive in, or create a new page.</p>

      <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
        {spaces.results.map((s) => (
          <Link
            key={s.id}
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            href={`/s/${s.slug}` as any}
            className="rounded-lg border border-zinc-200 bg-white p-4 hover:border-zinc-300 hover:shadow-sm"
          >
            <div className="flex items-center gap-2 text-base font-medium text-zinc-900">
              {s.icon && <span>{s.icon}</span>}
              {s.name}
            </div>
            {s.description && (
              <p className="mt-1 line-clamp-2 text-sm text-zinc-600">{s.description}</p>
            )}
          </Link>
        ))}
        {spaces.results.length === 0 && (
          <p className="text-sm text-zinc-500">No spaces yet. Ask an admin to create one in Django admin.</p>
        )}
      </div>
    </div>
  );
}
