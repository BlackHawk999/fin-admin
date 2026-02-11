<template>
  <div class="expenses-page" data-testid="expenses-page">
    <div class="expenses-page__header">
      <h1 class="expenses-page__title">Xarajatlar</h1>

      <div class="expenses-page__actions">
        <button type="button" class="btn btn_primary" @click="openCreate" data-testid="expense-add">
          Xarajat qo'shish
        </button>

        <button
          type="button"
          class="btn btn_secondary"
          :disabled="exporting"
          @click="exportExcel"
          data-testid="expenses-export"
        >
          {{ exporting ? 'Скачивание...' : 'Download Excel' }}
        </button>
      </div>
    </div>

    <div class="expenses-page__filters" data-testid="expenses-filters">
      <!-- DateRangePicker может не пробрасывать attrs, поэтому оборачиваем -->
      <div data-testid="expenses-daterange">
        <DateRangePicker v-model="dateRange" />
      </div>

      <BaseInput
        v-model="filterCategory"
        placeholder="Category"
        class="expenses-page__filter-input"
        data-testid="expenses-filter-category"
      />

      <select v-model="filterPayerType" class="expenses-page__select" data-testid="expenses-filter-payer-type">
        <option value="">Hammasi</option>
        <option value="owner">Boshliqlar</option>
        <option value="other">Boshqalar</option>
      </select>

      <select
        v-if="filterPayerType === 'owner'"
        v-model="filterOwnerId"
        class="expenses-page__select"
        data-testid="expenses-filter-owner"
      >
        <option :value="null">Hamma boshliqlar</option>
        <option v-for="o in owners" :key="o.id" :value="o.id">
          {{ o.name }}
        </option>
      </select>

      <BaseInput
        v-model="filterComment"
        placeholder="Search (comment)"
        class="expenses-page__filter-input"
        data-testid="expenses-filter-comment"
      />
    </div>

    <div v-if="loading" class="expenses-page__table-wrap" data-testid="expenses-loading">
      <SkeletonTable :columns="7" :rows="8" />
    </div>

    <template v-else>
      <div v-if="!expenses.length" class="expenses-page__empty" data-testid="expenses-empty">
        <EmptyState text="Bu vaqtda xarajatlar yo'q">
          <template #action>
            <button type="button" class="btn btn_primary" @click="openCreate" data-testid="expense-add-empty">
              Xarajat qo'shish
            </button>
          </template>
        </EmptyState>
      </div>

      <div v-else class="expenses-page__table-wrap" data-testid="expenses-table-wrap">
        <div data-testid="expenses-table">
          <BaseTable :columns="columns" :data="expenses" row-key="id" :summary="totalFormatted" actions>
            <template #cell="{ column, row, value }">
              <!-- ✅ row может приходить как unknown -->
              <template v-if="column.key === 'amount_uzs'">
                {{ formatUzs(Number(value || 0)) }}
              </template>

              <template v-else-if="column.key === 'payer_type'">
                <template v-if="(row as Expense).payer_type === 'owner'">Owner</template>
                <template v-else>Other</template>
              </template>

              <template v-else-if="column.key === 'owner_id'">
                <template v-if="(row as Expense).owner_id && ownerById((row as Expense).owner_id!)">
                  <span class="expenses-page__owner">
                    <span
                      class="expenses-page__owner-dot"
                      :style="{ background: ownerById((row as Expense).owner_id!)!.color_hex }"
                    />
                    {{ ownerById((row as Expense).owner_id!)!.name }}
                  </span>
                </template>
                <span v-else>—</span>
              </template>

              <template v-else>
                {{ value ?? '—' }}
              </template>
            </template>

            <template #actions="{ row }">
              <button
                type="button"
                class="btn btn_secondary btn_sm"
                @click="editExpense(row as Expense)"
                :data-testid="`expense-edit-${(row as Expense).id}`"
              >
                O'zgartirish
              </button>
              <button
                type="button"
                class="btn btn_danger btn_sm"
                @click="confirmDelete(row as Expense)"
                :data-testid="`expense-delete-${(row as Expense).id}`"
              >
                O'chirish
              </button>
            </template>
          </BaseTable>
        </div>
      </div>

      <p v-if="expenses.length" class="expenses-page__total" data-testid="expenses-total">
        Umumiy shu vaqtda: {{ formatUzs(totalSum) }}
      </p>
    </template>

    <BaseModal
      v-model="showModal"
      :title="editingId ? 'Xarajatni ozgartirish' : 'Yangi xarajat qoshish'"
      data-testid="expense-modal"
    >
      <form class="form" data-testid="expense-form">
        <BaseInput v-model="form.date" label="Sana" type="date" data-testid="expense-date" />
        <MoneyInput v-model="form.amount_uzs" label="Summa" data-testid="expense-amount" />
        <BaseInput v-model="form.category" label="Kategoriya" data-testid="expense-category" />

        <label class="form__label">To'lovchi turi</label>
        <select v-model="form.payer_type" class="form__select" data-testid="expense-payer-type">
          <option value="other">Boshqalar</option>
          <option value="owner">Boshliqlar</option>
        </select>

        <select
          v-if="form.payer_type === 'owner'"
          v-model="form.owner_id"
          class="form__select"
          data-testid="expense-owner"
        >
          <option :value="null">—</option>
          <option v-for="o in owners" :key="o.id" :value="o.id">
            {{ o.name }}
          </option>
        </select>

        <BaseInput v-model="form.comment" label="Izoh" data-testid="expense-comment" />
      </form>

      <template #footer>
        <button type="button" class="btn btn_secondary" @click="closeModal" data-testid="expense-cancel">
          Bekor qilish
        </button>
        <button type="button" class="btn btn_primary" @click="save" :disabled="saving" data-testid="expense-submit">
          {{ saving ? 'Saqlanyabdi...' : 'Saqlash' }}
        </button>
      </template>
    </BaseModal>

    <ConfirmModal
      v-model="showConfirm"
      text="Ushbu xarajat o'chirilsinmi?"
      confirm-label="O'chirish"
      @confirm="doDelete"
      data-testid="expense-confirm"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import DateRangePicker from '@/components/DateRangePicker/DateRangePicker.vue'
