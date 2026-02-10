import { api } from './client'
import type { Company, CompanyTransaction, TransactionDirection } from '@/types'

export function fetchCompanies(params?: { search?: string; is_active?: boolean }) {
  return api.get<Company[]>('/companies', { params })
}

export function createCompany(data: { name: string; is_active?: boolean }) {
  return api.post<Company>('/companies', data)
}

export function fetchCompany(id: number) {
  return api.get<Company>(`/companies/${id}`)
}

export function updateCompany(id: number, data: Partial<{ name: string; is_active: boolean }>) {
  return api.patch<Company>(`/companies/${id}`, data)
}

export function deleteCompany(id: number) {
  return api.delete(`/companies/${id}`)
}

export function fetchTransactions(companyId: number, params?: { date_from?: string; date_to?: string; skip?: number; limit?: number }) {
  return api.get<CompanyTransaction[]>(`/companies/${companyId}/transactions`, { params })
}

export function fetchTransactionsBalance(companyId: number, date_from: string, date_to: string) {
  return api.get<{ balance_uzs: number }>(`/companies/${companyId}/transactions/balance`, { params: { date_from, date_to } })
}

export function createTransaction(companyId: number, data: { date: string; amount_uzs: number; direction: TransactionDirection; comment?: string }) {
  return api.post<CompanyTransaction>(`/companies/${companyId}/transactions`, data)
}

export function deleteTransaction(companyId: number, transactionId: number) {
  return api.delete(`/companies/${companyId}/transactions/${transactionId}`)
}
