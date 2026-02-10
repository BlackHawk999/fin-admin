<template>
  <div class="money-input">
    <label v-if="label" class="money-input__label" :for="id">{{ label }}</label>

    <input
      v-bind="attrs"
      :id="id"
      class="money-input__field"
      type="text"
      inputmode="numeric"
      :value="displayValue"
      :placeholder="placeholder"
      :disabled="disabled"
      @input="onInput"
    />

    <span class="money-input__suffix">сум</span>
    <p v-if="error" class="money-input__error">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAttrs } from 'vue'

defineOptions({ inheritAttrs: false })
const attrs = useAttrs()

const props = withDefaults(
  defineProps<{
    modelValue: number
    label?: string
    placeholder?: string
    disabled?: boolean
    error?: string
  }>(),
  { modelValue: 0 }
)
const emit = defineEmits<{ (e: 'update:modelValue', v: number): void }>()

const id = computed(() => `money-${Math.random().toString(36).slice(2, 9)}`)

const displayValue = computed(() => {
  if (props.modelValue === 0) return ''
  return formatForInput(props.modelValue)
})

function formatForInput(n: number): string {
  return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
}

function parseInput(s: string): number {
  const digits = s.replace(/\s/g, '').replace(/\D/g, '')
  return digits ? parseInt(digits, 10) : 0
}

function onInput(e: Event) {
  const raw = (e.target as HTMLInputElement).value
  const num = parseInput(raw)
  emit('update:modelValue', num)
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.money-input {
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
    }
    &:disabled {
      background: #f5f5f5;
    }
  }

  &__suffix {
    margin-left: 0.5rem;
    font-size: 0.875rem;
    color: $text-muted;
  }

  &__error {
    margin: 0.25rem 0 0;
    font-size: 0.8rem;
    color: $danger;
  }
}
</style>
