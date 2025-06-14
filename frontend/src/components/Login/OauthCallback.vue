// src/components/Login/OauthCallback.vue
<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '@/stores/useAuth';
import config from '@/config';

const router = useRouter();
const { setAuthFromApiResponse, isActive } = useAuth();

onMounted(async () => {
  try {
    const response = await fetch(`${config.api.baseUrl}/auth/google/callback${window.location.search}`, {
      method: 'GET',
      credentials: 'include'
    });

    const data = await response.json();

    if (!response.ok) {
      console.error("Login failed:", data);
      alert(data.message || "Google login failed");
      return router.push('/login');
    }

    console.log("Google login response:", data);

    setAuthFromApiResponse(data);

    isActive.value = true;

    router.push('/');
  } catch (err) {
    console.error("OAuth callback error:", err);
    router.push('/login');
  }
});
</script>

<template>
  <div class="text-center mt-20 text-lg">
    Logging you in via Google...
  </div>
</template>
