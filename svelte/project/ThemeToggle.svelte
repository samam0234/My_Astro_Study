<script>
  let dark = $state(false);

  function toggle() {
    dark = !dark;
    document.documentElement.dataset.theme = dark ? 'dark' : 'light';
  }
</script>

<button class="theme" type="button" onclick={toggle}>
  {dark ? '밝게' : '어둡게'}
</button>
