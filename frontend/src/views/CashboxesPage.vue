<template>
  <div class="cashboxes-page" data-testid="cashboxes-page">
    <div class="page-header">
      <h1 class="page-header__title">Кассы</h1>

      <button type="button" class="btn btn_primary" @click="openCreateCashboxModal">
        Добавить кассу
      </button>
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
            <div class="summary__row">
              <span>Выручка:</span>
              <b>{{ formatUzs(cb.summary.total_income_uzs) }}</b>
            </div>
            <div class="summary__row">
              <span>Бонусы списано:</span>
              <b>{{ formatUzs(cb.summary.bonus_spent_uzs) }}</b>
            </div>
            <div class="summary__row">
              <span>Чистая продажа:</span>
              <b>{{ formatUzs(cb.summary.net_sales_uzs) }}</b>
            </div>
            <div class="summary__row">
              <span>Расходы (нал):</span>
              <b>{{ formatUzs(cb.summary.cash_exp_total_uzs) }}</b>
            </div>
            <div class="summary__row summary__row--accent">
              <span>Остаток наличных:</span>
              <b>{{ formatUzs(cb.summary.cash_end_uzs) }}</b>
            </div>
          </div>

          <button
            type="button"
            class="btn btn_primary btn_sm"
            @click="openCreateModal(cb.cashbox)"
            :data-testid="`cashbox-add-entry-${cb.cashbox.id}`"
          >
            Закрыть смену
          </button>
        </div>

        <div :data-testid="`cashbox-table-${cb.cashbox.id}`">
          <BaseTable
            :columns="entryColumns"
            :data="cb.entries"
            row-key="id"
            :summary="`Итого (выручка): ${formatUzs(cb.summary.total_income_uzs)}`"
            actions
          >
            <template #cell="{ column, value, row }">
              <template v-if="moneyKeys.has(column.key)">
                {{ formatUzs(Number(value || 0)) }}
              </template>

              <template v-else-if="column.key === 'total_income_uzs'">
                {{ formatUzs(Number((row as DailyCashboxEntryView).total_income_uzs || 0)) }}
              </template>

              <template v-else-if="column.key === 'net_sales_uzs'">
                {{ formatUzs(Number((row as DailyCashboxEntryView).net_sales_uzs || 0)) }}
              </template>

              <template v-else-if="column.key === 'cash_end_uzs'">
                {{ formatUzs(Number((row as DailyCashboxEntryView).cash_end_uzs || 0)) }}
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
                @click="openEditModal(row as DailyCashboxEntryView, cb.cashbox)"
                :data-testid="`cashbox-edit-entry-${(row as DailyCashboxEntryView).id}`"
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
        :title="isEditMode ? 'Редактировать закрытие смены' : 'Закрытие смены'"
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
              <div><b>Дата:</b> {{ originalSnapshot.date || '—' }}</div>

              <div><b>Наличные:</b> {{ formatUzs(originalSnapshot.cash_in_uzs) }}</div>
              <div><b>Карта:</b> {{ formatUzs(originalSnapshot.card_in_uzs) }}</div>
              <div><b>Click/Payme:</b> {{ formatUzs(originalSnapshot.click_payme_in_uzs) }}</div>

              <div><b>Бонусы списано:</b> {{ formatUzs(originalSnapshot.bonus_spent_uzs) }}</div>

              <div><b>Расходы фирмы (нал):</b> {{ formatUzs(originalSnapshot.cash_exp_company_uzs) }}</div>
              <div><b>Прочие расходы (нал):</b> {{ formatUzs(originalSnapshot.cash_exp_other_uzs) }}</div>

              <div class="form__old-wide">
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

          <div class="form__section">
            <p class="form__section-title">Приход</p>

            <MoneyInput
              v-model="form.cash_in_uzs"
              :label="isEditMode ? 'Новые наличные' : 'Наличные'"
              data-testid="entry-cash-in"
            />
            <MoneyInput
              v-model="form.card_in_uzs"
              :label="isEditMode ? 'Новая карта' : 'Карта'"
              data-testid="entry-card-in"
            />
            <MoneyInput
              v-model="form.click_payme_in_uzs"
              :label="isEditMode ? 'Новый Click/Payme' : 'Click/Payme'"
              data-testid="entry-click-in"
            />
          </div>

          <div class="form__section">
            <p class="form__section-title">Бонусы</p>

            <MoneyInput
              v-model="form.bonus_spent_uzs"
              :label="isEditMode ? 'Новые бонусы списано' : 'Бонусы списано'"
              data-testid="entry-bonus-spent"
            />
          </div>

          <div class="form__section">
            <p class="form__section-title">Расходы (только наличные)</p>

            <MoneyInput
              v-model="form.cash_exp_company_uzs"
              :label="isEditMode ? 'Новые расходы фирм (нал)' : 'Расходы фирм (нал)'"
              data-testid="entry-exp-company"
            />
            <MoneyInput
              v-model="form.cash_exp_other_uzs"
              :label="isEditMode ? 'Новые прочие расходы (нал)' : 'Прочие расходы (нал)'"
              data-testid="entry-exp-other"
            />
          </div>

          <BaseInput
            v-model="form.comment"
            :label="isEditMode ? 'Новый комментарий' : 'Комментарий'"
            data-testid="entry-comment"
          />

          <!-- ✅ Итоги (считаем на лету) -->
          <div class="form__totals" data-testid="entry-totals">
            <div class="totals__row">
              <span>Выручка:</span>
              <b>{{ formatUzs(uiTotals.total_income_uzs) }}</b>
            </div>
            <div class="totals__row">
              <span>Чистая продажа (− бонусы):</span>
              <b>{{ formatUzs(uiTotals.net_sales_uzs) }}</b>
            </div>
            <div class="totals__row">
              <span>Расходы (нал):</span>
              <b>{{ formatUzs(uiTotals.cash_exp_total_uzs) }}</b>
            </div>
            <div class="totals__row totals__row--accent">
              <span>Остаток наличных:</span>
              <b>{{ formatUzs(uiTotals.cash_end_uzs) }}</b>
            </div>
          </div>

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
                  : 'Закрытие...'
                : isEditMode
                  ? 'Сохранить'
                  : 'Закрыть смену'
            }}
          </button>
        </template>
      </BaseModal>
    </template>
  </div>

  <!-- Модалка создания кассы -->
  <BaseModal v-model="showCashboxModal" title="Новая касса">
    <form class="form">
      <BaseInput
        v-model="cashboxName"
        label="Название кассы"
        placeholder="Например: Основная касса"
        :error="cashboxNameError"
      />
    </form>

    <template #footer>
      <button type="button" class="btn btn_secondary" @click="showCashboxModal = false">
        Отмена
      </button>
      <button type="button" class="btn btn_primary" :disabled="saving" @click="submitCashbox">
        {{ saving ? 'Создание...' : 'Создать' }}
      </button>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'

