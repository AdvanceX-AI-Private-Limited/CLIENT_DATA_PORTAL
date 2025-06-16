<script setup>
import { ref } from 'vue'
import { useAuth } from '@/stores/useAuth';
import { verifyOtp } from '@/composables/api/authApi';

const props = defineProps({
  tempToken: { type: String, required: true },
  email: { type: String, required: true },
  isActive: { type: Boolean, required: true }
});

const emit = defineEmits(['otp-success']);

const otp = ref('');
const error = ref('');
const loading = ref(false);
const alreadySent = ref(false);
const message = ref('');
const { setAuthFromApiResponse } = useAuth();

const verifyOtpHandler = async () => {
  error.value = '';
  message.value = '';
  loading.value = true;
  try {
    const payload = { token: props.tempToken, otp: otp.value, is_active: props.isActive };
    const response = await verifyOtp(payload);
    console.log("OtpInput otp send data: ", response.data);
    const data = response.data;
    // Debug: log the full response and otp_already_sent value
    console.log('Full API response:', data);
    console.log('alreadySent from API:', data.otp_already_sent);
    if (data.otp_already_sent) {
      alreadySent.value = data.otp_already_sent;
      console.log('alreadySent ref updated to:', alreadySent.value);
      message.value = data.message || 'An OTP has already been sent to your email. Please check your inbox.';
      return;
    }
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
  <!-- <div v-if="!props.isActive" class="bg-yellow-50 border-l-4 border-yellow-500 text-yellow-800 p-6 rounded-md shadow-md flex flex-col items-center justify-center mt-6">
    <svg class="w-12 h-12 mb-4 text-yellow-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M12 20a8 8 0 100-16 8 8 0 000 16z"/></svg>
    <h2 class="text-xl font-bold mb-2">Account Under Review</h2>
    <p class="text-base text-center">Your account registration was successful.<br>Our team is currently reviewing your application and will contact you soon to activate your account.</p>
  </div> -->
  <div class="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 rounded-md">
    <!-- Debug: show alreadySent value -->
    <!-- <div>alreadySent: {{ alreadySent }}</div> -->
    <p v-if="alreadySent">
      {{ message.value || 'An OTP has already been sent to your email. Please check your inbox.' }}
    </p>
    <p v-else class="text-sm">
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
      :disabled="loading || !otp"
    >
      <span v-if="!loading">Verify OTP</span>
      <span v-else>Verifying...</span>
    </button>
    <div v-if="error" class="text-red-600 text-sm mt-2">{{ error }}</div>
  </div>
</template>
