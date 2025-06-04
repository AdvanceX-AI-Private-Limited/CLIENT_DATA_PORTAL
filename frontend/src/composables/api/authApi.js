import get, { post } from '@/composables/useApiClient'

export async function login(payload) {
  return await post('/auth/login', payload)
}

export async function logout() {
  return await post('/auth/logout', {})
}

export async function googleLogin() {
  return await get('/auth/google/login')
}

export async function googleCallback() {
  return await get('/auth/google/callback')
}
