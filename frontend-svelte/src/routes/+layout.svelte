<script lang="ts">
  import '../app.css';
  import { QueryClient, SvelteQueryClientProvider } from '@tanstack/svelte-query';
  const queryClient = new QueryClient();
</script>

<SvelteQueryClientProvider client={queryClient}>
  <slot />
</SvelteQueryClientProvider>
