// src/views/mappings/UserOutletView.vue
<script setup>
import { ref, onMounted, reactive } from "vue";
import { mappedUsersOutlets, mapUserToOutlet, getMappedUsers, unmapUserFromOutlet } from "@/composables/api/userToOutletMappings";
import { fetchUsers as fetchUsersApi } from "@/composables/api/teamManagement";
import { fetchOutlets } from "@/composables/api/brandManagementApi";
import DataTable from "@/components/DataTables/DataTable.vue";
import MappingPopup from "@/components/Mapping/MappingPopup.vue";
import LoadingSpinner from "@/components/LoadingSpinner.vue";
import MessageDialog from "@/components/MessageDialog.vue";
import Breadcrumb from "@/components/Breadcrumb.vue";
import Test from "@/components/Test.vue";
import { PencilIcon, PlusIcon, TrashIcon } from "@heroicons/vue/24/outline";
import { use } from "marked";

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
    const mapped_users_response = await getMappedUsers(localStorage.getItem("client_id"));
    console.log("Mapped users:", mapped_users_response.data);

    let mapped_users = [];
    if (mapped_users_response.status === 200 && Array.isArray(mapped_users_response.data) && mapped_users_response.data.length > 0) {
      console.log("Mapped users response is successful and not empty");
      mapped_users = mapped_users_response.data;
    } else {
      console.log("Mapped users response is empty or not an array, proceeding with empty mapping");
    }

    const mappingByEmail = {};
    mapped_users.forEach(mu => {
      mappingByEmail[mu.email] = mu.mapping_id;
    });

    const params = {
      client_id: localStorage.getItem("client_id"),
      skip: 0,
      limit: 100,
    };
    const response = await fetchUsersApi(params);
    users.value = response.data.map(user => ({
      ...user,
      mapping_id: mappingByEmail[user.useremail] || ""  
    }));

    console.log("Users with mapping_id:", users.value);
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
    const params = {
      client_id:  localStorage.getItem("client_id"),
      status: "all",
      skip: 0,
      limit: 100,
    };
    console.log("Fetching outlets with params:", params);
    const response = await fetchOutlets(params);
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
    displayMapping: { heading: "username", sub: "usernumber" },
  },
  {
    label: "Select Outlets",
    description: "Select outlets to map to the users",
    key: "outlets",
    fetchData: async () => {
      if (!outlets.value.length) await fetchMappedOutlets();
      return outlets.value;
    },
    displayMapping: { heading: "resshortcode", sub: "resid" },
  },
];

function transformDataForBackend(data) {
  const map_params = [];

  data.forEach(([user, outlet]) => {
    const userId = user.id;
    const outletId = outlet.id;
    const client_id = user.client_id || localStorage.getItem("client_id");
    console.log("Mapping user:", userId, "to outlet:", outletId, "for client_id:", client_id);
    if (!userId || !outletId || isNaN(client_id)) return;

    map_params.push({
      user_id: Number(userId),
      outlet_id: Number(outletId),
      client_id: Number(client_id),
    });
  });

  return map_params
}

