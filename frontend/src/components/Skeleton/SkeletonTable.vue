<template>
  <div class="skeleton-table" :style="{ '--cols': columns }">
    <div class="skeleton-table__head">
      <div v-for="i in columns" :key="i" class="skeleton-table__cell skeleton-table__cell_head">
        <Skeleton variant="text" width="80%" height="14" />
      </div>
    </div>
    <div v-for="row in rows" :key="row" class="skeleton-table__row">
      <div v-for="c in columns" :key="c" class="skeleton-table__cell">
        <Skeleton variant="text" width="90%" height="14" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Skeleton from './Skeleton.vue'

withDefaults(
  defineProps<{
    columns?: number
    rows?: number
  }>(),
  { columns: 5, rows: 6 }
)
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.skeleton-table {
  --cols: 5;
  background: $bg-card;
  border-radius: $radius;
  overflow: hidden;

  &__head {
    display: grid;
    grid-template-columns: repeat(var(--cols), 1fr);
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    background: #f9fafb;
    border-bottom: 1px solid $border-color;
  }

  &__row {
    display: grid;
    grid-template-columns: repeat(var(--cols), 1fr);
    gap: 0.5rem;
    padding: 0.6rem 1rem;
    border-bottom: 1px solid #f0f0f0;
  }

  &__cell {
    &_head {
      font-weight: 600;
    }
  }
}
</style>
