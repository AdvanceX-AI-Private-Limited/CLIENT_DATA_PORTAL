<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth, isActive } from '@/stores/useAuth';

const router = useRouter();
const { setAuthFromApiResponse } = useAuth();

onMounted(async () => {
  try {
    const fullUrl = window.location.href;

    // This makes GET /google/callback?code=XYZ

    // const response = await fetch(`http://localhost:8000/api/v1/auth/google/callback${window.location.search}`, {
    //   method: 'GET',
    //   credentials: 'include'
    // });
    
    const response = await fetch(`https://client.advancex.ai/api/v1/auth/google/callback${window.location.search}`, {
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
