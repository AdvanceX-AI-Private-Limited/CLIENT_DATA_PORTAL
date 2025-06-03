<script setup>
import { ref } from 'vue'
import OtpInput from '@/components/Login/OtpInput.vue'
import AuthForm from '@/components/Login/AuthForm.vue'

const username = ref('')
const password = ref('')
const showOtp = ref(false)
const userData = ref({})

const login = () => {
  if (username.value && password.value) {
    // console.log('Valid credentials:', username.value, password.value)
    showOtp.value = true
  } else {
    console.log('Please enter both fields')
  }
}

const handleVerified = (payload) => {
  // console.log('Received verified data:', payload)
  userData.value = payload
  showOtp.value = true
}
</script>
<template>
  <div class="h-full flex items-center justify-center px-4">
    <div class="max-w-md w-full space-y-6">
      <div class="text-center mb-9">
        <div class="flex justify-center mb-4">
          <!-- Logo -->
          <div class="rounded-full w-10 h-10 flex items-center justify-center">
            <img src="/public/favicon.ico" alt="Logo">
          </div>
        </div>
        <h2 class="text-3xl font-bold text-gray-900">Welcome Back</h2>
      </div>
      
      <AuthForm v-if="!showOtp" @verified="handleVerified" />
      <OtpInput v-else :user="userData" />

      <div class="flex items-center my-4">
        <div class="flex-grow border-t border-gray-300"></div>
        <span class="mx-2 text-gray-500">OR</span>
        <div class="flex-grow border-t border-gray-300"></div>
      </div>

      <div class="flex justify-between gap-4">
        <button class="w-full flex items-center justify-center gap-2 py-2.5 font-medium rounded-3xl hover:bg-purple-200 bg-purple-100">
          <img src="https://www.svgrepo.com/show/475656/google-color.svg" class="w-5 h-5" />
          Google
        </button>
      </div>

      <p class="text-center text-sm text-gray-500">
        Don’t have an account?
        <a href="/sign-up" class="text-blue-600 hover:underline">Sign Up</a>
      </p>
    </div>
  </div>
</template>

