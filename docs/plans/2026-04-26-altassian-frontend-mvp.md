# Altassian Frontend MVP — Implementation Plan (Plan 2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use `- [ ]` checkboxes.

**Goal:** A working Next.js frontend at `frontend-next/` wired to the Plan 1 backend. End state: a logged-in user can browse spaces, view a hierarchical page tree, view rendered markdown pages, edit pages in a split-pane markdown editor with live preview, create new pages, and search. Frontend is deployable behind the existing GCP LB.

**Architecture:** Next.js 16 (App Router) + React 19 + TanStack Query + ky + Tailwind v4. Auth via the backend's httpOnly cookies (no token in JS). Server Components for initial data fetches where it makes sense; Client Components for interactive bits (editor, search box). Backend at `/api/*` is reverse-proxied by the LB, so the frontend uses relative URLs.

**Tech Stack:** Next.js 16, React 19, TypeScript, Tailwind CSS v4, TanStack Query 5, ky, jotai, react-markdown + remark-gfm (for live preview), `@uiw/react-codemirror` + `@codemirror/lang-markdown` (markdown source pane), `lucide-react` (icons), `clsx` for class composition.

**Spec:** `docs/specs/2026-04-26-altassian-mvp-design.md`. Backend plan: `docs/plans/2026-04-26-altassian-backend-mvp.md`.

**Out of scope for v1 (intentionally):** Comments UI, attachments UI, version history UI, invite-accept page (admin uses Django admin to create users for v1), settings page, public-page rendering, mobile drawer polish, animations beyond the obvious.

---

## File Map

```
frontend-next/
  package.json                       # add deps
  next.config.ts                     # add /api/* rewrite to backend
  src/
    app/
      layout.tsx                     # root layout (providers)
      providers.tsx                  # QueryClientProvider, jotai Provider
      globals.css                    # tailwind base
      page.tsx                       # /  → redirect to /home or /login
      login/
        page.tsx                     # /login (form)
      (authed)/                      # auth-gated layout
        layout.tsx                   # auth check + chrome (sidebar + topbar)
        home/
          page.tsx                   # /home — recent pages
        s/
          [slug]/
            page.tsx                 # /s/<space>  → space welcome / first page
            [pageSlug]/
              page.tsx               # /s/<space>/<page> view
              edit/
                page.tsx             # /s/<space>/<page>/edit
        search/
          page.tsx                   # /search?q=
        new/
          page.tsx                   # /new — create a new page (pick space + title)
    components/
      Chrome.tsx                     # top bar + sidebar layout shell
      Sidebar.tsx                    # spaces list + page tree
      TopBar.tsx                     # logo, search input, user menu
      LoginForm.tsx
      PageTree.tsx                   # recursive nested list
      MarkdownView.tsx               # render server html (or client md fallback)
      Editor.tsx                     # split-pane: codemirror + preview
      SearchResults.tsx
      Empty.tsx                      # tiny "nothing here" stub
    lib/
      api.ts                         # ky instance, types, fetchers
      auth.ts                        # me() helper, server-side getCurrentUser
      types.ts                       # User, Space, Page, PageNode, SearchResult
      hooks.ts                       # useSpaces, useSpace, usePage, useSearch, etc.
  Dockerfile                         # already exists — replaced in this plan
```

Existing legacy under `src/` (login/page.tsx, register, [key], components like Pagination, etc.) gets deleted in Task 0.

---

## Task 0: Cleanup the legacy frontend-next scaffolding

The existing `src/app/*` and `src/components/*` were AI-built against the OLD backend (`Space.key`, separate `register` flow, etc.). Easier to nuke than refactor.

**Files:** Delete most of `src/`. Keep `src/app/globals.css` and `src/app/favicon.ico`/`src/app/layout.tsx` shell as references but plan to overwrite.

- [ ] **Step 1: Delete legacy app routes and components**

```bash
cd /home/namanbansal/.openclaw/workspace/altassian_backend/frontend-next
rm -rf src/app/login src/app/register src/app/spaces src/components
rm -f src/lib/query.tsx
# Keep src/app/layout.tsx and src/app/page.tsx for now — they'll be rewritten in Task 2
# Keep src/app/globals.css (tailwind base)
```

