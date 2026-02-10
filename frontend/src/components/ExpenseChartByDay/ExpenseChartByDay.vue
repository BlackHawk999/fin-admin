<template>
  <div class="expense-chart-by-day">
    <canvas ref="chartRef"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const props = defineProps<{
  data: { date: string; total_uzs: number }[]
}>()

const chartRef = ref<HTMLCanvasElement | null>(null)
let chart: Chart | null = null

function render() {
  if (!chartRef.value || !props.data.length) return
  if (chart) chart.destroy()
  chart = new Chart(chartRef.value, {
    type: 'line',
    data: {
      labels: props.data.map((d) => d.date.slice(0, 10)),
      datasets: [
        {
          label: 'Расходы (сум)',
          data: props.data.map((d) => d.total_uzs),
          borderColor: 'rgb(37, 99, 235)',
          backgroundColor: 'rgba(37, 99, 235, 0.1)',
          borderWidth: 2,
          fill: true,
          tension: 0.2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback(value) {
              const n = Number(value)
              if (n >= 1e6) return (n / 1e6).toFixed(0) + 'M'
              if (n >= 1e3) return (n / 1e3).toFixed(0) + 'K'
              return String(n)
            },
          },
        },
      },
    },
  })
}

onMounted(render)
watch(() => props.data, render, { deep: true })
</script>

<style lang="scss" scoped>
.expense-chart-by-day {
  max-height: 280px;
  padding: 1rem 0;
}
</style>
