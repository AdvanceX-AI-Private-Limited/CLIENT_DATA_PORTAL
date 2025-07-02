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
      // Try all possible keys for matching
      const outletKeys = ['id', 'resid', 'outlet_id'];
      const mappedUserKeys = ['outlet_id', 'resid', 'id', 'outlet', 'outletId', 'res_id'];
      // Build all possible string values for selectedOutlet
      const outletIdsToMatch = outletKeys.map(k => selectedOutlet[k]).filter(Boolean).map(String);
      // Try to match any mappedUser key to any selectedOutlet id
      const mappingsForOutlet = (mappedUsers.value || []).filter(mu => {
        let matched = false;
        for (const muKey of mappedUserKeys) {
          if (mu[muKey] && outletIdsToMatch.includes(String(mu[muKey]))) {
            matched = true;
            break;
          }
        }
        // Check for nested outlet object (e.g., mu.outlet.id)
        if (!matched && mu.outlet && typeof mu.outlet === 'object') {
          for (const k of outletKeys) {
            if (mu.outlet[k] && outletIdsToMatch.includes(String(mu.outlet[k]))) {
              matched = true;
              break;
            }
          }
        }
        return matched;
      });
      let result = [];
      mappingsForOutlet.forEach(mu => {
        if (Array.isArray(mu.users)) {
          mu.users.forEach(userObj => {
            let username, mapping_id, mapping_ids;
            if (typeof userObj === 'string') {
              username = userObj;
              mapping_id = mu.mapping_id;
            } else {
              username = userObj.username;
              mapping_id = userObj.mapping_id;
              mapping_ids = userObj.mapping_ids;
            }
            const user = users.value.find(u => u.username === username);
            if (user) {
              if (!mapping_id && mu.mapping_id) mapping_id = mu.mapping_id;
              if (!mapping_ids && mu.mapping_ids) mapping_ids = mu.mapping_ids;
              if (!mapping_id && user.mapping_id) mapping_id = user.mapping_id;
              if (!mapping_ids && user.mapping_ids) mapping_ids = user.mapping_ids;
              if (!mapping_id && !mapping_ids) {
                mapping_id = null;
                mapping_ids = null;
              }
              const userWithMapping = { ...user, mapping_id, mapping_ids };
              result.push(userWithMapping);
            }
          });
        }
      });
      return result;
    },
    displayMapping: { heading: "username", sub: "usernumber" },
  },
];

// Unmapping logic
async function onUnmappingGenerated(unmapData) {
  mappingLoading.value = true;
  try {
    const unmapPromises = [];
    unmapData.forEach(([outlet, user]) => {
      if (!user) return;
      if (Array.isArray(user.mapping_ids)) {
        user.mapping_ids.forEach(mid => {
          if (mid) unmapPromises.push(unmapUserFromOutlet(mid));
        });
      } else if (user.mapping_id) {
        unmapPromises.push(unmapUserFromOutlet(user.mapping_id));
      }
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

const mapHeaders = {
  res_id: "Res ID",
  brand: "Brand",
  aggregator: "Aggregator",
  // subzone: "Subzone",
  shortcode: "Shortcode",
  users: "Users",
};

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
    :table_headers="mapHeaders"
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