// src/views/auth/LoginView.vue
<script setup>
import MainLogin from "@/components/Login/MainLogin.vue";
import RightImg from "@/components/Login/RightImg.vue";
import { useAuth } from "@/stores/useAuth";
import { useRouter } from "vue-router";

const router = useRouter();
const { isSignedIn } = useAuth();
console.log(isSignedIn.value);
// Handle successful sign in
const handleSignIn = () => {
  // Use router to navigate programmatically
  // API CALL 1
  //     /auth/login
  //      (NEEDS: token_id + user_id + type)
  //      (RETURNS: A URL : challange_id + token_id + user_id + type)
  //     /auth/callback
  // API CALL 2 (NEEDS: challange_id + token_id + user_id + type)
  //     /auth/callback
  // RETURN CALLBACK URL + TOKEN
  // USE TOKEN TO SEND API REQUESTS
  router.push("/");
};
</script>
<template>
  <div class="grid lg:grid-cols-[1.1fr_1.5fr] p-2 h-screen">
    <div>
      <MainLogin />
      <!-- <div class="h-full flex items-center justify-center px-4">
        <div class="max-w-md w-full space-y-6">
          <SignIn 
            :routing="false"
            @sign-in="handleSignIn" 
          />
          </div>
        </div> -->
    </div>
    <div class="hidden lg:block">
      <!-- v-if="!isSignedIn"  -->
      <RightImg />
    </div>
  </div>
  <!-- <div class="p-2 px-5 h-screen flex items-center justify-center">
    <MainLogin />
  </div> -->
</template>
