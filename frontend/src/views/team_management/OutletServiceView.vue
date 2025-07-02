<script setup>
import { ref, onMounted, reactive } from "vue";
import { getAllOutlets, getAllServices, getMappedOutletServices, mapOutletToService, unmapOutletFromService } from "@/composables/api/outletServiceMapping";

import DataTable from "@/components/DataTables/DataTable.vue";
import MappingPopup from "@/components/Mapping/MappingPopup.vue";
import LoadingSpinner from "@/components/LoadingSpinner.vue";
import MessageDialog from "@/components/MessageDialog.vue";
import { PencilIcon, PlusIcon, TrashIcon } from "@heroicons/vue/24/outline";
import Breadcrumb from "@/components/Breadcrumb.vue";

const showPopup = ref(false);
const showUnmapPopup = ref(false);
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

// Fetch all outlets
async function fetchOutlets() {
  loadingOutlets.value = true;
  errorOutlets.value = null;
  try {
    const response = await getAllOutlets();
    outlets.value = response?.data || [];
  } catch (err) {
    errorOutlets.value = err.message || "Failed to fetch outlets";
  } finally {
    loadingOutlets.value = false;
  }
}

// Fetch all services
async function fetchAllServices() {
  loadingServices.value = true;
  errorServices.value = null;
  try {
    const response = await getAllServices();
    services.value = response?.data || [];
  } catch (err) {
    errorServices.value = err.message || "Failed to fetch services";
  } finally {
    loadingServices.value = false;
  }
}

// Fetch mapped outlet-service pairs
async function fetchMappedServices() {
  loadingMappedServices.value = true;
  errorMappedServices.value = null;
  try {
    const response = await getMappedOutletServices();
    mappedServices.value = response?.data || [];
  } catch (err) {
    errorMappedServices.value = err.message || "Failed to fetch mapped services";
  } finally {
    loadingMappedServices.value = false;
  }
}

function handleToolbarAction(action) {
  if (typeof action.onClick === "function") action.onClick();
}

// Mapping tabs: select outlets, then services
const mappingTabs = [
  {
    label: "Select Outlets",
    description: "Select outlets to map to the services",
    key: "outlets",
    fetchData: async () => {
      if (!outlets.value.length) await fetchOutlets();
      return outlets.value;
    },
    displayMapping: { heading: "resshortcode", sub: "resid" },
  },
  {
    label: "Select Services",
    description: "Select services to map to the outlets",
    key: "services",
    fetchData: async () => {
      if (!services.value.length) await fetchAllServices();
      return services.value;
    },
    displayMapping: { heading: "servicename", sub: "servicevariant" },
  },
];

// Unmapping state and logic (like UserServiceView)
// (showUnmapPopup already declared above)
// Only declare unmapSelections here
const unmapSelections = reactive({
  outlets: [],
  services: [],
});

const unmappingTabs = [
  {
    label: "Select Outlet",
    description: "Select an outlet to unmap services from",
    key: "outlets",
    fetchData: async () => {
      // Only show outlets that have at least one mapped service
      const mappedOutletIds = new Set(
        (mappedServices.value || []).map(ms =>
          ms.outlet_id ?? ms.id ?? (ms.outlet && ms.outlet.id) ?? ms.resid ?? ms.resshortcode
        )
      );
      return outlets.value.filter(outlet =>
        mappedOutletIds.has(outlet.id) ||
        mappedOutletIds.has(outlet.resid) ||
        mappedOutletIds.has(outlet.resshortcode)
      );
    },
    displayMapping: { heading: "resshortcode", sub: "resid" },
  },
  {
    label: "Select Mapped Services",
    description: "Select services mapped to the selected outlet",
    key: "services",
    fetchData: async (_selections) => {
      let selections = _selections || unmapSelections;
      if (!selections || !selections.outlets || selections.outlets.length === 0) {
        return [];
      }
      const selectedOutlet = selections.outlets[0];
      const outletId = selectedOutlet.id;
      // Find all mapped services for this outlet
      // Try to match by outlet id or resshortcode/resid if needed
      return (mappedServices.value || []).filter(ms => {
        // Try to match by id, resshortcode, resid, or aggregator if needed
        return (
          ms.outlet_id == outletId ||
          ms.id == outletId ||
          (ms.outlet && ms.outlet.id == outletId) ||
          (ms.resshortcode && selectedOutlet.resshortcode && ms.resshortcode === selectedOutlet.resshortcode) ||
          (ms.resid && selectedOutlet.resid && ms.resid === selectedOutlet.resid)
        );
      });
    },
    displayMapping: { heading: "servicename", sub: "servicevariant" },
  },
];

function transformDataForBackend(data) {
  // data: array of [outlet, service] pairs
  const map_params = [];
  const seen = new Set();
  data.forEach(([outlet, service]) => {
    if (!outlet || !service) return;
    const outletId = outlet.id;
    const serviceId = service.id;
    const clientId = outlet.client_id;
    if (!outletId || isNaN(serviceId) || isNaN(clientId)) return;
    const key = `${outletId}-${serviceId}`;
    if (seen.has(key)) return;
    seen.add(key);
    map_params.push({
      outlet_id: outletId,
      service_id: serviceId,
      client_id: clientId,
    });
  });
  return map_params;
}

