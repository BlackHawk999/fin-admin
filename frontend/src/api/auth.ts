import { api } from './client'

export interface LoginPayload {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export function login(payload: LoginPayload) {
  return api.post<TokenResponse>('/auth/login', payload)
}
