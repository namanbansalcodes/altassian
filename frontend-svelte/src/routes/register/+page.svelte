<script lang="ts">
  import { createMutation } from '@tanstack/svelte-query';
  import { api } from '$lib/api/client';
  import { goto } from '$app/navigation';

  let username = '';
  let password = '';

  const mutation = createMutation({
    mutationFn: async () => {
      await api.post('auth/register/', { json: { username, password } });
    },
    onSuccess: () => goto('/login')
  });
</script>

<div class="container mx-auto max-w-md p-6">
  <h1 class="text-2xl font-semibold mb-4">Register</h1>
  <form on:submit|preventDefault={() => mutation.mutate()} class="space-y-3">
    <input class="w-full border rounded px-3 py-2 bg-transparent" placeholder="Username" bind:value={username} />
    <input class="w-full border rounded px-3 py-2 bg-transparent" placeholder="Password" type="password" bind:value={password} />
    <button class="w-full px-4 py-2 rounded bg-blue-600 text-white disabled:opacity-60" disabled={mutation.isPending}>Register</button>
    {#if mutation.isError}
      <p class="text-red-500">Registration failed</p>
    {/if}
  </form>
</div>
