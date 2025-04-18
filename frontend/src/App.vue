<script setup>
import { ref, computed} from "vue";
import Sidebar from '@/components/Sidebar.vue';
import {
	ChartBarIcon,
	CubeIcon,
	CurrencyDollarIcon,
	AdjustmentsHorizontalIcon,
	LockClosedIcon,
	Cog6ToothIcon,
	HomeIcon,
} from '@heroicons/vue/24/outline';
import { storeToRefs } from "pinia";
import { useSidebarStore } from "@/stores/useSidebar"; 
import LoginView from "./views/auth/LoginView.vue";
import { useRoute } from 'vue-router';

const route = useRoute();


const sidebarStore = useSidebarStore();
const { isLocked } = storeToRefs(sidebarStore);

const navigation = [
	{ name: 'Home', path: '/', icon: HomeIcon },
	{
		name: 'Dashboard',
		path: '/dashboard',
		icon: ChartBarIcon,
		subLinks: [
			{ name: 'O2 Dashboard', path: '/dashboard/o2-dashboard' },
			{ name: 'Item Offline Tracker', path: '/dashboard/item-offline-tracker' },
			{ name: 'O2 W/S Dashboard', path: '/dashboard/o2ws-dashboard' }, 
			{ name: 'I/O W/S Dashboard', path: '/dashboard/item-offline-weekly-sales' }
		],
	},
	{ 
		name: 'Brand Management', 
		path: '/brand-management', 
		icon: CubeIcon,
		subLinks: [
			{ name: 'User', path: '/brand-management/user-management' }, 
			{ name: 'Role', path: '/brand-management/role-management' }, 
			{ name: 'Outlet', path: '/brand-management/outlet-management' } 
		]
	},
	{ 
		name: 'Access Management', 
		path: '/access-management', 
		icon: LockClosedIcon,
		subLinks: [
			{ name: 'User to Role Mappings', path: '/access-management/user-to-role-mappings' }, 
			{ name: 'Role to Service Mappings', path: '/access-management/role-to-service-mappings' }, 
			{ name: 'All Mappings', path: '/access-management/all-mappings' } 
		]
	},
	{ name: 'Automation', path: '/automation', icon: AdjustmentsHorizontalIcon },
	{ name: 'Subscriptions', path: '/subscription', icon: CurrencyDollarIcon }, 
	{ name: 'Settings', path: '/settings', icon: Cog6ToothIcon }
];

const hideSidebarRoutes = ['/login'];

const shouldShowSidebar = computed(() => !hideSidebarRoutes.includes(route.path));
console.log(shouldShowSidebar);
</script>

<template>
  <div :class="{ 'min-h-screen flex transition-all duration-300': isLocked, 'min-h-screen': !isLocked }">
    <Sidebar v-if="shouldShowSidebar" :navigation="navigation" />
	<!-- :is-open="isSidebarOpen" -->
    <main :class="[
		isSidebarOpen && !isLocked ? 'ml-64' : 'md:ml-16',
		{
			'transition-all duration-300 flex-1 lg:pl-48': isLocked,
			'transition-all duration-300': !isLocked,
			'ml-0': !shouldShowSidebar 
		}
		]">
		<router-view />
	</main>

  </div>
</template>

