<template>
  <div class="cashboxes-page" data-testid="cashboxes-page">
    <div class="page-header">
      <h1 class="page-header__title">Кассы</h1>
    </div>

    <DateRangePicker
      v-model="dateRange"
      class="cashboxes-page__daterange"
      data-testid="cashboxes-daterange"
    />

    <div v-if="loading" class="cashboxes-page__loading" data-testid="cashboxes-loading">
      Загрузка...
    </div>

    <template v-else>
      <div
        v-for="cb in cashboxesWithEntries"
        :key="cb.cashbox.id"
        class="cashbox-block"
        :data-testid="`cashbox-block-${cb.cashbox.id}`"
      >
        <div class="cashbox-block__header">
          <h2 class="cashbox-block__title">{{ cb.cashbox.name }}</h2>

          <div class="cashbox-block__summary">
            Итого за период: {{ formatUzs(cb.sum) }}
          </div>

          <button
            type="button"
            class="btn btn_primary btn_sm"
            @click="openCreateModal(cb.cashbox)"
            :data-testid="`cashbox-add-entry-${cb.cashbox.id}`"
          >
            Добавить запись
          </button>
        </div>

        <div :data-testid="`cashbox-table-${cb.cashbox.id}`">
          <BaseTable
            :columns="entryColumns"
            :data="cb.entries"
            row-key="id"
            :summary="`Итого: ${formatUzs(cb.sum)}`"
            actions
          >
            <template #cell="{ column, value }">
              <template v-if="column.key === 'amount_uzs'">
                {{ formatUzs(Number(value || 0)) }}
              </template>
              <template v-else>
                {{ value ?? '—' }}
              </template>
            </template>

            <!-- ✅ НЕЛЬЗЯ УДАЛЯТЬ: только изменить -->
            <template #actions="{ row }">
              <button
                type="button"
                class="btn btn_secondary btn_sm"
                @click="openEditModal(row as DailyCashboxEntry, cb.cashbox)"
                :data-testid="`cashbox-edit-entry-${(row as DailyCashboxEntry).id}`"
              >
                Изменить
              </button>
            </template>
          </BaseTable>
        </div>
      </div>

      <!-- ✅ ОДНА МОДАЛКА ДЛЯ CREATE/EDIT -->
      <BaseModal
        v-model="showEntryModal"
        :title="isEditMode ? 'Редактировать запись' : 'Новая запись в кассу'"
        data-testid="cashbox-entry-modal"
      >
        <form v-if="selectedCashbox" class="form" data-testid="cashbox-entry-form">
          <p class="form__info" data-testid="cashbox-selected-name">
            Касса: {{ selectedCashbox.name }}
          </p>

          <!-- ✅ Старые значения — СНИМОК, не меняется при вводе -->
          <div v-if="isEditMode" class="form__old" data-testid="cashbox-old-values">
            <p class="form__old-title">Старые значения</p>
            <div class="form__old-grid">
              <div data-testid="cashbox-old-date">
                <b>Дата:</b> {{ originalSnapshot.date || '—' }}
              </div>
              <div data-testid="cashbox-old-amount">
                <b>Сумма:</b>
                {{ formatUzs(Number(originalSnapshot.amount_uzs || 0)) }}
              </div>
              <div data-testid="cashbox-old-comment">
                <b>Комментарий:</b> {{ originalSnapshot.comment || '—' }}
              </div>
            </div>
          </div>

          <!-- ✅ Новые значения -->
          <BaseInput
            v-model="form.date"
            :label="isEditMode ? 'Новая дата' : 'Дата'"
            type="date"
            data-testid="entry-date"
          />
          <MoneyInput
            v-model="form.amount_uzs"
            :label="isEditMode ? 'Новая сумма' : 'Сумма'"
            data-testid="entry-amount"
          />
          <BaseInput
            v-model="form.comment"
            :label="isEditMode ? 'Новый комментарий' : 'Комментарий'"
            data-testid="entry-comment"
          />

          <!-- ✅ Причина редактирования ОБЯЗАТЕЛЬНА -->
          <BaseInput
            v-if="isEditMode"
            v-model="editReason"
            label="Причина редактирования (обязательно)"
            placeholder="Например: Ошибка при вводе"
            :error="editReasonError"
            data-testid="entry-edit-reason"
          />
        </form>

        <template #footer>
          <button
            type="button"
            class="btn btn_secondary"
            @click="showEntryModal = false"
            data-testid="entry-cancel"
          >
            Отмена
          </button>

          <button
            type="button"
            class="btn btn_primary"
            :disabled="saving"
            @click="submit"
            data-testid="entry-submit"
          >
            {{
              saving
                ? isEditMode
                  ? 'Сохранение...'
                  : 'Добавление...'
                : isEditMode
                  ? 'Сохранить'
                  : 'Добавить'
            }}
          </button>
        </template>
      </BaseModal>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'