import DateRangePicker from '@/components/DateRangePicker/DateRangePicker.vue'
import BaseTable from '@/components/BaseTable/BaseTable.vue'
import BaseModal from '@/components/BaseModal/BaseModal.vue'
import BaseInput from '@/components/BaseInput/BaseInput.vue'
import MoneyInput from '@/components/MoneyInput/MoneyInput.vue'
import type { Column } from '@/components/BaseTable/BaseTable.vue'

import { createCashbox, fetchCashboxes, fetchEntries, fetchEntriesSum, createEntry, updateEntry } from '@/api/cashboxes'
import { formatUzs } from '@/utils/format'
import { firstDayOfMonth, lastDayOfMonth } from '@/utils/date'
import { useToastStore } from '@/stores/toastStore'
import type { Cashbox } from '@/types'

const toast = useToastStore()

/**
 * Локальный тип, чтобы не ломать сборку, если @/types ещё не обновил.
 * Лучше потом обновить @/types/DailyCashboxEntry.
 */
type DailyCashboxEntryView = {
  id: number
  cashbox_id: number
  date: string

  cash_in_uzs: number
  card_in_uzs: number
  click_payme_in_uzs: number

  bonus_spent_uzs: number

  cash_exp_company_uzs: number
  cash_exp_other_uzs: number

  comment?: string | null

  total_income_uzs: number
  net_sales_uzs: number
  cash_exp_total_uzs: number
  cash_end_uzs: number
}

type CashboxSummary = {
  cash_in_uzs: number
  card_in_uzs: number
  click_payme_in_uzs: number
  total_income_uzs: number
  bonus_spent_uzs: number
  net_sales_uzs: number
  cash_exp_company_uzs: number
  cash_exp_other_uzs: number
  cash_exp_total_uzs: number
  cash_end_uzs: number
}

const moneyKeys = new Set([
  'cash_in_uzs',
  'card_in_uzs',
  'click_payme_in_uzs',
  'bonus_spent_uzs',
  'cash_exp_company_uzs',
  'cash_exp_other_uzs',
])

