<template>
  <div class="summary-cards">
    <div v-for="card in cards" :key="card.title" class="summary-cards__card">
      <span class="summary-cards__label">{{ card.title }}</span>
      <span class="summary-cards__value">{{ card.value }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  cards: { title: string; value: string | number }[]
}>()
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;

  &__card {
    padding: 1rem;
    background: $bg-card;
    border-radius: $radius;
    box-shadow: $shadow;
    border: 1px solid #eee;
  }

  &__label {
    display: block;
    font-size: 0.8rem;
    color: $text-muted;
    margin-bottom: 0.25rem;
  }

  &__value {
    font-size: 1.25rem;
    font-weight: 600;
    color: $text-primary;
  }
}
</style>
