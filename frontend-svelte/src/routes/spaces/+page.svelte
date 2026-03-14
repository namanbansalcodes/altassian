<script lang="ts">
  import { createQuery, createMutation, useQueryClient } from '@tanstack/svelte-query';
  import { api } from '$lib/api/client';
  import type { Space } from '$lib/api/schemas';
  import { goto } from '$app/navigation';
  import { toasts } from '$lib/stores/toast';
  import { z } from 'zod';
  import { fly, slide } from 'svelte/transition';

  const qc = useQueryClient();

  const spacesQuery = createQuery<Space[]>(() => ({
    queryKey: ['spaces'],
    queryFn: async () => api.get('spaces/').json()
  }));

  const CreateSpaceSchema = z.object({
    name: z.string().min(1, 'Name is required').max(100, 'Must be 100 characters or fewer'),
    key: z.string().min(1, 'Key is required').min(2, 'Must be at least 2 characters').max(10, 'Must be 10 characters or fewer').regex(/^[A-Z0-9]+$/, 'Only uppercase letters and numbers')
  });

  let showForm = $state(false);
  let name = $state('');
  let key = $state('');
  let fieldErrors = $state<Record<string, string>>({});
  let touched = $state<Record<string, boolean>>({});

  function validate(): boolean {
    const result = CreateSpaceSchema.safeParse({ name, key });
    if (result.success) {
      fieldErrors = {};
      return true;
    }
    const errs: Record<string, string> = {};
    for (const issue of result.error.issues) {
      const k = issue.path[0] as string;
      if (!errs[k]) errs[k] = issue.message;
    }
    fieldErrors = errs;
    return false;
  }

  function onBlur(field: string) {
    touched[field] = true;
    validate();
  }

  const createMut = createMutation(() => ({
    mutationFn: async () => {
      await api.post('spaces/', { json: { name, key } });
    },
    onSuccess: async () => {
      toasts.success(`Space "${name}" created`);
      await qc.invalidateQueries({ queryKey: ['spaces'] });
      showForm = false;
      name = '';
      key = '';
      fieldErrors = {};
      touched = {};
    },
    onError: () => {
      toasts.error('Failed to create space — key may already exist');
    }
  }));

  function handleCreate() {
    touched = { name: true, key: true };
    if (!validate()) return;
    createMut.mutate();
  }

  function resetForm() {
    showForm = false;
    name = '';
    key = '';
    fieldErrors = {};
    touched = {};
  }
</script>

<div class="max-w-4xl mx-auto">
  <div class="flex items-center justify-between mb-4">
    <h1 class="text-xl sm:text-2xl font-semibold">Spaces</h1>
    {#if !showForm}
      <button
        onclick={() => (showForm = true)}
        class="px-4 py-2.5 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 active:bg-blue-800 transition-colors min-h-[44px]"
        in:fly={{ x: 20, duration: 200 }}
      >
        + New Space
      </button>
    {/if}
  </div>

  {#if showForm}
    <div transition:slide={{ duration: 200 }} class="mb-6 p-4 rounded-lg border border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-800/50">
      <h2 class="text-base font-medium mb-3">Create a new space</h2>
      <form onsubmit={(e) => { e.preventDefault(); handleCreate(); }} class="space-y-3" novalidate>
        <div>
          <input
            class="w-full border rounded px-3 py-3 bg-transparent text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none min-h-[44px] {touched.name && fieldErrors.name ? 'border-red-400 dark:border-red-500' : 'border-neutral-300 dark:border-neutral-600'}"
            placeholder="Space name (e.g. Engineering)"
            bind:value={name}
            onblur={() => onBlur('name')}
          />
          {#if touched.name && fieldErrors.name}
            <p class="text-red-500 text-xs mt-1" in:fly={{ y: -4, duration: 150 }}>{fieldErrors.name}</p>
          {/if}
        </div>
        <div>
          <input
            class="w-full border rounded px-3 py-3 bg-transparent text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none min-h-[44px] uppercase {touched.key && fieldErrors.key ? 'border-red-400 dark:border-red-500' : 'border-neutral-300 dark:border-neutral-600'}"
            placeholder="Key (e.g. ENG)"
            bind:value={key}
            onblur={() => onBlur('key')}
            oninput={() => (key = key.toUpperCase())}
            maxlength={10}
          />
          {#if touched.key && fieldErrors.key}
            <p class="text-red-500 text-xs mt-1" in:fly={{ y: -4, duration: 150 }}>{fieldErrors.key}</p>
          {:else}
            <p class="text-neutral-400 text-xs mt-1">Uppercase letters and numbers only</p>
          {/if}
        </div>
        <div class="flex flex-col sm:flex-row gap-2">
          <button
            class="px-4 py-3 rounded bg-blue-600 text-white font-medium disabled:opacity-60 hover:bg-blue-700 active:bg-blue-800 transition-colors min-h-[44px]"
            disabled={createMut.isPending}
          >
            {#if createMut.isPending}
              <span class="inline-flex items-center gap-2">
                <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
                Creating...
              </span>
            {:else}
              Create Space
            {/if}
          </button>
          <button
            type="button"
            onclick={resetForm}
            class="px-4 py-3 rounded border border-neutral-300 dark:border-neutral-600 text-neutral-600 dark:text-neutral-300 font-medium hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-colors min-h-[44px]"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  {/if}

  {#if spacesQuery.isLoading}
    <div class="space-y-3">
      {#each Array(3) as _}
        <div class="h-14 rounded-lg bg-neutral-100 dark:bg-neutral-800 animate-pulse"></div>
      {/each}
    </div>
  {:else if spacesQuery.isError}
    <p class="text-red-500">Error loading spaces</p>
  {:else if spacesQuery.data && spacesQuery.data.length === 0}
    <p class="text-neutral-500 text-center py-8">No spaces yet. Create one to get started!</p>
  {:else if spacesQuery.data}
    <div class="grid gap-2 sm:gap-3">
      {#each spacesQuery.data as s, i}
        <button
          class="w-full text-left px-4 py-3.5 rounded-lg border border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors active:bg-neutral-100 dark:active:bg-neutral-700 min-h-[44px]"
          onclick={() => goto(`/spaces/${s.key}`)}
          in:fly={{ y: 10, duration: 200, delay: i * 40 }}
        >
          <span class="font-medium text-blue-600 dark:text-blue-400">{s.name}</span>
          <span class="text-neutral-500 text-sm ml-2">({s.key})</span>
        </button>
      {/each}
    </div>
  {/if}
</div>
