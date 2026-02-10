<template>
  <div class="base-input" :class="{ 'base-input_inline': inline }">
    <label v-if="label" class="base-input__label" :for="id">{{ label }}</label>

    <input
      v-bind="attrs"
      :id="id"
      ref="inputRef"
      class="base-input__field"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :readonly="readonly"
      @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />

    <p v-if="error" class="base-input__error">{{ error }}</p>
  </div>
</template>


<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAttrs } from 'vue'

defineOptions({ inheritAttrs: false })
const attrs = useAttrs()

const props = withDefaults(
  defineProps<{
    modelValue: string | number
    label?: string
    type?: string
    placeholder?: string
    disabled?: boolean
    readonly?: boolean
    error?: string
    inline?: boolean
  }>(),
  { type: 'text', inline: false }
)
const emit = defineEmits<{ (e: 'update:modelValue', v: string): void }>()

const id = computed(() => `input-${Math.random().toString(36).slice(2, 9)}`)
const inputRef = ref<HTMLInputElement | null>(null)
defineExpose({ focus: () => inputRef.value?.focus() })
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.base-input {
  &_inline {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    .base-input__label {
      margin-bottom: 0;
      min-width: 100px;
    }
  }

  &__label {
    display: block;
    margin-bottom: 0.35rem;
    font-size: 0.875rem;
    font-weight: 500;
    color: $text-primary;
  }

  &__field {
    width: 100%;
    padding: 0.5rem 0.75rem;
    border: 1px solid $border-color;
    border-radius: 4px;
    font-size: 0.875rem;
    &:focus {
      outline: none;
      border-color: $primary;
      box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
    }
    &:disabled {
      background: #f5f5f5;
      color: #888;
    }
  }

  &__error {
    margin: 0.25rem 0 0;
    font-size: 0.8rem;
    color: $danger;
  }
}
</style>
