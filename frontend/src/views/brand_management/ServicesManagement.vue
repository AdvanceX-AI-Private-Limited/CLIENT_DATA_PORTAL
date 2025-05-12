<script setup>
import { ref } from 'vue'
import { sendTestPayload } from '@/composables/api/testApi'

const payload = ref({
  name: 'Aslam'
})

const postResponse = ref(null)
const loading = ref(false)
const error = ref(null)

async function submitTestData() {
  console.log('Submitting test data:', payload.value)
  loading.value = true
  error.value = null

  try {
    const response = await sendTestPayload(payload.value)
    postResponse.value = response.data
    console.log('POST Response:', postResponse.value)
  } catch (err) {
    console.error('Error sending test data:', err)
    error.value = err.message || 'Failed to send'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>

    <h1 class="bg-blue-600">Send Test Data</h1>
    <button @click="submitTestData" :disabled="loading" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition duration-200 ease-in-out">
      {{ loading ? 'Sending...' : 'Send Data' }}
    </button>

    <div v-if="error" class="text-red-500">{{ error }}</div>
    <pre v-else-if="postResponse">{{ postResponse }}</pre>
  </div>
</template>
