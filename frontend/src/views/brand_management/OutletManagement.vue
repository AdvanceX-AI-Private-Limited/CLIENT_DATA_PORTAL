<script setup>
import { ref, onMounted } from 'vue'
import Breadcrumb from "@/components/Breadcrumb.vue";
import DataTable from "@/components/DataTables/DataTable.vue";
import MessageDialog from "@/components/MessageDialog.vue";
import EditOutletDialog from "@/components/OutletManagement/EditOutletDialog.vue";
import { currentUserData } from '@/stores/currentUser';
import { storeToRefs } from "pinia";
import { fetchOutlets as fetchOutletsApi } from '@/composables/api/brandManagementApi';

const { email, client_id } = currentUserData();

console.log("Current user email:", email.value);
console.log("Current user client_id:", client_id.value);

const outlets = ref([])
const loading = ref(false)
const error = ref(null)

const messageDialogVisible = ref(false)
const messageDialogContent = ref({
  title: "",
  message: "",
  icon: "",
})

const editDialogVisible = ref(false)
const editRow = ref(null)

function showMessage(message, title = "Message", icon = "") {
  messageDialogContent.value = {
    title,
    message,
    icon,
  }
  messageDialogVisible.value = true
}
function closeMessageDialog() {
  messageDialogVisible.value = false
}

async function fetchOutlets() {
  loading.value = true
  error.value = null
  try {
    const params = {
	  client_id: 67,
	  status: 'all',
	  skip: 0,
	  limit: 100,
	}
	console.log("Fetching outlets with params:", params);
	
	const response = await fetchOutletsApi(params);
    outlets.value = response?.data || []
	console.log("Fetched outlets:", outlets.value);
  } catch (err) {
    error.value = err.message || "Failed to fetch"
  } finally {
    loading.value = false
  }
}

function handleToolbarAction(action) {
  if (action.action === 'show_message') {
    showMessage('This is a demo message!', 'Demo', 'info')
  }
}

const editAllowed = {
  id: false,
  aggregator: true,
  resid: true,
  subzone: true,
  resshortcode: true,
  city: true,
  outletnumber: true,
  is_active: true,
  created_at: false,
  updated_at: false,
  client: false,
  brand: false,
}

function handleRowAction({ action, row }) {
  if (action.action === 'edit') {
    editRow.value = { ...row }
    editDialogVisible.value = true
  } else if (action.action === 'delete') {
    showMessage(`Delete clicked for Outlet ID: ${row.id}`, 'Delete', 'warning')
  }
}

function handleEditSave(editedData) {
  console.log("Edited data:", editedData)
  editDialogVisible.value = false
}

onMounted(() => {
  fetchOutlets()
})

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
  { label: "Brand Name", key: "brand.name" }
]

// Example row action buttons
const dataActionButtons = [
  { name: 'Edit', action: 'edit', color: 'blue' },
  { name: 'Delete', action: 'delete', color: 'red' }
];

const mapHeaders = {
  id: "ID",
  aggregator: "Aggregator",
  resid: "ResID",
  subzone: "Subzone",
  resshortcode: "Shortcode",
  city: "City",
  outletnumber: "Outlet Number",
  is_active: "Active",
}

</script>

<template>
  <Breadcrumb/>

  <DataTable
    title="Outlet Management"
    :table_data="outlets"
    :columns="columns"
    :loading="loading"
    :error="error"
    :table_headers="mapHeaders"
    :action_buttons="[{ name: 'Show Message', onClick: () => showMessage('This is a demo message!', 'Demo', 'info'), action: 'show_message' }]"
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
