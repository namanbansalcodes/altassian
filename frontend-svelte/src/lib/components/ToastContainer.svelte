<script lang="ts">
  import { toasts } from '$lib/stores/toast';
  import { fly, fade } from 'svelte/transition';
  import { flip } from 'svelte/animate';
</script>

<div class="fixed bottom-20 md:bottom-6 right-3 sm:right-6 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none" style="padding-right: env(safe-area-inset-right); padding-bottom: env(safe-area-inset-bottom);">
  {#each $toasts as toast (toast.id)}
    <div
      animate:flip={{ duration: 200 }}
      in:fly={{ x: 80, duration: 250 }}
      out:fade={{ duration: 150 }}
      role="alert"
      class="pointer-events-auto rounded-lg px-4 py-3 shadow-lg text-sm font-medium flex items-start gap-3 {toast.type === 'success'
        ? 'bg-green-600 text-white'
        : toast.type === 'error'
          ? 'bg-red-600 text-white'
          : 'bg-neutral-800 text-white dark:bg-neutral-200 dark:text-neutral-900'}"
    >
      <span class="flex-1 break-words">{toast.message}</span>
      <button
        on:click={() => toasts.dismiss(toast.id)}
        class="shrink-0 opacity-70 hover:opacity-100 transition-opacity -mr-1 -mt-0.5 p-1"
        aria-label="Dismiss"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  {/each}
</div>
