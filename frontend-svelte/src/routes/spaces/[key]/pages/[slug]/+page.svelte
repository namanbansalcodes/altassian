<script lang="ts">
  import { createQuery, createMutation, useQueryClient } from '@tanstack/svelte-query';
  import { api } from '$lib/api/client';
  import { page as pageStore } from '$app/stores';

  const key = $derived($pageStore.params.key);
  const slug = $derived($pageStore.params.slug);
  const qc = useQueryClient();

  const pageQuery = createQuery<{ id: number; title: string; content: string | null }>({
    queryKey: ['page', key, slug],
    queryFn: async () => api.get(`spaces/${key}/pages/${slug}/`).json(),
    enabled: !!key && !!slug
  });

  let content = $state('');
  $effect(() => { if ($pageQuery?.data) content = $pageQuery.data.content ?? ''; });

  const saveMutation = createMutation({
    mutationFn: async () =>
      api.patch(`spaces/${key}/pages/${slug}/`, { json: { content } }),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ['page', key, slug] });
    }
  });
</script>

<div class="max-w-4xl mx-auto space-y-3">
  {#if $pageQuery.isLoading}
    <p class="text-neutral-500">Loading...</p>
  {:else if $pageQuery.isError}
    <p class="text-red-500">Error loading page</p>
  {:else}
    <h1 class="text-xl sm:text-2xl font-semibold">{$pageQuery.data.title}</h1>
    <textarea
      class="w-full min-w-0 min-h-[12rem] sm:min-h-[14rem] md:min-h-[18rem] p-2.5 rounded border border-neutral-300 dark:border-neutral-600 bg-transparent text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-y"
      bind:value={content}
    />
    <div class="flex flex-col sm:flex-row flex-wrap items-stretch sm:items-center gap-3">
      <button
        class="px-4 py-3 rounded bg-blue-600 text-white font-medium disabled:opacity-60 hover:bg-blue-700 active:bg-blue-800 transition-colors"
        disabled={saveMutation.isPending}
        on:click={() => saveMutation.mutate()}
      >
        Save
      </button>
      {#if saveMutation.isSuccess}
        <span class="text-green-500 text-sm">Saved</span>
      {/if}
    </div>
  {/if}
</div>
