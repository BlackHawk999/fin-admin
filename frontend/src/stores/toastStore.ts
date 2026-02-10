import { defineStore } from 'pinia'

export type ToastType = 'success' | 'error'

export interface Toast {
  id: number
  type: ToastType
  message: string
}

export const useToastStore = defineStore('toast', {
  state: () => ({
    toasts: [] as Toast[],
    nextId: 1,
  }),
  actions: {
    success(message: string) {
      this.add('success', message)
    },
    error(message: string) {
      this.add('error', message)
    },
    add(type: ToastType, message: string) {
      const id = this.nextId++
      this.toasts.push({ id, type, message })
      setTimeout(() => {
        this.remove(id)
      }, 4000)
    },
    remove(id: number) {
      this.toasts = this.toasts.filter((t) => t.id !== id)
    },
  },
})
