import get, { post } from '@/composables/useApiClient'

export async function fetchUsers(params) {
  const skip = params.skip || 0
  const limit = params.limit || 100
  const client_id = params.client_id || null
  return await get('/admin/users/?skip=' + skip + '&limit=' + limit + '&client_id=' + client_id)
}

export async function createUser(data) {
  return await post('/admin/users/', data)
}

export async function updateUser(user_id, params) {
  return await get.put(`/admin/users/${user_id}`, params)
}
    