import { createRouter, createWebHistory } from 'vue-router';
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

const routes = [
	{
		path: '/',
		component: LayoutWrapper,
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
	path: '/:pathMatch(.*)*', 
	name: 'not-found',
	component: error_404,
	},
];

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes,
});

export default router;
