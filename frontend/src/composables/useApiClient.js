// src/composables/useApiClient.js
import axios from 'axios'
import config from '@/config'

const apiClient = axios.create({
	baseURL: config.api.baseUrl,
	headers: {
		'Content-Type': 'application/json',
		'Accept': 'application/json'
	}
})

// Try to detect common API prefixes if direct endpoint fails
async function createWithFallbacks(endpoint, payload) {
	// List of possible prefixes to try
	const prefixes = [
		'', // No prefix
		'/api', 
		'/api/v1',
		'/api/v1/dashboard'
	];

	// Try the first endpoint
	try {
		const response = await apiClient.post(endpoint, payload);
		return response;
	} catch (error) {
		console.log(`Failed with ${endpoint}, trying fallbacks...`);
		
		// If it fails with 404, try other prefixes
		if (error.response && error.response.status === 404) {
			// Try each prefix
			for (const prefix of prefixes) {
				try {
					const fullPath = `${prefix}${endpoint}`;
					console.log(`Trying ${fullPath}...`);
					const response = await apiClient.post(fullPath, payload);
					console.log(`Success with ${fullPath}`);
					return response;
				} catch (prefixError) {
					// Continue to next prefix if this fails
					console.log(`Failed with ${prefix}${endpoint}`);
				}
			}
		}
		
		// If we get here, no fallbacks worked, rethrow the original error
		throw error;
	}
}

const apiEndpoints = {
	users: {
		get: (params) => apiClient.get('/api/v1/admin/users/', { params }),
		create: (payload) => apiClient.post('/api/v1/admin/users/', payload)
	},
	outlets: {
		get: (params) => apiClient.get('/api/v1/admin/outlets/1', { params }),
		create: (payload) => apiClient.post('/api/v1/admin/outlets/1', payload)
	},
	test: {
		// Since the backend doesn't support GET, use a mock response
		get: () => Promise.resolve({ 
			data: { 
				message: "GET method not supported on this endpoint", 
				info: "Your backend only has a POST route for this endpoint",
				request: "get (mock)"
			} 
		}),
		create: (payload) => apiClient.post('/api/v1/dashboard/test', payload)
	},
	test2: {
		get: (params) => apiClient.get('/api/v1/dashboard/test2', { params }),
		create: (payload) => createWithFallbacks('/api/v1/dashboard/test2', payload)
	},
	login: {
		get: () => Promise.resolve({
			data: {
				message: "GET method not supported on this endpoint",
				info: "Your backend only has a POST route for this endpoint",
				request: "get (mock)"
			}
		}),
		create: (payload) => createWithFallbacks('/api/v1/auth/test_login', payload)
	},
}

export function useApiEndpoints() {
	return { apiClient, apiEndpoints }
}
