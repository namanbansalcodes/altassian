"use client";
import { useState, useEffect } from "react";
import Link from "next/link";

export function MobileNav() {
  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    const mql = window.matchMedia("(min-width: 1024px)");
    const handler = (e: MediaQueryListEvent) => {
      if (e.matches) setDrawerOpen(false);
    };
    mql.addEventListener("change", handler);
    return () => mql.removeEventListener("change", handler);
  }, []);

  useEffect(() => {
    if (drawerOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => { document.body.style.overflow = ""; };
  }, [drawerOpen]);

  return (
    <>
      {/* Top header bar */}
      <header className="sticky top-0 z-20 bg-white dark:bg-zinc-900 border-b border-zinc-200 dark:border-zinc-700 h-14 flex items-center px-3 sm:px-4 gap-2 sm:gap-4 shrink-0 safe-area-top">
        {/* Hamburger button (mobile) */}
        <button
          onClick={() => setDrawerOpen(true)}
          className="lg:hidden p-2.5 rounded-lg text-zinc-500 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800 active:bg-zinc-200 dark:active:bg-zinc-700 min-h-[44px] min-w-[44px] flex items-center justify-center"
          aria-label="Open navigation menu"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        <Link href="/" className="text-lg font-bold text-blue-600 dark:text-blue-400 shrink-0">
          Altassian
        </Link>

        {/* Desktop nav links */}
        <nav className="hidden md:flex items-center gap-1 ml-4">
          <Link href="/" className="px-3 py-2 text-sm text-zinc-600 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-md">Home</Link>
          <Link href="/spaces" className="px-3 py-2 text-sm text-zinc-600 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-md">Spaces</Link>
        </nav>

        <div className="flex-1" />

        <nav className="flex items-center gap-2">
          <Link className="hidden sm:inline-flex px-3 py-2 text-sm text-zinc-600 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-md" href="/login">Login</Link>
          <Link className="hidden sm:inline-flex px-3 py-2 text-sm text-zinc-600 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-md" href="/register">Register</Link>
        </nav>
      </header>

      {/* Mobile drawer backdrop */}
      {drawerOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/40 transition-opacity lg:hidden"
          onClick={() => setDrawerOpen(false)}
          role="presentation"
        />
      )}

      {/* Mobile drawer panel */}
      <div
        className={`fixed inset-y-0 left-0 z-40 w-72 max-w-[85vw] bg-white dark:bg-zinc-900 shadow-xl flex flex-col overflow-y-auto overscroll-y-contain transition-transform duration-300 lg:hidden ${drawerOpen ? "translate-x-0" : "-translate-x-full"}`}
        role="dialog"
        aria-label="Navigation drawer"
      >
        <div className="flex items-center justify-between h-14 px-4 border-b border-zinc-200 dark:border-zinc-700 shrink-0">
          <span className="text-lg font-bold text-blue-600 dark:text-blue-400">Altassian</span>
          <button
            onClick={() => setDrawerOpen(false)}
            className="p-2.5 rounded-lg text-zinc-500 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800 min-h-[44px] min-w-[44px] flex items-center justify-center"
            aria-label="Close navigation menu"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <nav className="flex flex-col px-3 py-3 gap-1">
          <Link href="/" onClick={() => setDrawerOpen(false)} className="px-3 py-3 text-base text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-md">Home</Link>
          <Link href="/spaces" onClick={() => setDrawerOpen(false)} className="px-3 py-3 text-base text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-md">Spaces</Link>
          <Link href="/login" onClick={() => setDrawerOpen(false)} className="px-3 py-3 text-base text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-md">Login</Link>
          <Link href="/register" onClick={() => setDrawerOpen(false)} className="px-3 py-3 text-base text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-md">Register</Link>
        </nav>
      </div>

      {/* Mobile bottom navigation bar */}
      <nav className="mobile-bottom-nav md:hidden fixed bottom-0 inset-x-0 z-30 bg-white dark:bg-zinc-900 border-t border-zinc-200 dark:border-zinc-700 safe-area-bottom" aria-label="Mobile navigation">
        <div className="flex items-center justify-around h-14">
          <Link href="/" className="flex flex-col items-center justify-center gap-0.5 flex-1 h-full text-xs text-zinc-500 dark:text-zinc-400">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0a1 1 0 01-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 01-1 1h-2z" /></svg>
            <span className="nav-label">Home</span>
          </Link>
          <Link href="/spaces" className="flex flex-col items-center justify-center gap-0.5 flex-1 h-full text-xs text-zinc-500 dark:text-zinc-400">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>
            <span className="nav-label">Spaces</span>
          </Link>
          <Link href="/login" className="flex flex-col items-center justify-center gap-0.5 flex-1 h-full text-xs text-zinc-500 dark:text-zinc-400">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" /></svg>
            <span className="nav-label">Login</span>
          </Link>
          <Link href="/register" className="flex flex-col items-center justify-center gap-0.5 flex-1 h-full text-xs text-zinc-500 dark:text-zinc-400">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" /></svg>
            <span className="nav-label">Register</span>
          </Link>
        </div>
      </nav>
    </>
  );
}
