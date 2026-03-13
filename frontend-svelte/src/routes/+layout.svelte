<script lang="ts">
  import '../app.css';
  import { QueryClient, QueryClientProvider } from '@tanstack/svelte-query';
  import ThemeToggle from '$lib/components/ThemeToggle.svelte';
  import { onMount } from 'svelte';

  const queryClient = new QueryClient();

  let mobileDrawerOpen = false;
  let isDesktop = false;

  function openDrawer() { mobileDrawerOpen = true; }
  function closeDrawer() { mobileDrawerOpen = false; }

  onMount(() => {
    const mql = window.matchMedia('(min-width: 1024px)');
    isDesktop = mql.matches;
    const handler = (e: MediaQueryListEvent) => {
      isDesktop = e.matches;
      if (e.matches) mobileDrawerOpen = false;
    };
    mql.addEventListener('change', handler);
    return () => mql.removeEventListener('change', handler);
  });
</script>

<QueryClientProvider client={queryClient}>
  <!-- Top navbar -->
  <header class="sticky top-0 z-20 bg-white dark:bg-neutral-900 border-b border-neutral-300 dark:border-neutral-700 h-14 flex items-center px-3 sm:px-4 gap-2 sm:gap-4 shrink-0" style="padding-top: env(safe-area-inset-top)">
    <!-- Mobile hamburger (< lg) -->
    <button
      on:click={openDrawer}
      class="lg:hidden p-2 rounded-lg text-neutral-500 hover:bg-neutral-100 dark:text-neutral-400 dark:hover:bg-neutral-800 active:bg-neutral-200 dark:active:bg-neutral-700"
      aria-label="Open navigation menu"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
      </svg>
    </button>

    <a href="/" class="text-lg font-bold text-blue-600 dark:text-blue-400 shrink-0">Altassian</a>

    <!-- Desktop nav links (md+) -->
    <nav class="hidden md:flex items-center gap-1 ml-4">
      <a href="/" class="px-3 py-1.5 text-sm text-neutral-600 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-md">Home</a>
      <a href="/spaces" class="px-3 py-1.5 text-sm text-neutral-600 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-md">Spaces</a>
    </nav>

    <div class="flex-1"></div>

    <nav class="flex items-center gap-2">
      <a class="hidden sm:inline-flex px-3 py-1.5 text-sm text-neutral-600 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-md" href="/login">Login</a>
      <a class="hidden sm:inline-flex px-3 py-1.5 text-sm text-neutral-600 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-md" href="/register">Register</a>
      <ThemeToggle />
    </nav>
  </header>

  <!-- Mobile sidebar drawer (< lg) -->
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <div
    class="drawer-backdrop"
    class:open={mobileDrawerOpen}
    on:click={closeDrawer}
    role="presentation"
  ></div>
  <div class="drawer-panel bg-white dark:bg-neutral-900 shadow-xl flex flex-col overflow-y-auto overscroll-y-contain" class:open={mobileDrawerOpen}>
    <div class="flex items-center justify-between h-14 px-4 border-b border-neutral-300 dark:border-neutral-700 shrink-0">
      <span class="text-lg font-bold text-blue-600 dark:text-blue-400">Altassian</span>
      <button
        on:click={closeDrawer}
        class="p-2 rounded-lg text-neutral-500 hover:bg-neutral-100 dark:text-neutral-400 dark:hover:bg-neutral-800 active:bg-neutral-200 dark:active:bg-neutral-700"
        aria-label="Close navigation menu"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
    <nav class="flex flex-col px-3 py-3 gap-1">
      <a href="/" on:click={closeDrawer} class="px-3 py-2.5 text-sm text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-md">Home</a>
      <a href="/spaces" on:click={closeDrawer} class="px-3 py-2.5 text-sm text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-md">Spaces</a>
      <a href="/login" on:click={closeDrawer} class="px-3 py-2.5 text-sm text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-md">Login</a>
      <a href="/register" on:click={closeDrawer} class="px-3 py-2.5 text-sm text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-md">Register</a>
    </nav>
  </div>

  <!-- Main content -->
  <main class="flex-1 p-3 sm:p-4 md:p-6 pb-20 md:pb-6">
    <slot />
  </main>

  <!-- Mobile bottom navigation bar (< md) -->
  <nav class="mobile-bottom-nav md:hidden fixed bottom-0 inset-x-0 z-30 bg-white dark:bg-neutral-900 border-t border-neutral-300 dark:border-neutral-700 safe-area-bottom" aria-label="Mobile navigation">
    <div class="flex items-center justify-around h-14">
      <a href="/" class="flex flex-col items-center justify-center gap-0.5 flex-1 h-full text-xs text-neutral-500 dark:text-neutral-400">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0a1 1 0 01-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 01-1 1h-2z" /></svg>
        <span class="nav-label">Home</span>
      </a>
      <a href="/spaces" class="flex flex-col items-center justify-center gap-0.5 flex-1 h-full text-xs text-neutral-500 dark:text-neutral-400">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>
        <span class="nav-label">Spaces</span>
      </a>
      <a href="/login" class="flex flex-col items-center justify-center gap-0.5 flex-1 h-full text-xs text-neutral-500 dark:text-neutral-400">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" /></svg>
        <span class="nav-label">Login</span>
      </a>
      <a href="/register" class="flex flex-col items-center justify-center gap-0.5 flex-1 h-full text-xs text-neutral-500 dark:text-neutral-400">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" /></svg>
        <span class="nav-label">Register</span>
      </a>
    </div>
  </nav>
</QueryClientProvider>
