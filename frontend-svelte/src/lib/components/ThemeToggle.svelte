<script lang="ts">
  import { onMount } from 'svelte';
  let dark = false;
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

<button class="btn btn-ghost" aria-label="Toggle theme" on:click={toggle}>
  {#if dark}🌙{:else}☀️{/if}
</button>
