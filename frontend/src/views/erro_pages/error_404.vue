<script setup>
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline';
</script>

<template>
<div class="flex flex-col items-center justify-center h-screen text-center px-6">
    <ExclamationTriangleIcon class="w-24 h-24 text-red-500" />
    <h1 class="text-6xl font-extrabold text-gray-800 mt-4">404</h1>
    <p class="text-lg text-gray-600 mt-2">Oops! The page you're looking for doesn't exist.</p>
    <router-link to="/" class="mt-6 bg-blue-600 text-white px-6 py-3 rounded-lg shadow-md text-lg font-medium hover:bg-blue-700">
    Go Home
    </router-link>
</div>
</template>