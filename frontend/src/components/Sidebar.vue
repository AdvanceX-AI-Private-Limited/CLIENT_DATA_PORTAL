<script setup>
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import { useAuth, UserButton } from '@clerk/vue';
import {
	LockClosedIcon,
	LockOpenIcon,
	UserCircleIcon,
	ArrowRightOnRectangleIcon,
	Bars3Icon,
	XMarkIcon,
} from '@heroicons/vue/24/outline';
import { storeToRefs } from "pinia";
import { useSidebarStore } from "@/stores/useSidebar";

const sidebarStore = useSidebarStore();
const { isLocked } = storeToRefs(sidebarStore);

// Toggle lock state
const toggleLock = () => {
    sidebarStore.isLocked = !sidebarStore.isLocked;
};

const isOpen = ref(false);
const route = useRoute();
const openSubmenus = ref({});

// Hover to open but respect lock state
const handleMouseEnter = () => {
	if (!isLocked.value) isOpen.value = true;
};
const handleMouseLeave = () => {
	if (!isLocked.value) isOpen.value = false;
};

// Toggle submenu expansion
const toggleSubmenu = (name) => {
	openSubmenus.value = { [name]: !openSubmenus.value[name] };
};
const isSubmenuOpen = (name) => openSubmenus.value[name] || false;

// Active route highlighting
const isActiveRoute = (path) => route.path === path;
const isSubItemActive = (subLinks) => subLinks.some((subItem) => isActiveRoute(subItem.path));

const logout = () => {
	console.log('User logged out');
};

const props = defineProps({
	navigation: Array,
	require: true,
});

</script>

<template>
	<button @click="isOpen = !isOpen" class="fixed bottom-4 right-4 bg-gray-500 opacity-30 text-white w-12 h-12 rounded-full shadow-lg flex items-center justify-center md:hidden z-50">
		<component :is="isOpen ? XMarkIcon : Bars3Icon" class="w-6 h-6" />
	</button>  
	
	<aside
		:class="[
			isOpen ? 'w-64 left-0' : 'w-16 -left-64',
			'fixed left-0 top-0 h-full bg-black/80 backdrop-blur-xs shadow-md shadow-white/5 text-white transition-all duration-300  overflow-hidden px-3 flex flex-col'
		]"
		@mouseenter="handleMouseEnter"
		@mouseleave="handleMouseLeave"
		>
	
		<!-- Toggle Button + Lock Button -->
		<div class="flex items-center pr-1 mt-1.5">
			<button @click="toggleLock" class="p-1 hover:bg-gray-700 rounded hidden md:block">
				<component :is="isLocked ? LockClosedIcon : LockOpenIcon" class="w-7 h-6" />
			</button>
			<router-link to="/" v-if="isOpen" class="ml-3 text-xl font-bold transition-opacity duration-300">
				AdvanceX&nbsp;AI
			</router-link>
		</div>

		<!-- Sidebar Content -->
		<div class="flex flex-col flex-1 justify-between overflow-y-auto scrollbar-hide">
			<nav class="mt-4 space-y-2 flex-1">
				<div v-for="(item, index) in props.navigation" :key="index">
					<button
						v-if="item.subLinks"
						@click.prevent="toggleSubmenu(item.name)"
						class="flex items-center justify-between p-2 w-full text-gray-300 rounded-md hover:bg-white/10 transition-all duration-300 min-w-0"
						:class="{ 'bg-blue-600 text-white': isActiveRoute(item.path) || isSubItemActive(item.subLinks) }"
					>
						<div class="flex items-center">
							<component :is="item.icon" class="w-6 h-6 min-w-[24px]" />
							<span class="ml-3 transition-opacity whitespace-nowrap overflow-hidden text-ellipsis" :class="{ hidden: !isOpen, block: isOpen }">
								{{ item.name }}
							</span>
						</div>
						<svg
							v-if="isOpen"
							:class="{ 'rotate-180': isSubmenuOpen(item.name) }"
							class="w-4 h-4 transition-transform duration-300 text-gray-400"
							fill="currentColor"
							viewBox="0 0 20 20"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"></path>
						</svg>
					</button>

					<router-link
						v-else
						:to="item.path"
						class="flex items-center p-2 text-gray-300 rounded-md transition-all hover:bg-white/10 duration-300 min-w-0"
						:class="{ 'bg-blue-600 text-white': isActiveRoute(item.path) }"
					>
						<component :is="item.icon" class="w-6 h-6 min-w-[24px]" />
						<span class="ml-3 transition-opacity whitespace-nowrap overflow-hidden text-ellipsis" :class="{ hidden: !isOpen, block: isOpen }">
							{{ item.name }}
						</span>
					</router-link>

					<!-- Animated Submenu -->
					<transition name="expand">
						<div v-if="isSubmenuOpen(item.name) && isOpen" class="ml-4 space-y-1 mt-1 overflow-hidden">
							<router-link
								v-for="(subItem, subIndex) in item.subLinks"
								:key="subIndex"
								:to="subItem.path"
								class="block p-2 text-sm text-gray-300 rounded-md transition-colors hover:bg-gray-700"
								:class="{ 'bg-blue-500 text-white': isActiveRoute(subItem.path) }"
							>
								{{ subItem.name }}
							</router-link>
						</div>
					</transition>
				</div>
			</nav>

			<!-- User Actions & Logout -->
			<div id="userActions" class="pb-4">
				<div class="w-full py-2">
					<div class="flex items-center space-x-3 p-2 rounded-xl bg-gray-900">
						<!-- <UserCircleIcon class="w-8 h-8 text-gray-400" /> -->
						 <UserButton after-sign-out-url="/login"/>
						<div v-if="isOpen" class="overflow-hidden whitespace-nowrap">
							<div class="text-sm font-med">aslam.miya@advancex.ai</div>
						</div>
					</div>
				</div>

				<!-- <div class="w-full py-2">
					<button
						@click="logout"
						class="flex items-center space-x-3 w-full text-md font-medium text-white opacity-85 hover:bg-red-600/50 transition-all duration-300 cursor-pointer bg-red-700 p-2 rounded-xl"
					>
						<ArrowRightOnRectangleIcon class="w-6 h-6 text-white" />
						<span v-if="isOpen">Logout</span>
					</button>
				</div> -->
			</div>
		</div>
	</aside>
</template>


<style scoped>
	/* Expanding animation */
	.expand-enter-active, .expand-leave-active {
	transition: max-height 0.5s ease-out, opacity 0.5s ease-out;
	overflow: hidden;
	}
	.expand-enter-from, .expand-leave-to {
	max-height: 0;
	opacity: 0;
	}
	.expand-enter-to, .expand-leave-from {
	max-height: 500px; /* Adjust if needed */
	opacity: 1;
	}

	.expand-enter-active, .expand-leave-active {
		transition: max-height 0.5s ease-out, opacity 0.5s ease-out;
		overflow: hidden;
	}

	aside {
		box-shadow: inset 0 0 10px rgba(255, 255, 255, 0.1);
	}
	@media (max-width: 768px) {
		aside {
			position: fixed;
			z-index: 50;
			left: -100%;
			width: 60%;
			transition: left 0.3s ease-in-out;
		}

		aside.w-64 {
			left: 0;
		}

		button.fixed {
			z-index: 100;
		}
	}

</style>
