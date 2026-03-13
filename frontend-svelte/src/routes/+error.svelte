<script lang="ts">
  export let error: Error & { status?: number };
</script>

<div class="p-6">
  <h1 class="text-2xl font-semibold mb-2">Error {error?.status ?? ''}</h1>
  <pre class="bg-neutral-800 text-neutral-100 p-3 rounded">{error?.message}</pre>
</div>
