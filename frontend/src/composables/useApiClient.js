// src/composables/useget.js
import axios from 'axios'
import config from '@/config'

// Create the axios instance
const get = axios.create({
  baseURL: config.api.baseUrl,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// Function to POST with fallback prefixes if endpoint fails
async function post(endpoint, payload) {
  const prefixes = [
    '', // No prefix
    '/api',
    '/api/v1',
    '/api/v1/dashboard'
  ]

  try {
    // Try the original endpoint first
    const response = await get.post(endpoint, payload)
    return response
  } catch (error) {
    console.warn(`Failed with ${endpoint}, trying fallbacks...`)

    if (error.response && error.response.status === 404) {
      // Try all the fallback prefixes
      for (const prefix of prefixes) {
        try {
          const fullPath = `${prefix}${endpoint}`
          console.log(`Trying fallback: ${fullPath}`)
          const response = await get.post(fullPath, payload)
          console.log(`Success with ${fullPath}`)
          return response
        } catch (prefixError) {
          // Continue trying next prefix
          console.warn(`Failed with fallback ${prefix}${endpoint}`)
        }
      }
    }
    // If all attempts fail, throw the original error
    throw error
  }
}

import * as adminApi from '@/composables/api/adminApi'
import * as dashboardApi from '@/composables/api/dashboardApi'
import * as testApi from '@/composables/api/testApi'

export function useApiEndpoints() {
	return {
		apiEndpoints: {
			// Admin APIs
			fetchAdminUsers: adminApi.fetchAdminUsers,
			createAdminUser: adminApi.createAdminUser,
			updateAdminUser: adminApi.updateAdminUser,
			deleteAdminUser: adminApi.deleteAdminUser,

			// Dashboard APIs
			fetchOutlets: dashboardApi.fetchOutlets,
			createOutlet: dashboardApi.createOutlet,
			updateOutlet: dashboardApi.updateOutlet,
			deleteOutlet: dashboardApi.deleteOutlet,

			// Test APIs
			testApiFunction: testApi.testApiFunction,
		}
	}
}

export default get
export { post }
