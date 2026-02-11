<template>
  <div class="worker-detail-page" data-testid="worker-detail-page">
    <div class="page-header">
      <h1 class="page-header__title" data-testid="worker-detail-title">
        {{ employee?.full_name || 'Ishchi' }}
      </h1>

      <router-link to="/workers" class="btn btn_secondary" data-testid="worker-detail-back">
        ← Ro'yxatga
      </router-link>
    </div>

    <div v-if="loading" class="worker-detail-page__loading" data-testid="worker-detail-loading">
      Yuklanyabdi...
    </div>

    <template v-else-if="employee">
      <div data-testid="worker-summary">
        <SummaryCards :cards="summaryCards" />
      </div>

      <div class="worker-detail-page__daterange" data-testid="worker-advances-daterange">
        <DateRangePicker v-model="dateRange" />
      </div>

      <div class="worker-detail-page__table-wrap" data-testid="worker-advances-wrap">
        <div class="worker-detail-page__table-header">
          <h2>Avanslar</h2>
          <button type="button" class="btn btn_primary btn_sm" @click="openAdvanceModal" data-testid="advance-add">
            Avans qo'shish
          </button>
        </div>

        <div data-testid="worker-advances-table">
          <BaseTable :columns="advanceColumns" :data="advances" row-key="id" :summary="advancesSummary" actions>
            <template #cell="{ column, value }">
              <template v-if="column.key === 'amount_uzs'">
                {{ formatUzs(Number(value || 0)) }}
              </template>
              <template v-else>
                {{ value ?? '—' }}
              </template>
            </template>

            <template #actions="{ row }">
              <button
                type="button"
                class="btn btn_danger btn_sm"
                @click="deleteAdv(row as Advance)"
                :data-testid="`advance-delete-${(row as Advance).id}`"
              >
                O'chirish
              </button>
            </template>
          </BaseTable>
        </div>
      </div>

      <BaseModal v-model="showAdvanceModal" title="Yangi avans" data-testid="advance-modal">
        <form class="form" @submit.prevent="addAdvance" data-testid="advance-form">
          <BaseInput v-model="advanceForm.date" label="Sana" type="date" data-testid="advance-date" />
          <MoneyInput v-model="advanceForm.amount_uzs" label="Summa" data-testid="advance-amount" />
          <BaseInput v-model="advanceForm.comment" label="Izoh" data-testid="advance-comment" />
        </form>

        <template #footer>
          <button type="button" class="btn btn_secondary" @click="showAdvanceModal = false" data-testid="advance-cancel">
            Bekor qilish
          </button>
          <button type="button" class="btn btn_primary" @click="addAdvance" data-testid="advance-submit">
            Qo'shish
          </button>
        </template>
      </BaseModal>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { fetchEmployee, fetchAdvances, fetchAdvancesSum, createAdvance, deleteAdvance } from '@/api/employees'
import { formatUzs } from '@/utils/format'
import { firstDayOfMonth, lastDayOfMonth } from '@/utils/date'
import SummaryCards from '@/components/SummaryCards/SummaryCards.vue'
import DateRangePicker from '@/components/DateRangePicker/DateRangePicker.vue'
import BaseTable from '@/components/BaseTable/BaseTable.vue'
import BaseModal from '@/components/BaseModal/BaseModal.vue'
import BaseInput from '@/components/BaseInput/BaseInput.vue'
import MoneyInput from '@/components/MoneyInput/MoneyInput.vue'
import type { Column } from '@/components/BaseTable/BaseTable.vue'
import type { Employee, Advance } from '@/types'

const route = useRoute()
const id = computed(() => Number(route.params.id))

const employee = ref<Employee | null>(null)
const advances = ref<Advance[]>([])
const advancesSum = ref(0)
const loading = ref(true)

const showAdvanceModal = ref(false)
const dateRange = ref({ date_from: firstDayOfMonth(), date_to: lastDayOfMonth() })

const advanceForm = ref({
  date: new Date().toISOString().slice(0, 10),
  amount_uzs: 0,
  comment: '',
})

const advanceColumns: Column[] = [
  { key: 'date', label: 'Дата' },
  { key: 'amount_uzs', label: 'Сумма' },
  { key: 'comment', label: 'Комментарий' },
]

const summaryCards = computed(() => {
  if (!employee.value) return []
  const salary = employee.value.monthly_salary_uzs
  const remainder = salary - advancesSum.value

  return [
    { title: 'Oylik (мес)', value: formatUzs(salary) },
    { title: 'Авансы за период', value: formatUzs(advancesSum.value) },
    { title: 'Остаток к выдаче', value: formatUzs(remainder > 0 ? remainder : 0) },
  ]
})

const advancesSummary = computed(() => `Jami avanslar: ${formatUzs(advancesSum.value)}`)

async function loadEmployee() {
  const { data } = await fetchEmployee(id.value)
  employee.value = data
}

async function loadAdvances() {
  const [advRes, sumRes] = await Promise.all([
    fetchAdvances(id.value, { date_from: dateRange.value.date_from, date_to: dateRange.value.date_to }),
    fetchAdvancesSum(id.value, dateRange.value.date_from, dateRange.value.date_to),
  ])

  advances.value = advRes.data
  advancesSum.value = sumRes.data.sum_uzs
}

function openAdvanceModal() {
  advanceForm.value = {
    date: new Date().toISOString().slice(0, 10),
    amount_uzs: 0,
    comment: '',
  }
  showAdvanceModal.value = true
}

async function addAdvance() {
  await createAdvance(id.value, advanceForm.value)
  showAdvanceModal.value = false
  await loadAdvances()
}

async function deleteAdv(row: Advance) {
  if (!confirm('Удалить аванс?')) return
  await deleteAdvance(id.value, row.id)
  await loadAdvances()
}

watch(dateRange, loadAdvances, { deep: true })

onMounted(async () => {
  try {
    await loadEmployee()
    await loadAdvances()
  } finally {
    loading.value = false
  }
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.worker-detail-page {
  &__loading {
    padding: 2rem;
    color: $text-muted;
  }

  &__daterange {
    margin-bottom: 1rem;
  }

  &__table-wrap {
    background: $bg-card;
    border-radius: $radius;
    overflow: hidden;
    box-shadow: $shadow;
  }

  &__table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.25rem;
    border-bottom: 1px solid $border-color;

    h2 {
      margin: 0;
      font-size: 1.1rem;
    }
  }
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style>
