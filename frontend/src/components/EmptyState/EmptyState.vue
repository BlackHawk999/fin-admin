<template>
  <div class="empty-state">
    <div class="empty-state__icon" aria-hidden="true">{{ icon }}</div>
    <p class="empty-state__text">{{ text }}</p>
    <slot name="action"></slot>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    text?: string
    icon?: string
  }>(),
  { text: 'Нет данных', icon: '—' }
)
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.empty-state {
  padding: 2.5rem 1.5rem;
  text-align: center;
  background: $bg-card;
  border-radius: $radius;
  border: 1px dashed $border-color;

  &__icon {
    font-size: 2rem;
    color: $text-muted;
    margin-bottom: 0.5rem;
  }

  &__text {
    margin: 0 0 1rem;
    font-size: 0.9375rem;
    color: $text-muted;
  }
}
</style>
