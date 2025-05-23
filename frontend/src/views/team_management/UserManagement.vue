// src/views/mappings/UserOutletView.vue
<script setup>
import { ref, onMounted, reactive, computed } from "vue";
import { getOutlets, getUsers, mappedUsersOutlets, mapUserToOutlet } from "@/composables/api/testApi";
import DataTable from "@/components/DataTables/DataTable.vue";
import MappingPopup from "@/components/Mapping/MappingPopup.vue";
import AddUsersPopup from "@/components/Mapping/AddUsersPopup.vue";
import LoadingSpinner from "@/components/LoadingSpinner.vue";
import MessageDialog from "@/components/MessageDialog.vue";
import Breadcrumb from "@/components/Breadcrumb.vue";
import Test from "@/components/Test.vue";
import { PencilIcon, PlusIcon, TrashIcon } from "@heroicons/vue/24/outline";
import { BuildingStorefrontIcon, WrenchScrewdriverIcon, UserPlusIcon } from '@heroicons/vue/24/solid'


const showPopup = ref(false);

const outlets = ref([]);
const users = ref([]);
const mappedUsers = ref([]);

const loadingOutlets = ref(false);
const loadingUsers = ref(false);
const loadingMappedUsers = ref(false);

const errorOutlets = ref(null);
const errorUsers = ref(null);
const errorMappedUsers = ref(null);

const mappingLoading = ref(false);

const messageDialogVisible = ref(false);
const messageDialogContent = ref({
  title: "",
  message: "",
  icon: "",
});

const fetchUsers = async () => {
  console.log("Fetching users...");
  loadingUsers.value = true;
  errorUsers.value = null;
  try {
    const response = await getUsers();
    users.value = response.data;
    console.log("Users:", users.value);
  } catch (err) {
    errorUsers.value = err.message || "Failed to fetch";
  } finally {
    loadingUsers.value = false;
  }
};

async function fetchMappedOutlets() {
  console.log("Fetching mapped outlets...");
  loadingOutlets.value = true;
  errorOutlets.value = null;
  try {
    const response = await getOutlets();
    outlets.value = response.data;
    console.log("Mapped outlets:", outlets.value);
  } catch (err) {
    errorOutlets.value = err.message || "Failed to fetch";
  } finally {
    loadingOutlets.value = false;
  }
}

function handleToolbarAction(action) {
  if (typeof action.onClick === "function") action.onClick();
}

const mappingTabs = [
  {
    label: "Select Users",
    description: "Select users to map to the outlets",
    key: "users",
    fetchData: async () => {
      if (!users.value.length) await fetchUsers();
      return users.value;
    },
    displayMapping: { heading: "user_name", sub: "user_number" },
  },
  {
    label: "Select Outlets",
    description: "Select outlets to map to the users",
    key: "outlets",
    fetchData: async () => {
      if (!outlets.value.length) await fetchMappedOutlets();
      return outlets.value;
    },
    displayMapping: { heading: "res_shortcode", sub: "res_id" },
  },
];

function transformDataForBackend(data) {
  console.log("data", data);
  const redIdSet = new Set();
  const userMap = new Map();

  data.forEach(([user, outlet]) => {
    const userNumber = user.user_number;
    const userName = user.user_name;
    const resId = parseInt(outlet.res_id);

    if (!userNumber || !userName || isNaN(resId)) return;

    redIdSet.add(resId);

    // Use Map to avoid duplicate users
    if (!userMap.has(userNumber)) {
      userMap.set(userNumber, { name: userName, number: userNumber });
    }
  });

  return {
    red_id: Array.from(redIdSet),
    users: Array.from(userMap.values()),
    action: "map",
  };
}

// Function to show message dialog
function showMessage(message, title = "Message") {
  messageDialogContent.value = {
    title,
    message,
    icon,
  };
  messageDialogVisible.value = true;
}

// Function to close message dialog
function closeMessageDialog() {
  messageDialogVisible.value = false;
}

async function fetchMappedUsers() {
  console.log("Fetching mapped users...");
  loadingMappedUsers.value = true;
  errorMappedUsers.value = null;
  try {
    const response = await mappedUsersOutlets();
    mappedUsers.value = response.data;
    // console.log("Mapped users:", mappedUsers.value);
  } catch (err) {
    errorMappedUsers.value = err.message || "Failed to fetch";
  } finally {
    loadingMappedUsers.value = false;
  }
}

