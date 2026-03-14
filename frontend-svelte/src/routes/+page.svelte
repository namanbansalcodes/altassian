<script lang="ts">
  import { createQuery } from '@tanstack/svelte-query';
  import { api } from '$lib/api/client';
  import { fade } from 'svelte/transition';

  const meQuery = createQuery(() => ({
    queryKey: ['me'],
    queryFn: async () => api.get('auth/me/').json()
  }));
</script>

<div class="max-w-3xl mx-auto">
  <h1 class="text-xl sm:text-2xl font-semibold">Dashboard</h1>
  {#if meQuery.isLoading}
    <div class="mt-4 space-y-3 animate-pulse">
      <div class="h-4 w-1/3 bg-neutral-100 dark:bg-neutral-800 rounded"></div>
      <div class="h-32 bg-neutral-100 dark:bg-neutral-800 rounded"></div>
    </div>
  {:else if meQuery.isError}
    <p class="mt-4 text-red-500" in:fade={{ duration: 150 }}>Error loading profile</p>
  {:else}
    <pre class="mt-4 bg-neutral-800 text-neutral-100 p-3 rounded text-xs sm:text-sm overflow-x-auto" in:fade={{ duration: 150 }}>{JSON.stringify(meQuery.data, null, 2)}</pre>
  {/if}
</div>
