<!-- src/components/Mapping/AddUsersPopup.vue -->
<script setup>
import { defineProps, defineEmits, ref, computed } from 'vue'

const props = defineProps({
  title: { type: String, default: "" },
  subheading: { type: String, default: "" },
  closeBtnBar: { type: Boolean, default: false },
  action_buttons: { type: Array }
})

const emit = defineEmits(['close'])

function close() {
  emit('close')
}
</script>

<template>
  <div class="fixed inset-0 bg-black/50 flex justify-center items-center z-50 overflow-hidden">
    <div class="bg-white rounded-lg shadow-xl w-[90%] max-w-3xl relative h-[85vh] flex flex-col">
      
      <!-- Header -->
      <div v-if="title || subheading" class="p-4 pb-3 border-b bg-gradient-to-r from-gray-50 to-white">
        <div class="flex justify-between items-center">
          <h2 v-if="title" class="text-lg font-bold text-gray-800">{{ title }}</h2>
          <button @click="close" class="w-6 h-6 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-600 hover:text-gray-800 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <p v-if="subheading" class="text-gray-500 text-xs mt-1">{{ subheading }}</p>
      </div>

      <!-- Body -->
      <div class="flex-1 min-h-0">
        <!-- Add slot content here -->
        <slot />
      </div>

      <!-- Footer -->
      <div class="rounded-b-lg p-3.5 border-t flex items-center gap-2 bg-gray-50" :class="[action_buttons && action_buttons.length ? 'justify-between' : 'justify-end']" v-if="closeBtnBar || (action_buttons && action_buttons.length)">
        <button v-if="closeBtnBar" @click="close" class="text-xs text-gray-700 py-2 px-4 border rounded-lg hover:bg-gray-100 cursor-pointer">Cancel</button>

        <div class="flex gap-2 ml-auto" v-if="action_buttons && action_buttons.length">
          <button
            v-for="(btn, index) in action_buttons"
            :key="index"
            @click="btn.onClick"
            class="text-xs text-white bg-blue-600 hover:bg-blue-700 py-2 px-4 rounded-lg transition-colors"
          >
            {{ btn.name }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
