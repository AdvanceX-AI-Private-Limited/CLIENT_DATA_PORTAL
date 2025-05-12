<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router';
import { computed, ref, onMounted, watch } from 'vue';
import { HomeIcon, ChevronRightIcon } from '@heroicons/vue/24/solid';

// Props
interface BreadcrumbProps {
  title?: string;
  showHomeIcon?: boolean;
  showPageTitle?: boolean;
  customRoutes?: Record<string, string>;
  separator?: string;
  clickable?: boolean;
  showParams?: boolean;
}
const props = withDefaults(defineProps<BreadcrumbProps>(), {
  title: "",
  showHomeIcon: true,
  showPageTitle: true,
  customRoutes: () => ({}),
  separator: undefined,
  clickable: true,
  showParams: false,
});

const route = useRoute();
const router = useRouter();

const isLoading = ref(true);
const error = ref<string | null>(null);

const formatRouteName = (name: string) => {
  if (!name) return '';
  // Custom route name from map
  if (props.customRoutes && props.customRoutes[name]) {
    return props.customRoutes[name];
  }
  // Make readable
  return name
    .replace(/[-_]/g, ' ')
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/\b\w/g, l => l.toUpperCase());
};

const breadcrumbItems = computed(() => {
  if (!route.matched || !route.matched.length) return [];
  try {
    return route.matched
      .filter(routeRecord => !!routeRecord.name)
      .map((routeRecord, idx, filteredMatched) => {
        const params: Record<string, string> = {};
        if (props.showParams) {
          Object.entries(route.params).forEach(([key, value]) => {
            if (routeRecord.path.includes(`:${key}`)) {
              params[key] = String(value);
            }
          });
        }

        return {
          name: String(routeRecord.name),
          displayName: routeRecord.meta?.title || formatRouteName(String(routeRecord.name)),
          path: router.resolve({ name: routeRecord.name, params: props.showParams ? params : {} }).path,
          isLast: idx === filteredMatched.length - 1,
          params: props.showParams ? params : {},
        };
      });
  } catch (err:any) {
    error.value = err.message;
    return [];
  }
});

const pageTitle = computed(() => {
  if (props.title) return props.title;
  if (breadcrumbItems.value.length > 0) {
    return breadcrumbItems.value.at(-1)?.displayName;
  }
  return "Page";
});

function handleNavigate(path: string) {
  if (props.clickable && path) router.push(path);
}

onMounted(() => { isLoading.value = false; });
watch(() => route.fullPath, () => {
  isLoading.value = false;
  error.value = null;
});
</script>

<template>
  <div class="breadcrumb-root w-full py-3 mb-5">
    <!-- Error -->
    <div v-if="error" class="text-red-600 mb-2 text-sm">
      <span>Breadcrumb error: {{ error }}</span>
    </div>

    <!-- Breadcrumb -->
    <nav aria-label="Breadcrumb" class="block">
      <ol class="flex items-center flex-wrap gap-1 text-sm font-medium text-gray-600">
        <!-- Home Icon -->
        <li v-if="showHomeIcon" class="flex items-center">
          <button
            @click="handleNavigate('/')"
            type="button"
            :disabled="!clickable"
            class="group flex items-center px-2 py-1 rounded hover:bg-primary-50 focus:bg-primary-100 transition-colors disabled:opacity-50"
            :aria-current="breadcrumbItems.length === 0 ? 'page' : undefined"
          >
            <HomeIcon class="h-5 w-5 text-primary-600 group-hover:scale-110" aria-hidden="true" />
            <span class="sr-only">Home</span>
          </button>
          <!-- Separator -->
          <template v-if="breadcrumbItems.length">
            <span class="mx-1 text-gray-400 select-none" aria-hidden="true">
              <template v-if="separator">{{ separator }}</template>
              <ChevronRightIcon v-else class="h-4 w-4" />
            </span>
          </template>
        </li>

        <!-- Breadcrumb Items -->
        <li
          v-for="(item, i) in breadcrumbItems"
          :key="item.name"
          class="flex items-center overflow-hidden"
        >
          <!-- Breadcrumb link (not last) -->
          <button
            v-if="!item.isLast"
            type="button"
            @click="handleNavigate(item.path)"
            :disabled="!clickable"
            class="text-left px-2 py-1 rounded hover:bg-primary-50 focus:bg-primary-100 transition-colors group disabled:opacity-50"
          >
            <!-- :title="item.displayName" -->
            <span class="group-hover:text-primary-600 transition-colors">
              <span>{{ item.displayName }}</span>
              <span v-if="showParams && Object.keys(item.params).length"
                class="ml-1 text-xs text-gray-400"
              >
                ({{ Object.entries(item.params).map(([k,v]) => `${k}: ${v}`).join(', ') }})
              </span>
            </span>
          </button>
          <!-- Current page (last item) -->
          <span
            v-else
            class="font-semibold text-primary-700 px-2 py-1 bg-primary-50 rounded"
            aria-current="page"
          >
            <!-- :title="item.displayName" -->
            <span>{{ item.displayName }}</span>
            <span v-if="showParams && Object.keys(item.params).length"
              class="ml-1 text-xs text-gray-400"
            >
              ({{ Object.entries(item.params).map(([k,v]) => `${k}: ${v}`).join(', ') }})
            </span>
          </span>
          <!-- Separator if not last -->
          <span v-if="!item.isLast" class="mx-1 text-gray-400 select-none" aria-hidden="true">
            <template v-if="separator">{{ separator }}</template>
            <ChevronRightIcon v-else class="h-4 w-4" />
          </span>
        </li>
      </ol>
    </nav>
  </div>
</template>

<style scoped>
.breadcrumb-root {
  /* Theme override here; adjust variables as needed */
  --primary-600: #2563eb;
  --primary-700: #1d4ed8;
  --primary-50: #eef4ff;
}
.text-primary-600 {
  color: var(--primary-600);
}
.text-primary-700 {
  color: var(--primary-700);
}
.bg-primary-50 {
  background-color: var(--primary-50);
}
.hover\:bg-primary-50:hover {
  background-color: var(--primary-50);
}
.focus\:bg-primary-100:focus {
  background-color: #dbeafe;
}
.group-hover\:text-primary-600:hover {
  color: var(--primary-600);
}
</style>