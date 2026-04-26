import Link from "next/link";
import {redirect} from "next/navigation";
import {cookies} from "next/headers";
import {ssrApi} from "@/lib/api";
import {PageTree} from "@/components/PageTree";
import type {Route} from "next";

export default async function SpacePage({params}: {params: Promise<{slug: string}>}) {
  const {slug} = await params;
  const cookieHeader = (await cookies()).toString();
  let space;
  try {
    space = await ssrApi.getSpace(cookieHeader, slug);
  } catch {
    return (
      <div className="mx-auto max-w-3xl px-6 py-10">
        <h1 className="text-xl font-semibold">Space not found</h1>
        <Link href={"/home" as Route} className="mt-2 block text-sm text-zinc-600 underline">Back to home</Link>
      </div>
    );
  }

  const firstRoot = space.pages[0];
  if (firstRoot) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    redirect(`/s/${slug}/${firstRoot.slug}` as any);
  }

  return (
    <div className="flex min-h-full">
      <aside className="hidden w-64 shrink-0 border-r border-zinc-200 bg-zinc-50 lg:block">
        <div className="border-b border-zinc-200 px-4 py-3 text-sm font-medium text-zinc-900">
          {space.icon} {space.name}
        </div>
        <div className="p-2">
          <PageTree nodes={space.pages} spaceSlug={space.slug} />
        </div>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col items-start px-6 py-10">
        <h1 className="text-2xl font-semibold tracking-tight">{space.name}</h1>
        {space.description && <p className="mt-1 text-sm text-zinc-600">{space.description}</p>}
        <p className="mt-6 text-sm text-zinc-500">No pages yet in this space.</p>
        <Link
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          href={`/new?space=${space.slug}` as any}
          className="mt-3 rounded-md bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-zinc-700"
        >
          Create the first page
        </Link>
      </div>
    </div>
  );
}