import BaseTable from '@/components/BaseTable/BaseTable.vue'
import BaseInput from '@/components/BaseInput/BaseInput.vue'
import MoneyInput from '@/components/MoneyInput/MoneyInput.vue'
import BaseModal from '@/components/BaseModal/BaseModal.vue'
import ConfirmModal from '@/components/ConfirmModal/ConfirmModal.vue'
import EmptyState from '@/components/EmptyState/EmptyState.vue'
import SkeletonTable from '@/components/Skeleton/SkeletonTable.vue'
import type { Column } from '@/components/BaseTable/BaseTable.vue'

import { fetchOwners } from '@/api/owners'
import { downloadExpensesExcel } from '@/api/exports'
import { fetchExpenses, createExpense, updateExpense, deleteExpense } from '@/api/expenses'

import { formatUzs } from '@/utils/format'
import { firstDayOfMonth, lastDayOfMonth } from '@/utils/date'

import { useToastStore } from '@/stores/toastStore'
import type { Expense, Owner } from '@/types'

const toast = useToastStore()

const columns: Column[] = [
  { key: 'date', label: 'Date' },
  { key: 'category', label: 'Category' },
  { key: 'payer_type', label: 'Payer type' },
  { key: 'owner_id', label: 'Owner' },
  { key: 'comment', label: 'Comment' },
  { key: 'amount_uzs', label: 'Amount', tdClass: 'base-table__cell_right' },
]

const loading = ref(true)
const saving = ref(false)
const exporting = ref(false)

const expenses = ref<Expense[]>([])
const owners = ref<Owner[]>([])

const dateRange = ref<{ date_from: string; date_to: string }>({
  date_from: firstDayOfMonth(),
  date_to: lastDayOfMonth(),
})

const filterCategory = ref('')
const filterPayerType = ref<'' | 'owner' | 'other'>('')
const filterOwnerId = ref<number | null>(null)
const filterComment = ref('')

const showModal = ref(false)
const showConfirm = ref(false)

const deleteTarget = ref<Expense | null>(null)
const editingId = ref<number | null>(null)

const form = ref<{
  date: string
  amount_uzs: number
  category: string
  comment: string
  payer_type: 'owner' | 'other'
  owner_id: number | null
}>({
  date: new Date().toISOString().slice(0, 10),
  amount_uzs: 0,
  category: '',
  comment: '',
  payer_type: 'other',
  owner_id: null,
})

const totalSum = computed(() => expenses.value.reduce((s, e) => s + (Number(e.amount_uzs) || 0), 0))
const totalFormatted = computed(() => `Total: ${formatUzs(totalSum.value)}`)

function ownerById(id: number) {
  return owners.value.find((o) => o.id === id)
}

function closeModal() {
  showModal.value = false
  editingId.value = null
}

