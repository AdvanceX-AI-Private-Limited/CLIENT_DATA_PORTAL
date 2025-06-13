<script setup>
import { useRoute, useRouter } from 'vue-router'
import { onMounted, ref } from 'vue'

const route = useRoute()
const router = useRouter()
const errorMsg = ref('Google login failed.')

onMounted(() => {
  const encoded = route.query.data
  if (encoded) {
    try {
      const decoded = JSON.parse(atob(encoded))
      errorMsg.value = decoded.message || 'Google login failed.'
    } catch (e) {
      // ignore
    }
  }
})

function goToLogin() {
  router.push('/login')
}
</script>

<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-50">
    <div class="bg-white p-8 rounded-2xl shadow-lg max-w-sm w-full flex flex-col items-center">
      <div class="bg-red-100 rounded-full p-4 mb-4">
        <svg class="w-8 h-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5"
                d="M12 8v4m0 4h.01M21 12c0 4.97-4.03 9-9 9s-9-4.03-9-9 4.03-9 9-9 9 4.03 9 9Z"/>
        </svg>
      </div>
      <h2 class="text-xl font-bold text-red-700 mb-2">Google Login Error</h2>
      <p class="text-gray-600 mb-6">{{ errorMsg }}</p>
      <button
        @click="goToLogin"
        class="bg-red-600 hover:bg-red-700 text-white rounded-md px-6 py-2 font-medium transition focus:outline-none focus:ring focus:ring-red-300"
      >
        Back to Login
      </button>
    </div>
  </div>
</template>