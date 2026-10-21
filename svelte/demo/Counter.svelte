<script>
  let { label = 'Svelte' } = $props();
  let count = $state(0);
</script>

<button class="island-button" type="button" onclick={() => (count += 1)}>
  {label} {count}
</button>
