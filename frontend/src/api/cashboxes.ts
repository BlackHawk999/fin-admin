// /frontend/api/cashboxes.ts
import { api } from './client'
import type { Cashbox, DailyCashboxEntry } from '@/types'

/**
 * Cashboxes
 */
export function fetchCashboxes() {
  return api.get<Cashbox[]>('/cashboxes')
}

export function createCashbox(payload: { name: string }) {
  return api.post('/cashboxes', payload)
}

export function fetchCashbox(id: number) {
  return api.get<Cashbox>(`/cashboxes/${id}`)
}

/**
 * Cashbox entries
 */
export function fetchEntries(
  cashboxId: number,
  params?: {
    date_from?: string
    date_to?: string
    skip?: number
    limit?: number
  }
) {
  return api.get<DailyCashboxEntry[]>(`/cashboxes/${cashboxId}/entries`, {
    params,
  })
}

export function fetchEntriesSum(
  cashboxId: number,
  date_from: string,
  date_to: string
) {
  return api.get<{ sum_uzs: number }>(
    `/cashboxes/${cashboxId}/entries/sum`,
    {
      params: { date_from, date_to },
    }
  )
}

/**
 * Create entry
 */
export function createEntry(data: {
  cashbox_id: number
  date: string
  amount_uzs: number
  comment?: string
}) {
  return api.post<DailyCashboxEntry>('/cashboxes/entries', data)
}

/**
 * ✅ Update entry (PATCH)
 * edit_reason ОБЯЗАТЕЛЕН — иначе backend вернёт 400
 */
export function updateEntry(
  entryId: number,
  data: {
    date: string
    amount_uzs: number
    comment?: string
    edit_reason: string
  }
) {
  return api.patch<DailyCashboxEntry>(
    `/cashboxes/entries/${entryId}`,
    data
  )
}

/**
 * ❌ УДАЛЕНИЕ ЗАПРЕЩЕНО
 * По бизнес-логике кассовые записи не удаляются.
 * Метод намеренно удалён.
 */
