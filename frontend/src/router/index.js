import { createRouter, createWebHistory } from 'vue-router';
import { nextTick } from 'vue';

import HomeView from '@/views/home/HomeView.vue';
import LayoutWrapper from '@/components/LayoutWrapper.vue';
import AutomationView from '@/views/automation/AutomationView.vue';
import OutletManagement from '@/views/brand_management/OutletManagement.vue';
import ServicesManagement from '@/views/brand_management/ServicesManagement.vue';
import IoWsDashboard from '@/views/dashboard/IoWsDashboard.vue';
import ItemOfflineTracker from '@/views/dashboard/ItemOfflineTracker.vue';
import O2Dashboard from '@/views/dashboard/O2Dashboard.vue';
import O2WSDashboard from '@/views/dashboard/O2WSDashboard.vue';
import Settings from '@/views/settings/Settings.vue';
import Subscription from '@/views/subscription/Subscription.vue';
import error_404 from '@/views/erro_pages/error_404.vue';
import LoginView from '@/views/auth/LoginView.vue';
import SignUpView from '@/views/auth/SignUpView.vue';
import UserManagement from '@/views/team_management/UserManagement.vue';
import UserOutletView from '@/views/team_management/UserOutletView.vue';
import UserServiceView from '@/views/team_management/UserServiceView.vue';
import OutletServiceView from '@/views/team_management/OutletServiceView.vue';

const publicRoutes = ['/login', '/sign-up'];

const routes = [
	{
		path: '/',
		component: LayoutWrapper,
		meta: { requiresAuth: true },
		children: [
		{
			path: '',
			name: 'Home',
			component: HomeView,
		},
		{
			path: 'automation',
			name: 'Automation',
			component: AutomationView,
		},
		{
			path: 'dashboard',
			name: 'Dashboard',
			children: [
			{
				path: 'item-offline-tracker',
				name: 'Item Offline Tracker',
				component: ItemOfflineTracker,
			},
			{
				path: 'item-offline-weekly-sales',
				name: 'Item Offline Weekly Sales',
				component: IoWsDashboard,
			},
			{
				path: 'o2-dashboard',
				name: 'O2 Dashboard',
				component: O2Dashboard,
			},
			{
				path: 'o2ws-dashboard',
				name: 'O2WS Dashboard',
				component: O2WSDashboard,
			},
				],
		},
		{
			path: 'team-management',
			name: 'Tema Management',
			children: [
			{
				path: 'users-management',
				name: 'Users Management',
				component: UserManagement,
			},
			{
				path: 'user-to-outlet-mappings',
				name: 'User to Outlet Mappings',
				component: UserOutletView,
			},
			{
				path: 'user-to-service-mappings',
				name: 'User to Service Mappings',
				component: UserServiceView,
			},
			{
				path: 'outlet-service-mappings',
				name: 'Outlet Service Mappings',
				component: OutletServiceView,
			},
				],
		},
		{
			path: 'brand-management',
			name: 'Brand Management',
			children: [
			{
				path: 'outlet-management',
				name: 'Outlet Management',
				component: OutletManagement,
			},
			{
				path: 'services-management',
				name: 'Services Management',
				component: ServicesManagement,
			},
				],
		},
		{
			path: 'settings',
			name: 'Settings',
			component: Settings,
		},
		{
			path: 'subscription',
			name: 'Subscription',
			component: Subscription,
		},
			],
	},
	{
		path: '/login',
		name: 'Login',
		component: LoginView,
		meta: { requiresAuth: false },
	},
	{
		path: '/sign-up',
		name: 'Sign Up',
		component: SignUpView,
		meta: { requiresAuth: false },
	},
	{
		path: '/test',
		name: 'Test',
		component: () => import('@/views/test/TestView.vue'),
		meta: { requiresAuth: true }
	},
	{
		path: '/:pathMatch(.*)*',
		name: 'Not Found',
		component: error_404,
	},
];

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes,
});

let isUserAuthenticated = false;

try {
	isUserAuthenticated = localStorage.getItem('auth-token') === 'true';
} catch (e) {
	console.error('Error accessing localStorage:', e);
}

export function setAuthState(authenticated) {
	isUserAuthenticated = authenticated;

	if (authenticated) {
		localStorage.setItem('auth-token', 'true');
	} else {
		localStorage.removeItem('auth-token');
	}
}

router.beforeEach((to, from, next) => {
	const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
	const isPublicRoute = publicRoutes.includes(to.path);

	if (isPublicRoute) {
		next();
		return;
	}

	if (requiresAuth) {
		const isPageRefresh = from.name === undefined;

		if (isPageRefresh) {
			const hasStoredAuth = localStorage.getItem('auth-token') || 
				sessionStorage.getItem('auth-token') ||
				isUserAuthenticated;

			if (hasStoredAuth) {
				next();
			} else {
				next('/login');
			}
		} else if (!isUserAuthenticated) {
			next('/login');
		} else {
			next();
		}
	} else {
		next();
	}
});

export default router;
