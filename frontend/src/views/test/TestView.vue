<script setup>
import { useAuth } from '@clerk/vue'

const { getToken, isLoaded, isSignedIn, sessionId } = useAuth()

const token = await getToken.value()
// const sessionid = await sessionId.value()
// console.log("Session id: ", sessionid)
console.log("TOKEN", token)
</script>

<template>
    <h1>as</h1>
</template>