// Function to show message dialog
function showMessage(message, title = "Message", iconType = "info") {
  messageDialogContent.value = {
    title,
    message,
    icon: iconType,
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
    const response = await mappedUsersOutlets(localStorage.getItem("client_id"));
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

    console.log("Payload being sent:", payload);
    const response = await mapUserToOutlet(payload);
    await fetchMappedUsers();
    await fetchMappedUsers();
    await fetchUsers();
    showMessage(
      response.data?.message || "Mapping completed successfully",
      "Success",
      "success"
    );
  } catch (error) {
    console.error("Error mapping users to outlets:", error);
    showMessage(
      error.response?.data?.message?.response || error.response.data.detail || "Failed to process mapping.",
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


// Unmapping popup state
const showUnmapPopup = ref(false);
const unmapSelections = reactive({
  users: [],
  outlets: [],
});

function showUnmappingPopup() {
  console.log("Opening unmapping popup");
  showUnmapPopup.value = true;
}

function closeUnmapPopup() {
  showUnmapPopup.value = false;
}

// Tabs for unmapping: first select outlet, then show mapped users for that outlet
const unmappingTabs = [
  {
    label: "Select Outlet",
    description: "Select an outlet to unmap users from",
    key: "outlets",
    fetchData: async () => {
      // Show all outlets
      return outlets.value;
    },
    displayMapping: { heading: "resshortcode", sub: "resid" },
  },
  {
    label: "Select Mapped Users",
    description: "Select users mapped to the selected outlet",
    key: "users",
    fetchData: async (_selections) => {
      // Defensive: try to get selections from unmapSelections if not passed
      let selections = _selections;
      if (!selections) {
        // fallback to global reactive unmapSelections
        selections = unmapSelections;
        console.log('[UnmapPopup] users fetchData selections was undefined, using unmapSelections:', selections);
      } else {
        console.log('[UnmapPopup] users fetchData selections:', selections);
      }
      if (!selections || !selections.outlets || selections.outlets.length === 0) {
        console.log('[UnmapPopup] No outlet selected, returning empty array');
        return [];
      }
      const selectedOutlet = selections.outlets[0];
      console.log('[UnmapPopup] Selected outlet:', selectedOutlet);
      console.log('[UnmapPopup] mappedUsers.value:', mappedUsers.value);
      console.log('[UnmapPopup] users.value:', users.value);
      // Find all mappings for this outlet
      const mappingsForOutlet = (mappedUsers.value || []).filter(mu => mu.outlet_id === selectedOutlet.id);
      console.log('[UnmapPopup] mappingsForOutlet:', mappingsForOutlet);
      // For each mapping, find the user and attach mapping_id
      const result = mappingsForOutlet.map(mu => {
        const user = users.value.find(u => u.id === mu.user_id);
        if (user) {
          const userWithMapping = { ...user, mapping_id: mu.mapping_id };
          console.log('[UnmapPopup] Found mapped user:', userWithMapping);
          return userWithMapping;
        }
        console.log('[UnmapPopup] No user found for mapping:', mu);
        return null;
      }).filter(Boolean);
      console.log('[UnmapPopup] Final users to show:', result);
      return result;
    },
    displayMapping: { heading: "username", sub: "usernumber" },
  },
];

// Unmapping logic
async function onUnmappingGenerated(unmapData) {
  mappingLoading.value = true;
  try {
    const unmapPromises = unmapData.map(([user, outlet]) => {
      if (user.mapping_id) {
        return unmapUserFromOutlet(user.mapping_id);
      }
      return Promise.resolve();
    });
    await Promise.all(unmapPromises);
    await fetchMappedUsers();
    await fetchUsers();
    showMessage("Unmapping completed successfully", "Success", "success");
  } catch (error) {
    showMessage(
      error.response?.data?.message?.response || error.response?.data?.detail || "Failed to process unmapping.",
      "Error",
      "error"
    );
  } finally {
    mappingLoading.value = false;
    showUnmapPopup.value = false;
  }
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
  fetchMappedOutlets();
  fetchMappedUsers();
  fetchUsers();
});
</script>

<template>
  <Breadcrumb />
  
    <!-- title="Outlet Mapper" -->
  <DataTable
    :table_data="mappedUsers || []"
    :loading="loadingMappedUsers"
    :error="errorMappedUsers"
    :action_buttons="[{ name: 'Map&nbsp;Users', onClick: showMappingPopup, action: 'user_map', icon: PlusIcon}, { name: 'Unmap&nbsp;Users', onClick: showUnmappingPopup, action: 'unmap', icon: TrashIcon }]"
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

  <!-- Unmapping Popup -->
  <MappingPopup
    v-if="showUnmapPopup"
    :tabs="unmappingTabs"
    v-model:selections="unmapSelections"
    @close="closeUnmapPopup"
    @submit="onUnmappingGenerated"
    :step-mode="true"
  />

  <!-- Show loading spinner when mapping is in progress -->
  <LoadingSpinner v-if="mappingLoading" />

  <!-- Message Dialog -->
  <MessageDialog
    :visible="messageDialogVisible"
    :title="messageDialogContent.title"
    :message="messageDialogContent.message"
    @close="closeMessageDialog"
  />
</template>
    // :icon="messageDialogContent.icon"
