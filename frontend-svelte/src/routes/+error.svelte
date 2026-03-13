<script lang="ts">
  const { error } = $props<{ error: Error & { status?: number } }>();
</script>

<div class="max-w-xl mx-auto">
  <h1 class="text-xl sm:text-2xl font-semibold mb-2">Error {error?.status ?? ''}</h1>
  <pre class="bg-neutral-800 text-neutral-100 p-3 rounded text-xs sm:text-sm overflow-x-auto break-words whitespace-pre-wrap">{error?.message}</pre>
</div>
