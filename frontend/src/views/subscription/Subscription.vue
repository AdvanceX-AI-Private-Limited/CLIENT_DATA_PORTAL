<script setup>
import { ref, onMounted } from 'vue'
import { protectedProfile } from '@/composables/api/authApi'

const profile = ref(null)
const error = ref('')
const loading = ref(true)

onMounted(async () => {
  try {
    const response = await protectedProfile()
    profile.value = response?.data || {}
    console.log("profile", profile.value)
  } catch (e) {
    error.value = e.response?.data?.message || e.message || 'Failed to fetch profile.'
  } finally {
    loading.value = false
  }
})
</script>
<template>
  <h1>Subscriptions</h1>

  <div v-if="loading">Loading...</div>
  <div v-else-if="error" class="text-red-500">{{ error }}</div>
  <div v-else>
    <pre>{{ profile }}</pre>
  </div>
  <br>
  <br>
  <pre>{{ JSON.stringify(profile, null, 2) }}</pre>
</template>
