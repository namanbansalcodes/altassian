<script lang="ts">
  import { createMutation } from '@tanstack/svelte-query';
  import { api } from '$lib/api/client';
  import { goto } from '$app/navigation';
  import { toasts } from '$lib/stores/toast';
  import { z } from 'zod';
  import { fly } from 'svelte/transition';

  const RegisterSchema = z.object({
    username: z.string().min(1, 'Username is required').min(3, 'Must be at least 3 characters').max(30, 'Must be 30 characters or fewer').regex(/^[a-zA-Z0-9_]+$/, 'Only letters, numbers, and underscores'),
    password: z.string().min(1, 'Password is required').min(8, 'Must be at least 8 characters'),
    confirmPassword: z.string().min(1, 'Please confirm your password')
  }).refine((d) => d.password === d.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword']
  });

  let username = $state('');
  let password = $state('');
  let confirmPassword = $state('');
  let fieldErrors = $state<Record<string, string>>({});
  let touched = $state<Record<string, boolean>>({});

  function validate(): boolean {
    const result = RegisterSchema.safeParse({ username, password, confirmPassword });
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

  function passwordStrength(pw: string): { label: string; color: string; width: string } {
    if (pw.length === 0) return { label: '', color: '', width: '0%' };
    let score = 0;
    if (pw.length >= 8) score++;
    if (pw.length >= 12) score++;
    if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) score++;
    if (/\d/.test(pw)) score++;
    if (/[^a-zA-Z0-9]/.test(pw)) score++;
    if (score <= 1) return { label: 'Weak', color: 'bg-red-500', width: '20%' };
    if (score <= 2) return { label: 'Fair', color: 'bg-orange-500', width: '40%' };
    if (score <= 3) return { label: 'Good', color: 'bg-yellow-500', width: '60%' };
    if (score <= 4) return { label: 'Strong', color: 'bg-green-500', width: '80%' };
    return { label: 'Very strong', color: 'bg-green-600', width: '100%' };
  }

  let strength = $derived(passwordStrength(password));

  const mutation = createMutation(() => ({
    mutationFn: async () => {
      await api.post('auth/register/', { json: { username, password } });
    },
    onSuccess: () => {
      toasts.success('Account created! Please log in.');
      goto('/login');
    },
    onError: () => {
      toasts.error('Registration failed — username may already be taken');
    }
  }));

  function handleSubmit() {
    touched = { username: true, password: true, confirmPassword: true };
    if (!validate()) return;
    mutation.mutate();
  }
</script>

<div class="container mx-auto max-w-md px-4 sm:px-6 py-6 sm:py-10">
  <h1 class="text-xl sm:text-2xl font-semibold mb-4">Register</h1>
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
        autocomplete="new-password"
        bind:value={password}
        onblur={() => onBlur('password')}
      />
      {#if touched.password && fieldErrors.password}
        <p class="text-red-500 text-xs mt-1" in:fly={{ y: -4, duration: 150 }}>{fieldErrors.password}</p>
      {/if}
      {#if password.length > 0}
        <div class="mt-2" in:fly={{ y: -4, duration: 150 }}>
          <div class="h-1.5 w-full bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
            <div class="h-full rounded-full transition-all duration-300 {strength.color}" style="width: {strength.width}"></div>
          </div>
          <p class="text-xs mt-1 text-neutral-500">{strength.label}</p>
        </div>
      {/if}
    </div>
    <div>
      <input
        class="w-full border rounded px-3 py-3 bg-transparent text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none min-h-[44px] {touched.confirmPassword && fieldErrors.confirmPassword ? 'border-red-400 dark:border-red-500' : 'border-neutral-300 dark:border-neutral-600'}"
        placeholder="Confirm password"
        type="password"
        autocomplete="new-password"
        bind:value={confirmPassword}
        onblur={() => onBlur('confirmPassword')}
      />
      {#if touched.confirmPassword && fieldErrors.confirmPassword}
        <p class="text-red-500 text-xs mt-1" in:fly={{ y: -4, duration: 150 }}>{fieldErrors.confirmPassword}</p>
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
          Creating account...
        </span>
      {:else}
        Register
      {/if}
    </button>
    {#if mutation.isError}
      <p class="text-red-500 text-sm" in:fly={{ y: -4, duration: 150 }}>Registration failed</p>
    {/if}
    <p class="text-sm text-neutral-500 text-center">
      Already have an account? <a href="/login" class="text-blue-600 dark:text-blue-400 underline">Login</a>
    </p>
  </form>
</div>