- [ ] **Step 2: Verify deletions**

```bash
ls src/app/
# Expected: globals.css, layout.tsx, page.tsx, favicon.ico (or similar small set)
ls src/components 2>&1 | tail -1
# Expected: "No such file or directory"
```

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "chore(frontend): nuke legacy frontend-next scaffolding"
```

---

## Task 1: Add deps + Next config

**Files:** `frontend-next/package.json`, `frontend-next/next.config.ts`

- [ ] **Step 1: Add new dependencies**

```bash
cd /home/namanbansal/.openclaw/workspace/altassian_backend/frontend-next
npm install --save \
  @uiw/react-codemirror@^4.23 \
  @codemirror/lang-markdown@^6.3 \
  lucide-react@^0.460 \
  clsx@^2.1
```

- [ ] **Step 2: Replace `next.config.ts` with this**

```typescript
import type {NextConfig} from "next";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    // In dev, the Next server proxies /api/* to the Django dev server.
    // In prod, the GCP LB does the routing — these rewrites are a no-op there.
    return [
      {source: "/api/:path*", destination: `${apiBase}/api/:path*`},
    ];
  },
  reactStrictMode: true,
  experimental: {typedRoutes: true},
};

export default nextConfig;
```

- [ ] **Step 3: Add `.env.local` with dev API base**

```bash
echo 'NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000' > .env.local
```

(Confirm `.env.local` is in `.gitignore` — Next.js's default `.gitignore` covers it.)

- [ ] **Step 4: Smoke test**

```bash
npm run build 2>&1 | tail -20
# Expected: build fails because pages are gone — that's fine.
# Or "compiled successfully" with warnings about empty pages — also fine.
```

- [ ] **Step 5: Commit**

```bash
git add package.json package-lock.json next.config.ts
git commit -m "chore(frontend): add codemirror, lucide, clsx; wire dev API rewrite"
```

---

## Task 2: API client + types + auth helpers

**Files:** Create `src/lib/api.ts`, `src/lib/types.ts`, `src/lib/auth.ts`

- [ ] **Step 1: `src/lib/types.ts`**

```typescript
export type Role = "admin" | "member";

export interface User {
  id: number;
  email: string;
  display_name: string;
  avatar_url: string;
  role: Role;
  joined_at: string;
}

export interface Space {
  id: number;
  slug: string;
  name: string;
  description: string;
  icon: string;
  position: number;
  created_at: string;
  updated_at: string;
}

export interface PageNode {
  id: number;
  slug: string;
  title: string;
  is_draft: boolean;
  is_public: boolean;
  position: number;
  children: PageNode[];
}

export interface SpaceDetail extends Space {
  pages: PageNode[];
}

export interface PageDetail {
  id: number;
  space: number;
  parent: number | null;
  slug: string;
  title: string;
  body_md: string;
  body_html: string;
  position: number;
  is_public: boolean;
  is_draft: boolean;
  created_by: number;
  updated_by: number;
  created_at: string;
  updated_at: string;
}

