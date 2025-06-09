<script setup>
import { useAuth } from '@/stores/useAuth'

const { isSignedIn, loaded } = useAuth()

// Example usage
console.log('Is signed in:', isSignedIn.value, 'Loaded:', loaded.value)
</script>

<template>
    <h1>as</h1>
</template>