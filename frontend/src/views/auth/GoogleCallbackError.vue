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
</script>
<template>
  <div>
    <h2>Google Login Error</h2>
    <p>{{ errorMsg }}</p>
    <router-link to="/login">Back to Login</router-link>
  </div>
</template>