import { api } from './client'

export interface ExpenseCategory {
  id: number
  name: string
  is_active: boolean
}

export function fetchExpenseCategories(params?: { include_inactive?: boolean }) {
  return api.get<ExpenseCategory[]>('/expense-categories', { params })
}

export function createExpenseCategory(payload: { name: string }) {
  return api.post<ExpenseCategory>('/expense-categories', payload)
}
