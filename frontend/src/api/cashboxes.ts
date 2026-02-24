// /frontend/api/cashboxes.ts
import { api } from './client'
import type { Cashbox, DailyCashboxEntry } from '@/types'

export function fetchCashboxes() {
  return api.get<Cashbox[]>('/cashboxes')
}

export function createCashbox(payload: { name: string }) {
  return api.post<Cashbox>('/cashboxes', payload)
}

export function fetchEntries(
  cashboxId: number,
  params?: { date_from?: string; date_to?: string; skip?: number; limit?: number },
) {
  return api.get<DailyCashboxEntry[]>(`/cashboxes/${cashboxId}/entries`, { params })
}

export type CashboxSummary = {
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

export function fetchEntriesSum(cashboxId: number, date_from: string, date_to: string) {
  return api.get<CashboxSummary>(`/cashboxes/${cashboxId}/entries/sum`, {
    params: { date_from, date_to },
  })
}

export type DailyCashboxEntryCreatePayload = {
  cashbox_id: number
  date: string

  cash_in_uzs: number
  card_in_uzs: number
  click_payme_in_uzs: number

  bonus_spent_uzs: number

  cash_exp_company_uzs: number
  cash_exp_other_uzs: number

  comment?: string
}

export function createEntry(payload: DailyCashboxEntryCreatePayload) {
  return api.post<DailyCashboxEntry>('/cashboxes/entries', payload)
}

export type DailyCashboxEntryUpdatePayload = {
  date: string

  cash_in_uzs: number
  card_in_uzs: number
  click_payme_in_uzs: number

  bonus_spent_uzs: number

  cash_exp_company_uzs: number
  cash_exp_other_uzs: number

  comment?: string
  edit_reason: string
}

export function updateEntry(entryId: number, payload: DailyCashboxEntryUpdatePayload) {
  return api.patch<DailyCashboxEntry>(`/cashboxes/entries/${entryId}`, payload)
}