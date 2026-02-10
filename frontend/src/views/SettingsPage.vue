<template>
  <div class="settings-page">
    <h1 class="page-header__title">Settings</h1>
    <p class="settings-page__placeholder">Настройки (опционально).</p>
  </div>
</template>

<script setup lang="ts">
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.settings-page {
  &__placeholder {
    color: $text-muted;
    font-size: 0.9375rem;
  }
}
</style>
