import { api } from './client'
import type { Employee, Advance } from '@/types'

export function fetchEmployees(params?: { search?: string; is_active?: boolean; skip?: number; limit?: number }) {
  return api.get<Employee[]>('/employees', { params })
}

export function createEmployee(data: { full_name: string; monthly_salary_uzs?: number; is_active?: boolean }) {
  return api.post<Employee>('/employees', data)
}

export function fetchEmployee(id: number) {
  return api.get<Employee>(`/employees/${id}`)
}

export function updateEmployee(id: number, data: Partial<{ full_name: string; monthly_salary_uzs: number; is_active: boolean }>) {
  return api.patch<Employee>(`/employees/${id}`, data)
}

export function deleteEmployee(id: number) {
  return api.delete(`/employees/${id}`)
}

export function fetchAdvances(employeeId: number, params?: { date_from?: string; date_to?: string; skip?: number; limit?: number }) {
  return api.get<Advance[]>(`/employees/${employeeId}/advances`, { params })
}

export function fetchAdvancesSum(employeeId: number, date_from: string, date_to: string) {
  return api.get<{ sum_uzs: number }>(`/employees/${employeeId}/advances/sum`, { params: { date_from, date_to } })
}

export function createAdvance(employeeId: number, data: { date: string; amount_uzs: number; comment?: string }) {
  return api.post<Advance>(`/employees/${employeeId}/advances`, data)
}

export function deleteAdvance(employeeId: number, advanceId: number) {
  return api.delete(`/employees/${employeeId}/advances/${advanceId}`)
}
