// src/components/Auth/AccountReviewNotice.vue
<script setup>
import { logout as apiLogout } from '@/composables/api/authApi';

function deleteCookie(name) {
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
}

function clearAuth() {
    sessionStorage.removeItem('session_token');
    sessionStorage.removeItem('expires_at');
    deleteCookie('session_token');
    deleteCookie('expires_at');
}

async function logout() {
    try {
        await apiLogout();
    } catch (error) {
        console.warn("Logout API failed or returned error, proceeding with frontend logout", error);
    }
    clearAuth(); 
    window.location.href = '/login';
}
</script>
<template>
  <div
    class="mx-auto mt-24 max-w-md bg-white/90
      shadow-lg rounded-2xl border border-yellow-200
      p-10 flex flex-col items-center"
    role="alert"
    aria-live="polite"
  >
    <!-- Animated yellow info icon -->
    <div class="animate-pulse bg-gradient-to-t from-yellow-200/80 to-yellow-100 rounded-full p-6 mb-4">
      <svg 
        class="w-14 h-14 text-yellow-500"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M13 16h-1v-4h-1m1-4h.01M12 20a8 8 0 100-16 8 8 0 000 16z"
        />
      </svg>
    </div>

    <h2 class="text-xl font-extrabold mb-2 text-gray-900 tracking-tight">
      We’re reviewing your account
    </h2>
    <p class="text-base text-gray-700 text-center mb-7 leading-relaxed">
      Thank you for signing up! Your registration was successful and is now under review.
      <span class="block mt-1">
        Our team is verifying your details. You’ll receive an email as soon as your account is activated.
      </span>
    </p>

    <button
      @click="logout()"
      class="w-full inline-flex justify-center px-4 py-2
             bg-yellow-500 hover:bg-yellow-600 text-white rounded-lg
             font-medium transition shadow focus:outline-none focus:ring-2 focus:ring-yellow-400"
    >
      Logout
    </button>
  </div>
</template>