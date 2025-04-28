<script setup>
import { SignUp } from '@clerk/vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// Handle successful sign up
const handleSignUp = () => {
  // Use router to navigate programmatically
  router.push('/');
};
</script>

<template>
    <div class="flex flex-col items-center justify-center h-screen p-2 px-5">
        <SignUp 
          :routing="false"
          @sign-up="handleSignUp"
        />
    </div>
</template>