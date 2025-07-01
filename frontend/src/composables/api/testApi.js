import get, { post } from '@/composables/useApiClient'

// const get = apiClient.get

export async function fetchTestData() {
  return get('/dashboard/test2')
}

export async function sendTestPayload(payload) {
  return post('/dashboard/test', payload)
}

export async function getUsers() {
  return get('/access/user-outlet-mappings/')
}

export async function getOutlets() {
  return get('/dashboard/outlets-data')
}

export async function getServices() {
  return get('/dashboard/services-data')
}

// Mapped Data API
export async function mappedUsersOutlets() {
  return get('/access/user-outlet-mappings/')
}

export async function mappedUsersServices() {
  return get('/dashboard/mapped-users-to-services')
}  

export async function mappedServicesOutlets() {
  return get('/dashboard/mapped-outlets-to-services')
}  

// POST requests of mapping API's
export async function mapUserToOutlet(payload) {
  return post('/dashboard/map-users-to-outlets', payload)
}

export async function mapUserToService(payload) {
  return post('/dashboard/map-users-to-outlets', payload)
}

export async function mapServiceToOutlet(payload) {
  return post('/dashboard/map-users-to-outlets', payload)
}

export async function login_test(payload) {
  return post('/dashboard/login', payload)
}