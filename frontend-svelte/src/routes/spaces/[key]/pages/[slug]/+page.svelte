<script lang="ts">
  import { createQuery, createMutation, useQueryClient } from '@tanstack/svelte-query';
  import { api } from '$lib/api/client';
  import { page as pageStore } from '$app/stores';
  import { toasts } from '$lib/stores/toast';

  const key = $derived($pageStore.params.key);
  const slug = $derived($pageStore.params.slug);
  const qc = useQueryClient();

  const pageQuery = createQuery<{ id: number; title: string; content: string | null }>(() => ({
    queryKey: ['page', key, slug],
    queryFn: async () => api.get(`spaces/${key}/pages/${slug}/`).json(),
    enabled: !!key && !!slug
  }));

  let content = $state('');
  let dirty = $state(false);
  $effect(() => {
    if (pageQuery?.data) {
      content = pageQuery.data.content ?? '';
      dirty = false;
    }
  });

  function onInput() {
    dirty = true;
  }

  const saveMutation = createMutation(() => ({
    mutationFn: async () =>
      api.patch(`spaces/${key}/pages/${slug}/`, { json: { content } }),
    onSuccess: async () => {
      dirty = false;
      toasts.success('Page saved');
      await qc.invalidateQueries({ queryKey: ['page', key, slug] });
    },
    onError: () => {
      toasts.error('Failed to save page');
    }
  }));
</script>

<svelte:head>
  {#if pageQuery.data}
    <title>{pageQuery.data.title} — Altassian</title>
    <meta name="description" content="{pageQuery.data.title} — documentation page on Altassian workspace" />
    <meta property="og:title" content={pageQuery.data.title} />
    <meta property="og:type" content="article" />
    <meta property="og:site_name" content="Altassian" />
    <link rel="canonical" href="/spaces/{key}/pages/{slug}" />
    {@html `<script type="application/ld+json">${JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'Article',
      headline: pageQuery.data.title,
      publisher: { '@type': 'Organization', name: 'Altassian' },
    })}</script>`}
  {/if}
</svelte:head>

<div class="max-w-4xl mx-auto space-y-3">
  {#if pageQuery.isLoading}
    <div class="space-y-3 animate-pulse">
      <div class="h-8 w-2/3 bg-neutral-100 dark:bg-neutral-800 rounded"></div>
      <div class="h-48 bg-neutral-100 dark:bg-neutral-800 rounded"></div>
    </div>
  {:else if pageQuery.isError}
    <p class="text-red-500">Error loading page</p>
  {:else if pageQuery.data}
    <h1 class="text-xl sm:text-2xl font-semibold break-words">{pageQuery.data.title}</h1>
    <textarea
      class="w-full min-w-0 min-h-[10rem] sm:min-h-[14rem] md:min-h-[18rem] max-h-[60vh] p-2.5 rounded border border-neutral-300 dark:border-neutral-600 bg-transparent text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-y"
      bind:value={content}
      oninput={onInput}
    ></textarea>
    <div class="flex flex-col sm:flex-row flex-wrap items-stretch sm:items-center gap-3">
      <button
        class="px-4 py-3 rounded bg-blue-600 text-white font-medium disabled:opacity-60 hover:bg-blue-700 active:bg-blue-800 transition-colors min-h-[44px]"
        disabled={saveMutation.isPending || !dirty}
        onclick={() => saveMutation.mutate()}
      >
        {#if saveMutation.isPending}
          <span class="inline-flex items-center gap-2">
            <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            Saving...
          </span>
        {:else}
          Save
        {/if}
      </button>
      {#if dirty}
        <span class="text-yellow-600 dark:text-yellow-400 text-sm">Unsaved changes</span>
      {/if}
    </div>
  {/if}
</div>
