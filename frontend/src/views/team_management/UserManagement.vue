// src/views/mappings/UserOutletView.vue
<script setup>
import { ref, onMounted, reactive, watch } from "vue";
import { getOutlets, getUsers, mappedUsersOutlets, mapUserToOutlet } from "@/composables/api/testApi";
import DataTable from "@/components/DataTables/DataTable.vue";
import MappingPopup from "@/components/Mapping/MappingPopup.vue";
import AddUsersPopup from "@/components/Mapping/AddUsersPopup.vue";
import LoadingSpinner from "@/components/LoadingSpinner.vue";
import MessageDialog from "@/components/MessageDialog.vue";
import Breadcrumb from "@/components/Breadcrumb.vue";
import Test from "@/components/Test.vue";
import { PencilIcon, PlusIcon, TrashIcon } from "@heroicons/vue/24/outline";

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

function backBtn(){
  console.log("Back Btn click");
}

function nextBtn(){
  console.log("Next btn click");
}

const selections = reactive({
  users: [],
  outlets: [],
});

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
    alert("Please fill all the fields.");
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

const deleteUser = (index) => {
  usersReview.value.splice(index, 1)
}

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
    :action_buttons="[{ name: 'Back', onClick: backBtn }, { name: 'Next', onClick: nextBtn }]"
    @close="closePopup"
    
  >
    <div class="w-full mx-auto h-full overflow-y-auto no-scrollbar">
      <div id="dropdwon" class="sticky top-0 z-10 bg-white pb-2">
        <!-- Toggle Button -->
        <button 
          @click="toggleDropdown" 
          class="w-full flex justify-between items-center text-sm font-bold px-3 rounded-lg text-white shadow-sm p-1 transition-all"
          :class="isExpanded ? 'rounded-t-lg bg-red-400 hover:bg-red-500' : 'rounded-lg bg-green-500 hover:bg-green-600'" 
        >
          <span>{{ isExpanded ? 'Hide User Form' : 'Add New User' }}</span>
          <!-- Plus icon that turns into an 'X' (close) when expanded -->
          <svg 
            :class="['w-4 h-4 transform transition-transform duration-200', isExpanded ? 'rotate-45' : '']" 
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            viewBox="0 0 24 24"
          >
            <line x1="12" y1="5" x2="12" y2="19" stroke-linecap="round" />
            <line x1="5" y1="12" x2="19" y2="12" stroke-linecap="round" />
          </svg>
        </button>
        <!-- Dropdown Form -->
        <transition name="fade">
          <div
            v-if="isExpanded"
            class="bg-white shadow-sm rounded-b-lg py-3 px-0.5 space-y-2.5"
          >
            <!-- Row 1: Username and Number -->
            <div class="flex flex-col sm:flex-row gap-4">
              <label for="">Username: </label>
              <div class="w-full">
                <input
                  type="text"
                  id="username"
                  v-model="form.username"
                  placeholder="Enter username"
                  class="w-full border border-gray-300 rounded-md p-1.5 px-3 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
            </div>
            </div>

            <div class="w-full">
              <input
                type="number"
                id="user_number"
                v-model="form.number"
                placeholder="Enter number"
                class="w-full border border-gray-300 rounded-md p-1.5 px-3 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <input
                type="email"
                id="user_email"
                v-model="form.email"
                placeholder="Enter email"
                class="w-full border border-gray-300 rounded-md p-1.5 px-3 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
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
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
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