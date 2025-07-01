import get, { post } from '@/composables/useApiClient'

export async function mappedUsersOutlets(client_id) {
  console.log('client_id', client_id)
  return get(`/access/user-outlet-mappings/?client_id=${client_id}&grouped=true&skip=0&limit=99999`)
}

export async function getOutlets() {
  return get('/access/outlets-data/')
}

export async function getMappedUsers(client_id) {
  return get(`/access/user-outlet-mappings/?client_id=${client_id}&grouped=false&skip=0&limit=99999`)
}

export async function mapUserToOutlet(payload) {
  return post('/access/user-outlet-mappings', payload)
}

export async function unmapUserFromOutlet(mapping_id) {
  return get.delete(`/access/user-outlet-mappings/${mapping_id}`)
}