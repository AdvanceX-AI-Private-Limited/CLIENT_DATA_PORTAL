<script setup>
import { ref } from 'vue'

const emit = defineEmits(['verified'])

const username = ref('')
const password = ref('')
const userData = ref({})

const handleVerified = (payload) => {
  console.log('Verified credentials:', payload)
  userData.value = payload
  showOtp.value = true
}

const handleLogin = () => {
  if (username.value && password.value) {
    emit('verified', { username: username.value, password: password.value })
  } else {
    alert('Please enter both username and password')
  }
}
</script>

<template>
    <form @submit.prevent="handleLogin" class="space-y-4">
        <div id="authInput">
            <input
            v-model="username"
            type="text"
            placeholder="Username"
            class="w-full px-4 py-2 rounded-3xl border-0 focus:outline-none outline-3 outline-purple-200 focus:ring-3 focus:ring-blue-600 mb-6 h-10.5 font-"
            />
            <input
            v-model="password"
            type="password"
            placeholder="Password"
            class="w-full px-4 py-2 rounded-3xl border-0 focus:outline-none outline-3 outline-purple-200 focus:ring-3 focus:ring-blue-600 h-10.5"
            />
            <div class="text-right mt-2">
            <a href="#" class="text-sm text-blue-600 hover:underline">Forgot Password?</a>
            </div>
        </div>
        <button
            type="submit"
            class="w-full bg-blue-800 text-white py-2.5 rounded-3xl hover:bg-blue-900 transition font-medium"
        >
            Login
        </button>
    </form>
</template>
