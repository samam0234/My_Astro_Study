<script setup>
import { ref } from 'vue';

const pinned = ref(false);
</script>

<template>
  <button class="pin" type="button" @click="pinned = !pinned">
    {{ pinned ? '이 메모를 고정함' : '이 메모 고정' }}
  </button>
</template>
