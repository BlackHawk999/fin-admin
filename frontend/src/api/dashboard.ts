import { api } from './client'

export interface DashboardSummary {
  expenses_today_uzs: number
  expenses_this_month_uzs: number
  cashboxes_today_total_uzs: number
  companies_out_this_month_uzs: number
}

export function fetchDashboardSummary() {
  return api.get<DashboardSummary>('/dashboard/summary')
}
