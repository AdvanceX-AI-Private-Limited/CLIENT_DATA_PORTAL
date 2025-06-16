<script setup>
import { ref, onMounted } from 'vue'
import { marked } from 'marked' // or use markdown-it if preferred

const termsHtml = ref('')

onMounted(async () => {
  // Fetch the md file (if in public/ folder, just '/terms.md')
  const response = await fetch('/terms.md');
  const md = await response.text();
  // Convert Markdown to HTML
  termsHtml.value = marked.parse(md);
});
</script>

<template>
  <div>
    <h3 class="text-lg font-medium text-gray-900">Terms and Conditions</h3>
    <div 
      class="bg-gray-50 p-4 text-xs rounded-md border border-gray-200 h-80 overflow-y-auto prose"
      v-html="termsHtml"
    ></div>
  </div>
</template>