function openCreate() {
  editingId.value = null
  form.value = {
    date: new Date().toISOString().slice(0, 10),
    amount_uzs: 0,
    category: '',
    comment: '',
    payer_type: 'other',
    owner_id: null,
  }
  showModal.value = true
}

function editExpense(row: Expense) {
  editingId.value = row.id
  form.value = {
    date: row.date,
    amount_uzs: Number(row.amount_uzs || 0),
    category: row.category,
    comment: row.comment || '',
    payer_type: row.payer_type,
    owner_id: row.owner_id ?? null,
  }
  showModal.value = true
}

function confirmDelete(row: Expense) {
  deleteTarget.value = row
  showConfirm.value = true
}

async function doDelete() {
  if (!deleteTarget.value) return
  try {
    await deleteExpense(deleteTarget.value.id)
    toast.success('Расход удалён')
    await load()
  } catch {
    toast.error('Ошибка удаления')
  } finally {
    deleteTarget.value = null
  }
}

async function loadOwners() {
  const { data } = await fetchOwners()
  owners.value = data
}

async function load() {
  loading.value = true
  try {
    const { data } = await fetchExpenses({
      date_from: dateRange.value.date_from,
      date_to: dateRange.value.date_to,
      category: filterCategory.value || undefined,
      owner_id: filterPayerType.value === 'owner' ? filterOwnerId.value ?? undefined : undefined,
      limit: 500,
    })

    let list = data

    if (filterPayerType.value) {
      list = list.filter((e) => e.payer_type === filterPayerType.value)
    }

    const q = filterComment.value.trim().toLowerCase()
    if (q) {
      list = list.filter((e) => (e.comment || '').toLowerCase().includes(q))
    }

    expenses.value = list
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || 'Ошибка загрузки расходов')
    expenses.value = []
  } finally {
    loading.value = false
  }
}

async function save() {
  saving.value = true
  try {
    if (!form.value.date || !form.value.category) {
      toast.error('Заполните дату и категорию')
      return
    }

    if (form.value.payer_type !== 'owner') {
      form.value.owner_id = null
    }

    if (editingId.value) {
      await updateExpense(editingId.value, {
        date: form.value.date,
        amount_uzs: Number(form.value.amount_uzs || 0),
        category: form.value.category,
        comment: form.value.comment || undefined,
        payer_type: form.value.payer_type,
        owner_id: form.value.owner_id,
      })
      toast.success('Расход обновлён')
    } else {
      await createExpense({
        date: form.value.date,
        amount_uzs: Number(form.value.amount_uzs || 0),
        category: form.value.category,
        comment: form.value.comment || undefined,
        payer_type: form.value.payer_type,
        owner_id: form.value.owner_id,
      })
      toast.success('Расход добавлен')
    }

    closeModal()
    await load()
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || 'Ошибка сохранения')
  } finally {
    saving.value = false
  }
}

async function exportExcel() {
  exporting.value = true
  try {
    await downloadExpensesExcel({
      date_from: dateRange.value.date_from,
      date_to: dateRange.value.date_to,
      category: filterCategory.value || undefined,
      owner_id: filterPayerType.value === 'owner' ? filterOwnerId.value ?? undefined : undefined,
    })
    toast.success('Файл скачан')
  } catch {
    toast.error('Ошибка скачивания')
  } finally {
    exporting.value = false
  }
}

watch(filterPayerType, (v) => {
  if (v !== 'owner') filterOwnerId.value = null
})

let t: number | undefined
watch([dateRange, filterCategory, filterPayerType, filterOwnerId], () => load(), { deep: true })

watch(filterComment, () => {
  window.clearTimeout(t)
  t = window.setTimeout(() => load(), 250)
})

onMounted(async () => {
  await loadOwners()
  await load()
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.expenses-page {
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

  &__filters {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-end;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  &__filter-input {
    max-width: 220px;
  }

  &__select {
    padding: 0.5rem 0.75rem;
    border: 1px solid $border-color;
    border-radius: 4px;
    min-width: 140px;
    background: #fff;
  }

  &__table-wrap {
    background: $bg-card;
    border-radius: $radius;
    overflow: hidden;
    box-shadow: $shadow;
  }

  &__empty {
    margin-bottom: 1rem;
  }

  &__total {
    margin: 0.75rem 0 0;
    font-weight: 600;
    font-size: 1rem;
  }

  &__owner {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
  }

  &__owner-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
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
    background: #fff;
  }
}
</style>
