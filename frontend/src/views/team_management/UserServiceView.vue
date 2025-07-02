<script setup>
import { ref, onMounted, reactive } from "vue";
import { getMappedUsers } from "@/composables/api/userToOutletMappings";
import { getMappedServices, mapUserToService, unmapUserFromService, getAllServices } from "@/composables/api/userToServiceMappings";
import { fetchUsers as fetchUsersApi } from "@/composables/api/teamManagement";
import DataTable from "@/components/DataTables/DataTable.vue";
import MappingPopup from "@/components/Mapping/MappingPopup.vue";
import LoadingSpinner from "@/components/LoadingSpinner.vue";
import MessageDialog from "@/components/MessageDialog.vue";
import { PencilIcon, PlusIcon, TrashIcon } from "@heroicons/vue/24/outline";
import Breadcrumb from "@/components/Breadcrumb.vue";

const showPopup = ref(false);
const showUnmapPopup = ref(false);
const unmapSelections = reactive({
  users: [],
  services: [],
});
function showUnmappingPopup() {
  console.log("Opening unmapping popup");
  showUnmapPopup.value = true;
}

function closeUnmapPopup() {
  showUnmapPopup.value = false;
}
// Tabs for unmapping: first select user, then show mapped services for that user
const unmappingTabs = [
  {
    label: "Select User",
    description: "Select a user to unmap services from",
    key: "users",
    fetchData: async () => {
      return users.value;
    },
    displayMapping: { heading: "username", sub: "usernumber" },
  },
  {
    label: "Select Mapped Services",
    description: "Select services mapped to the selected user",
    key: "services",
    fetchData: async (_selections) => {
      let selections = _selections || unmapSelections;
      if (!selections || !selections.users || selections.users.length === 0) {
        return [];
      }
      const selectedUser = selections.users[0];
      const userId = selectedUser.id;
      // Find all mapped services for this user
      return (mappedUsers.value || []).filter(mu => {
        // Defensive: support both user_id and user.id
        return (
          mu.user_id == userId ||
          (mu.user && mu.user.id == userId)
        );
      });
    },
    displayMapping: { heading: "service", sub: "service_variant" },
  },
];
// Unmapping logic
async function onUnmappingGenerated(unmapData) {
  mappingLoading.value = true;
  try {
    // Collect all unique mapping_ids to unmap
    const mappingIds = new Set();
    unmapData.forEach(([user, service]) => {
      // The second item is the mapped service object (from the second tab)
      if (!service) return;
      if (Array.isArray(service.mapping_ids)) {
        service.mapping_ids.forEach(mid => {
          if (mid) mappingIds.add(mid);
        });
      } else if (service.mapping_id) {
        mappingIds.add(service.mapping_id);
      }
    });
    const unmapPromises = Array.from(mappingIds).map(mid => unmapUserFromService(mid));
    await Promise.all(unmapPromises);
    await fetchMappedUsers();
    showMessage("Unmapping completed successfully", "Success", "success");
  } catch (error) {
    showMessage(
      error?.response?.data?.message?.response || error?.response?.data?.detail || "Failed to process unmapping.",
      "Error",
      "error"
    );
  } finally {
    mappingLoading.value = false;
    showUnmapPopup.value = false;
  }
}

const services = ref([]);
const users = ref([]);
const mappedUsers = ref([]);

const loadingServices = ref(false);
const loadingUsers = ref(false);
const loadingMappedUsers = ref(false);

const errorServices = ref(null);
const errorUsers = ref(null);
const errorMappedUsers = ref(null);

const mappingLoading = ref(false);

const messageDialogVisible = ref(false);
const messageDialogContent = ref({
  title: "",
  message: "",
  icon: "",
});

async function fetchUsers() {
  loadingUsers.value = true;
  errorUsers.value = null;
  try {
    const params = {
      client_id: localStorage.getItem("client_id"),
      skip: 0,
      limit: 100,
    };
    const response = await fetchUsersApi(params);
    users.value = response?.data || [];
    console.log("Fetched users:", users.value);
  } catch (err) {
    errorUsers.value = err.message || "Failed to fetch";
  } finally {
    loadingUsers.value = false;
  }
}

