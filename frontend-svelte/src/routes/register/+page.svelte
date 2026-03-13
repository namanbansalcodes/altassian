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

<div class="container mx-auto max-w-md px-4 sm:px-6 py-6 sm:py-10">
  <h1 class="text-xl sm:text-2xl font-semibold mb-4">Register</h1>
  <form on:submit|preventDefault={() => mutation.mutate()} class="space-y-3">
    <input
      class="w-full border border-neutral-300 dark:border-neutral-600 rounded px-3 py-3 bg-transparent text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
      placeholder="Username"
      autocomplete="username"
      bind:value={username}
    />
    <input
      class="w-full border border-neutral-300 dark:border-neutral-600 rounded px-3 py-3 bg-transparent text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
      placeholder="Password"
      type="password"
      autocomplete="new-password"
      bind:value={password}
    />
    <button
      class="w-full px-4 py-3 rounded bg-blue-600 text-white font-medium disabled:opacity-60 hover:bg-blue-700 active:bg-blue-800 transition-colors"
      disabled={mutation.isPending}
    >
      Register
    </button>
    {#if mutation.isError}
      <p class="text-red-500 text-sm">Registration failed</p>
    {/if}
    <p class="text-sm text-neutral-500 text-center">
      Already have an account? <a href="/login" class="text-blue-600 dark:text-blue-400 underline">Login</a>
    </p>
  </form>
</div>
