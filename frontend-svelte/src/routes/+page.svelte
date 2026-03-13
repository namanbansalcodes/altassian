<script lang="ts">
  import { createQuery } from '@tanstack/svelte-query';
  import { api } from '$lib/api/client';

  const meQuery = createQuery({
    queryKey: ['me'],
    queryFn: async () => api.get('auth/me/').json()
  });
</script>

<div class="max-w-3xl mx-auto">
  <h1 class="text-xl sm:text-2xl font-semibold">Dashboard</h1>
  {#if $meQuery.isLoading}
    <p class="mt-4 text-neutral-500">Loading...</p>
  {:else if $meQuery.isError}
    <p class="mt-4 text-red-500">Error loading profile</p>
  {:else}
    <pre class="mt-4 bg-neutral-800 text-neutral-100 p-3 rounded text-xs sm:text-sm overflow-x-auto">{JSON.stringify($meQuery.data, null, 2)}</pre>
  {/if}
</div>