const entryColumns: Column[] = [
  { key: 'date', label: 'Дата' },
  { key: 'cash_in_uzs', label: 'Нал' },
  { key: 'card_in_uzs', label: 'Карта' },
  { key: 'click_payme_in_uzs', label: 'Click/Payme' },
  { key: 'bonus_spent_uzs', label: 'Бонусы' },
  { key: 'cash_exp_company_uzs', label: 'Расх. фирм' },
  { key: 'cash_exp_other_uzs', label: 'Расх. прочие' },
  { key: 'total_income_uzs', label: 'Выручка' },
  { key: 'net_sales_uzs', label: 'Чистая' },
  { key: 'cash_end_uzs', label: 'Ост. нал' },
  { key: 'comment', label: 'Комментарий' },
]

const showCashboxModal = ref(false)
const cashboxName = ref('')
const cashboxNameError = ref<string | undefined>(undefined)

function openCreateCashboxModal() {
  cashboxName.value = ''
  cashboxNameError.value = undefined
  showCashboxModal.value = true
}

const saving = ref(false)

async function submitCashbox() {
  const name = cashboxName.value.trim()
  if (!name) {
    cashboxNameError.value = 'Название обязательно'
    return
  }

  saving.value = true
  try {
    await createCashbox({ name })
    toast.success('Касса создана')

    showCashboxModal.value = false
    await loadCashboxes()
    await loadEntries()
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || 'Ошибка создания кассы')
  } finally {
    saving.value = false
  }
}

const cashboxes = ref<Cashbox[]>([])
const entriesByCashbox = ref<Record<number, { entries: DailyCashboxEntryView[]; summary: CashboxSummary }>>({})
const loading = ref(true)

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

const emptySummary: CashboxSummary = {
  cash_in_uzs: 0,
  card_in_uzs: 0,
  click_payme_in_uzs: 0,
  total_income_uzs: 0,
  bonus_spent_uzs: 0,
  net_sales_uzs: 0,
  cash_exp_company_uzs: 0,
  cash_exp_other_uzs: 0,
  cash_exp_total_uzs: 0,
  cash_end_uzs: 0,
}

/**
 * ✅ Снимок "старых" значений — НЕ меняется при вводе
 */
const originalSnapshot = ref<
  Omit<DailyCashboxEntryView, 'id' | 'cashbox_id' | 'total_income_uzs' | 'net_sales_uzs' | 'cash_exp_total_uzs' | 'cash_end_uzs'>
>({
  date: '',
  cash_in_uzs: 0,
  card_in_uzs: 0,
  click_payme_in_uzs: 0,
  bonus_spent_uzs: 0,
  cash_exp_company_uzs: 0,
  cash_exp_other_uzs: 0,
  comment: '',
})

/**
 * ✅ Форма закрытия смены — меняется пользователем
 */
const form = ref<{
  date: string
  cash_in_uzs: number
  card_in_uzs: number
  click_payme_in_uzs: number
  bonus_spent_uzs: number
  cash_exp_company_uzs: number
  cash_exp_other_uzs: number
  comment: string
}>({
  date: new Date().toISOString().slice(0, 10),
  cash_in_uzs: 0,
  card_in_uzs: 0,
  click_payme_in_uzs: 0,
  bonus_spent_uzs: 0,
  cash_exp_company_uzs: 0,
  cash_exp_other_uzs: 0,
  comment: '',
})

const uiTotals = computed(() => {
  const cashIn = Number(form.value.cash_in_uzs || 0)
  const cardIn = Number(form.value.card_in_uzs || 0)
  const clickIn = Number(form.value.click_payme_in_uzs || 0)
  const bonus = Number(form.value.bonus_spent_uzs || 0)
  const expCompany = Number(form.value.cash_exp_company_uzs || 0)
  const expOther = Number(form.value.cash_exp_other_uzs || 0)

  const totalIncome = cashIn + cardIn + clickIn
  const expTotal = expCompany + expOther

  return {
    total_income_uzs: totalIncome,
    net_sales_uzs: totalIncome - bonus,
    cash_exp_total_uzs: expTotal,
    cash_end_uzs: cashIn - expTotal,
  }
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
    summary: entriesByCashbox.value[cashbox.id]?.summary ?? emptySummary,
  })),
)

async function loadCashboxes() {
  const { data } = await fetchCashboxes()
  cashboxes.value = data
}

