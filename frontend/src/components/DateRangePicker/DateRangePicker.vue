<template>
  <div class="date-range-picker">
    <div class="date-range-picker__presets">
      <button
        v-for="p in presets"
        :key="p.key"
        type="button"
        class="date-range-picker__preset"
        :class="{ 'date-range-picker__preset_active': preset === p.key }"
        @click="selectPreset(p.key)"
      >
        {{ p.label }}
      </button>
    </div>

    <div class="date-range-picker__custom">
      <input v-model="localFrom" type="date" class="date-range-picker__input" />
      <span class="date-range-picker__sep">—</span>
      <input v-model="localTo" type="date" class="date-range-picker__input" />

      <button type="button" class="btn btn_secondary btn_sm" @click="applyCustom">
        OK
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { today, daysAgo, firstDayOfMonth, lastDayOfMonth } from '@/utils/date'

type DateRange = { date_from: string; date_to: string }
type PresetKey = 'today' | '7' | '30' | 'month' | 'custom'

const props = defineProps<{
  modelValue: DateRange
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', v: DateRange): void
}>()

const presets: Array<{ key: PresetKey; label: string }> = [
  { key: 'today', label: 'Today' },
  { key: '7', label: '7 days' },
  { key: '30', label: '30 days' },
  { key: 'month', label: 'Month' },
  { key: 'custom', label: 'Custom' },
]

const preset = ref<PresetKey>('custom')
const localFrom = ref(props.modelValue.date_from)
const localTo = ref(props.modelValue.date_to)

watch(
  () => props.modelValue,
  (v) => {
    localFrom.value = v.date_from
    localTo.value = v.date_to
  },
  { deep: true }
)

function selectPreset(k: PresetKey) {
  preset.value = k

  if (k === 'today') {
    const d = today()
    emit('update:modelValue', { date_from: d, date_to: d })
    return
  }

  if (k === '7') {
    emit('update:modelValue', { date_from: daysAgo(6), date_to: today() })
    return
  }

  if (k === '30') {
    emit('update:modelValue', { date_from: daysAgo(29), date_to: today() })
    return
  }

  if (k === 'month') {
    emit('update:modelValue', { date_from: firstDayOfMonth(), date_to: lastDayOfMonth() })
    return
  }

  // custom — просто оставляем поля, пользователь нажмёт OK
}

function applyCustom() {
  preset.value = 'custom'
  emit('update:modelValue', { date_from: localFrom.value, date_to: localTo.value })
}
</script>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.date-range-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;

  &__presets {
    display: flex;
    gap: 0.25rem;
  }

  &__preset {
    padding: 0.35rem 0.6rem;
    border: 1px solid $border-color;
    border-radius: 4px;
    background: #fff;
    font-size: 0.8rem;
    cursor: pointer;

    &:hover {
      background: $bg-hover;
    }
  }

  &__preset_active {
    background: $primary;
    border-color: $primary;
    color: #fff;
  }

  &__custom {
    display: flex;
    align-items: center;
    gap: 0.35rem;
  }

  &__input {
    padding: 0.35rem 0.5rem;
    border: 1px solid $border-color;
    border-radius: 4px;
    font-size: 0.8rem;
  }

  &__sep {
    color: $text-muted;
    font-size: 0.8rem;
  }
}
</style>
