<script lang="ts">
  import { createQuery } from '@tanstack/svelte-query';
  import { api } from '$lib/api/client';
  import { page } from '$app/stores';
  import type { Page as Pg } from '$lib/api/schemas';
  import { goto } from '$app/navigation';
  import { fly } from 'svelte/transition';

  const key = $derived($page.params.key);

  const pagesQuery = createQuery<Pg[]>(() => ({
    queryKey: ['pages', key],
    queryFn: async () => api.get(`spaces/${key}/pages/`).json(),
    enabled: !!key
  }));
</script>

<svelte:head>
  <title>Space: {key} — Altassian</title>
  <meta name="description" content="Browse pages in the {key} workspace on Altassian — collaborative team knowledge base." />
  <meta property="og:title" content="Space: {key}" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="Altassian" />
  <link rel="canonical" href="/spaces/{key}" />
</svelte:head>

<div class="max-w-4xl mx-auto">
  <h1 class="text-xl sm:text-2xl font-semibold mb-4">Space: {key}</h1>
  {#if pagesQuery.isLoading}
    <div class="space-y-3">
      {#each Array(3) as _}
        <div class="h-14 rounded-lg bg-neutral-100 dark:bg-neutral-800 animate-pulse"></div>
      {/each}
    </div>
  {:else if pagesQuery.isError}
    <p class="text-red-500">Error loading pages</p>
  {:else if pagesQuery.data}
    <div class="grid gap-2 sm:gap-3">
      {#each pagesQuery.data as p, i}
        <button
          class="w-full text-left px-4 py-3.5 rounded-lg border border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors active:bg-neutral-100 dark:active:bg-neutral-700 min-h-[44px]"
          onclick={() => goto(`/spaces/${key}/pages/${p.slug}`)}
          in:fly={{ y: 10, duration: 200, delay: i * 40 }}
        >
          <span class="font-medium text-blue-600 dark:text-blue-400">{p.title}</span>
        </button>
      {/each}
    </div>
  {/if}
</div>
