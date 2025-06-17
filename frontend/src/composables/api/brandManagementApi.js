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

export async function updateOutlet({ outlet_id, payload }) {
  return await get.put(`/admin/outlets/${outlet_id}`, payload);
}

export async function deleteOutlet(outlet_id) {
  return await get.delete(`/admin/outlets/${outlet_id}`);
}

export async function addOutlet(payload) {
  return await post('/admin/outlets/', payload);
}