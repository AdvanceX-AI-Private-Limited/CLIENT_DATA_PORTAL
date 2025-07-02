import get, { post } from '@/composables/useApiClient'

export async function getMappedServices() {
  return get(`/access/user-service-mappings/?client_id=${localStorage.getItem("client_id")}&grouped=true&skip=0&limit=99999`)
}

export async function getAllServices() {
  return get(`/admin/services/`)
}

export async function mapUserToService(payload) {
  return post('/access/user-service-mappings', payload)
}

export async function unmapUserFromService(mapping_id) {
  return get.delete(`/access/user-service-mappings/${mapping_id}`)
}
