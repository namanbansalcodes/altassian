<!--
  ResponsiveTable — wraps table content so it scrolls horizontally on small screens
  while using full-width on desktop. Mirrors the React ResponsiveTable component.
-->
<script lang="ts">
  import { onMount } from 'svelte';

  export let className: string = '';

  let scrollEl: HTMLDivElement;
  let canScrollLeft = false;
  let canScrollRight = false;

  function updateScrollState() {
    if (!scrollEl) return;
    canScrollLeft = scrollEl.scrollLeft > 1;
    canScrollRight = scrollEl.scrollLeft + scrollEl.clientWidth < scrollEl.scrollWidth - 1;
  }

  onMount(() => {
    updateScrollState();
    const ro = new ResizeObserver(updateScrollState);
    ro.observe(scrollEl);
    scrollEl.addEventListener('scroll', updateScrollState, { passive: true });
    return () => {
      ro.disconnect();
      scrollEl.removeEventListener('scroll', updateScrollState);
    };
  });
</script>

<div class="relative {className}">
  {#if canScrollLeft}
    <div class="absolute left-0 top-0 bottom-0 w-6 sm:w-8 bg-gradient-to-r from-white dark:from-neutral-900 to-transparent z-10 pointer-events-none md:hidden" />
  {/if}
  {#if canScrollRight}
    <div class="absolute right-0 top-0 bottom-0 w-6 sm:w-8 bg-gradient-to-l from-white dark:from-neutral-900 to-transparent z-10 pointer-events-none md:hidden" />
  {/if}
  <div bind:this={scrollEl} class="overflow-x-auto -mx-4 sm:-mx-6 md:mx-0 scrollbar-thin">
    <div class="inline-block min-w-full px-4 sm:px-6 md:px-0 align-middle">
      <slot />
    </div>
  </div>
</div>
