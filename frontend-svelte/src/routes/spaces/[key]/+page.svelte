<script lang="ts">
  import { createQuery } from '@tanstack/svelte-query';
  import { api } from '$lib/api/client';
  import { page } from '$app/stores';
  import type { Page as Pg } from '$lib/api/schemas';
  import { goto } from '$app/navigation';

  const key = $derived($page.params.key);

  const pagesQuery = createQuery<Pg[]>({
    queryKey: ['pages', key],
    queryFn: async () => api.get(`spaces/${key}/pages/`).json(),
    enabled: !!key
  });
</script>

<div class="max-w-4xl mx-auto">
  <h1 class="text-xl sm:text-2xl font-semibold mb-4">Space: {key}</h1>
  {#if $pagesQuery.isLoading}
    <p class="text-neutral-500">Loading...</p>
  {:else if $pagesQuery.isError}
    <p class="text-red-500">Error loading pages</p>
  {:else}
    <div class="grid gap-2 sm:gap-3">
      {#each $pagesQuery.data as p}
        <button
          class="w-full text-left px-4 py-3.5 rounded-lg border border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors active:bg-neutral-100 dark:active:bg-neutral-700 min-h-[44px]"
          on:click={() => goto(`/spaces/${key}/pages/${p.slug}`)}
        >
          <span class="font-medium text-blue-600 dark:text-blue-400">{p.title}</span>
        </button>
      {/each}
    </div>
  {/if}
</div>
