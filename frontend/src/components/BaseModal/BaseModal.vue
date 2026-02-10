<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        v-bind="attrs"
        class="base-modal"
        @click.self="emit('update:modelValue', false)"
      >
        <div class="base-modal__backdrop"></div>

        <div class="base-modal__box" role="dialog">
          <div class="base-modal__header">
            <h2 class="base-modal__title">{{ title }}</h2>
            <button
              type="button"
              class="base-modal__close"
              aria-label="Закрыть"
              @click="emit('update:modelValue', false)"
            >
              ×
            </button>
          </div>

          <div class="base-modal__body">
            <slot></slot>
          </div>

          <div v-if="$slots.footer" class="base-modal__footer">
            <slot name="footer"></slot>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { useAttrs } from 'vue'

defineOptions({ inheritAttrs: false })
const attrs = useAttrs()

defineProps<{
  modelValue: boolean
  title: string
}>()

const emit = defineEmits<{ (e: 'update:modelValue', v: boolean): void }>()
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.base-modal {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;

  &__backdrop {
    position: absolute;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
  }

  &__box {
    position: relative;
    width: 100%;
    max-width: 480px;
    max-height: 90vh;
    overflow: auto;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  }

  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.25rem;
    border-bottom: 1px solid $border-color;
  }

  &__title {
    margin: 0;
    font-size: 1.125rem;
    font-weight: 600;
  }

  &__close {
    width: 32px;
    height: 32px;
    border: none;
    background: transparent;
    font-size: 1.5rem;
    line-height: 1;
    color: #666;
    cursor: pointer;
    border-radius: 4px;

    &:hover {
      background: #f0f0f0;
    }
  }

  &__body {
    padding: 1.25rem;
  }

  &__footer {
    padding: 1rem 1.25rem;
    border-top: 1px solid $border-color;
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
  }
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s;

  .base-modal__box {
    transition: transform 0.2s;
  }
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;

  .base-modal__box {
    transform: scale(0.96);
  }
}
</style>
