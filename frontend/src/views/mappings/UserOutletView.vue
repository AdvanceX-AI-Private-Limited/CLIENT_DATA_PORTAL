// src/views/mappings/UserOutletView.vue
<script setup>
import { ref, onMounted, reactive } from "vue";
import { getOutlets, getUsers, mappedUsersOutlets, mapUserToOutlet } from "@/composables/api/testApi";
import DataTable from "@/components/DataTables/DataTable.vue";
import MappingPopup from "@/components/Mapping/MappingPopup.vue";
import LoadingSpinner from "@/components/LoadingSpinner.vue";
import MessageDialog from "@/components/MessageDialog.vue";
import { PencilIcon, TrashIcon } from "@heroicons/vue/24/outline";

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
function showMessage(message, title = "Message", icon = "") {
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

const selections = reactive({
  users: [],
  outlets: [],
});

onMounted(() => {
  fetchUsers();
  fetchMappedOutlets();
  fetchMappedUsers();
});
</script>

<template>
  <DataTable
    title="Users To Outlet"
    :table_data="mappedUsers"
    :loading="loadingMappedUsers"
    :error="errorMappedUsers"
    :action_buttons="[{ name: 'Map Users', onClick: showMappingPopup, action: 'user_map' }]"
    @action-click="handleToolbarAction"
    :csv_download="true"
  />

  <MappingPopup
    v-if="showPopup"
    :tabs="mappingTabs"
    v-model:selections="selections"
    @close="closePopup"
    @submit="onMappingGenerated"
  />

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