async function loadEntries() {
  if (!cashboxes.value.length) return

  const result: Record<number, { entries: DailyCashboxEntryView[]; summary: CashboxSummary }> = {}

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

        const entries = (entRes.data ?? []) as DailyCashboxEntryView[]
        const summary = (sumRes.data ?? emptySummary) as CashboxSummary

        result[cb.id] = { entries, summary }
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

  originalSnapshot.value = {
    date: '',
    cash_in_uzs: 0,
    card_in_uzs: 0,
    click_payme_in_uzs: 0,
    bonus_spent_uzs: 0,
    cash_exp_company_uzs: 0,
    cash_exp_other_uzs: 0,
    comment: '',
  }

  form.value = {
    date: new Date().toISOString().slice(0, 10),
    cash_in_uzs: 0,
    card_in_uzs: 0,
    click_payme_in_uzs: 0,
    bonus_spent_uzs: 0,
    cash_exp_company_uzs: 0,
    cash_exp_other_uzs: 0,
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

function openEditModal(row: DailyCashboxEntryView, cb: Cashbox) {
  resetModalState()

  selectedCashbox.value = cb
  editingEntryId.value = row.id

  originalSnapshot.value = {
    date: row.date,
    cash_in_uzs: Number(row.cash_in_uzs || 0),
    card_in_uzs: Number(row.card_in_uzs || 0),
    click_payme_in_uzs: Number(row.click_payme_in_uzs || 0),
    bonus_spent_uzs: Number(row.bonus_spent_uzs || 0),
    cash_exp_company_uzs: Number(row.cash_exp_company_uzs || 0),
    cash_exp_other_uzs: Number(row.cash_exp_other_uzs || 0),
    comment: row.comment || '',
  }

  form.value = {
    date: row.date,
    cash_in_uzs: Number(row.cash_in_uzs || 0),
    card_in_uzs: Number(row.card_in_uzs || 0),
    click_payme_in_uzs: Number(row.click_payme_in_uzs || 0),
    bonus_spent_uzs: Number(row.bonus_spent_uzs || 0),
    cash_exp_company_uzs: Number(row.cash_exp_company_uzs || 0),
    cash_exp_other_uzs: Number(row.cash_exp_other_uzs || 0),
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

        cash_in_uzs: Number(form.value.cash_in_uzs || 0),
        card_in_uzs: Number(form.value.card_in_uzs || 0),
        click_payme_in_uzs: Number(form.value.click_payme_in_uzs || 0),

        bonus_spent_uzs: Number(form.value.bonus_spent_uzs || 0),

        cash_exp_company_uzs: Number(form.value.cash_exp_company_uzs || 0),
        cash_exp_other_uzs: Number(form.value.cash_exp_other_uzs || 0),

        comment: form.value.comment || undefined,
        edit_reason: editReason.value.trim(),
      })
      toast.success('Смена обновлена')
    } else {
      await createEntry({
        cashbox_id: selectedCashbox.value.id,
        date: form.value.date,

        cash_in_uzs: Number(form.value.cash_in_uzs || 0),
        card_in_uzs: Number(form.value.card_in_uzs || 0),
        click_payme_in_uzs: Number(form.value.click_payme_in_uzs || 0),

        bonus_spent_uzs: Number(form.value.bonus_spent_uzs || 0),

        cash_exp_company_uzs: Number(form.value.cash_exp_company_uzs || 0),
        cash_exp_other_uzs: Number(form.value.cash_exp_other_uzs || 0),

        comment: form.value.comment || undefined,
      })
      toast.success('Смена закрыта')
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
    align-items: flex-start;
    gap: 1rem;
    padding: 1rem 1.25rem;
    border-bottom: 1px solid $border-color;
  }

  &__title {
    margin: 0;
    font-size: 1.1rem;
  }

  &__summary {
    margin-left: auto;
    display: grid;
    gap: 0.25rem;
    min-width: 280px;
  }
}

.summary__row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  font-size: 0.95rem;
}

.summary__row--accent {
  padding-top: 0.25rem;
  border-top: 1px dashed $border-color;
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

.form__section {
  padding: 0.75rem;
  border: 1px solid $border-color;
  border-radius: 8px;
  background: #fff;
  display: grid;
  gap: 0.75rem;
}

.form__section-title {
  margin: 0;
  font-weight: 700;
  font-size: 0.95rem;
}

.form__totals {
  padding: 0.75rem;
  border: 1px solid $border-color;
  border-radius: 8px;
  background: #fff;
  display: grid;
  gap: 0.35rem;
}

.totals__row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.totals__row--accent {
  padding-top: 0.35rem;
  border-top: 1px dashed $border-color;
}

.form__old {
  padding: 0.75rem;
  border: 1px solid $border-color;
  border-radius: 8px;
  background: #fff;
}

.form__old-title {
  margin: 0 0 0.5rem;
  font-weight: 700;
}

.form__old-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.35rem;
}

.form__old-wide {
  padding-top: 0.35rem;
  border-top: 1px dashed $border-color;
}
</style>