import DateRangePicker from '@/components/DateRangePicker/DateRangePicker.vue'
import BaseTable from '@/components/BaseTable/BaseTable.vue'
import BaseModal from '@/components/BaseModal/BaseModal.vue'
import BaseInput from '@/components/BaseInput/BaseInput.vue'
import MoneyInput from '@/components/MoneyInput/MoneyInput.vue'
import type { Column } from '@/components/BaseTable/BaseTable.vue'

import { fetchCashboxes, fetchEntries, fetchEntriesSum, createEntry, updateEntry } from '@/api/cashboxes'
import { formatUzs } from '@/utils/format'
import { firstDayOfMonth, lastDayOfMonth } from '@/utils/date'
import { useToastStore } from '@/stores/toastStore'
import type { Cashbox, DailyCashboxEntry } from '@/types'

const toast = useToastStore()

const entryColumns: Column[] = [
  { key: 'date', label: 'Дата' },
  { key: 'amount_uzs', label: 'Сумма' },
  { key: 'comment', label: 'Комментарий' },
]

const cashboxes = ref<Cashbox[]>([])
const entriesByCashbox = ref<Record<number, { entries: DailyCashboxEntry[]; sum: number }>>({})
const loading = ref(true)
const saving = ref(false)

const dateRange = ref<{ date_from: string; date_to: string }>({
  date_from: firstDayOfMonth(),
  date_to: lastDayOfMonth(),
})

const showEntryModal = ref(false)
const selectedCashbox = ref<Cashbox | null>(null)

/**
 * ✅ Режимы:
 * - create: editingEntryId = null
 * - edit:   editingEntryId = number
 */
const editingEntryId = ref<number | null>(null)
const isEditMode = computed(() => editingEntryId.value !== null)

/**
 * ✅ Снимок "старых" значений — НЕ меняется при вводе
 */
const originalSnapshot = ref<{ date: string; amount_uzs: number; comment: string }>({
  date: '',
  amount_uzs: 0,
  comment: '',
})

/**
 * ✅ Форма редактирования/создания — меняется пользователем
 */
const form = ref<{ date: string; amount_uzs: number; comment: string }>({
  date: new Date().toISOString().slice(0, 10),
  amount_uzs: 0,
  comment: '',
})

/**
 * ✅ Причина редактирования
 */
const editReason = ref('')
const editReasonError = ref<string | undefined>(undefined)

const cashboxesWithEntries = computed(() =>
  cashboxes.value.map((cashbox) => ({
    cashbox,
    entries: entriesByCashbox.value[cashbox.id]?.entries ?? [],
    sum: entriesByCashbox.value[cashbox.id]?.sum ?? 0,
  })),
)

async function loadCashboxes() {
  const { data } = await fetchCashboxes()
  cashboxes.value = data
}

