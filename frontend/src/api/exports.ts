import { api } from './client'

export async function downloadExpensesExcel(params: { date_from: string; date_to: string; category?: string; owner_id?: number }) {
  const res = await api.get('/exports/expenses.xlsx', {
    params: {
      date_from: params.date_from,
      date_to: params.date_to,
      category: params.category,
      owner_id: params.owner_id,
    },
    responseType: 'blob',
  })
  const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
  const filename = `expenses_${params.date_from}_to_${params.date_to}.xlsx`
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = filename
  a.click()
  URL.revokeObjectURL(a.href)
}
