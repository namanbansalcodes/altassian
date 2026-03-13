<script lang="ts">
  import { createMutation } from '@tanstack/svelte-query';
  import { login } from '$lib/auth/store';
  import { goto } from '$app/navigation';

  let username = '';
  let password = '';

  const mutation = createMutation({
    mutationFn: async () => {
      await login(username, password);
    },
    onSuccess: () => goto('/')
  });
</script>

<div class="container mx-auto max-w-md p-6">
  <h1 class="text-2xl font-semibold mb-4">Login</h1>
  <form on:submit|preventDefault={() => mutation.mutate()} class="space-y-3">
    <input class="input input-bordered w-full" placeholder="Username" bind:value={username} />
    <input class="input input-bordered w-full" placeholder="Password" type="password" bind:value={password} />
    <button class="btn btn-primary w-full" disabled={mutation.isPending}>Login</button>
    {#if mutation.isError}
      <p class="text-red-500">Login failed</p>
    {/if}
  </form>
</div>
