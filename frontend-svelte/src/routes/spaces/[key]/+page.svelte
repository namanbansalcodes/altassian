<script lang="ts">
  import { createQuery } from '@tanstack/svelte-query';
  import { api } from '$lib/api/client';
  import { page } from '$app/stores';
  import type { Page as Pg } from '$lib/api/schemas';
  import { goto } from '$app/navigation';

  $: key = $page.params.key;

  const pagesQuery = createQuery<Pg[]>({
    queryKey: ['pages', key],
    queryFn: async () => api.get(`spaces/${key}/pages/`).json(),
    enabled: !!key
  });
</script>

<div class="p-6">
  <h1 class="text-2xl font-semibold mb-4">Space: {key}</h1>
  {#if $pagesQuery.isLoading}
    <p>Loading...</p>
  {:else if $pagesQuery.isError}
    <p>Error loading pages</p>
  {:else}
    <ul class="space-y-2">
      {#each $pagesQuery.data as p}
        <li>
          <button class="link" on:click={() => goto(`/spaces/${key}/pages/${p.slug}`)}>{p.title}</button>
        </li>
      {/each}
    </ul>
  {/if}
</div>
