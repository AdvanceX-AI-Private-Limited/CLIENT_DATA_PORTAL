<script setup>
import { onMounted, ref } from 'vue'
import { useApiStore } from '@/composables/useApiStore'

const apiStore = useApiStore()
const { outlets, fetchOutlets } = apiStore

const getResponse = ref([])
const error = ref(null)
const loading = ref(false)

async function sendRequests() {
  loading.value = true
  error.value = null
  getResponse.value = []

  try {
    await fetchOutlets()
    const responseData = outlets.value?.data

    // Fix: Make sure it's an array
    if (Array.isArray(responseData)) {
      getResponse.value = responseData
    } else if (responseData && typeof responseData === 'object') {
      getResponse.value = [responseData]
    } else {
      getResponse.value = []
    }

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
  <main>
    <div class="mx-auto p-4 md:p-6 2xl:p-10">
      <!-- Breadcrumb Start -->
      <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h2 class="text-2xl font-semibold text-gray-900">
          Data Tables
        </h2>
        <nav>
          <ol class="flex items-center gap-2">
            <li>
              <a class="font-medium text-gray-600 hover:text-primary" href="index.html">Dashboard /</a>
            </li>
            <li class="font-medium text-primary">Data Tables</li>
          </ol>
        </nav>
      </div>
      <!-- Breadcrumb End -->

      <div class="flex flex-col gap-5 md:gap-7">
        <div class="overflow-x-auto rounded-lg border border-gray-200">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-700">ID</th>
                <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-700">Aggregator</th>
                <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-700">Res ID</th>
                <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-700">Subzone</th>
                <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-700">Shortcode</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 bg-white">
              <tr v-for="(item, index) in getResponse" :key="index">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ item.id }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ item.aggregator }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ item.resid }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ item.subzone }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ item.resshortcode }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="loading" class="p-4 text-center text-sm text-gray-500">Loading...</div>
          <div v-if="error" class="p-4 text-center text-sm text-red-500">{{ error }}</div>
          <div v-if="!loading && getResponse.length === 0 && !error" class="p-4 text-center text-sm text-gray-500">
            No data available
          </div>
        </div>
      </div>
    </div>
  </main>
</template>
