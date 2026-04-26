import Link from "next/link";
import type {Route} from "next";
import type {Space} from "@/lib/types";

export function Sidebar({spaces}: {spaces: Space[]}) {
  return (
    <aside className="hidden w-64 shrink-0 border-r border-zinc-200 bg-zinc-50 lg:block">
      <div className="flex h-14 items-center border-b border-zinc-200 px-4">
        <Link href={"/home" as Route} className="font-semibold tracking-tight">
          Altassian
        </Link>
      </div>
      <nav className="flex flex-col gap-1 p-3 text-sm">
        <Link href={"/home" as Route} className="rounded-md px-2 py-1.5 text-zinc-700 hover:bg-zinc-200">
          Home
        </Link>
        <Link href={"/new" as Route} className="rounded-md px-2 py-1.5 text-zinc-700 hover:bg-zinc-200">
          + New page
        </Link>
        <div className="mt-4 px-2 text-xs uppercase tracking-wide text-zinc-500">Spaces</div>
        {spaces.length === 0 ? (
          <p className="px-2 py-1.5 text-xs text-zinc-500">No spaces yet.</p>
        ) : (
          spaces.map((s) => (
            <Link
              key={s.id}
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              href={`/s/${s.slug}` as any}
              className="rounded-md px-2 py-1.5 text-zinc-700 hover:bg-zinc-200"
            >
              {s.icon ? <span className="mr-1">{s.icon}</span> : null}
              {s.name}
            </Link>
          ))
        )}
      </nav>
    </aside>
  );
}
