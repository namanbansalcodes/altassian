<script lang="ts">
  import { createQuery } from '@tanstack/svelte-query';
  import { api } from '$lib/api/client';

  const meQuery = createQuery({
    queryKey: ['me'],
    queryFn: async () => api.get('auth/me/').json()
  });
</script>

<div class="p-6">
  <h1 class="text-2xl font-semibold">Dashboard</h1>
  {#if $meQuery.isLoading}
    <p>Loading...</p>
  {:else if $meQuery.isError}
    <p>Error loading profile</p>
  {:else}
    <pre class="mt-4 bg-neutral-800 text-neutral-100 p-3 rounded">{JSON.stringify($meQuery.data, null, 2)}</pre>
  {/if}
</div>
