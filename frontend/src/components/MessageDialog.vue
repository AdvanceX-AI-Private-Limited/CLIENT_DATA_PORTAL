<template>
  <div v-if="visible" class="fixed inset-0 bg-black/50 flex justify-center items-center z-9999 overflow-hidden">
    <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full">
      <div class="flex items-start mb-4">
        <!-- Success icon -->
        <div v-if="icon === 'success'" class="mr-3 flex-shrink-0 flex items-center justify-center w-10 h-10 rounded-full bg-green-100">
          <svg class="h-6 w-6 text-green-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        
        <!-- Error icon -->
        <div v-else-if="icon === 'error'" class="mr-3 flex-shrink-0 flex items-center justify-center w-10 h-10 rounded-full bg-red-100">
          <svg class="h-6 w-6 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
        
        <!-- Info icon -->
        <div v-else-if="icon === 'info'" class="mr-3 flex-shrink-0 flex items-center justify-center w-10 h-10 rounded-full bg-blue-100">
          <svg class="h-6 w-6 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        
        <!-- Warning icon -->
        <div v-else-if="icon === 'warning'" class="mr-3 flex-shrink-0 flex items-center justify-center w-10 h-10 rounded-full bg-yellow-100">
          <svg class="h-6 w-6 text-yellow-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        
        <div class="flex-1">
          <h3 class="text-lg font-medium text-gray-900">{{ title }}</h3>
          <p class="mt-1 text-sm text-gray-500">{{ message }}</p>
        </div>
      </div>
      
      <div class="flex justify-end">
        <button 
          @click="close" 
          class="px-4 py-2 bg-blue-500 text-white text-sm font-medium rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          OK
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue';

const props = defineProps({
  visible: { type: Boolean, default: false },
  title: { type: String, default: 'Message' },
  message: { type: String, required: true },
  icon: { type: String, default: '' } // 'success', 'error', 'info', 'warning'
});

const emit = defineEmits(['close']);

function close() {
  emit('close');
}
</script> 