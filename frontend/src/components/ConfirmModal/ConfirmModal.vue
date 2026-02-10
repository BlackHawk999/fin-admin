<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modelValue" class="confirm-modal" @click.self="emit('update:modelValue', false)">
        <div class="confirm-modal__backdrop"></div>
        <div class="confirm-modal__box" role="dialog" aria-modal="true">
          <p class="confirm-modal__text">{{ text }}</p>
          <div class="confirm-modal__actions">
            <button type="button" class="btn btn_secondary" @click="emit('update:modelValue', false)">
              {{ cancelLabel }}
            </button>
            <button type="button" class="btn btn_danger" @click="confirm">
              {{ confirmLabel }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    modelValue: boolean
    text: string
    confirmLabel?: string
    cancelLabel?: string
  }>(),
  { confirmLabel: 'Удалить', cancelLabel: 'Отмена' }
)
const emit = defineEmits<{ (e: 'update:modelValue', v: boolean): void; (e: 'confirm'): void }>()

function confirm() {
  emit('confirm')
  emit('update:modelValue', false)
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.confirm-modal {
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
    padding: 1.5rem;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
    max-width: 400px;
  }

  &__text {
    margin: 0 0 1.25rem;
    font-size: 0.9375rem;
  }

  &__actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
  }
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
