<script lang="ts">
  import { createMutation } from '@tanstack/svelte-query';
  import { login } from '$lib/auth/store';
  import { goto } from '$app/navigation';
  import { toasts } from '$lib/stores/toast';
  import { z } from 'zod';
  import { fly } from 'svelte/transition';

  const LoginSchema = z.object({
    username: z.string().min(1, 'Username is required').min(3, 'Username must be at least 3 characters'),
    password: z.string().min(1, 'Password is required')
  });

  let username = $state('');
  let password = $state('');
  let fieldErrors = $state<Record<string, string>>({});
  let touched = $state<Record<string, boolean>>({});

  function validate(): boolean {
    const result = LoginSchema.safeParse({ username, password });
    if (result.success) {
      fieldErrors = {};
      return true;
    }
    const errs: Record<string, string> = {};
    for (const issue of result.error.issues) {
      const key = issue.path[0] as string;
      if (!errs[key]) errs[key] = issue.message;
    }
    fieldErrors = errs;
    return false;
  }

  function onBlur(field: string) {
    touched[field] = true;
    validate();
  }

  const mutation = createMutation(() => ({
    mutationFn: async () => {
      await login(username, password);
    },
    onSuccess: () => {
      toasts.success('Welcome back!');
      goto('/');
    },
    onError: () => {
      toasts.error('Invalid username or password');
    }
  }));

  function handleSubmit() {
    touched = { username: true, password: true };
    if (!validate()) return;
    mutation.mutate();
  }
</script>

<div class="container mx-auto max-w-md px-4 sm:px-6 py-6 sm:py-10">
  <h1 class="text-xl sm:text-2xl font-semibold mb-4">Login</h1>
  <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-3" novalidate>
    <div>
      <input
        class="w-full border rounded px-3 py-3 bg-transparent text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none min-h-[44px] {touched.username && fieldErrors.username ? 'border-red-400 dark:border-red-500' : 'border-neutral-300 dark:border-neutral-600'}"
        placeholder="Username"
        autocomplete="username"
        bind:value={username}
        onblur={() => onBlur('username')}
      />
      {#if touched.username && fieldErrors.username}
        <p class="text-red-500 text-xs mt-1" in:fly={{ y: -4, duration: 150 }}>{fieldErrors.username}</p>
      {/if}
    </div>
    <div>
      <input
        class="w-full border rounded px-3 py-3 bg-transparent text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none min-h-[44px] {touched.password && fieldErrors.password ? 'border-red-400 dark:border-red-500' : 'border-neutral-300 dark:border-neutral-600'}"
        placeholder="Password"
        type="password"
        autocomplete="current-password"
        bind:value={password}
        onblur={() => onBlur('password')}
      />
      {#if touched.password && fieldErrors.password}
        <p class="text-red-500 text-xs mt-1" in:fly={{ y: -4, duration: 150 }}>{fieldErrors.password}</p>
      {/if}
    </div>
    <button
      class="w-full px-4 py-3 rounded bg-blue-600 text-white font-medium disabled:opacity-60 hover:bg-blue-700 active:bg-blue-800 transition-colors min-h-[44px]"
      disabled={mutation.isPending}
    >
      {#if mutation.isPending}
        <span class="inline-flex items-center gap-2">
          <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
          </svg>
          Logging in...
        </span>
      {:else}
        Login
      {/if}
    </button>
    {#if mutation.isError}
      <p class="text-red-500 text-sm" in:fly={{ y: -4, duration: 150 }}>Login failed — check your credentials</p>
    {/if}
    <p class="text-sm text-neutral-500 text-center">
      Don't have an account? <a href="/register" class="text-blue-600 dark:text-blue-400 underline">Register</a>
    </p>
  </form>
</div>
