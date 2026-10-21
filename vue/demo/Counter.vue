<script setup>
import { ref } from 'vue';

defineProps({
  label: {
    type: String,
    default: 'Vue',
  },
});

const count = ref(0);
</script>

<template>
  <button class="island-button" type="button" @click="count++">{{ label }} {{ count }}</button>
</template>
