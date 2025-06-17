<script setup>
import { ref, onMounted } from "vue";
import Breadcrumb from "@/components/Breadcrumb.vue";
import DataTable from "@/components/DataTables/DataTable.vue";
import MessageDialog from "@/components/MessageDialog.vue";
import EditOutletDialog from "@/components/OutletManagement/EditOutletDialog.vue";
import { fetchOutlets as fetchOutletsApi, deleteOutlet } from "@/composables/api/brandManagementApi";

console.log("Current user email:", sessionStorage.getItem("email"));
console.log("Current user client_id:", sessionStorage.getItem("client_id"));

const outlets = ref([]);
const loading = ref(false);
const error = ref(null);

const messageDialogVisible = ref(false);
const messageDialogContent = ref({
  title: "",
  message: "",
  icon: "",
});

const editDialogVisible = ref(false);
const editRow = ref(null);

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

async function fetchOutlets() {
  loading.value = true;
  error.value = null;
  try {
    const params = {
      client_id:  sessionStorage.getItem("client_id"),
      status: "all",
      skip: 0,
      limit: 100,
    };
    console.log("Fetching outlets with params:", params);

    const response = await fetchOutletsApi(params);
    outlets.value = response?.data || [];
    console.log("Fetched outlets:", outlets.value);
  } catch (err) {
    error.value = err.message || "Failed to fetch";
  } finally {
    loading.value = false;
  }
}

async function messageParse(outlet_id) {
  const outlet = outlets.value.find(o => o.id === outlet_id);
  if (!outlet) {
    showMessage(`Outlet ID ${outlet_id} not found.`, "Error", "error");
    return null; // better to return null for error
  }
  const message = `${outlet.aggregator} - ${outlet.resshortcode}`;
  return message;
}

async function deleteOutletById(outletId) {
  try {
    await deleteOutlet(outletId);

    // Get the aggregator-shortcode message
    const message = await messageParse(outletId);
    if (message) {
      showMessage(`${message} deleted successfully.`, "Success", "success");
    }
    // Optionally, if messageParse failed, you may want to adjust the message above

    fetchOutlets();
  } catch (err) {
    const message = await messageParse(outletId);
    if (message) {
      showMessage(`Failed to delete ${message} : ${err.message}`, "Error", "error");
    } else {
      showMessage(`Failed to delete Outlet ID ${message}: ${err.message}`, "Error", "error");
    }
  }
}

function handleToolbarAction(action) {
  if (action.action === "show_message") {
    showMessage("This is a demo message!", "Demo", "info");
  }
}

const editAllowed = {
  id: false,
  aggregator: true,
  resid: true,
  subzone: true,
  resshortcode: false,
  city: true,
  outletnumber: true,
  is_active: false,
  created_at: false,
  updated_at: false,
  client: false,
  brand: false,
};

function handleRowAction({ action, row }) {
  if (action.action === "edit") {
    editRow.value = { ...row };
    editDialogVisible.value = true;
  } else if (action.action === "delete") {
    deleteOutletById(row.id);
  }else {
    console.warn("Unhandled row action:", action);
  }
}

function handleEditSave(editedData) {
  console.log("Edited data:", editedData);
  editDialogVisible.value = false;
  fetchOutlets();
}

onMounted(() => {
  fetchOutlets();
});

const columns = [
  { label: "ID", key: "id" },
  { label: "Aggregator", key: "aggregator" },
  { label: "ResID", key: "resid" },
  { label: "Subzone", key: "subzone" },
  { label: "Shortcode", key: "resshortcode" },
  { label: "City", key: "city" },
  { label: "Outlet Number", key: "outletnumber" },
  { label: "Active", key: "is_active" },
  { label: "Created At", key: "created_at" },
  { label: "Updated At", key: "updated_at" },
  { label: "Client Name", key: "client.name" },
  { label: "Brand Name", key: "brand.name" },
];

// Example row action buttons
const dataActionButtons = [
  { name: "Edit", action: "edit", color: "blue" },
  { name: "Delete", action: "delete", color: "red" },
];

const mapHeaders = {
  aggregator: "Aggregator",
  resid: "Res ID",
  subzone: "Subzone",
  resshortcode: "Shortcode",
  city: "City",
  outletnumber: "Outlet Number",
  is_active: "Active",
};
</script>

<template>
  <Breadcrumb />

  <DataTable
    title="Outlet Management"
    :table_data="outlets"
    :columns="columns"
    :loading="loading"
    :error="error"
    :table_headers="mapHeaders"
    :action_buttons="[
      {
        name: 'Add Outlets',
        onClick: () => showMessage('This is a demo message!', 'Demo', 'info'),
        action: 'add_outlets',
      },
    ]"
    :data_action_buttons="dataActionButtons"
    @action-click="handleToolbarAction"
    @row-action="handleRowAction"
    :csv_download="true"
  />

  <MessageDialog
    :visible="messageDialogVisible"
    :title="messageDialogContent.title"
    :message="messageDialogContent.message"
    :icon="messageDialogContent.icon"
    @close="closeMessageDialog"
  />

  <EditOutletDialog
    :visible="editDialogVisible"
    :row="editRow"
    :edit-allowed="editAllowed"
    :map-headers="mapHeaders"
    @close="editDialogVisible = false"
    @save="handleEditSave"
  />
</template>
