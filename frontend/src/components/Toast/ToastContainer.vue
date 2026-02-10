<template>
  <div class="toast-container">
    <TransitionGroup name="toast">
      <div
        v-for="t in toastStore.toasts"
        :key="t.id"
        class="toast toast-container__item"
        :class="`toast_${t.type}`"
        role="alert"
      >
        <span class="toast__message">{{ t.message }}</span>
        <button type="button" class="toast__close" aria-label="Закрыть" @click="toastStore.remove(t.id)">×</button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { useToastStore } from '@/stores/toastStore'
const toastStore = useToastStore()
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.toast-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 1100;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 360px;
  pointer-events: none;

  &__item {
    pointer-events: auto;
  }
}

.toast {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: $radius;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  font-size: 0.875rem;

  &_success {
    background: $success;
    color: #fff;
  }

  &_error {
    background: $danger;
    color: #fff;
  }

  &__message {
    flex: 1;
  }

  &__close {
    flex-shrink: 0;
    width: 24px;
    height: 24px;
    border: none;
    background: rgba(255, 255, 255, 0.3);
    color: inherit;
    font-size: 1.25rem;
    line-height: 1;
    cursor: pointer;
    border-radius: 4px;
    &:hover {
      background: rgba(255, 255, 255, 0.5);
    }
  }
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(1rem);
}
</style>
