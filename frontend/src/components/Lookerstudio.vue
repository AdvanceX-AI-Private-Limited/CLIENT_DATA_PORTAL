<script setup>
const props = defineProps({
    url: String
})

</script>

<template>
	<iframe class="w-full h-[calc(100vh-10px)]" :src="props.url" frameborder="0" style="border:0" allowfullscreen sandbox="allow-storage-access-by-user-activation allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox"></iframe>
</template>