export interface SearchResult {
  page_id: number;
  space_slug: string;
  page_slug: string;
  title: string;
  snippet_html: string;
  rank: number;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
```

- [ ] **Step 2: `src/lib/api.ts`**

```typescript
import ky, {HTTPError} from "ky";
import type {
  PageDetail,
  Paginated,
  SearchResult,
  Space,
  SpaceDetail,
  User,
} from "./types";

// Browser uses relative /api (handled by Next rewrite in dev, by LB in prod).
// Server-side rendering needs an absolute base.
const isServer = typeof window === "undefined";
const SERVER_API_BASE =
  process.env.INTERNAL_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://127.0.0.1:8000";

const browser = ky.create({
  prefixUrl: "/api",
  credentials: "include",
  retry: 0,
  timeout: 15_000,
});

function server(cookieHeader?: string) {
  return ky.create({
    prefixUrl: `${SERVER_API_BASE}/api`,
    headers: cookieHeader ? {cookie: cookieHeader} : undefined,
    retry: 0,
    timeout: 15_000,
  });
}

export const api = {
  // Auth
  login: (email: string, password: string) =>
    browser.post("auth/login", {json: {email, password}}).json<User>(),
  logout: () => browser.post("auth/logout"),
  me: () => browser.get("auth/me").json<User>(),

  // Spaces
  listSpaces: () => browser.get("spaces/").json<Paginated<Space>>(),
  getSpace: (slug: string) => browser.get(`spaces/${slug}/`).json<SpaceDetail>(),
  createSpace: (data: {slug: string; name: string; description?: string}) =>
    browser.post("spaces/", {json: data}).json<Space>(),

  // Pages
  getPage: (id: number) => browser.get(`pages/${id}/`).json<PageDetail>(),
  createPage: (data: {space: number; parent?: number | null; title: string; body_md: string}) =>
    browser.post("pages/", {json: data}).json<PageDetail>(),
  updatePage: (id: number, data: Partial<PageDetail>) =>
    browser.patch(`pages/${id}/`, {json: data}).json<PageDetail>(),
  deletePage: (id: number) => browser.delete(`pages/${id}/`),
  movePage: (id: number, parent_id: number | null, position: number) =>
    browser.post(`pages/${id}/move`, {json: {parent_id, position}}).json<PageDetail>(),

  // Search
  search: (q: string, space?: string) =>
    browser
      .get("search/", {searchParams: space ? {q, space} : {q}})
      .json<{results: SearchResult[]}>(),
};

// Server-side fetchers (need cookies forwarded from incoming request)
export const ssrApi = {
  me: (cookieHeader?: string) => server(cookieHeader).get("auth/me").json<User>(),
  getSpace: (cookieHeader: string, slug: string) =>
    server(cookieHeader).get(`spaces/${slug}/`).json<SpaceDetail>(),
  listSpaces: (cookieHeader: string) =>
    server(cookieHeader).get("spaces/").json<Paginated<Space>>(),
  getPage: (cookieHeader: string, id: number) =>
    server(cookieHeader).get(`pages/${id}/`).json<PageDetail>(),
};

export {HTTPError};
```

- [ ] **Step 3: `src/lib/auth.ts`**

```typescript
import {cookies} from "next/headers";
import {redirect} from "next/navigation";
import type {User} from "./types";
import {ssrApi} from "./api";

/** Get current user during SSR. Redirects to /login on 401. */
export async function requireUser(): Promise<User> {
  const cookieHeader = (await cookies()).toString();
  try {
    return await ssrApi.me(cookieHeader);
  } catch {
    redirect("/login");
  }
}

/** Try to get user; returns null instead of redirecting. */
export async function maybeUser(): Promise<User | null> {
  const cookieHeader = (await cookies()).toString();
  try {
    return await ssrApi.me(cookieHeader);
  } catch {
    return null;
  }
}
```

- [ ] **Step 4: Build to verify TypeScript**

```bash
npm run build 2>&1 | tail -10
# Expected: no type errors. Pages still missing — that's fine.
```

- [ ] **Step 5: Commit**

```bash
git add src/lib/
git commit -m "feat(frontend): API client (browser + SSR), types, auth helpers"
```

---

## Task 3: Root layout, providers, redirect

**Files:** `src/app/layout.tsx`, `src/app/providers.tsx`, `src/app/page.tsx`

- [ ] **Step 1: `src/app/providers.tsx`**

```tsx
"use client";

import {Provider as JotaiProvider} from "jotai";
import {QueryClient, QueryClientProvider} from "@tanstack/react-query";
import {useState} from "react";

export function Providers({children}: {children: React.ReactNode}) {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000,
            refetchOnWindowFocus: false,
            retry: 0,
          },
        },
      }),
  );
  return (
    <QueryClientProvider client={client}>
      <JotaiProvider>{children}</JotaiProvider>
    </QueryClientProvider>
  );
}
```

- [ ] **Step 2: `src/app/layout.tsx`**

```tsx
import "./globals.css";
import type {Metadata} from "next";
import {Providers} from "./providers";

export const metadata: Metadata = {
  title: "Altassian",
  description: "Markdown-first wiki",
};