async function onMappingGenerated(mappings) {
  console.log("MAPPING RESULT", mappings);
  mappingLoading.value = true;
  try {
    // Compose payload according to your API's requirements
    let payload = await transformDataForBackend(mappings);
    payload = {
      data: payload,
    };
    console.log("Payload being sent:", JSON.stringify(payload));
    const response = await mapUserToOutlet(payload);
    showMessage(
      response.data?.message || "Mapping completed successfully",
      "Success",
      "success"
    );
    await fetchMappedUsers();
  } catch (error) {
    console.error("Error mapping users to outlets:", error);
    showMessage(
      error.response?.data?.message || error.message || "Failed to process mapping.",
      "Error",
      "error"
    );
  } finally {
    mappingLoading.value = false;
    showPopup.value = false;
  }
}

function showMappingPopup() {
  console.log("Opening popup");
  showPopup.value = true;
}

function closePopup() {
  console.log("Closing popup");
  showPopup.value = false;
}

const isExpanded = ref(false);

function toggleDropdown() {
  isExpanded.value = !isExpanded.value;
}

onMounted(() => {
  fetchUsers();
  fetchMappedOutlets();
  fetchMappedUsers();
});

const usersReview = ref([]);

const form = reactive({
  username: '',
  number: '',
  email: '',
  is_active: false
})

const addUser = () => {
  if(!form.username || !form.email || !form.number){
    // alert("Please fill all the fields.");
    return
  }

  usersReview.value.unshift({...form})

  console.log('User added:', form)
  console.log('Updated usersReview:', usersReview.value)
  
  form.email = ''
  form.username = ''
  form.number = ''
  form.is_active = ''
}

onMounted(() => {
  // Auto-generate 100 test users with alternating is_active values
  for (let i = 1; i <= 100; i++) {
    usersReview.value.push({
      username: `User ${i}`,
      number: `90000000${i.toString().padStart(2, '0')}`,
      email: `user${i}@example.com`,
      is_active: i % 2 === 0 // true for even, false for odd
    });
  }

  // Optional: Also set the form with the first user's values
  form.username = 'User 1';
  form.number = '9000000001';
  form.email = 'user1@example.com';
  form.is_active = false;
});

const deleteUser = (index) => {
  usersReview.value.splice(index, 1)
}

const mappingTabList = [
  { label: "Add Users", key: "add-users" },
  // { label: "Review", key: "review" },
  { label: "Submit", key: "submit" }
];

const activeTab = ref("add-users");

const tabIndex = () =>
  mappingTabList.findIndex((tab) => tab.key === activeTab.value);

const goToTab = (key) => { activeTab.value = key };

const nextTab = () => {
  if (tabIndex() < mappingTabList.length - 1) {
    activeTab.value = mappingTabList[tabIndex() + 1].key;
  }
};

const prevTab = () => {
  if (tabIndex() > 0) {
    activeTab.value = mappingTabList[tabIndex() - 1].key;
  }
};

const addUsersActionButtons = computed(() => {
  const buttons = [];
  if (tabIndex() > 0) {
    buttons.push({ name: 'Back', onClick: () => prevTab() });
  }
  if (tabIndex() < mappingTabList.length - 1) {
    buttons.push({ name: 'Next', onClick:() => nextTab() });
  }
  return buttons;
});

const submitCards = [
  {
    title: 'Add & Map Outlets',
    description: 'Map users to outlets quickly.',
    icon: BuildingStorefrontIcon,
    iconColor: 'text-blue-600',
    bg: 'bg-blue-50',
    hoverBg: 'hover:bg-blue-100',
    onClick: () => console.log('Clicked Add & Map Outlets')
  },
  {
    title: 'Add & Map Services',
    description: 'Map users to available services.',
    icon: WrenchScrewdriverIcon,
    iconColor: 'text-pink-600',
    bg: 'bg-pink-50',
    hoverBg: 'hover:bg-pink-100',
    onClick: () => console.log('Clicked Add & Map Services')
  },
  {
    title: 'Add Users',
    description: 'Add new team members.',
    icon: UserPlusIcon,
    iconColor: 'text-emerald-600',
    bg: 'bg-emerald-50',
    hoverBg: 'hover:bg-emerald-100',
    onClick: () => console.log('Clicked Add Users')
  }
]
</script>

