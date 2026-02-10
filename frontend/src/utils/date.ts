export function today(): string {
  return new Date().toISOString().slice(0, 10)
}

export function yesterday(): string {
  const d = new Date()
  d.setDate(d.getDate() - 1)
  return d.toISOString().slice(0, 10)
}

export function firstDayOfMonth(d: Date = new Date()): string {
  const x = new Date(d.getFullYear(), d.getMonth(), 1)
  return x.toISOString().slice(0, 10)
}

export function lastDayOfMonth(d: Date = new Date()): string {
  const x = new Date(d.getFullYear(), d.getMonth() + 1, 0)
  return x.toISOString().slice(0, 10)
}

export function firstDayOfPrevMonth(): string {
  const d = new Date()
  return firstDayOfMonth(new Date(d.getFullYear(), d.getMonth() - 1))
}

export function lastDayOfPrevMonth(): string {
  const d = new Date()
  return lastDayOfMonth(new Date(d.getFullYear(), d.getMonth() - 1))
}

export function daysAgo(n: number): string {
  const d = new Date()
  d.setDate(d.getDate() - n)
  return d.toISOString().slice(0, 10)
}

export type PresetKey = 'today' | 'yesterday' | 'this_month' | 'last_month' | 'last_30'

export function getPresetRange(preset: PresetKey): { date_from: string; date_to: string } {
  switch (preset) {
    case 'today':
      return { date_from: today(), date_to: today() }
    case 'yesterday':
      return { date_from: yesterday(), date_to: yesterday() }
    case 'this_month':
      return { date_from: firstDayOfMonth(), date_to: lastDayOfMonth() }
    case 'last_month':
      return { date_from: firstDayOfPrevMonth(), date_to: lastDayOfPrevMonth() }
    case 'last_30':
      return { date_from: daysAgo(29), date_to: today() }
    default:
      return { date_from: firstDayOfMonth(), date_to: lastDayOfMonth() }
  }
}
