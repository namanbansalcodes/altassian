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

<div class="p-6">
  <h1 class="text-2xl font-semibold mb-4">Spaces</h1>
  {#if $spacesQuery.isLoading}
    <p>Loading...</p>
  {:else if $spacesQuery.isError}
    <p>Error loading spaces</p>
  {:else}
    <ul class="space-y-2">
      {#each $spacesQuery.data as s}
        <li>
          <button class="text-blue-600 underline" on:click={() => goto(`/spaces/${s.key}`)}>{s.name} ({s.key})</button>
        </li>
      {/each}
    </ul>
  {/if}
</div>
