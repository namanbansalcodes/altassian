export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-100 dark:from-gray-950 dark:to-gray-900 text-gray-900 dark:text-gray-50">
      <header className="sticky top-0 backdrop-blur bg-white/70 dark:bg-gray-950/60 border-b border-gray-100 dark:border-gray-800 z-10">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 py-3 sm:py-4 flex items-center justify-between">
          <div className="font-semibold text-xl tracking-tight">Altassian</div>
          <nav className="hidden md:flex items-center gap-8 text-sm">
            <a href="#features" className="hover:opacity-80">Features</a>
            <a href="#pricing" className="hover:opacity-80">Pricing</a>
            <a href="#security" className="hover:opacity-80">Security</a>
          </nav>
          <div className="flex items-center gap-2 sm:gap-3">
            <a href="/login" className="text-sm font-medium hover:opacity-80">Sign in</a>
            <a href="/register" className="inline-flex items-center rounded-full bg-black text-white dark:bg-white dark:text-black px-3 sm:px-4 py-2 text-sm font-semibold shadow hover:scale-[1.01] transition">Get started</a>
          </div>
        </div>
      </header>

      <main>
        <section className="mx-auto max-w-7xl px-4 sm:px-6 py-16 sm:py-24 md:py-32 grid grid-cols-1 md:grid-cols-2 gap-8 sm:gap-10 items-center">
          <div>
            <h1 className="text-3xl sm:text-4xl md:text-6xl font-extrabold leading-tight tracking-tight">
              Your team’s knowledge, beautifully organized
            </h1>
            <p className="mt-5 text-lg md:text-xl text-gray-600 dark:text-gray-300 max-w-prose">
              Altassian is a Git-powered workspace for docs, decisions, and discovery. Blazing-fast search, version history, and a modern editor — without the bloat.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <a href="/register" className="inline-flex items-center rounded-full bg-black text-white dark:bg-white dark:text-black px-5 py-3 text-sm font-semibold shadow hover:scale-[1.01] transition">Create free account</a>
              <a href="#demo" className="inline-flex items-center rounded-full border border-gray-300 dark:border-gray-700 px-5 py-3 text-sm font-semibold hover:bg-gray-50 dark:hover:bg-gray-900 transition">Watch demo</a>
            </div>
            <div className="mt-6 text-xs text-gray-500 dark:text-gray-400">Open source • Git-native • SSO ready</div>
          </div>
          <div className="relative">
            <div className="absolute -inset-6 bg-gradient-to-tr from-blue-200 to-purple-200 dark:from-blue-900/40 dark:to-purple-900/30 blur-3xl rounded-3xl"/>
            <div className="relative rounded-2xl border border-gray-200 dark:border-gray-800 overflow-hidden shadow-xl bg-white/70 dark:bg-gray-950/60">
              <img src="/hero.png" alt="Altassian preview" className="w-full" />
            </div>
          </div>
        </section>

        <section id="features" className="mx-auto max-w-7xl px-4 sm:px-6 py-12 sm:py-16 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 sm:gap-8">
          {[
            {title: 'Git-powered', desc: 'Every page is versioned. Merge. Diff. Branch. Roll back with confidence.'},
            {title: 'Lightning search', desc: 'Instantly find docs, decisions, and people — all in one place.'},
            {title: 'Modern editor', desc: 'Slash commands, keyboard-first, embeds, and markdown shortcuts.'},
          ].map((f) => (
            <div key={f.title} className="rounded-2xl border border-gray-200 dark:border-gray-800 p-6 bg-white/60 dark:bg-gray-950/60">
              <div className="text-sm uppercase tracking-widest text-gray-500 dark:text-gray-400">{f.title}</div>
              <div className="mt-2 text-base text-gray-600 dark:text-gray-300">{f.desc}</div>
            </div>
          ))}
        </section>
      </main>

      <footer className="mx-auto max-w-7xl px-4 sm:px-6 py-8 sm:py-12 text-sm text-gray-500 dark:text-gray-400 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>© {new Date().getFullYear()} Altassian</div>
        <div className="flex items-center gap-4">
          <a href="#">Terms</a>
          <a href="#">Privacy</a>
        </div>
      </footer>
    </div>
  )
}
