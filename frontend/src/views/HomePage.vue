<template>
  <div class="home-page" data-testid="home-page">
    <div class="home-page__header" data-testid="home-header">
      <h1 class="home-page__title" data-testid="home-title">Home</h1>

      <div class="home-page__actions" data-testid="home-actions">
        <button
          type="button"
          class="btn btn_primary"
          @click="openAddExpense"
          data-testid="home-add-expense"
        >
          Xarajat qo'shish
        </button>

        <button
          type="button"
          class="btn btn_secondary"
          :disabled="exporting"
          @click="exportExcel"
          data-testid="home-export-excel"
        >
          {{ exporting ? 'Скачивание...' : 'Xarajatni yuklash Excel' }}
        </button>
      </div>
    </div>

    <!-- 4 summary cards -->
    <section v-if="loadingSummary" class="home-page__section" data-testid="home-summary-loading">
      <SkeletonCards :count="4" />
    </section>
    <section v-else class="home-page__section" data-testid="home-summary">
      <SummaryCards :cards="summaryCards" />
    </section>

    <!-- Line chart: Expenses by day, 7/30/90 -->
    <section class="home-page__section" data-testid="home-chart-section">
      <div class="home-page__chart-block">
        <div class="home-page__chart-header">
          <h2 class="home-page__chart-title" data-testid="home-chart-title">Kunlik xarajatlar</h2>

          <div class="home-page__chart-toggles" data-testid="home-chart-toggles">
            <button
              v-for="d in chartDaysOptions"
              :key="d"
              type="button"
              class="home-page__chart-toggle"
              :class="{ 'home-page__chart-toggle_active': chartDays === d }"
              @click="setChartDays(d)"
              :data-testid="`home-chart-days-${d}`"
            >
              {{ d }}
            </button>
          </div>
        </div>

        <div v-if="loadingChart" class="home-page__chart-wrap" data-testid="home-chart-loading">
          <Skeleton width="100%" height="240" rounded />
        </div>

        <div v-else-if="byDay.length" class="home-page__chart-wrap" data-testid="home-chart">
          <ExpenseChartByDay :data="byDay" />
        </div>

        <EmptyState v-else text="Нет данных за период" data-testid="home-chart-empty" />
      </div>
    </section>

    <!-- Last 10 expenses -->
    <section class="home-page__section" data-testid="home-last-expenses-section">
      <h2 class="home-page__section-title" data-testid="home-last-expenses-title">Oxirgi 10 ta xarajatlar</h2>

      <div v-if="loadingExpenses" class="home-page__table-wrap" data-testid="home-last-expenses-loading">
        <SkeletonTable :columns="4" :rows="10" />
      </div>

      <div v-else-if="lastExpenses.length" class="home-page__table-wrap" data-testid="home-last-expenses">
        <BaseTable :columns="expenseColumns" :data="lastExpenses" row-key="id">
          <template #cell="{ column, value, row }">
            <template v-if="column.key === 'amount_uzs'">{{ formatUzs(value) }}</template>
            <template v-else-if="column.key === 'payer'">{{ payerLabel(row) }}</template>
            <template v-else>{{ value }}</template>
          </template>
        </BaseTable>
      </div>

      <EmptyState v-else text="Xarajatlar yo'q" data-testid="home-last-expenses-empty" />
    </section>

    <!-- Add Expense modal -->
    <BaseModal
      v-model="showExpenseModal"
      :title="'Yangi xarajat'"
      @update:model-value="showExpenseModal = false"
      data-testid="home-expense-modal"
    >
      <form class="form" data-testid="home-expense-form">
        <BaseInput v-model="expenseForm.date" label="Sana" type="date" data-testid="home-expense-date" />
        <MoneyInput v-model="expenseForm.amount_uzs" label="Summa" data-testid="home-expense-amount" />
        <BaseInput v-model="expenseForm.category" label="Kategoriya" data-testid="home-expense-category" />

        <label class="form__label">To'landi</label>
        <select v-model="expenseForm.payer_type" class="form__select" data-testid="home-expense-payer-type">
          <option value="other">Boshqalar</option>
          <option value="owner">Boshliqlar</option>
        </select>

        <select
          v-if="expenseForm.payer_type === 'owner'"
          v-model="expenseForm.owner_id"
          class="form__select"
          data-testid="home-expense-owner"
        >
          <option :value="null">—</option>
          <option v-for="o in owners" :key="o.id" :value="o.id">{{ o.name }}</option>
        </select>

        <BaseInput v-model="expenseForm.comment" label="Izoh" data-testid="home-expense-comment" />
      </form>

      <template #footer>
        <button
          type="button"
          class="btn btn_secondary"
          @click="showExpenseModal = false"
          data-testid="home-expense-cancel"
        >
          Bekor qilish
        </button>
        <button type="button" class="btn btn_primary" @click="submitExpense" data-testid="home-expense-submit">
          Saqlash
        </button>
      </template>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { fetchDashboardSummary } from '@/api/dashboard'
