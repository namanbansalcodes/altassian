<script lang="ts">
  import { createQuery } from '@tanstack/svelte-query';
  import { api } from '$lib/api/client';
  import type { Space } from '$lib/api/schemas';
  import { goto } from '$app/navigation';

  const spacesQuery = createQuery<Space[]>({
    queryKey: ['spaces'],
    queryFn: async () => api.get('spaces/').json()
  });
</script>

<div class="max-w-4xl mx-auto">
  <h1 class="text-xl sm:text-2xl font-semibold mb-4">Spaces</h1>
  {#if $spacesQuery.isLoading}
    <p class="text-neutral-500">Loading...</p>
  {:else if $spacesQuery.isError}
    <p class="text-red-500">Error loading spaces</p>
  {:else}
    <div class="grid gap-2 sm:gap-3">
      {#each $spacesQuery.data as s}
        <button
          class="w-full text-left px-4 py-3 rounded-lg border border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors active:bg-neutral-100 dark:active:bg-neutral-700"
          on:click={() => goto(`/spaces/${s.key}`)}
        >
          <span class="font-medium text-blue-600 dark:text-blue-400">{s.name}</span>
          <span class="text-neutral-500 text-sm ml-2">({s.key})</span>
        </button>
      {/each}
    </div>
  {/if}
</div>
