<template>
  <div class="topbar-date-range">
    <div class="topbar-date-range__presets">
      <button
        type="button"
        class="topbar-date-range__preset"
        :class="{ 'topbar-date-range__preset_active': globalDate.preset === 'today' }"
        @click="setToday"
      >
        Today
      </button>

      <button
        type="button"
        class="topbar-date-range__preset"
        :class="{ 'topbar-date-range__preset_active': globalDate.preset === 'month' }"
        @click="setMonth"
      >
        Month
      </button>

      <button
        type="button"
        class="topbar-date-range__preset"
        :class="{ 'topbar-date-range__preset_active': globalDate.preset === 'custom' }"
        @click="openCustom"
      >
        Custom
      </button>
    </div>

    <div v-if="showCustom" class="topbar-date-range__custom">
      <input v-model="customFrom" type="date" class="topbar-date-range__input" />
      <span class="topbar-date-range__sep">—</span>
      <input v-model="customTo" type="date" class="topbar-date-range__input" />
      <button type="button" class="btn btn_secondary btn_sm" @click="applyCustom">OK</button>
      <button type="button" class="btn btn_secondary btn_sm" @click="cancelCustom">Cancel</button>
    </div>

    <span class="topbar-date-range__label">{{ rangeLabel }}</span>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useGlobalDateStore } from '@/stores/globalDateStore'

const globalDate = useGlobalDateStore()

const showCustom = ref(false)
const customFrom = ref<string>(globalDate.date_from)
const customTo = ref<string>(globalDate.date_to)

const rangeLabel = computed(() => {
  if (globalDate.preset === 'today') return `Сегодня: ${globalDate.date_from}`
  return `${globalDate.date_from} — ${globalDate.date_to}`
})

function openCustom() {
  showCustom.value = true
  // когда открываем — синхронизируем значения
  customFrom.value = globalDate.date_from
  customTo.value = globalDate.date_to
}

function cancelCustom() {
  showCustom.value = false
}

function setToday() {
  globalDate.setToday()
  showCustom.value = false
}

function setMonth() {
  globalDate.setMonth()
  showCustom.value = false
}

function applyCustom() {
  // минимальная защита от пустых дат
  if (!customFrom.value || !customTo.value) return

  globalDate.setCustom(customFrom.value, customTo.value)
  showCustom.value = false
}

watch(
  () => globalDate.preset,
  (p) => {
    // если пресет меняется не на custom — закрываем кастомный блок
    if (p !== 'custom') showCustom.value = false
  }
)
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.topbar-date-range {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;

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

    &_active {
      background: $primary;
      border-color: $primary;
      color: #fff;
    }
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

  &__label {
    font-size: 0.8rem;
    color: $text-muted;
  }
}
</style>
