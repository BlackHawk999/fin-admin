export interface Employee {
  id: number
  full_name: string
  monthly_salary_uzs: number
  is_active: boolean
}

export interface Advance {
  id: number
  employee_id: number
  date: string
  amount_uzs: number
  comment: string | null
}

export interface Company {
  id: number
  name: string
  is_active: boolean
}

export type TransactionDirection = 'IN' | 'OUT'

export interface CompanyTransaction {
  id: number
  company_id: number
  date: string
  amount_uzs: number
  direction: TransactionDirection
  comment: string | null
}

export interface Cashbox {
  id: number
  name: string
}

export interface DailyCashboxEntry {
  id: number
  cashbox_id: number
  date: string
  amount_uzs: number
  comment: string | null
}

export interface Owner {
  id: number
  name: string
  color_hex: string
}

export type PayerType = 'owner' | 'other'

export interface Expense {
  id: number
  date: string
  amount_uzs: number
  category: string
  comment: string | null
  payer_type: PayerType
  owner_id: number | null
}

export interface DateRange {
  date_from: string
  date_to: string
}
