import { defineStore } from 'pinia'
import { login as apiLogin } from '@/api/auth'
import type { LoginPayload } from '@/api/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') as string | null,
  }),
  getters: {
    isAuthenticated(): boolean {
      return !!this.token
    },
  },
  actions: {
    setToken(t: string | null) {
      this.token = t
      if (t) localStorage.setItem('token', t)
      else localStorage.removeItem('token')
    },
    async login(payload: LoginPayload) {
      const { data } = await apiLogin(payload)
      this.setToken(data.access_token)
    },
    logout() {
      this.setToken(null)
    },
  },
})