import { fetchExpensesByDay, fetchExpenses, createExpense } from '@/api/expenses'
import { fetchOwners } from '@/api/owners'
import { downloadExpensesExcel } from '@/api/exports'
import { today, daysAgo } from '@/utils/date'
import { formatUzs } from '@/utils/format'
import type { DashboardSummary } from '@/api/dashboard'

import SummaryCards from '@/components/SummaryCards/SummaryCards.vue'
import BaseTable from '@/components/BaseTable/BaseTable.vue'
import type { Column } from '@/components/BaseTable/BaseTable.vue'
import ExpenseChartByDay from '@/components/ExpenseChartByDay/ExpenseChartByDay.vue'
import SkeletonCards from '@/components/Skeleton/SkeletonCards.vue'
import SkeletonTable from '@/components/Skeleton/SkeletonTable.vue'
import Skeleton from '@/components/Skeleton/Skeleton.vue'
import EmptyState from '@/components/EmptyState/EmptyState.vue'
import BaseModal from '@/components/BaseModal/BaseModal.vue'
import BaseInput from '@/components/BaseInput/BaseInput.vue'
import MoneyInput from '@/components/MoneyInput/MoneyInput.vue'

import { useToastStore } from '@/stores/toastStore'
import type { Expense, Owner } from '@/types'

const toast = useToastStore()

const loadingSummary = ref(true)
const loadingChart = ref(true)
const loadingExpenses = ref(true)
const exporting = ref(false)

const summary = ref<DashboardSummary>({
  expenses_today_uzs: 0,
  expenses_this_month_uzs: 0,
  cashboxes_today_total_uzs: 0,
  companies_out_this_month_uzs: 0,
})

const byDay = ref<{ date: string; total_uzs: number }[]>([])
const lastExpenses = ref<Expense[]>([])
const owners = ref<Owner[]>([])

const chartDays = ref<number>(30)
const chartDaysOptions = [7, 30, 90] as const

const showExpenseModal = ref(false)

const summaryCards = computed(() => [
  { title: 'Bugungi xarajatlar', value: formatUzs(summary.value.expenses_today_uzs) },
  { title: 'Bu oy xarajatlar', value: formatUzs(summary.value.expenses_this_month_uzs) },
  { title: 'Bugungi kassalar jami', value: formatUzs(summary.value.cashboxes_today_total_uzs) },
  { title: 'Bu oyda chiqadigan kompaniyalar', value: formatUzs(summary.value.companies_out_this_month_uzs) },
])

const expenseForm = ref({
  date: today(),
  amount_uzs: 0,
  category: '',
  comment: '',
  payer_type: 'other' as 'owner' | 'other',
  owner_id: null as number | null,
})

const expenseColumns: Column[] = [
  { key: 'date', label: 'Date' },
  { key: 'category', label: 'Category' },
  { key: 'payer', label: 'Payer' },
  { key: 'amount_uzs', label: 'Amount', tdClass: 'base-table__cell_right' },
]

