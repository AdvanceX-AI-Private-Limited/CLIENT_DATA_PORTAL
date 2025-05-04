import apiClient, { post } from '@/composables/useApiClient'

// Example: Fetch list of admin users
export async function fetchAdminUsers() {
  return apiClient.get('/admin/users')
}

// Example: Create a new admin user
export async function createAdminUser(payload) {
  // Using fallback logic in case /admin/users is 404
  return post('/admin/users', payload)
}

// Example: Delete an admin user by ID
export async function deleteAdminUser(userId) {
  return apiClient.delete(`/admin/users/${userId}`)
}

// Example: Update an admin user by ID
export async function updateAdminUser(userId, payload) {
  return apiClient.put(`/admin/users/${userId}`, payload)
}
