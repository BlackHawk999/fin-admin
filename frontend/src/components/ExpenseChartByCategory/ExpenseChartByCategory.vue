<template>
  <div class="expense-chart-by-category">
    <canvas ref="chartRef"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const COLORS = [
  '#2563eb',
  '#16a34a',
  '#ca8a04',
  '#dc2626',
  '#9333ea',
  '#0d9488',
  '#ea580c',
]

const props = defineProps<{
  data: { category: string; total_uzs: number }[]
}>()

const chartRef = ref<HTMLCanvasElement | null>(null)
let chart: Chart | null = null

function render() {
  if (!chartRef.value || !props.data.length) return
  if (chart) chart.destroy()
  chart = new Chart(chartRef.value, {
    type: 'doughnut',
    data: {
      labels: props.data.map((d) => d.category),
      datasets: [
        {
          data: props.data.map((d) => d.total_uzs),
          backgroundColor: props.data.map((_, i) => COLORS[i % COLORS.length]),
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { position: 'right' },
      },
    },
  })
}

onMounted(render)
watch(() => props.data, render, { deep: true })
</script>

<style lang="scss" scoped>
.expense-chart-by-category {
  max-height: 280px;
  padding: 1rem 0;
}
</style>
