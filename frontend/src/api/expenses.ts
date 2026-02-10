import { api } from './client'
import type { Expense } from '@/types'

export function fetchExpenses(params?: {
  date_from?: string
  date_to?: string
  category?: string
  owner_id?: number
  skip?: number
  limit?: number
}) {
  return api.get<Expense[]>('/expenses', { params })
}

export function fetchExpensesSum(params: { date_from: string; date_to: string; category?: string; owner_id?: number }) {
  return api.get<{ sum_uzs: number }>('/expenses/sum', { params })
}

export function fetchExpensesByDay(date_from: string, date_to: string) {
  return api.get<{ date: string; total_uzs: number }[]>('/expenses/by-day', { params: { date_from, date_to } })
}

export function fetchExpensesByCategory(date_from: string, date_to: string) {
  return api.get<{ category: string; total_uzs: number }[]>('/expenses/by-category', { params: { date_from, date_to } })
}

export function createExpense(data: {
  date: string
  amount_uzs: number
  category: string
  comment?: string
  payer_type?: 'owner' | 'other'
  owner_id?: number | null
}) {
  return api.post<Expense>('/expenses', data)
}

export function updateExpense(id: number, data: Partial<{ date: string; amount_uzs: number; category: string; comment: string; payer_type: string; owner_id: number | null }>) {
  return api.patch<Expense>(`/expenses/${id}`, data)
}

export function deleteExpense(id: number) {
  return api.delete(`/expenses/${id}`)
}
