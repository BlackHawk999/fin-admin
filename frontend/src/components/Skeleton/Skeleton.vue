<template>
  <div class="skeleton" :class="[`skeleton_${variant}`, { skeleton_rounded: rounded }]" :style="style"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    width?: string | number
    height?: string | number
    variant?: 'text' | 'card' | 'avatar' | 'block'
    rounded?: boolean
  }>(),
  { variant: 'block', rounded: false }
)

const style = computed(() => {
  const s: Record<string, string> = {}
  if (props.width) s.width = typeof props.width === 'number' ? `${props.width}px` : props.width
  if (props.height) s.height = typeof props.height === 'number' ? `${props.height}px` : props.height
  return s
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.skeleton {
  background: linear-gradient(90deg, #eee 25%, #f5f5f5 50%, #eee 75%);
  background-size: 200% 100%;
  animation: skeleton-shine 1.2s ease-in-out infinite;

  &_text {
    height: 1em;
    border-radius: 2px;
  }

  &_card {
    height: 80px;
    border-radius: $radius;
  }

  &_avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
  }

  &_block {
    border-radius: 4px;
  }

  &_rounded {
    border-radius: 8px;
  }
}

@keyframes skeleton-shine {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