function setChartDays(d: number) {
  chartDays.value = d
}

function payerLabel(row: Expense): string {
  if (row.payer_type === 'owner' && row.owner_id) {
    const o = owners.value.find((x) => x.id === row.owner_id)
    return o ? o.name : '—'
  }
  return 'Other'
}

async function loadSummary() {
  loadingSummary.value = true
  try {
    const { data } = await fetchDashboardSummary()
    summary.value = data
  } catch {
    toast.error('Ошибка загрузки summary')
  } finally {
    loadingSummary.value = false
  }
}

async function loadChart() {
  loadingChart.value = true
  const n = chartDays.value
  const dateFrom = daysAgo(n - 1)
  const dateTo = today()
  try {
    const { data } = await fetchExpensesByDay(dateFrom, dateTo)
    byDay.value = data
  } catch {
    toast.error('Ошибка загрузки графика')
  } finally {
    loadingChart.value = false
  }
}

async function loadLastExpenses() {
  loadingExpenses.value = true
  try {
    const { data } = await fetchExpenses({ limit: 10 })
    lastExpenses.value = data
  } catch {
    toast.error('Ошибка загрузки расходов')
  } finally {
    loadingExpenses.value = false
  }
}

async function loadOwners() {
  try {
    const { data } = await fetchOwners()
    owners.value = data
  } catch {
    toast.error('Ошибка загрузки владельцев')
  }
}

function openAddExpense() {
  expenseForm.value = {
    date: today(),
    amount_uzs: 0,
    category: '',
    comment: '',
    payer_type: 'other',
    owner_id: null,
  }
  showExpenseModal.value = true
}

async function submitExpense() {
  try {
    await createExpense({
      date: expenseForm.value.date,
      amount_uzs: expenseForm.value.amount_uzs,
      category: expenseForm.value.category,
      comment: expenseForm.value.comment || undefined,
      payer_type: expenseForm.value.payer_type,
      owner_id: expenseForm.value.owner_id,
    })
    toast.success('Xarajat qoshildi')
    showExpenseModal.value = false
    loadSummary()
    loadChart()
    loadLastExpenses()
  } catch (e: unknown) {
    toast.error((e as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Xatolik')
  }
}

async function exportExcel() {
  exporting.value = true
  try {
    await downloadExpensesExcel({
      date_from: today(),
      date_to: today(),
    })
    toast.success('Файл yuklandi')
  } catch {
    toast.error('Yuklashda xatolik')
  } finally {
    exporting.value = false
  }
}

watch(chartDays, () => {
  loadChart()
})

onMounted(async () => {
  await loadOwners()
  loadSummary()
  loadChart()
  loadLastExpenses()
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.home-page {
  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  &__title {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 600;
  }

  &__actions {
    display: flex;
    gap: 0.5rem;
  }

  &__section {
    margin-bottom: 2rem;
  }

  &__section-title {
    margin: 0 0 0.75rem;
    font-size: 1.1rem;
    font-weight: 600;
  }

  &__chart-block {
    background: $bg-card;
    padding: 1.25rem;
    border-radius: $radius;
    box-shadow: $shadow;
  }

  &__chart-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin-bottom: 1rem;
  }

  &__chart-title {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
  }

  &__chart-toggles {
    display: flex;
    gap: 0.25rem;
  }

  &__chart-toggle {
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

  &__chart-wrap {
    max-height: 280px;
    padding: 0.5rem 0;
  }

  &__table-wrap {
    background: $bg-card;
    border-radius: $radius;
    overflow: hidden;
    box-shadow: $shadow;
  }
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;

  &__label {
    font-size: 0.875rem;
    font-weight: 500;
  }

  &__select {
    padding: 0.5rem 0.75rem;
    border: 1px solid $border-color;
    border-radius: 4px;
  }
}
</style>
