// src/composables/useApiStore.js
import { reactive, toRefs } from 'vue'
import { useApiEndpoints } from './useApiClient'

function capitalize(str) {
	return str.charAt(0).toUpperCase() + str.slice(1)
}

export function useApiStore() {
	const { apiEndpoints } = useApiEndpoints()

	const state = reactive({})

	// Initialize state for each endpoint
	Object.keys(apiEndpoints).forEach(endpoint => {
		state[endpoint] = {
			data: null,
			loading: false,
			error: null,
			lastFetched: null,
			params: null
		}
	})

	async function fetchEndpoint(endpoint, params = {}) {
		const endpointObj = apiEndpoints[endpoint]
		const s = state[endpoint]

		if (s.loading || (s.lastFetched && JSON.stringify(params) === JSON.stringify(s.params))) {
			return
		}

		s.loading = true
		s.error = null
		s.params = params

		try {
			const response = await endpointObj.get(params)
			s.data = response.data
			s.lastFetched = Date.now()
		} catch (error) {
			s.error = error.response?.data || error.message
		} finally {
			s.loading = false
		}
	}

	async function createEndpoint(endpoint, payload) {
		const endpointObj = apiEndpoints[endpoint]
		const s = state[endpoint]

		s.loading = true
		s.error = null

		try {
			const response = await endpointObj.create(payload)
			if (endpointObj.get) {
				await fetchEndpoint(endpoint, s.params)
			}
			return response.data
		} catch (error) {
			s.error = error.response?.data || error.message
			throw error
		} finally {
			s.loading = false
		}
	}

	// Create dynamic fetchX / createX functions
	const actionFns = {}

	Object.keys(apiEndpoints).forEach(endpoint => {
		const endpointObj = apiEndpoints[endpoint]

		if (endpointObj.get) {
			actionFns['fetch' + capitalize(endpoint)] = params => fetchEndpoint(endpoint, params)
		}

		if (endpointObj.create) {
			actionFns['create' + capitalize(endpoint)] = payload => createEndpoint(endpoint, payload)
		}
	})

	return {
		...toRefs(state),
		...actionFns,
		fetchEndpoint,
		createEndpoint
	}
}
