/** Формат: 4 000 000 сум (UZS) */
export function formatUzs(value: number): string {
  const s = String(value).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
  return s + ' сум'
}
