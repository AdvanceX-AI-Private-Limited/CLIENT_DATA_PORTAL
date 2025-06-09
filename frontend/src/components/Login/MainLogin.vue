<script setup>
import { ref } from 'vue'
import OtpInput from '@/components/Login/OtpInput.vue'
import AuthForm from '@/components/Login/AuthForm.vue'
import { useRouter } from "vue-router";
import { useAuth } from '@/stores/useAuth';

const { setAuthFromApiResponse } = useAuth();

const showOtp = ref(false)
const otpData = ref({ temp_token: '', email: '' })
const router = useRouter();

const handleOtpRequired = ({ temp_token, email }) => {
  otpData.value = { temp_token, email };
  showOtp.value = true;
}

const handleLoginSuccess = () => {
  // Redirect to dashboard or home
  console.log("MainLogin handleLoginSuccess")
  router.push('/');
}

const handleOtpSuccess = () => {
  router.push('/');
}

const handleGoogleLogin = () => {
  window.location.href = 'http://localhost:8000/api/v1/auth/google/login';
  
};
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
      
      <AuthForm 
        v-if="!showOtp" 
        @otp-required="handleOtpRequired" 
        @login-success="handleLoginSuccess" 
      />
      <OtpInput 
        v-else 
        :temp-token="otpData.temp_token" 
        :email="otpData.email" 
        @otp-success="handleOtpSuccess"
      />

      <div class="flex items-center my-4">
        <div class="flex-grow border-t border-gray-300"></div>
        <span class="mx-2 text-gray-500">OR</span>
        <div class="flex-grow border-t border-gray-300"></div>
      </div>

      <div class="flex justify-between gap-4" id="google-login-btn">
        <button @click="handleGoogleLogin" class="w-full flex items-center justify-center gap-2 py-2.5 font-medium rounded-3xl hover:bg-purple-200 bg-purple-100">
          <img src="https://www.svgrepo.com/show/475656/google-color.svg" class="w-5 h-5" />
          Google
        </button>
      </div>

      <p class="text-center text-sm text-gray-500">
        Don't have an account?
        <a href="/sign-up" class="text-blue-600 hover:underline">Sign Up</a>
      </p>
    </div>
  </div>
</template>

