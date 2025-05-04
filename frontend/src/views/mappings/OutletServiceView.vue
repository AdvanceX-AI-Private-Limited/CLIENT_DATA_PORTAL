<script setup>
import { ref, onMounted, reactive } from "vue";
import { getOutlets, getServices, mappedServicesOutlets, mapServiceToOutlet } from "@/composables/api/testApi";
import DataTable from "@/components/DataTables/DataTable.vue";
import MappingPopup from "@/components/Mapping/MappingPopup.vue";
import LoadingSpinner from "@/components/LoadingSpinner.vue";
import MessageDialog from "@/components/MessageDialog.vue";
import { PencilIcon, TrashIcon } from "@heroicons/vue/24/outline";

const showPopup = ref(false);

const outlets = ref([]);
const services = ref([]);
const mappedServices = ref([]);

const loadingOutlets = ref(false);
const loadingServices = ref(false);
const loadingMappedServices = ref(false);

const errorOutlets = ref(null);
const errorServices = ref(null);
const errorMappedServices = ref(null);

const mappingLoading = ref(false);

const messageDialogVisible = ref(false);
const messageDialogContent = ref({
  title: "",
  message: "",
  icon: "",
});

const fetchServices = async () => {
  console.log("Fetching services...");
  loadingServices.value = true;
  errorServices.value = null;
  try {
    const response = await getServices();
    services.value = response.data;
    console.log("Services:", services.value);
  } catch (err) {
    errorServices.value = err.message || "Failed to fetch";
  } finally {
    loadingServices.value = false;
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
    label: "Select Outlets",
    description: "Select outlets to map to the services",
    key: "outlets",
    fetchData: async () => {
      if (!outlets.value.length) await fetchMappedOutlets();
      return outlets.value;
    },
    displayMapping: { heading: "res_shortcode", sub: "res_id" },
  },
  {
    label: "Select Services",
    description: "Select services to map to the outlets",
    key: "services",
    fetchData: async () => {
      if (!services.value.length) await fetchServices();
      return services.value;
    },
    displayMapping: { heading: "service_name", sub: "service_variant" },
  },
];

function transformDataForBackend(data) {
  console.log("data", data);
  const redIdSet = new Set();
  const serviceMap = new Map();

  data.forEach(([service, outlet]) => {
    const serviceNumber = service.service_number;
    const serviceName = service.service_name;
    const resId = parseInt(outlet.res_id);

    if (!serviceNumber || !serviceName || isNaN(resId)) return;

    redIdSet.add(resId);

    // Use Map to avoid duplicate services
    if (!serviceMap.has(serviceNumber)) {
      serviceMap.set(serviceNumber, { name: serviceName, number: serviceNumber });
    }
  });

  return {
    red_id: Array.from(redIdSet),
    services: Array.from(serviceMap.values()),
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

async function fetchMappedServices() {
  console.log("Fetching mapped services...");
  loadingMappedServices.value = true;
  errorMappedServices.value = null;
  try {
    const response = await mappedServicesOutlets();
    mappedServices.value = response.data;
  } catch (err) {
    errorMappedServices.value = err.message || "Failed to fetch";
  } finally {
    loadingMappedServices.value = false;
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
    const response = await mapServiceToOutlet(payload);
    showMessage(
      response.data?.message || "Mapping completed successfully",
      "Success",
      "success"
    );
    await fetchMappedServices();
  } catch (error) {
    console.error("Error mapping services to outlets:", error);
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
  services: [],
  outlets: [],
});

onMounted(() => {
  fetchServices();
  fetchMappedOutlets();
  fetchMappedServices();
});
</script>

<template>
  <DataTable
    title="Outlet To Service"
    :table_data="mappedServices"
    :loading="loadingMappedServices"
    :error="errorMappedServices"
    :action_buttons="[{ name: 'Map Services', onClick: showMappingPopup, action: 'service_map' }]"
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