export default function RootLayout({children}: {children: React.ReactNode}) {
  return (
    <html lang="en">
      <body className="bg-zinc-50 text-zinc-900 antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

- [ ] **Step 3: `src/app/page.tsx`** — root redirect

```tsx
import {redirect} from "next/navigation";
import {maybeUser} from "@/lib/auth";

export default async function RootPage() {
  const user = await maybeUser();
  redirect(user ? "/home" : "/login");
}
```

- [ ] **Step 4: TS path alias**

In `tsconfig.json`, ensure `"paths": { "@/*": ["./src/*"] }` is set under `compilerOptions`. (It usually is by default.)

- [ ] **Step 5: Build**

```bash
npm run build 2>&1 | tail -10
# Expected: builds; some warnings about missing routes are fine.
```

- [ ] **Step 6: Commit**

```bash
git add src/app/
git commit -m "feat(frontend): root layout + providers + auth-aware redirect"
```

---

## Task 4: Login page

**Files:** `src/app/login/page.tsx`, `src/components/LoginForm.tsx`

- [ ] **Step 1: `src/components/LoginForm.tsx`**

```tsx
"use client";

import {useState} from "react";
import {useRouter} from "next/navigation";
import {api, HTTPError} from "@/lib/api";

export function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await api.login(email, password);
      router.push("/home");
      router.refresh();
    } catch (err) {
      if (err instanceof HTTPError) {
        const body = await err.response.json().catch(() => null);
        setError((body as {detail?: string})?.detail ?? "Login failed.");
      } else {
        setError("Login failed.");
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="flex w-full max-w-sm flex-col gap-3">
      <label className="flex flex-col gap-1">
        <span className="text-sm font-medium text-zinc-700">Email</span>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          autoFocus
          className="rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm focus:border-zinc-900 focus:outline-none"
        />
      </label>
      <label className="flex flex-col gap-1">
        <span className="text-sm font-medium text-zinc-700">Password</span>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm focus:border-zinc-900 focus:outline-none"
        />
      </label>
      {error && (
        <p className="rounded-md bg-rose-50 px-3 py-2 text-sm text-rose-700" role="alert">
          {error}
        </p>
      )}
      <button
        type="submit"
        disabled={busy}
        className="mt-2 rounded-md bg-zinc-900 px-3 py-2 text-sm font-medium text-white hover:bg-zinc-700 disabled:opacity-50"
      >
        {busy ? "Signing in…" : "Sign in"}
      </button>
    </form>
  );
}
```

- [ ] **Step 2: `src/app/login/page.tsx`**

```tsx
import Link from "next/link";
import {LoginForm} from "@/components/LoginForm";

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center px-4">
      <div className="flex w-full max-w-sm flex-col items-center gap-6">
        <Link href="/" className="text-2xl font-semibold tracking-tight">
          Altassian
        </Link>
        <LoginForm />
        <p className="text-xs text-zinc-500">Invite-only. Ask an admin for access.</p>
      </div>
    </main>
  );
}
```

- [ ] **Step 3: Manual smoke test (skip if backend isn't running locally — this is for dev only)**

```bash
# In one terminal:
cd /home/namanbansal/.openclaw/workspace/altassian_backend
source venv/bin/activate
python manage.py runserver 127.0.0.1:8000
```

```bash
# In another terminal:
cd /home/namanbansal/.openclaw/workspace/altassian_backend/frontend-next
npm run dev
# Visit http://localhost:3000/login → submit admin@altassian.local / adminpass123
# (Created earlier by seed_demo.) Confirm cookies set; redirect to /home (404 — page doesn't exist yet).
```

If you can't run the live test (e.g. ports busy), skip and trust the build.

- [ ] **Step 4: Build**

```bash
npm run build 2>&1 | tail -10
```

- [ ] **Step 5: Commit**

```bash
git add src/app/login/ src/components/LoginForm.tsx
git commit -m "feat(frontend): /login with email+password form"
```

---

## Task 5: Authed layout (chrome) + sidebar + topbar

**Files:** `src/app/(authed)/layout.tsx`, `src/components/Chrome.tsx`, `src/components/Sidebar.tsx`, `src/components/TopBar.tsx`, `src/components/PageTree.tsx`

- [ ] **Step 1: `src/app/(authed)/layout.tsx` — auth gate + chrome**

```tsx
import {requireUser} from "@/lib/auth";
import {ssrApi} from "@/lib/api";
import {cookies} from "next/headers";
import {Chrome} from "@/components/Chrome";

export default async function AuthedLayout({children}: {children: React.ReactNode}) {
  const user = await requireUser();
  const cookieHeader = (await cookies()).toString();
  const spaces = await ssrApi.listSpaces(cookieHeader).catch(() => ({results: []}));
  return <Chrome user={user} spaces={spaces.results}>{children}</Chrome>;
}
```

- [ ] **Step 2: `src/components/Chrome.tsx`**

```tsx
import type {Space, User} from "@/lib/types";
import {Sidebar} from "./Sidebar";
import {TopBar} from "./TopBar";

export function Chrome({user, spaces, children}: {user: User; spaces: Space[]; children: React.ReactNode}) {
  return (
    <div className="flex min-h-screen">
      <Sidebar spaces={spaces} />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar user={user} />
        <main className="flex-1 overflow-auto bg-white">{children}</main>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: `src/components/Sidebar.tsx`**

```tsx
import Link from "next/link";
import type {Space} from "@/lib/types";

export function Sidebar({spaces}: {spaces: Space[]}) {
  return (
    <aside className="hidden w-64 shrink-0 border-r border-zinc-200 bg-zinc-50 lg:block">
      <div className="flex h-14 items-center border-b border-zinc-200 px-4">
        <Link href="/home" className="font-semibold tracking-tight">
          Altassian
        </Link>
      </div>
      <nav className="flex flex-col gap-1 p-3 text-sm">
        <Link
          href="/home"
          className="rounded-md px-2 py-1.5 text-zinc-700 hover:bg-zinc-200"
        >
          Home
        </Link>
        <Link
          href="/new"
          className="rounded-md px-2 py-1.5 text-zinc-700 hover:bg-zinc-200"
        >
          + New page
        </Link>
        <div className="mt-4 px-2 text-xs uppercase tracking-wide text-zinc-500">
          Spaces
        </div>
        {spaces.length === 0 ? (
          <p className="px-2 py-1.5 text-xs text-zinc-500">No spaces yet.</p>
        ) : (
          spaces.map((s) => (
            <Link
              key={s.id}
              href={`/s/${s.slug}`}
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
```

- [ ] **Step 4: `src/components/TopBar.tsx`**

```tsx
"use client";

import Link from "next/link";
import {useRouter} from "next/navigation";
import {useState} from "react";
import {Search, LogOut} from "lucide-react";
import {api} from "@/lib/api";
import type {User} from "@/lib/types";

export function TopBar({user}: {user: User}) {
  const router = useRouter();
  const [q, setQ] = useState("");

  function onSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!q.trim()) return;
    router.push(`/search?q=${encodeURIComponent(q.trim())}`);
  }

  async function logout() {
    await api.logout();
    router.push("/login");
    router.refresh();
  }

  return (
    <header className="flex h-14 items-center justify-between border-b border-zinc-200 bg-white px-4">
      <form onSubmit={onSearch} className="relative w-full max-w-md">
        <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400" size={16} />
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search…"
          className="w-full rounded-md border border-zinc-200 bg-zinc-50 py-1.5 pl-9 pr-3 text-sm focus:border-zinc-900 focus:bg-white focus:outline-none"
        />
      </form>
      <div className="flex items-center gap-3 pl-4 text-sm">
        <span className="text-zinc-600" title={user.email}>{user.display_name || user.email}</span>
        <button
          onClick={logout}
          className="flex items-center gap-1 rounded-md border border-zinc-200 px-2 py-1 text-zinc-700 hover:bg-zinc-100"
          title="Log out"
        >
          <LogOut size={14} /> Log out
        </button>
      </div>
    </header>
  );
}
```

- [ ] **Step 5: `src/components/PageTree.tsx`**

```tsx
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
            href={`/s/${spaceSlug}/${n.slug}`}
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
```

- [ ] **Step 6: Build**

```bash
cd /home/namanbansal/.openclaw/workspace/altassian_backend/frontend-next
npm run build 2>&1 | tail -15
# Expected: build succeeds. /home, /s/[slug], etc. routes still 404 — fine.
```

- [ ] **Step 7: Commit**

```bash
git add src/app/\(authed\)/ src/components/
git commit -m "feat(frontend): authed layout with sidebar (spaces list) + topbar (search/logout)"
```

---

## Task 6: /home — recent pages (server component)

**Files:** `src/app/(authed)/home/page.tsx`

For v1, "home" is a list of all spaces with a few recent pages. Keep it simple.

- [ ] **Step 1: Write the page**

```tsx
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
            href={`/s/${s.slug}`}
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
```

- [ ] **Step 2: Build**

```bash
npm run build 2>&1 | tail -10
```

- [ ] **Step 3: Commit**

```bash
git add src/app/\(authed\)/home/
git commit -m "feat(frontend): /home — recent spaces grid"
```

---

## Task 7: Space detail with page tree

**Files:** `src/app/(authed)/s/[slug]/page.tsx`, update Sidebar to embed page tree when in a space

The route shows the space's name + description + first page rendered, with the page tree in the sidebar.

- [ ] **Step 1: `src/app/(authed)/s/[slug]/page.tsx`**

```tsx
import Link from "next/link";
import {redirect} from "next/navigation";
import {cookies} from "next/headers";
import {ssrApi} from "@/lib/api";
import {PageTree} from "@/components/PageTree";

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
        <Link href="/home" className="mt-2 block text-sm text-zinc-600 underline">Back to home</Link>
      </div>
    );
  }

  // If the space has pages, redirect to the first root page; otherwise show empty state.
  const firstRoot = space.pages[0];
  if (firstRoot) {
    redirect(`/s/${slug}/${firstRoot.slug}`);
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
          href={`/new?space=${space.slug}`}
          className="mt-3 rounded-md bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-zinc-700"
        >
          Create the first page
        </Link>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Build**

```bash
npm run build 2>&1 | tail -10
```

- [ ] **Step 3: Commit**

```bash
git add src/app/\(authed\)/s/
git commit -m "feat(frontend): /s/<slug> with page tree sidebar; redirect to first root page"
```

---

## Task 8: Page view route

**Files:** `src/app/(authed)/s/[slug]/[pageSlug]/page.tsx`, `src/components/MarkdownView.tsx`

- [ ] **Step 1: `src/components/MarkdownView.tsx`** — renders the cached HTML safely

```tsx
export function MarkdownView({html}: {html: string}) {
  // The backend renders Markdown via markdown-it-py with html: false, so HTML
  // is escaped at render time. Treat body_html_cache as trusted server output.
  return (
    <article
      className="prose prose-zinc max-w-none prose-headings:font-semibold prose-headings:tracking-tight prose-pre:rounded-md prose-pre:bg-zinc-900 prose-pre:text-zinc-50"
      dangerouslySetInnerHTML={{__html: html}}
    />
  );
}
```

- [ ] **Step 2: Add Tailwind typography plugin**

```bash
cd /home/namanbansal/.openclaw/workspace/altassian_backend/frontend-next
npm install --save @tailwindcss/typography@^0.5
```

In `src/app/globals.css`, ensure the plugin is loaded. With Tailwind v4 the syntax is:

```css
@import "tailwindcss";
@plugin "@tailwindcss/typography";
```

(Check the existing `globals.css` first — may already have `@import "tailwindcss"`. Add the `@plugin` line if missing.)

- [ ] **Step 3: `src/app/(authed)/s/[slug]/[pageSlug]/page.tsx`**

```tsx
import Link from "next/link";
import {cookies} from "next/headers";
import {ssrApi} from "@/lib/api";
import {PageTree} from "@/components/PageTree";
import {MarkdownView} from "@/components/MarkdownView";
import {Pencil} from "lucide-react";

export default async function PageView({params}: {params: Promise<{slug: string; pageSlug: string}>}) {
  const {slug, pageSlug} = await params;
  const cookieHeader = (await cookies()).toString();

  const space = await ssrApi.getSpace(cookieHeader, slug).catch(() => null);
  if (!space) {
    return <div className="px-6 py-10">Space not found.</div>;
  }

  // Walk the tree to find the page node by slug, then fetch the full page.
  const node = findNodeBySlug(space.pages, pageSlug);
  if (!node) {
    return (
      <div className="px-6 py-10">
        <p>Page not found.</p>
        <Link href={`/s/${slug}`} className="text-sm text-zinc-600 underline">Back to {space.name}</Link>
      </div>
    );
  }

  const page = await ssrApi.getPage(cookieHeader, node.id);

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
      <div className="flex min-w-0 flex-1 flex-col px-6 py-8">
        <div className="mb-4 flex items-center justify-between">
          <h1 className="text-3xl font-semibold tracking-tight">{page.title}</h1>
          <Link
            href={`/s/${slug}/${pageSlug}/edit`}
            className="flex items-center gap-1 rounded-md border border-zinc-200 px-3 py-1.5 text-sm text-zinc-700 hover:bg-zinc-50"
          >
            <Pencil size={14} /> Edit
          </Link>
        </div>
        <MarkdownView html={page.body_html} />
      </div>
    </div>
  );
}

function findNodeBySlug(nodes: import("@/lib/types").PageNode[], slug: string): import("@/lib/types").PageNode | null {
  for (const n of nodes) {
    if (n.slug === slug) return n;
    const child = findNodeBySlug(n.children, slug);
    if (child) return child;
  }
  return null;
}
```

- [ ] **Step 4: Build**

```bash
npm run build 2>&1 | tail -10
```

- [ ] **Step 5: Commit**

```bash
git add src/app/\(authed\)/s/\[slug\]/\[pageSlug\]/ src/components/MarkdownView.tsx src/app/globals.css package.json package-lock.json
git commit -m "feat(frontend): /s/<slug>/<page> view with rendered markdown + tree sidebar"
```

---

## Task 9: Editor — split-pane (CodeMirror + live preview)

**Files:** `src/app/(authed)/s/[slug]/[pageSlug]/edit/page.tsx`, `src/components/Editor.tsx`

- [ ] **Step 1: `src/components/Editor.tsx`** (client component)

```tsx
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
      startTransition(() => router.push(`/s/${spaceSlug}/${updated.slug}`));
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
```

- [ ] **Step 2: `src/app/(authed)/s/[slug]/[pageSlug]/edit/page.tsx`**

```tsx
import {cookies} from "next/headers";
import {ssrApi} from "@/lib/api";
import {Editor} from "@/components/Editor";

export default async function EditPage({params}: {params: Promise<{slug: string; pageSlug: string}>}) {
  const {slug, pageSlug} = await params;
  const cookieHeader = (await cookies()).toString();
  const space = await ssrApi.getSpace(cookieHeader, slug);
  const node = findNodeBySlug(space.pages, pageSlug);
  if (!node) {
    return <div className="px-6 py-10">Page not found.</div>;
  }
  const page = await ssrApi.getPage(cookieHeader, node.id);
  return <Editor initial={page} spaceSlug={slug} />;
}

function findNodeBySlug(nodes: import("@/lib/types").PageNode[], slug: string): import("@/lib/types").PageNode | null {
  for (const n of nodes) {
    if (n.slug === slug) return n;
    const child = findNodeBySlug(n.children, slug);
    if (child) return child;
  }
  return null;
}
```

- [ ] **Step 3: Build**

```bash
npm run build 2>&1 | tail -15
```

- [ ] **Step 4: Commit**

```bash
git add src/app/\(authed\)/s/\[slug\]/\[pageSlug\]/edit/ src/components/Editor.tsx
git commit -m "feat(frontend): split-pane editor (CodeMirror + react-markdown live preview)"
```

---

## Task 10: New-page route

**Files:** `src/app/(authed)/new/page.tsx`

- [ ] **Step 1: Write the page (client component because of form state)**

```tsx
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
      router.push(`/s/${slug}/${page.slug}/edit`);
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
```

- [ ] **Step 2: Build**

```bash
npm run build 2>&1 | tail -10
```

- [ ] **Step 3: Commit**

```bash
git add src/app/\(authed\)/new/
git commit -m "feat(frontend): /new — create page (pick space + title, then redirect to editor)"
```

---

## Task 11: Search results

**Files:** `src/app/(authed)/search/page.tsx`, `src/components/SearchResults.tsx`

- [ ] **Step 1: `src/components/SearchResults.tsx`** (client component using TanStack Query)

```tsx
"use client";

import Link from "next/link";
import {useQuery} from "@tanstack/react-query";
import {api} from "@/lib/api";

export function SearchResults({query}: {query: string}) {
  const {data, isLoading, isError} = useQuery({
    queryKey: ["search", query],
    queryFn: () => api.search(query),
    enabled: query.length > 0,
  });

  if (!query) return <p className="text-sm text-zinc-500">Type a query to search.</p>;
  if (isLoading) return <p className="text-sm text-zinc-500">Searching…</p>;
  if (isError) return <p className="text-sm text-rose-600">Search failed.</p>;
  if (!data?.results.length) return <p className="text-sm text-zinc-500">No results.</p>;

  return (
    <ul className="flex flex-col divide-y divide-zinc-100">
      {data.results.map((r) => (
        <li key={r.page_id} className="py-3">
          <Link
            href={`/s/${r.space_slug}/${r.page_slug}`}
            className="block hover:bg-zinc-50"
          >
            <div className="text-sm font-medium text-zinc-900">{r.title}</div>
            <div className="mt-0.5 text-xs uppercase tracking-wide text-zinc-500">{r.space_slug}</div>
            <p
              className="mt-1 text-sm text-zinc-600"
              // The backend wraps matches in <b>...</b>; safe to render.
              dangerouslySetInnerHTML={{__html: r.snippet_html}}
            />
          </Link>
        </li>
      ))}
    </ul>
  );
}
```

- [ ] **Step 2: `src/app/(authed)/search/page.tsx`**

```tsx
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
```

- [ ] **Step 3: Build**

```bash
npm run build 2>&1 | tail -10
```

- [ ] **Step 4: Commit**

```bash
git add src/app/\(authed\)/search/ src/components/SearchResults.tsx
git commit -m "feat(frontend): /search route with FTS results + snippet highlighting"
```

---

## Task 12: Final verification

- [ ] **Step 1: Confirm all routes build**

```bash
cd /home/namanbansal/.openclaw/workspace/altassian_backend/frontend-next
npm run build 2>&1 | tail -25
# Expected: every route compiled, no TS errors.
```

- [ ] **Step 2: Quick e2e smoke (only if you can run both servers)**

```bash
# Terminal A:
cd /home/namanbansal/.openclaw/workspace/altassian_backend
source venv/bin/activate
python manage.py runserver 127.0.0.1:8000

# Terminal B:
cd /home/namanbansal/.openclaw/workspace/altassian_backend/frontend-next
npm run dev
# Visit http://localhost:3000 → redirects to /login.
# Login with admin@altassian.local / adminpass123.
# Should land on /home, see the seeded "Engineering" + "Product" spaces.
# Click into Engineering → see "Architecture" + "Onboarding" pages.
# Open one → render markdown. Click Edit → split-pane.
# Make a change, save, see it persisted.
# Search "architecture" from the topbar → see the result.
```

If both ports are busy, skip the e2e — trust the build and deal with edge cases in Plan 3 once it's live.

- [ ] **Step 3: Tag the milestone**

```bash
cd /home/namanbansal/.openclaw/workspace/altassian_backend
git tag frontend-mvp-v0.1
```

---

## Self-review checklist

- All routes build without TS errors
- Login → home → space → page → edit → save flow works in dev (or trust build)
- Sidebar shows spaces; per-space sidebar shows page tree on space/page routes
- TopBar search posts to `/search?q=`; results render with snippet highlights
- New page form works
- httpOnly cookies; no token in localStorage anywhere
- No `dangerouslySetInnerHTML` of unsanitized user input (only of server-rendered html_cache and FTS snippet_html — both produced server-side and safe)

## Out of scope (deferred to v1.1+)

- Comments thread under page view
- Attachments UI (upload from editor)
- Version history UI
- Public page rendering at `/p/<space>/<page>`
- Settings (org name, members list, invite UI)
- Mobile drawer for sidebar
- Drag-and-drop in page tree
- Optimistic updates beyond TanStack defaults
- Dark mode
