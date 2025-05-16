<script setup>
import { ref } from 'vue'

const otp = ref('')

const verifyOtp = () => {
  console.log('OTP entered:', otp.value)
  // add your verification logic here
}
</script>

<template>
<div class="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 rounded-md">
<p class="text-sm">
  If you already have an account, an OTP will be sent to your email. If not, please visit the <a href="#" class="underline hover:text-green-900">registration page</a>.
</p>
</div>
  <div class="space-y-4">
    <input
    v-model="otp"
    type="text"
    placeholder="Enter OTP"
    class="w-full px-4 py-2 rounded-3xl border-0 focus:outline-none outline-3 outline-purple-200 focus:ring-3 focus:ring-blue-600 mb-6 h-10.5 font-"
    />
    <button
      @click="verifyOtp"
      class="w-full bg-blue-800 text-white py-2.5 rounded-3xl hover:bg-blue-900 transition font-medium"
    >
      Verify OTP
    </button>
  </div>
</template>
