<script setup>
import { ref } from "vue";
import { EyeIcon, EyeSlashIcon } from "@heroicons/vue/24/outline";
import { login } from "@/composables/api/authApi";
import { useAuth } from "@/stores/useAuth";

const emit = defineEmits(["otp-required", "login-success"]);

const email = ref("");
const password = ref("");
const showPassword = ref(false);

const userData = ref(null);
const loginLoading = ref(false);
const loginError = ref("");
const showError = ref(false);

const { setAuthFromApiResponse, isActive } = useAuth();

const handleLogin = async () => {
  // email.value = "aslam.miya@advancex.ai"
  // password.value = "123@Aslam"
  if (!email.value || !password.value) {
    return;
  }

  loginLoading.value = true;
  loginError.value = "";
  showError.value = false;

  try {
    const payload = { email: email.value, password: password.value };
    const response = await login(payload);
    const data = response.data;
    console.log("response: ", data);

    if (response.status === 200) {
      if (data.is_active === false) {
        isActive.value = false;
        console.log("User is inactive, redirecting to opt login.");
      } else {
        console.log("User is active, proceeding with login.");
      }
    }

    if (data.is_signed_in) {
      setAuthFromApiResponse(data);
      emit("login-success");
    } else if (data.temp_token) {
      emit("otp-required", {
        temp_token: data.temp_token,
        email: email.value,
        is_active: data.is_active,
      });
    } else {
      loginError.value = data.message || "Unknown login error.";
      showError.value = true;
    }
  } catch (error) {
    showError.value = true;
    loginError.value =
      error.response?.data?.message ||
      error.message ||
      "An error occurred. Please try again later.";
    setTimeout(() => {
      showError.value = false;
    }, 3000);
  } finally {
    loginLoading.value = false;
  }
};

const hideError = () => {
  showError.value = false;
};

const handleGoogleLogin = () => {
  window.location.href = "/api/v1/auth/google/login";
};
</script>

<template>
  <form @submit.prevent="handleLogin" class="space-y-4">
    <!-- Error Message -->
    <transition name="fade">
      <div
        v-if="showError"
        class="bg-red-50 border-l-4 border-red-500 p-4 mb-4 rounded shadow-md"
      >
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
              <path
                fill-rule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clip-rule="evenodd"
              />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-red-700">{{ loginError }}</p>
          </div>
          <div class="ml-auto pl-3">
            <div class="-mx-1.5 -my-1.5">
              <button
                type="button"
                @click="hideError"
                class="inline-flex rounded-md p-1.5 text-red-500 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-600"
              >
                <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fill-rule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clip-rule="evenodd"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <div id="authInputEmail">
      <input
        v-model="email"
        type="text"
        placeholder="Email"
        class="w-full px-4 py-2 rounded-3xl border-0 focus:outline-none outline-3 outline-purple-200 focus:ring-3 focus:ring-blue-600 h-10.5 font-"
        :disabled="loginLoading"
      />
    </div>
    <div i
    d="authInputPass" class="relative">
      <input
        v-model="password"
        :type="showPassword ? 'text' : 'password'"
        placeholder="Password"
        class="w-full px-4 py-2 rounded-3xl border-0 focus:outline-none outline-3 outline-purple-200 focus:ring-3 focus:ring-blue-600 h-10.5"
        :disabled="loginLoading"
      />
      <button
        type="button"
        class="absolute right-0.5 top-5.5 -translate-y-1/2 text-gray-400 flex items-center justify-center"
        style="height: 2.5rem; width: 2.5rem;"
        @click="showPassword = !showPassword"
        tabindex="-1"
        aria-label="Toggle password visibility"
      >
        <EyeIcon v-if="!showPassword" class="h-6 w-6" />
        <EyeSlashIcon v-else class="h-6 w-6" />
      </button>
    </div>
    <button
      type="submit"
      class="w-full bg-blue-800 text-white py-2.5 rounded-3xl hover:bg-blue-900 transition font-medium"
      :disabled="loginLoading"
    >
      <span v-if="!loginLoading">Login</span>
      <span v-else>Logging in...</span>
    </button>
  </form>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s, transform 0.5s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
