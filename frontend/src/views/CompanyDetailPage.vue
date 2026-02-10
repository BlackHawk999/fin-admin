<template>
  <div class="company-detail-page">
    <div class="page-header">
      <h1 class="page-header__title">{{ company?.name || 'Фирма' }}</h1>
      <router-link to="/companies" class="btn btn_secondary">← Ro'yxatga</router-link>
    </div>
    <div v-if="loading" class="company-detail-page__loading">Yuklanyabdi...</div>
    <template v-else-if="company">
      <SummaryCards :cards="summaryCards" />
      <DateRangePicker v-model="dateRange" class="company-detail-page__daterange" />
      <div class="company-detail-page__table-wrap">
        <div class="company-detail-page__table-header">
          <h2>Operatsiyalar</h2>
          <button type="button" class="btn btn_primary btn_sm" @click="openTransactionModal">Qo'shish</button>
        </div>
        <BaseTable :columns="txColumns" :data="transactions" row-key="id" :summary="balanceFormatted" actions>
          <template #cell="{ column, value }">
            <template v-if="column.key === 'amount_uzs'">{{ formatUzs(value) }}</template>
            <template v-else-if="column.key === 'direction'">{{ value === 'IN' ? 'Qabul qilindi' : 'Berildi' }}</template>
            <template v-else>{{ value }}</template>
          </template>
          <template #actions="{ row }">
            <button type="button" class="btn btn_danger btn_sm" @click="deleteTx(row)">O'chirish</button>
          </template>
        </BaseTable>
      </div>
      <BaseModal v-model="showTxModal" title="Yangi operatsiya" @update:model-value="showTxModal = false">
        <form class="form">
          <BaseInput v-model="txForm.date" label="Sana" type="date" />
          <MoneyInput v-model="txForm.amount_uzs" label="Summa" />
          <label class="form__label">Yo'nalish</label>
          <select v-model="txForm.direction" class="form__select">
            <option value="OUT">Berildi (OUT)</option>
            <option value="IN">Olindi (IN)</option>
          </select>
          <BaseInput v-model="txForm.comment" label="Izoh" />
        </form>
        <template #footer>
          <button type="button" class="btn btn_secondary" @click="showTxModal = false">Bekor qilish</button>
          <button type="button" class="btn btn_primary" @click="addTransaction">Qo'shish</button>
        </template>
      </BaseModal>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { fetchCompany, fetchTransactions, fetchTransactionsBalance, createTransaction, deleteTransaction } from '@/api/companies'
import { formatUzs } from '@/utils/format'
import { firstDayOfMonth, lastDayOfMonth } from '@/utils/date'
import SummaryCards from '@/components/SummaryCards/SummaryCards.vue'
import DateRangePicker from '@/components/DateRangePicker/DateRangePicker.vue'
import BaseTable from '@/components/BaseTable/BaseTable.vue'
import BaseModal from '@/components/BaseModal/BaseModal.vue'
import BaseInput from '@/components/BaseInput/BaseInput.vue'
import MoneyInput from '@/components/MoneyInput/MoneyInput.vue'
import type { Column } from '@/components/BaseTable/BaseTable.vue'
import type { Company, CompanyTransaction } from '@/types'
import type { TransactionDirection } from '@/types'

const route = useRoute()
const id = computed(() => Number(route.params.id))
const company = ref<Company | null>(null)
const transactions = ref<CompanyTransaction[]>([])
const balance = ref(0)
const loading = ref(true)
const showTxModal = ref(false)
const dateRange = ref({ date_from: firstDayOfMonth(), date_to: lastDayOfMonth() })
const txForm = ref({
  date: new Date().toISOString().slice(0, 10),
  amount_uzs: 0,
  direction: 'OUT' as TransactionDirection,
  comment: '',
})

const txColumns: Column[] = [
  { key: 'date', label: 'Дата' },
  { key: 'amount_uzs', label: 'Сумма' },
  { key: 'direction', label: 'Направление' },
  { key: 'comment', label: 'Комментарий' },
]

const summaryCards = computed(() => [
  { title: 'Баланс за период', value: formatUzs(balance.value) },
])

const balanceFormatted = computed(() => `Баланс: ${formatUzs(balance.value)}`)

async function loadCompany() {
  const { data } = await fetchCompany(id.value)
  company.value = data
}

async function loadTransactions() {
  const [txRes, balRes] = await Promise.all([
    fetchTransactions(id.value, { date_from: dateRange.value.date_from, date_to: dateRange.value.date_to }),
    fetchTransactionsBalance(id.value, dateRange.value.date_from, dateRange.value.date_to),
  ])
  transactions.value = txRes.data
  balance.value = balRes.data.balance_uzs
}

function openTransactionModal() {
  txForm.value = {
    date: new Date().toISOString().slice(0, 10),
    amount_uzs: 0,
    direction: 'OUT',
    comment: '',
  }
  showTxModal.value = true
}

async function addTransaction() {
  await createTransaction(id.value, txForm.value)
  showTxModal.value = false
  loadTransactions()
}

async function deleteTx(row: CompanyTransaction) {
  if (!confirm('Удалить операцию?')) return
  await deleteTransaction(id.value, row.id)
  loadTransactions()
}

watch(dateRange, loadTransactions, { deep: true })
onMounted(async () => {
  try {
    await loadCompany()
    await loadTransactions()
  } finally {
    loading.value = false
  }
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.company-detail-page {
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

.form__label {
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
}
.form__select {
  padding: 0.5rem 0.75rem;
  border: 1px solid $border-color;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}
</style>
