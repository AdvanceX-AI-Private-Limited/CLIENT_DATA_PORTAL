<script setup>
import { ref } from 'vue'
import { useApiEndpoints } from '@/composables/useApiClient'

const { apiEndpoints } = useApiEndpoints()
const emit = defineEmits(['verified'])

const email = ref('')
const userData = ref({})
const error = ref('')
const showError = ref(false)

const handleLogin = async() => {
  if (!email.value) {
    alert('Please enter email')
    return
  }
  
  // Reset error state before each attempt
  error.value = ''
  showError.value = false
  
  try{
    const response = await apiEndpoints.login.create({email: email.value})
    userData.value = response.data
    // console.log('User data:', response.data)
    emit('verified', { email: email.value})
  }catch (error){
    console.error('API Error:', error)
    if (error.response && error.response.status === 401) {
      showError.value = true
      error.value = 'Unauthorized: Please check your email and try again'
    } else {
      showError.value = true
      error.value = 'An error occurred. Please try again later.'
    }
  }
}

// Auto-hide error message after 5 seconds
const hideError = () => {
  showError.value = false
}
</script>

<template>
    <form @submit.prevent="handleLogin" class="space-y-4">
        <!-- Error Message -->
        <transition name="fade">
            <div v-if="showError" class="bg-red-50 border-l-4 border-red-500 p-4 mb-4 rounded shadow-md">
                <div class="flex items-center">
                    <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm text-red-700">Unauthorized</p>
                    </div>
                    <div class="ml-auto pl-3">
                        <div class="-mx-1.5 -my-1.5">
                            <button type="button" @click="hideError" class="inline-flex rounded-md p-1.5 text-red-500 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-600">
                                <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </transition>

        <div id="authInput">
            <input
            v-model="email"
            type="text"
            placeholder="Email"
            class="w-full px-4 py-2 rounded-3xl border-0 focus:outline-none outline-3 outline-purple-200 focus:ring-3 focus:ring-blue-600 mb-6 h-10.5 font-"
            />
        </div>
        <button
            type="submit"
            class="w-full bg-blue-800 text-white py-2.5 rounded-3xl hover:bg-blue-900 transition font-medium"
        >
            Login
        </button>
    </form>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s, transform 0.5s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
