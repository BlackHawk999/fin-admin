import { defineStore } from 'pinia'
import { getPresetRange, type PresetKey } from '@/utils/date'
import { firstDayOfMonth, lastDayOfMonth } from '@/utils/date'

export type GlobalDatePreset = 'today' | 'month' | 'custom'

export const useGlobalDateStore = defineStore('globalDate', {
  state: () => ({
    preset: 'today' as GlobalDatePreset,
    date_from: getPresetRange('today').date_from,
    date_to: getPresetRange('today').date_to,
  }),
  getters: {
    range(): { date_from: string; date_to: string } {
      return { date_from: this.date_from, date_to: this.date_to }
    },
  },
  actions: {
    setToday() {
      this.preset = 'today'
      const r = getPresetRange('today')
      this.date_from = r.date_from
      this.date_to = r.date_to
    },
    setMonth() {
      this.preset = 'month'
      this.date_from = firstDayOfMonth()
      this.date_to = lastDayOfMonth()
    },
    setCustom(date_from: string, date_to: string) {
      this.preset = 'custom'
      this.date_from = date_from
      this.date_to = date_to
    },
    setFromPreset(key: PresetKey) {
      const r = getPresetRange(key)
      this.date_from = r.date_from
      this.date_to = r.date_to
      if (key === 'today') this.preset = 'today'
      else if (key === 'this_month') this.preset = 'month'
      else this.preset = 'custom'
    },
  },
})
