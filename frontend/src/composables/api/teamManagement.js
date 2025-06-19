import get, { post } from '@/composables/useApiClient'

export async function fetchUsers(params) {
  return await get.get('/admin/users/', { params })
}

export async function createUser(data) {
  return await post('/admin/users/', data)
}

export async function updateUser(user_id, params) {
  return await get.put(`/admin/users/${user_id}`, params)
}

export async function deleteUser(user_id) {
  return await get.delete(`/admin/users/${user_id}`)
}