import { createRouter, createWebHistory } from 'vue-router';
import { nextTick } from 'vue';

import HomeView from '@/views/home/HomeView.vue';
import LayoutWrapper from '@/components/LayoutWrapper.vue';
import AllMappings from '@/views/access_management/AllMappings.vue';
import RoleToServiceMappings from '@/views/access_management/RoleToServiceMappings.vue';
import UserToRoleMappings from '@/views/access_management/UserToRoleMappings.vue';
import AutomationView from '@/views/automation/AutomationView.vue';
import OutletManagement from '@/views/brand_management/OutletManagement.vue';
import RoleManagement from '@/views/brand_management/RoleManagement.vue';
import UserManagement from '@/views/brand_management/UserManagement.vue';
import IoWsDashboard from '@/views/dashboard/IoWsDashboard.vue';
import ItemOfflineTracker from '@/views/dashboard/ItemOfflineTracker.vue';
import O2Dashboard from '@/views/dashboard/O2Dashboard.vue';
import O2WSDashboard from '@/views/dashboard/O2WSDashboard.vue';
import Settings from '@/views/settings/Settings.vue';
import Subscription from '@/views/subscription/Subscription.vue';
import error_404 from '@/views/erro_pages/error_404.vue';
import LoginView from '@/views/auth/LoginView.vue';
import SignUpView from '@/views/auth/SignUpView.vue';

// Define public routes that don't require authentication
const publicRoutes = ['/login', '/sign-up'];

const routes = [
	{
		path: '/',
		component: LayoutWrapper,
		meta: { requiresAuth: true },
		children: [
					{
						path: '',
						name: 'home',
						component: HomeView,
					},
					{
						path: 'automation',
						name: 'automation',
						component: AutomationView,
					},
					{
						path: 'dashboard',
						name: 'dashboard',
						component: LayoutWrapper,
						children: [
							{
								path: 'item-offline-tracker',
								name: 'item-offline-tracker',
								component: ItemOfflineTracker,
							},
							{
								path: 'item-offline-weekly-sales',
								name: 'item-offline-weekly-sales',
								component: IoWsDashboard,
							},
							{
								path: 'o2-dashboard',
								name: 'o2-dashboard',
								component: O2Dashboard,
							},
							{
								path: 'o2ws-dashboard',
								name: 'o2ws-dashboard',
								component: O2WSDashboard,
							},
						],
					},
					{
						path: 'access-management',
						name: 'access-management',
						component: LayoutWrapper,
						children: [
							{
								path: 'all-mappings',
								name: 'all-mappings',
								component: AllMappings,
							},
							{
								path: 'role-to-service-mappings',
								name: 'role-to-service-mappings',
								component: RoleToServiceMappings,
							},
							{
								path: 'user-to-role-mappings',
								name: 'user-to-role-mappings',
								component: UserToRoleMappings,
							},
						],
					},
					{
						path: 'brand-management',
						name: 'brand-management',
						component: LayoutWrapper,
						children: [
							{
								path: 'outlet-management',
								name: 'outlet-management',
								component: OutletManagement,
							},
							{
								path: 'role-management',
								name: 'role-management',
								component: RoleManagement,
							},
							{
								path: 'user-management',
								name: 'user-management',
								component: UserManagement,
							},
						],
					},
			{
				path: 'settings',
				name: 'settings',
				component: Settings,
			},
			{
				path: 'subscription',
				name: 'subscription',
				component: Subscription,
			},
	],
	},
	{
		path: '/login',
		name: 'login',
		component: LoginView,
		meta: { requiresAuth: false },
	},
	{
		path: '/sign-up',
		name: 'signup',
		component: SignUpView,
		meta: { requiresAuth: false },
	},
	{
	path: '/:pathMatch(.*)*', 
	name: 'not-found',
	component: error_404,
	},
];

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes,
});

// Global variable to track authentication state
let isUserAuthenticated = false;

// Function to set authentication state
export function setAuthState(authenticated) {
  isUserAuthenticated = authenticated;
}

router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const isPublicRoute = publicRoutes.includes(to.path);
  
  // Allow all navigation to public routes
  if (isPublicRoute) {
    next();
    return;
  }
  
  // For authenticated routes
  if (requiresAuth) {
    // If coming from a page refresh (from is an empty route), we want to
    // let the app.vue component handle this after Clerk is fully loaded
    const isPageRefresh = from.name === undefined;
    
    if (isPageRefresh) {
      // Let the App.vue handle authentication check after Clerk loads
      // This prevents premature redirects during page refresh
      next();
    } else if (!isUserAuthenticated) {
      // Only redirect to login if not authenticated and not a page refresh
      next('/login');
    } else {
      // Allow navigation
      next();
    }
  } else {
    // For any other route that doesn't require auth
    next();
  }
});

export default router;
