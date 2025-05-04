<script setup>
import { ref, onMounted } from 'vue'
import { fetchTestData } from '@/composables/api/testApi'

const testData = ref(null)
const loading = ref(false)
const error = ref(null)

async function loadTestData() {
	loading.value = true
	error.value = null

	try {
		const response = await fetchTestData()
		testData.value = response.data
		console.log('Test Data:', testData.value)
	} catch (err) {
		console.error('Error fetching test data:', err)
		error.value = err.message || 'Failed to fetch'
	} finally {
		loading.value = false
	}
}

onMounted(() => {
	loadTestData()
})
</script>

<template>
	<div>
		<h1>Test Data</h1>
		<div v-if="loading">Loading...</div>
		<div v-else-if="error">{{ error }}</div>
		<pre v-else>{{ testData }}</pre>
	</div>
</template>
