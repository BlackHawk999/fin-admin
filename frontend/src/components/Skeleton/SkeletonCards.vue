<template>
  <div class="skeleton-cards">
    <div v-for="i in count" :key="i" class="skeleton-cards__card">
      <Skeleton variant="text" width="70%" height="12" />
      <Skeleton variant="text" width="50%" height="24" style="margin-top: 0.5rem" />
    </div>
  </div>
</template>

<script setup lang="ts">
import Skeleton from './Skeleton.vue'
withDefaults(defineProps<{ count?: number }>(), { count: 4 })
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.skeleton-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1rem;

  &__card {
    padding: 1rem;
    background: $bg-card;
    border-radius: $radius;
    box-shadow: $shadow;
  }
}
</style>
