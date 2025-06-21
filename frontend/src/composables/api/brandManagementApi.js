import get, { post } from '@/composables/useApiClient'

// OUTLET API'S
export async function fetchOutlets(params) {
  return await get.get('/admin/outlets/', { params })
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

// SERVICES API'S
export async function fetchServices(params) {
  return await get.get('/admin/services/', { params })
}

export async function updateService(service_id, payload) {
  console.log("updateService payload: ", service_id, payload);
  return await get.put(`/admin/services/${service_id}`, payload);
}

export async function deleteService(service_id) {
  return await get.delete(`/admin/services/${service_id}`);
}

export async function addService(payload) {
  return await post('/admin/services/', payload);
}