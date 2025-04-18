<script setup>
import MainLogin from '@/components/Login/MainLogin.vue';
import RightImg from '@/components/Login/RightImg.vue';
</script>
<template>
	<div class="grid grid-cols-[1.1fr_1.5fr] p-2 h-screen">
    <div class="px-28">
      <MainLogin />
    </div>
    <div class="">
      <RightImg/>
    </div>
  </div>
  <!-- <div class="p-2 px-5 h-screen flex items-center justify-center">
    <MainLogin />
  </div> -->
</template>