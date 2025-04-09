<script setup>
import { ref } from 'vue';
import { Bars3Icon, UserCircleIcon } from '@heroicons/vue/24/outline';

const emit = defineEmits(['toggle-sidebar']);
const showUserDropdown = ref(false);

const logout = () => {
	// Add logout logic
};

const settings = () => {
	// Add settings logic
};
</script>

<template>
	<nav class="fixed top-0 left-0 right-0 h-12 bg-black text-white z-50">
		<div class="flex justify-between items-center h-full px-6">
			<div class="flex items-center space-x-4">
				<button @click="$emit('toggle-sidebar')" class="p-1 hover:bg-gray-700 rounded">
					<Bars3Icon class="w-6 h-6" />
				</button>
				<span class="text-lg sm:text-xl md:text-2xl font-bold">AdvanceX AI</span>
			</div>

      <div class="justify-end flex">
        <div class="mt-2 mx-3 font-extralight text-md hidden lg:block">aslm.miya@advancex.ai</div>
          <div class="relative">
            <button 
              @click="showUserDropdown = !showUserDropdown"
              class="flex items-center space-x-2 hover:bg-gray-900 p-1 rounded-3xl"
            >
              <UserCircleIcon class="w-8 h-8" />
            </button>

            <div 
              v-if="showUserDropdown"
              class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 text-black z-50"
            >
              <button @click="settings" class="block px-4 py-2 w-full text-left hover:bg-gray-100">
                Settings
              </button>
              <button @click="logout" class="block px-4 py-2 w-full text-left hover:bg-gray-100">
                Logout
              </button>
          </div>
        </div>
    </div>
		</div>
	</nav>
</template>