// Show message dialog
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

// Mapping submit handler (robust for bulk, handles errors gracefully)
async function onMappingGenerated(mappings) {
  mappingLoading.value = true;
  try {
    let payload = await transformDataForBackend(mappings);
    if (!payload.length) {
      showMessage("No mappings selected.", "Info", "info");
      return;
    }
    let response, errorMsg;
    if (payload.length === 1) {
      try {
        response = await mapOutletToService(payload);
      } catch (err) {
        errorMsg = err?.response?.data?.message?.response || err?.response?.data?.detail || err?.message;
      }
    } else {
      // Multiple mappings: try all, ignore duplicates/errors if already mapped
      const results = await Promise.allSettled(payload.map(p => mapOutletToService([p])));
      response = results.find(r => r.status === "fulfilled");
      errorMsg = results.find(r => r.status === "rejected")?.reason?.response?.data?.message?.response || results.find(r => r.status === "rejected")?.reason?.response?.data?.detail || results.find(r => r.status === "rejected")?.reason?.message;
    }
    await fetchMappedServices();
    if (response) {
      showMessage(
        response?.value?.data?.message || response?.data?.message || "Mapping completed successfully",
        "Success",
        "success"
      );
    } else {
      showMessage(
        errorMsg || "Failed to process mapping.",
        "Error",
        "error"
      );
    }
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

// Unmapping submit handler (robust for bulk, handles errors gracefully)
async function onUnmappingGenerated(unmapData) {
  mappingLoading.value = true;
  try {
    // For each selected [outlet, service] pair, find the mapping_id in mappedServices
    const mappingIds = new Set();
    // For each selected [outlet, service] pair, find ALL matching mapping_ids in mappedServices
    unmapData.forEach(([outlet, service]) => {
      if (!outlet || !service) return;
      // Find all mappings in mappedServices that match both outlet and service
      const matches = (mappedServices.value || []).filter(ms => {
        const outletMatch = ms.outlet_id == outlet.id || ms.id == outlet.id || (ms.outlet && ms.outlet.id == outlet.id) || (ms.resshortcode && outlet.resshortcode && ms.resshortcode === outlet.resshortcode) || (ms.resid && outlet.resid && ms.resid === outlet.resid);
        const serviceMatch = ms.service_id == service.id || ms.service == service.service || ms.service === service.servicename;
        return outletMatch && serviceMatch;
      });
      if (matches.length) {
        matches.forEach(m => {
          if (m.mapping_id) mappingIds.add(m.mapping_id);
        });
      } else if (service.mapping_id) {
        mappingIds.add(service.mapping_id);
      }
    });
    if (mappingIds.size === 0) {
      showMessage("No mappings selected for unmapping.", "Info", "info");
      return;
    }
    // Try all unmap requests, but ignore errors if mapping is already deleted or not found
    console.log("Unmapping IDs:", Array.from(mappingIds));
    const results = await Promise.allSettled(Array.from(mappingIds).map(mid => unmapOutletFromService(mid)));
    // If at least one was successful, treat as success
    const anySuccess = results.some(r => r.status === "fulfilled");
    await fetchMappedServices();
    if (anySuccess) {
      showMessage("Unmapping completed successfully", "Success", "success");
    } else {
      // Show the first error message
      const firstError = results.find(r => r.status === "rejected");
      showMessage(
        firstError?.reason?.response?.data?.message?.response || firstError?.reason?.response?.data?.detail || firstError?.reason?.message || "Failed to process unmapping.",
        "Error",
        "error"
      );
    }
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

function showMappingPopup() {
  showPopup.value = true;
}

function closePopup() {
  showPopup.value = false;
}

function showUnmappingPopup() {
  showUnmapPopup.value = true;
}

function closeUnmapPopup() {
  showUnmapPopup.value = false;
}

const selections = reactive({
  outlets: [],
  services: [],
});

const mappedHeaders = {
  mapping_id: "Mapping ID",
  resid: "Res ID",
  aggregator: "Aggregator",
  subzone: "Subzone",
  resshortcode: "Shortcode",
  city: "City",
  is_active: "Is Active",
  servicename: "Service Name",
  servicevariant: "Service Variant",
};

onMounted(() => {
  fetchOutlets();
  fetchAllServices();
  fetchMappedServices();
});
</script>

<template>
  <Breadcrumb/>

<DataTable
    :table_data="mappedServices"
    :table_headers="mappedHeaders"
    :loading="loadingMappedServices"
    :error="errorMappedServices"
    :action_buttons="[
      { name: 'Map\u00A0Services', onClick: showMappingPopup, action: 'service_map', icon: PlusIcon },
      { name: 'Unmap\u00A0Services', onClick: showUnmappingPopup, action: 'unmap', icon: TrashIcon }
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