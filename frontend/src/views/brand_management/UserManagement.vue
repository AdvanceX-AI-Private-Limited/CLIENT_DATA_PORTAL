<script setup>
import { onMounted, ref } from 'vue'
import { useApiStore } from '@/composables/useApiStore'

const apiStore = useApiStore()
const { test, fetchTest, createTest, test2, fetchTest2 } = apiStore

const response = ref(null)
const getResponse = ref(null)
const error = ref(null)
const loading = ref(false)

async function sendRequests() {
	loading.value = true
	error.value = null
	response.value = null
	getResponse.value = null
	
	try {
		
		// Then make the POST request (this should work)
		// const result = await createTest({ name: 'aslam' })
		// response.value = result
		// console.log('POST response:', result)

        let payload = { name: 'aslam' }
        await fetchTest2(payload=payload)
        getResponse.value = test2.value?.data
        console.log('GET response:', JSON.parse(JSON.stringify(getResponse.value)))

	} catch (err) {
		error.value = err.message || 'Failed to communicate with API'
		console.error('API Error:', err)
	} finally {
		loading.value = false
	}
}

onMounted(() => {
	sendRequests()
})
</script>

<template>
	<h1>User Management</h1>

	<div v-if="error" class="error">
		<h3>Error</h3>
		<p>{{ error }}</p>
		<button @click="sendRequests">Retry</button>
	</div>
</template>
