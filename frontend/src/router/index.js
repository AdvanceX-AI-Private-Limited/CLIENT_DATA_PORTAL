import { createRouter, createWebHistory } from 'vue-router';

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
import ClientRegistration from '@/views/registration/ClientRegistration.vue';

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
		path: '/client-registration',
		name: 'Client Registration',
		component: ClientRegistration,
		meta: { requiresAuth: false }
	},
	{
		path: '/oauth/callback',
		name: 'OauthCallback',
		component: () => import('@/components/Login/OauthCallback.vue')
	},
	{
		path: '/auth/callback/success',
		name: 'GoogleCallbackSuccess',
		component: () => import('@/views/auth/GoogleCallbackSuccess.vue'),
		meta: { requiresAuth: false }
	},
	{
		path: '/auth/callback/error',
		name: 'GoogleCallbackError',
		component: () => import('@/views/auth/GoogleCallbackError.vue'),
		meta: { requiresAuth: false }
	},
	{
		path: '/test',
		name: 'Test',
		component: () => import('@/views/test/TestView.vue'),
		meta: { requiresAuth: false }
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
	// console.log("setAuthState isUserAuthenticated: ", isUserAuthenticated);
	if (authenticated) {
		localStorage.setItem('auth-token', 'true');
	} else {
		localStorage.removeItem('auth-token');
	}
}

// router.beforeEach((to, from, next) => {
// 	const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
// 	const isPublicRoute = publicRoutes.includes(to.path);

// 	if (isPublicRoute) {
// 		next();
// 		return;
// 	}

// 	if (requiresAuth) {
// 		const isPageRefresh = from.name === undefined;

// 		if (isPageRefresh) {
// 			const hasStoredAuth = localStorage.getItem('auth-token') || 
// 				sessionStorage.getItem('auth-token') ||
// 				isUserAuthenticated;

// 			if (hasStoredAuth) {
// 				next();
// 			} else {
// 				next('/login');
// 			}
// 		} else if (!isUserAuthenticated) {
// 			next('/login');
// 		} else {
// 			next();
// 		}
// 	} else {
// 		next();
// 	}
// });

function isAuthPage(route) {
  return publicRoutes.includes(route.path);
}

router.afterEach((to, from) => {
  // Only save last route if it's not an auth page
  if (!isAuthPage(to)) {
    sessionStorage.setItem('lastRoute', to.fullPath);
  }
});

router.beforeEach((to, from, next) => {
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
    const isPublicRoute = publicRoutes.includes(to.path);

    if (isPublicRoute && isUserAuthenticated) {
		// Use sessionStorage for last visited route (excluding login/sign-up)
		const lastRoute = sessionStorage.getItem('lastRoute') || '/';
		next(lastRoute === to.fullPath ? '/' : lastRoute); // avoid redirect loop
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