async function fetchAllServices() {
  console.log("Fetching all services...");
  loadingServices.value = true;
  errorServices.value = null;
  try {
    const response = await getAllServices();
    services.value = response.data;
    console.log("Mapped services:", services.value);
  } catch (err) {
    errorServices.value = err.message || "Failed to fetch";
  } finally {
    loadingServices.value = false;
  }
}

function handleToolbarAction(action) {
  if (typeof action.onClick === "function") action.onClick();
}

// Tabs for mapping: first select user, then select services to map
const mappingTabs = [
  {
    label: "Select Users",
    description: "Select users to map to the services",
    key: "users",
    fetchData: async () => {
      if (!users.value.length) await fetchUsers();
      return users.value;
    },
    displayMapping: { heading: "username", sub: "usernumber" },
  },
  {
    label: "Select Services",
    description: "Select services to map to the users",
    key: "services",
    fetchData: async () => {
      if (!services.value.length) await fetchAllServices();
      return services.value;
    },
    displayMapping: { heading: "servicename", sub: "servicevariant" },
  }
];

function transformDataForBackend(data) {
  // data: array of [user, service] pairs
  const map_params = [];
  // Collect unique user-service pairs
  const seen = new Set();
  data.forEach(([user, service]) => {
    if (!user || !service) return;
    const userId = user.id;
    const serviceId = service.id;
    const clientId = user.client_id;
    if (!userId || isNaN(serviceId) || isNaN(clientId)) return;
    const key = `${userId}-${serviceId}`;
    if (seen.has(key)) return;
    seen.add(key);
    map_params.push({
      user_id: userId,
      service_id: serviceId,
      client_id: clientId,
    });
  });
  return map_params;
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

function closeMessageDialog() {
  messageDialogVisible.value = false;
}

async function fetchMappedUsers() {
  console.log("Fetching mapped users...");
  loadingMappedUsers.value = true;
  errorMappedUsers.value = null;
  try {
    const response = await getMappedServices();
    mappedUsers.value = response.data;
  } catch (err) {
    errorMappedUsers.value = err.message || "Failed to fetch";
  } finally {
    loadingMappedUsers.value = false;
  }
}

async function onMappingGenerated(mappings) {
  mappingLoading.value = true;
  try {
    // Compose payload according to your API's requirements
    let payload = await transformDataForBackend(mappings);
    const response = await mapUserToService(payload);
    showMessage(
      response?.data?.message || "Mapping completed successfully",
      "Success",
      "success"
    );
    await fetchMappedUsers();
  } catch (error) {
    showMessage(
      error?.response?.data?.message?.response || error?.response?.data?.detail || error?.message || "Failed to process mapping.",
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
  services: [],
});

const mappedHeaders = {
  mapping_id: "Mapping ID",
  username: "User Name",
  usernumber: "Number",
  useremail: "Email",
  service: "Service",
  service_variant: "Service Variant",
  service_id: "Service ID",
  created_at: "Created At",
};

onMounted(() => {
  fetchUsers();
  fetchAllServices();
  fetchMappedUsers();
});
</script>

<template>
  <Breadcrumb />

  <DataTable
    :table_headers="mappedHeaders"
    :table_data="mappedUsers"
    :loading="loadingMappedUsers"
    :error="errorMappedUsers"
    :action_buttons="[
      { name: 'Map&nbsp;Users', onClick: showMappingPopup, action: 'user_map', icon: PlusIcon },
      { name: 'Unmap&nbsp;Users', onClick: showUnmappingPopup, action: 'unmap', icon: TrashIcon }
    ]"
    @action-click="handleToolbarAction"
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
    :title="'Bulk Unassign Mappings'"
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
    :icon="messageDialogContent.icon"
    @close="closeMessageDialog"
  />
</template>