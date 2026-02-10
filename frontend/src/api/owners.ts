import { api } from './client'
import type { Owner } from '@/types'

export function fetchOwners() {
  return api.get<Owner[]>('/owners')
}

export function createOwner(data: { name: string; color_hex?: string }) {
  return api.post<Owner>('/owners', data)
}

export function updateOwner(id: number, data: Partial<{ name: string; color_hex: string }>) {
  return api.patch<Owner>(`/owners/${id}`, data)
}

export function deleteOwner(id: number) {
  return api.delete(`/owners/${id}`)
}
