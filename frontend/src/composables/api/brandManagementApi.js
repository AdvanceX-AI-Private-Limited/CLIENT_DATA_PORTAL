import get, { post } from '@/composables/useApiClient'

export async function fetchOutlets(params) {
  return await get.get('/admin/outlets/', { params })
}

export async function verifyOtp(payload) {
  return await post('', payload)
}

export async function googleLogin() {
  return await get('')
}