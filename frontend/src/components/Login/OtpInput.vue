<script setup>
import { ref } from 'vue'

const otp = ref('')

const verifyOtp = () => {
  console.log('OTP entered:', otp.value)
  // add your verification logic here
}
</script>

<template>
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
