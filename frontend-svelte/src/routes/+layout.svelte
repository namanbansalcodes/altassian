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
  <header class="sticky top-0 z-20 bg-white dark:bg-neutral-900 border-b border-neutral-300 dark:border-neutral-700 h-14 flex items-center px-3 sm:px-4 gap-2 sm:gap-4 shrink-0">
    <!-- Mobile hamburger (< lg) -->
    <button
      on:click={openDrawer}
      class="lg:hidden p-1.5 rounded-lg text-neutral-500 hover:bg-neutral-100 dark:text-neutral-400 dark:hover:bg-neutral-800"
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
  <div class="drawer-panel bg-white dark:bg-neutral-900 shadow-xl flex flex-col" class:open={mobileDrawerOpen}>
    <div class="flex items-center justify-between h-14 px-4 border-b border-neutral-300 dark:border-neutral-700 shrink-0">
      <span class="text-lg font-bold text-blue-600 dark:text-blue-400">Altassian</span>
      <button
        on:click={closeDrawer}
        class="p-1.5 rounded-lg text-neutral-500 hover:bg-neutral-100 dark:text-neutral-400 dark:hover:bg-neutral-800"
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
  <main class="flex-1 p-3 sm:p-4 md:p-6">
    <slot />
  </main>
</QueryClientProvider>
