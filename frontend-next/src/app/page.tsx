import Link from "next/link";
import {ArrowRight, FileText, Search, KeyRound, GitBranch, Lock, Sparkles} from "lucide-react";
import {maybeUser} from "@/lib/auth";

export default async function LandingPage() {
  const user = await maybeUser();
  const ctaHref = user ? "/home" : "/login";
  const ctaLabel = user ? "Open your wiki" : "Get started";

  return (
    <main className="relative isolate overflow-hidden bg-white">
      {/* subtle grid */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10 opacity-[0.04]"
        style={{
          backgroundImage:
            "linear-gradient(to right, #000 1px, transparent 1px), linear-gradient(to bottom, #000 1px, transparent 1px)",
          backgroundSize: "32px 32px",
        }}
      />

      {/* nav */}
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
        <Link href="/" className="text-xl font-semibold tracking-tight">
          altassian
          <span className="text-zinc-400">.ai</span>
        </Link>
        <nav className="flex items-center gap-3 text-sm">
          {user ? (
            <Link href="/home" className="rounded-md px-3 py-1.5 text-zinc-700 hover:bg-zinc-100">
              Open wiki
            </Link>
          ) : (
            <Link href="/login" className="rounded-md px-3 py-1.5 text-zinc-700 hover:bg-zinc-100">
              Sign in
            </Link>
          )}
        </nav>
      </header>

      {/* hero */}
      <section className="mx-auto max-w-3xl px-6 pb-16 pt-12 text-center sm:pt-20">
        <p className="mb-5 inline-flex items-center gap-2 rounded-full border border-zinc-200 bg-white px-3 py-1 text-xs font-medium text-zinc-700 shadow-sm">
          <Sparkles size={12} className="text-amber-500" /> Confluence, but built for people who like markdown
        </p>
        <h1 className="text-balance text-5xl font-semibold tracking-tight text-zinc-900 sm:text-6xl">
          A wiki that doesn&apos;t feel like a chore.
        </h1>
        <p className="mx-auto mt-5 max-w-2xl text-balance text-lg text-zinc-600">
          Altassian is a markdown-first team wiki. Spaces, hierarchical pages, full-text search, and
          version history. No bloat, no block-editor lock-in, no passwords.
        </p>
        <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Link
            href={ctaHref}
            className="inline-flex items-center gap-2 rounded-md bg-zinc-900 px-5 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-zinc-700"
          >
            {ctaLabel} <ArrowRight size={16} />
          </Link>
          {!user && (
            <span className="text-xs text-zinc-500">No password — sign in with a code emailed to you.</span>
          )}
        </div>
      </section>

      {/* features */}
      <section className="mx-auto grid max-w-5xl grid-cols-1 gap-4 px-6 pb-20 sm:grid-cols-3">
        <Feature
          icon={<FileText size={18} />}
          title="Markdown is the source of truth"
          body="Plain markdown in, rendered HTML out. Live split-pane preview while you write. Your docs stay portable forever."
        />
        <Feature
          icon={<Search size={18} />}
          title="Real search, not autocomplete"
          body="Postgres full-text search across every page in your org. Highlights matched terms in context. Sub-100 ms at MVP scale."
        />
        <Feature
          icon={<KeyRound size={18} />}
          title="No passwords. Ever."
          body="OTP-only auth. Type your email, get a 6-digit code, you're in. Sessions are httpOnly cookies — XSS-safe by construction."
        />
        <Feature
          icon={<GitBranch size={18} />}
          title="Version history that actually makes sense"
          body="Every save is a version. Click a version to restore. Diffs come next."
        />
        <Feature
          icon={<Lock size={18} />}
          title="Public pages, when you want them"
          body="Flip a page to public and share a link. Everything else stays behind your org's auth."
        />
        <Feature
          icon={<Sparkles size={18} />}
          title="Built to feel fast"
          body="Single-page navigation, server-rendered pages, no spinners on the happy path. Optimized for keyboard, not clicks."
        />
      </section>

      {/* second CTA */}
      <section className="border-t border-zinc-200 bg-zinc-50 py-16">
        <div className="mx-auto flex max-w-3xl flex-col items-center px-6 text-center">
          <h2 className="text-balance text-3xl font-semibold tracking-tight text-zinc-900">
            Ready in 30 seconds.
          </h2>
          <p className="mt-3 text-zinc-600">
            Type your email. We send a code. You&apos;re writing markdown 30 seconds later.
          </p>
          <Link
            href={ctaHref}
            className="mt-6 inline-flex items-center gap-2 rounded-md bg-zinc-900 px-5 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-zinc-700"
          >
            {ctaLabel} <ArrowRight size={16} />
          </Link>
        </div>
      </section>

      <footer className="mx-auto flex max-w-5xl items-center justify-between px-6 py-6 text-xs text-zinc-500">
        <span>© {new Date().getFullYear()} Altassian.</span>
        <span>
          built by <a href="https://hiringsignal.ai" className="underline-offset-2 hover:underline">naman</a>
        </span>
      </footer>
    </main>
  );
}

function Feature({icon, title, body}: {icon: React.ReactNode; title: string; body: string}) {
  return (
    <article className="rounded-xl border border-zinc-200 bg-white p-5">
      <div className="mb-3 inline-flex h-8 w-8 items-center justify-center rounded-lg bg-zinc-100 text-zinc-700">
        {icon}
      </div>
      <h3 className="text-sm font-semibold tracking-tight text-zinc-900">{title}</h3>
      <p className="mt-1 text-sm leading-relaxed text-zinc-600">{body}</p>
    </article>
  );
}
