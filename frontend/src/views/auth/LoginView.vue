// src/views/auth/LoginView.vue
<script setup>
import MainLogin from '@/components/Login/MainLogin.vue';
import RightImg from '@/components/Login/RightImg.vue';
import { SignIn } from '@clerk/vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// Handle successful sign in
const handleSignIn = () => {
  // Use router to navigate programmatically
  router.push('/');
};
</script>
<template>
	<div class="grid grid-cols-[1.1fr_1.5fr] p-2 h-screen">
    <div>
      <!-- <MainLogin /> -->
      <div class="h-full flex items-center justify-center px-4">
        <div class="max-w-md w-full space-y-6">
          <SignIn 
            :routing="false"
            @sign-in="handleSignIn" 
          />
          </div>
        </div>
    </div>
    <div class="">
      <RightImg/>
    </div>
  </div>
  <!-- <div class="p-2 px-5 h-screen flex items-center justify-center">
    <MainLogin />
  </div> -->
</template>