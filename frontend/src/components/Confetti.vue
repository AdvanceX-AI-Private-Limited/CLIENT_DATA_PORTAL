<template>
  <div v-if="showConfetti" class="confetti-container">
    <div
      v-for="n in 50"
      :key="n"
      class="confetti"
      :style="{
        '--fall-delay': `${Math.random() * 3}s`,
        '--fall-duration': `${Math.random() * 3 + 2}s`,
        '--left-pos': `${Math.random() * 100}vw`,
        '--bg-color': `hsl(${Math.random() * 360}, 100%, 50%)`,
        '--size': `${Math.random() * 0.5 + 0.2}rem`
      }"
    />
  </div>
</template>

<script setup>
defineProps({ showConfetti: Boolean });
</script>

<style scoped>
.confetti-container {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 1000;
}
.confetti {
  position: absolute; width: var(--size); height: var(--size);
  background: var(--bg-color); top: -20px; left: var(--left-pos); opacity: 0.8;
  animation:
    fall var(--fall-duration) var(--fall-delay) linear forwards,
    sway 3s ease-in-out infinite alternate;
}
@keyframes fall {
  0% { top: -20px; opacity: 1; }
  100% { top: 100vh; opacity: 0;}
}
@keyframes sway {
  0% { margin-left: -10px; }
  100% { margin-left: 10px; }
}
</style>