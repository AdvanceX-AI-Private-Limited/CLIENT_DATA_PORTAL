<script setup>
import { ref, computed, onMounted, watchEffect } from "vue";
import Sidebar from '@/components/Sidebar.vue';
import {
	ChartBarIcon,
	CubeIcon,
	CurrencyDollarIcon,
	AdjustmentsHorizontalIcon,
	LockClosedIcon,
	Cog6ToothIcon,
	HomeIcon,
	LinkIcon,
} from '@heroicons/vue/24/outline';
import { storeToRefs } from "pinia";
import { useSidebarStore } from "@/stores/useSidebar"; 
import LoginView from "./views/auth/LoginView.vue";
import { useRoute, useRouter } from 'vue-router';
import { useAuth, ClerkLoaded, useUser } from '@clerk/vue';
import { setAuthState } from '@/router';

const isSidebarOpen = ref(false)
const route = useRoute();
const router = useRouter();
const { isSignedIn, isLoaded } = useAuth();

// For debugging
watchEffect(() => {
  if (isLoaded.value) {
    // console.log('Clerk authentication loaded, isSignedIn:', isSignedIn.value);
    // console.log('Current route:', route.path);
  }
});

// Track previous auth state to avoid unnecessary redirects
let previousAuthState = null;

// Initialize the auth state once when component is mounted
onMounted(() => {
  // Use watchEffect within onMounted to handle async loading of Clerk
  const stopWatcher = watchEffect(() => {
    if (isLoaded.value) {
    //   console.log('Component mounted and Clerk loaded, setting initial auth state:', isSignedIn.value);
      previousAuthState = isSignedIn.value;
      setAuthState(isSignedIn.value);
      // Stop this watcher once it's executed
      stopWatcher();
    }
  });
});

// Watch for changes in authentication state and update the router's global state
watchEffect(() => {
  if (isLoaded.value) {
    // Always update the global auth state
    setAuthState(isSignedIn.value);
    
    // Set or remove authentication token in storage
    if (isSignedIn.value) {
      localStorage.setItem('auth-token', 'true');
    } else {
      localStorage.removeItem('auth-token');
    }
    
    // Only redirect if auth state actually changes from a previous known state 
    // AND this isn't the initial load (previousAuthState will be non-null after onMounted)
    if (previousAuthState !== null && previousAuthState !== isSignedIn.value) {
      previousAuthState = isSignedIn.value;
      
      // Handle current route based on new auth state
      const currentPath = route.path;
      const publicRoutes = ['/login', '/sign-up'];
      const isPublicRoute = publicRoutes.includes(currentPath);
      
      // Redirect if needed based on auth state change
      if (isSignedIn.value && isPublicRoute) {
        router.push('/');
      } else if (!isSignedIn.value && !isPublicRoute) {
        router.push('/login');
      }
    }
  }
});

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
		name: 'Mappings',
		path: '/mappings',
		icon: LinkIcon,
		subLinks: [
			{ name: 'User to Outlet', path: '/mappings/user-to-outlet-mappings' },
			{ name: 'Outlet Service', path: '/mappings/outlet-service-mappings' },
			{ name: 'Uset to Service', path: '/mappings/user-to-service-mappings' }
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

const hideSidebarRoutes = ['/login', '/sign-up'];

const shouldShowSidebar = computed(() => !hideSidebarRoutes.includes(route.path) && isSignedIn.value);
</script>

<template>
	<ClerkLoaded>
		<div :class="{ 'min-h-screen flex transition-all duration-300': isLocked, 'min-h-screen': !isLocked }">
			<Sidebar v-if="shouldShowSidebar" :navigation="navigation" />
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
	</ClerkLoaded>
</template>

<style>
/* Hide scrollbars globally on page */
html, body {
  scrollbar-width: none;
  -ms-overflow-style: none;
  overflow: auto;
}

html::-webkit-scrollbar,
body::-webkit-scrollbar {
  display: none;
}

/* Hide horizontal scrollbar on table's scroll container */
.overflow-x-auto {
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.overflow-x-auto::-webkit-scrollbar {
  display: none;
}

/* Hide vertical scrollbar on filter dropdown options container */
.max-h-36.overflow-y-auto {
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.max-h-36.overflow-y-auto::-webkit-scrollbar {
  display: none;
}
</style>