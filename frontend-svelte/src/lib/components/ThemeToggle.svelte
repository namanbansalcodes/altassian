<script lang="ts">
  import { onMount } from 'svelte';
  let dark = $state(false);
  onMount(() => {
    const saved = localStorage.getItem('theme');
    dark = saved ? saved === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.documentElement.classList.toggle('dark', dark);
  });
  function toggle() {
    dark = !dark;
    document.documentElement.classList.toggle('dark', dark);
    localStorage.setItem('theme', dark ? 'dark' : 'light');
  }
</script>

<button class="p-2 rounded-lg text-neutral-500 hover:bg-neutral-100 dark:text-neutral-400 dark:hover:bg-neutral-800 transition-colors" aria-label="Toggle theme" onclick={toggle}>
  {#if dark}🌙{:else}☀️{/if}
</button>
