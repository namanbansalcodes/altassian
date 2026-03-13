<!--
  ResponsiveTable — wraps table content so it scrolls horizontally on small screens
  while using full-width on desktop. Mirrors the React ResponsiveTable component.
-->
<div class="overflow-x-auto -mx-4 sm:-mx-6 md:mx-0 {className}">
  <div class="inline-block min-w-full px-4 sm:px-6 md:px-0 align-middle">
    <slot />
  </div>
</div>

<script lang="ts">
  export let className: string = '';
</script>
