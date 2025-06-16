<script setup>
import { ref, computed, onMounted, watchEffect, watch } from "vue";
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
import { useAuth } from '@/stores/useAuth';
import { setAuthState } from '@/router';
import AccountReviewNotice from "./components/Auth/AccountReviewNotice.vue";
import { userIsActive } from "@/composables/api/authApi";

const isSidebarOpen = ref(false)
const route = useRoute();
const router = useRouter();
const { isSignedIn, loaded, isActive, setIsActive } = useAuth();
const checkingActiveStatus = ref(true); // <-- Add this

// For debugging
watchEffect(() => {
  if (loaded.value) {
    // console.log("App watchEffect isSignedIn: ", isSignedIn.value);
    // console.log('Clerk authentication loaded, isSignedIn:', isSignedIn.value);
    // console.log('Current route:', route.path);
  }
});

// Track previous auth state to avoid unnecessary redirects
let previousAuthState = null;

// Initialize the auth state once when component is mounted
onMounted(() => {
  let stopWatcher = null;
  stopWatcher = watchEffect(() => {
    if (loaded.value) {
      previousAuthState = isSignedIn.value;
      setAuthState(isSignedIn.value);
      // Stop this watcher once it's executed
      if (stopWatcher) stopWatcher();
    }
  });
});

// Watch for changes in authentication state and update the router's global state
watchEffect(() => {
  if (loaded.value) {
    // console.log("App watchEffect isSignedIn: ", isSignedIn.value);
    setAuthState(isSignedIn.value);
    if (isSignedIn.value) {
      localStorage.setItem('auth-token', 'true');
    } else {
      localStorage.removeItem('auth-token');
    }
    if (previousAuthState !== null && previousAuthState !== isSignedIn.value) {
      previousAuthState = isSignedIn.value;
      const currentPath = route.path;
      const publicRoutes = ['/login', '/sign-up'];
      const isPublicRoute = publicRoutes.includes(currentPath);
      if (isSignedIn.value && isPublicRoute) {
        router.push('/');
      } else if (!isSignedIn.value && !isPublicRoute) {
        router.push('/login');
      }
    }
  }
});

// Check and set user active status on mounted
onMounted(async () => {
  if (isSignedIn.value) {
    try {
      const res = await userIsActive();
      if (res && typeof res.data.is_active === "boolean") {
        setIsActive(res.data.is_active);
      }
    } catch (e) {
      console.warn("Failed to fetch user active status", e);
    }
  }
  checkingActiveStatus.value = false;
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
			{ name: 'Services', path: '/brand-management/services-management' }, 
			{ name: 'Outlet', path: '/brand-management/outlet-management' } 
		]
	},
	{
		name: 'Tema Management', 
		path: '/team-management', 
		icon: LockClosedIcon,
		subLinks: [
			{ name: 'Users', path: '/team-management/users-management' },
			{ name: 'User to Outlet', path: '/team-management/user-to-outlet-mappings' },
			{ name: 'Outlet Service', path: '/team-management/outlet-service-mappings' },
			{ name: 'Uset to Service', path: '/team-management/user-to-service-mappings' }
		]
	},
	{ name: 'Automation', path: '/automation', icon: AdjustmentsHorizontalIcon },
	{ name: 'Subscriptions', path: '/subscription', icon: CurrencyDollarIcon }, 
	{ name: 'Settings', path: '/settings', icon: Cog6ToothIcon }
];

watch(isActive, val => {
  console.log("isActive changed to:", val);
})

const hideSidebarRoutes = ['/login', '/sign-up'];

const shouldShowSidebar = computed(() => !hideSidebarRoutes.includes(route.path) && isSignedIn.value);
</script>

<template>
  <!-- Show nothing until active status is checked -->
  <div v-if="checkingActiveStatus"></div>
  <!-- Show review notice if user is signed in but not active -->
  <div v-else-if="!isActive && isSignedIn">
    <AccountReviewNotice/>
  </div>
  <!-- Show main app if user is active or not signed in -->
  <div v-else :class="{ 'min-h-screen flex transition-all duration-300': isLocked, 'min-h-screen': !isLocked }">
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