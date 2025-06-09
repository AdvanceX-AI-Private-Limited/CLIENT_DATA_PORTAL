<script setup>
import { ref } from 'vue'
import { useAuth } from '@/stores/useAuth';
import { verifyOtp } from '@/composables/api/authApi';

const props = defineProps({
  tempToken: { type: String, required: true },
  email: { type: String, required: true }
});

const emit = defineEmits(['otp-success']);

const otp = ref('');
const error = ref('');
const loading = ref(false);
const { setAuthFromApiResponse } = useAuth();

const verifyOtpHandler = async () => {
  error.value = '';
  loading.value = true;
  try {
    const payload = { token: props.tempToken, otp: otp.value };
    const response = await verifyOtp(payload);
    console.log("OtpInput otp send data: ", response.data);
    const data = response.data;
    if (data.session_token) {
      setAuthFromApiResponse(data);
      emit('otp-success');
    } else {
      error.value = data.message || 'OTP verification failed.';
    }
  } catch (e) {
    error.value = e.response?.data?.message || e.message || 'OTP verification failed.';
  } finally {
    loading.value = false;
  }
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
    :disabled="loading"
    />
    <button
      @click="verifyOtpHandler"
      class="w-full bg-blue-800 text-white py-2.5 rounded-3xl hover:bg-blue-900 transition font-medium"
      :disabled="loading"
    >
      <span v-if="!loading">Verify OTP</span>
      <span v-else>Verifying...</span>
    </button>
    <div v-if="error" class="text-red-600 text-sm mt-2">{{ error }}</div>
  </div>
</template>
