<script lang="ts">
  import '../app.css';
  import { QueryClient, SvelteQueryClientProvider } from '@tanstack/svelte-query';
  import ThemeToggle from '$lib/components/ThemeToggle.svelte';
  const queryClient = new QueryClient();
</script>

<SvelteQueryClientProvider client={queryClient}>
  <header class="p-4 flex items-center justify-between border-b border-neutral-300 dark:border-neutral-700">
    <a href="/" class="font-semibold">Altassian</a>
    <nav class="flex items-center gap-3">
      <a class="link" href="/spaces">Spaces</a>
      <a class="link" href="/login">Login</a>
      <ThemeToggle />
    </nav>
  </header>
  <slot />
</SvelteQueryClientProvider>
