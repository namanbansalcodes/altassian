<script lang="ts">
  import { createQuery, createMutation, queryClient } from '@tanstack/svelte-query';
  import { api } from '$lib/api/client';
  import { page as pageStore } from '$app/stores';

  $: key = $pageStore.params.key;
  $: slug = $pageStore.params.slug;

  const pageQuery = createQuery<{ id: number; title: string; content: string | null }>({
    queryKey: ['page', key, slug],
    queryFn: async () => api.get(`spaces/${key}/pages/${slug}/`).json(),
    enabled: !!key && !!slug
  });

  let content = '';
  $: if ($pageQuery?.data) content = $pageQuery.data.content ?? '';

  const saveMutation = createMutation({
    mutationFn: async () =>
      api.patch(`spaces/${key}/pages/${slug}/`, { json: { content } }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['page', key, slug] });
    }
  });
</script>

<div class="p-6 space-y-3">
  {#if $pageQuery.isLoading}
    <p>Loading...</p>
  {:else if $pageQuery.isError}
    <p>Error loading page</p>
  {:else}
    <h1 class="text-2xl font-semibold">{$pageQuery.data.title}</h1>
    <textarea class="w-full h-64 p-2 rounded border border-neutral-400 bg-transparent" bind:value={content} />
    <button class="px-4 py-2 rounded bg-blue-600 text-white disabled:opacity-60" disabled={saveMutation.isPending} on:click={() => saveMutation.mutate()}>
      Save
    </button>
    {#if saveMutation.isSuccess}
      <span class="text-green-500">Saved</span>
    {/if}
  {/if}
</div>
