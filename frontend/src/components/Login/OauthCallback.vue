<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '@/stores/useAuth';

const router = useRouter();
const { setAuthFromApiResponse } = useAuth();

onMounted(async () => {
  try {
    const fullUrl = window.location.href;

    // This makes GET /google/callback?code=XYZ

    // const response = await fetch(`http://localhost:8000/api/v1/auth/google/callback${window.location.search}`, {
    //   method: 'GET',
    //   credentials: 'include'  // Use this only if you're using cookies
    // });
    
    const response = await fetch(`http://35.154.63.163/api/v1/auth/google/callback${window.location.search}`, {
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

    // 🔥 HERE: Call your composable's auth function
    setAuthFromApiResponse(data);

    // Redirect to home or dashboard
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
