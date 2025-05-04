import apiClient, { post } from '@/composables/useApiClient'

// Example: Fetch dashboard statistics
export async function fetchDashboardStats() {
  return apiClient.get('/dashboard/stats')
}

// Example: Fetch dashboard recent activities
export async function fetchRecentActivities() {
  return apiClient.get('/dashboard/activities')
}

// Example: Post a custom dashboard widget
export async function createDashboardWidget(payload) {
  return post('/dashboard/widgets', payload)
}
