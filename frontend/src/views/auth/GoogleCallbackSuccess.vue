<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/stores/useAuth'
import { onMounted } from 'vue'

const route = useRoute()
const router = useRouter()
const { setAuthFromApiResponse } = useAuth()

onMounted(() => {
  const encoded = route.query.data
  if (encoded) {
    try {
      const decoded = JSON.parse(atob(encoded))
      if (decoded.session_token) {
        setAuthFromApiResponse(decoded)
        router.replace('/') // Redirect to dashboard/home
      } else {
        // No session token, show error or redirect
        router.replace('/login')
      }
    } catch (e) {
      router.replace('/login')
    }
  } else {
    router.replace('/login')
  }
})
</script>
<template>
  <div>Signing you in with Google...</div>
</template>