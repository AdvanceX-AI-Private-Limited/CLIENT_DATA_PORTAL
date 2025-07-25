<script setup>
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import { useAuth } from '@/stores/useAuth';
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

const { user, logout } = useAuth();

const props = defineProps({
	navigation: Array,
	require: true,
});

const userEmail = localStorage.getItem("email");
</script>

<template>
	<button @click="isOpen = !isOpen" class="fixed bottom-4 right-4 bg-gray-500 opacity-30 text-white w-12 h-12 rounded-full shadow-lg flex items-center justify-center md:hidden z-50">
		<component :is="isOpen ? XMarkIcon : Bars3Icon" class="w-6 h-6" />
	</button>  
	
	<aside
		:class="[
			isOpen ? 'w-64 left-0' : 'w-16 -left-64',
			'fixed left-0 top-0 h-full bg-black/80 backdrop-blur-xs shadow-md shadow-white/5 text-white transition-all duration-300  overflow-hidden px-3 flex flex-col z-[1000]'
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
				<div class="p-3 rounded-xl bg-gray-900 space-y-3">
				
				<!-- Top Row: Icon + Email -->
				<div class="flex items-center space-x-3">
					<UserCircleIcon v-if="!isOpen" class="w-8 h-8 text-gray-400" />
					<div v-if="isOpen" class="overflow-hidden whitespace-nowrap">
					<div class="text-sm font-medium text-white">{{ userEmail }}</div>
					</div>
				</div>

				<!-- Bottom Row: Logout Button -->
				<button
					v-if="isOpen"
					@click="logout"
					class="flex items-center space-x-2 text-sm font-medium text-white bg-red-700 hover:bg-red-600/50 transition-all duration-300 px-3 py-1.5 rounded-lg"
				>
					<ArrowRightOnRectangleIcon class="w-5 h-5 text-white" />
					<span>Logout</span>
				</button>

				</div>
			</div>
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
			z-index: 1000;
			left: -100%;
			width: 60%;
			transition: left 0.3s ease-in-out;
		}

		aside.w-64 {
			left: 0;
		}

		button.fixed {
			z-index: 1001;
		}
	}

</style>
