<script setup>
import { ref, onMounted } from 'vue'
import { protectedProfile } from '@/composables/api/authApi'

const currentUserProfile = ref(null)
const currentUserError = ref('')
const currentUserLoading = ref(true)

onMounted(async () => {
  try {
    const response = await protectedProfile()
    currentUserProfile.value = response?.data || {}
    console.log("currentUserProfile", currentUserProfile.value)
  } catch (e) {
    currentUserError.value = e.response?.data?.message || e.message || 'Failed to fetch currentUserProfile.'
  } finally {
    currentUserLoading.value = false
  }
});
</script>
<template>
  <h1>Subscriptions</h1>

  <div v-if="currentUserLoading">currentUserLoading...</div>
  <div v-else-if="currentUserError" class="text-red-500">{{ currentUserError }}</div>
  <div v-else>
    <pre>{{ currentUserProfile }}</pre>
  </div>
  <br>
  <br>
  <pre>{{ JSON.stringify(currentUserProfile, null, 2) }}</pre>
</template>
