import get, { post } from '@/composables/useApiClient'

export async function getMappedOutletServices() {
  return get(`/access/outlet-service-mappings/?client_id=${localStorage.getItem("client_id")}&grouped=true&skip=0&limit=99999`)
}

export async function getAllServices() {
  return get(`/admin/services/`)
}

export async function getAllOutlets() {
  return get(`/admin/outlets/?client_id=${localStorage.getItem("client_id")}&status=all&skip=0&limit=99999`)
}

export async function mapOutletToService(payload) {
  return post('/access/outlet-service-mappings', payload)
}

export async function unmapOutletFromService(mapping_id) {
  return get.delete(`/access/outlet-service-mappings/${mapping_id}`)
}