async function loadEntries() {
  if (!cashboxes.value.length) return

  const result: Record<number, { entries: DailyCashboxEntry[]; sum: number }> = {}

  try {
    await Promise.all(
      cashboxes.value.map(async (cb) => {
        const [entRes, sumRes] = await Promise.all([
          fetchEntries(cb.id, {
            date_from: dateRange.value.date_from,
            date_to: dateRange.value.date_to,
          }),
          fetchEntriesSum(cb.id, dateRange.value.date_from, dateRange.value.date_to),
        ])

        result[cb.id] = {
          entries: entRes.data ?? [],
          sum: Number((sumRes.data as any)?.sum_uzs ?? 0),
        }
      }),
    )

    entriesByCashbox.value = result
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || 'Ошибка загрузки касс')
    entriesByCashbox.value = {}
  }
}

function resetModalState() {
  editingEntryId.value = null
  selectedCashbox.value = null

  originalSnapshot.value = { date: '', amount_uzs: 0, comment: '' }
  form.value = {
    date: new Date().toISOString().slice(0, 10),
    amount_uzs: 0,
    comment: '',
  }

  editReason.value = ''
  editReasonError.value = undefined
}

function openCreateModal(cb: Cashbox) {
  resetModalState()
  selectedCashbox.value = cb
  showEntryModal.value = true
}

function openEditModal(row: DailyCashboxEntry, cb: Cashbox) {
  resetModalState()

  selectedCashbox.value = cb
  editingEntryId.value = row.id

  originalSnapshot.value = {
    date: row.date,
    amount_uzs: Number((row as any).amount_uzs || 0),
    comment: row.comment || '',
  }

  form.value = {
    date: row.date,
    amount_uzs: Number((row as any).amount_uzs || 0),
    comment: row.comment || '',
  }

  showEntryModal.value = true
}

async function submit() {
  if (!selectedCashbox.value) return

  if (isEditMode.value && !editReason.value.trim()) {
    editReasonError.value = 'Причина обязательна'
    toast.error('Укажи причину редактирования')
    return
  }

  saving.value = true
  try {
    if (isEditMode.value && editingEntryId.value !== null) {
      await updateEntry(editingEntryId.value, {
        date: form.value.date,
        amount_uzs: Number(form.value.amount_uzs || 0),
        comment: form.value.comment || undefined,
        edit_reason: editReason.value.trim(),
      })
      toast.success('Запись обновлена')
    } else {
      await createEntry({
        cashbox_id: selectedCashbox.value.id,
        date: form.value.date,
        amount_uzs: Number(form.value.amount_uzs || 0),
        comment: form.value.comment || undefined,
      })
      toast.success('Запись добавлена')
    }

    showEntryModal.value = false
    await loadEntries()
    resetModalState()
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || 'Ошибка сохранения')
  } finally {
    saving.value = false
  }
}

watch(dateRange, loadEntries, { deep: true })

onMounted(async () => {
  loading.value = true
  try {
    await loadCashboxes()
    await loadEntries()
  } finally {
    loading.value = false
  }
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables' as *;

.cashboxes-page {
  &__daterange {
    margin-bottom: 1.5rem;
  }

  &__loading {
    padding: 2rem;
    color: $text-muted;
  }
}

.cashbox-block {
  margin-bottom: 2rem;
  background: $bg-card;
  border-radius: $radius;
  box-shadow: $shadow;
  overflow: hidden;

  &__header {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 1rem;
    padding: 1rem 1.25rem;
    border-bottom: 1px solid $border-color;
  }

  &__title {
    margin: 0;
    font-size: 1.1rem;
  }

  &__summary {
    font-weight: 600;
    margin-left: auto;
  }
}

.form__info {
  margin: 0 0 1rem;
  color: $text-muted;
  font-size: 0.9rem;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form__old {
  padding: 0.75rem;
  border: 1px solid $border-color;
  border-radius: 6px;
  background: #fff;
}

.form__old-title {
  margin: 0 0 0.5rem;
  font-weight: 600;
}

.form__old-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.35rem;
}
</style>