<template>
  <Breadcrumb />
  
  <DataTable
    title="Mapped Users"
    :table_data="mappedUsers"
    :loading="loadingMappedUsers"
    :error="errorMappedUsers"
    :action_buttons="[{ name: 'Add&nbsp;Users', onClick: showMappingPopup, action: 'user_map', icon: PlusIcon}]"
    @action-click="handleToolbarAction"
    :csv_download="true"
  />

  <!-- v-if="showPopup" -->
  <AddUsersPopup
    :title="'Add Users'"
    :closeBtnBar="true"
    :subheading="'Create multiple mappings between users, outlets, and services simultaneously.'"
    :action_buttons="addUsersActionButtons"
    @close="closePopup"
    
  >
    <div class="px-4 py-3 border-b bg-white w-full">
      <div class="flex">
        <div
          v-for="(tab, index) in mappingTabList"
          :key="tab.key"
          class="flex items-center text-sm relative"
        >
          <div class="flex items-center select-none" style="cursor:pointer;" @click="goToTab(tab.key)">
            <!-- Circle -->
            <div
              class="w-6 h-6 rounded-full flex items-center justify-center mr-2 text-xs shadow-sm transition-all"
              :class="{
                'bg-gradient-to-r from-blue-500 to-indigo-600 text-white': activeTab === tab.key,
                'bg-white text-gray-500 border border-gray-200': activeTab !== tab.key && index < tabIndex(),
                'bg-gray-100 text-gray-400 border border-gray-200': activeTab !== tab.key && index > tabIndex()
              }"
            >
              <svg
                v-if="activeTab !== tab.key && index < tabIndex()"
                xmlns="http://www.w3.org/2000/svg"
                class="h-3 w-3 text-blue-500"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
              <span v-else>{{ index + 1 }}</span>
            </div>
            <span
              class="text-sm"
              :class="{
                'font-medium text-gray-900': activeTab === tab.key,
                'text-blue-500': activeTab !== tab.key && index < tabIndex(),
                'text-gray-400': activeTab !== tab.key && index > tabIndex()
              }"
            >
              {{ tab.label }}
            </span>
          </div>
          <div v-if="index < mappingTabList.length - 1" class="mx-2 text-gray-300 flex items-center">
            <div class="h-px w-4 bg-gray-300"></div>
          </div>
        </div>
      </div>
    </div>
    <div class="my-3 mx-2 h-full overflow-y-auto no-scrollbar">
      <div v-if="activeTab == 'add-users'">
        <div id="dropdwon" class="sticky top-0 z-10 bg-white pb-2">
          <!-- Toggle Button -->
          <button @click="toggleDropdown" class="ml-auto flex justify-between items-center text-sm font-bold px-3 rounded-lg text-white shadow-sm p-1.5 transition-all bg-green-600 hover:bg-green-700"
          :class="isExpanded ? 'hidden': ''"
          >
            <svg 
              :class="['w-4 h-4 me-1.5 transform transition-transform duration-200', isExpanded ? 'rotate-45' : '']" 
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              viewBox="0 0 24 24"
            >
            <!-- Plus icon that turns into an 'X' (close) when expanded -->
              <line x1="12" y1="5" x2="12" y2="19" stroke-linecap="round" />
              <line x1="5" y1="12" x2="19" y2="12" stroke-linecap="round" />
            </svg>
            <span>{{ isExpanded ? 'Hide Form' : 'Add' }}</span>
          </button>

          <!-- Dropdown Form -->
          <transition name="slide-expand-tr">
            <div
              v-if="isExpanded"
              class="bg-white shadow-sm rounded-lg p-3 border border-gray-200 space-y-2.5"
            >
              <button @click="toggleDropdown" class="w-full ml-auto rounded-lg bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-500 font-bold py-0.5 hover:text-gray-800 transition-colors">
                <!-- <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg> -->
                Close
              </button>
              <!-- Row 1: Username and Number -->
              <div class="w-full">
                <input
                  type="text"
                  id="username"
                  v-model="form.username"
                  placeholder="Enter username"
                  class="w-full border border-gray-300 rounded-md p-1.5 px-3 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div class="flex flex-col sm:flex-row gap-4">
                <div class="w-full">
                  <input
                    type="number"
                    id="user_number"
                    v-model="form.number"
                    placeholder="Enter number"
                    class="w-full border border-gray-300 rounded-md p-1.5 px-3 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>

                <div class="w-full">
                  <input
                    type="email"
                    id="user_email"
                    v-model="form.email"
                    placeholder="Enter email"
                    class="w-full border border-gray-300 rounded-md p-1.5 px-3 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
              </div>

              <div class="px-2">
              <!-- Row 3: Toggle + Confirm Button -->
              <div class="flex flex-col sm:flex-row items-center justify-between gap-4">
                <div class="flex items-center gap-3">
                  <label for="is_active" class="text-sm font-medium text-gray-700">Active</label>
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" id="is_active" v-model="form.is_active" class="sr-only peer">
                    <div class="w-11 h-6 bg-gray-200 peer-focus:ring-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:bg-blue-600 transition-all"></div>
                    <div class="absolute left-1 top-1 bg-white w-4 h-4 rounded-full transition-all peer-checked:translate-x-full"></div>
                  </label>
                </div>

                <button
                  @click="addUser"
                  class="text-sm text-white bg-blue-600 hover:bg-blue-700 py-1.5 px-4 rounded-lg transition-colors shadow"
                >
                  Confirm
                </button>
              </div>
              </div>
            </div>
          </transition>
        </div>

        <div class="overflow-y-auto flex-grow min-h-0 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
          <ul class="space-y-2 mt-2">
            <li
              v-for="(user, index) in usersReview"
              :key="index"
              class="flex justify-between items-center border border-gray-200 rounded-md px-3 py-2 bg-white shadow-sm text-sm"
            >
              <!-- Left: User Info -->
              <div class="text-gray-800">
                <div class="font-medium">
                  {{ user.username }} • {{ user.number }}
                </div>
                <div class="text-gray-600 text-xs">
                  {{ user.email }} • 
                  <span :class="user.is_active ? 'text-green-600' : 'text-red-500'">
                    {{ user.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </div>
              </div>

              <!-- Right: Delete Button -->
              <button
                @click="deleteUser(index)"
                class="text-red-500 hover:text-red-700 ml-4"
                title="Delete user"
              >
                <!-- Trash Icon (Heroicon or alternative) -->
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none"
                  viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round"
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6M9 7h6m2 0a2 2 0 00-2-2H9a2 2 0 00-2 2h10z" />
                </svg>
              </button>
            </li>
          </ul>
        </div>
      </div>
      <div v-if="activeTab == 'review'">
        <div class="">
          <ul class="space-y-2 mt-2">
            <li
              v-for="(user, index) in usersReview"
              :key="index"
              class="flex justify-between items-center border border-gray-200 rounded-md px-3 py-2 bg-white shadow-sm text-sm"
            >
              <!-- Left: User Info -->
              <div class="text-gray-800">
                <div class="font-medium">
                  {{ user.username }} • {{ user.number }}
                </div>
                <div class="text-gray-600 text-xs">
                  {{ user.email }} • 
                  <span :class="user.is_active ? 'text-green-600' : 'text-red-500'">
                    {{ user.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </div>
              </div>

              <!-- Right: Delete Button -->
              <button
                @click="deleteUser(index)"
                class="text-red-500 hover:text-red-700 ml-4"
                title="Delete user"
              >
                <!-- Trash Icon (Heroicon or alternative) -->
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none"
                  viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round"
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6M9 7h6m2 0a2 2 0 00-2-2H9a2 2 0 00-2 2h10z" />
                </svg>
              </button>
            </li>
          </ul>
        </div>
      </div>
      <div v-if="activeTab === 'submit'" class="max-w-6xl mx-auto px-4 py-10">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 m-7">
          <div
            v-for="(card, index) in submitCards"
            :key="index"
            @click="card.onClick"
            :class="`${card.bg} ${card.hoverBg} transition-all duration-300 cursor-pointer hover:scale-105 rounded-lg p-6 flex flex-col items-start`"
          >
            <div :class="`h-12 w-12 rounded-full bg-white shadow flex items-center justify-center mb-4 ${card.iconColor}`">
              <component :is="card.icon" class="h-6 w-6" />
            </div>
            <h3 class="text-lg font-semibold text-gray-800 mb-1">{{ card.title }}</h3>
            <p class="text-gray-600">{{ card.description }}</p>
          </div>
        </div>
      </div>
    </div>
  </AddUsersPopup>

  <!-- Show loading spinner when mapping is in progress -->
  <LoadingSpinner v-if="mappingLoading" />

  <!-- Message Dialog -->
  <MessageDialog
    :visible="messageDialogVisible"
    :title="messageDialogContent.title"
    :message="messageDialogContent.message"
    :icon="messageDialogContent.icon"
    @close="closeMessageDialog"
  />
</template>

<style scoped>
.slide-expand-tr-enter-active,
.slide-expand-tr-leave-active {
  transition:
    opacity 0.36s cubic-bezier(0.5, 1.12, 0.72, 1),
    transform 0.37s cubic-bezier(0.5, 1.23, 0.72, 1.05),
    clip-path 0.38s cubic-bezier(0.47, 1.64, 0.41, 0.87)
  ;
  will-change: opacity, transform, clip-path;
  /* Ensures overflowing content is hidden during animation */
  overflow: hidden;
}

.slide-expand-tr-enter-from,
.slide-expand-tr-leave-to {
  opacity: 0;
  /* Start slightly offset and shrunken in top-right */
  transform: translateY(-22px) translateX(42px) scale(0.88);
  clip-path: inset(0 90% 90% 0 round 20px);
  pointer-events: none;
}

.slide-expand-tr-enter-to,
.slide-expand-tr-leave-from {
  opacity: 1;
  transform: translateY(0) translateX(0) scale(1);
  clip-path: inset(0 0 0 0 round 12px);
}

.no-scrollbar::-webkit-scrollbar {
  display: none;
}

/* Hide scrollbar for Firefox */
.no-scrollbar {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}
</style>