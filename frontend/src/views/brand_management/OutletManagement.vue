<script setup>
import { ref, onMounted , reactive, watch } from "vue";
import Breadcrumb from "@/components/Breadcrumb.vue";
import DataTable from "@/components/DataTables/DataTable.vue";
import MessageDialog from "@/components/MessageDialog.vue";
import EditDialog from "@/components/OutletManagement/EditDialog.vue";
import AddUsersPopup from "@/components/Mapping/AddUsersPopup.vue";
import { fetchOutlets as fetchOutletsApi, deleteOutlet, addOutlet } from "@/composables/api/brandManagementApi";
import { PencilIcon, TrashIcon } from "@heroicons/vue/24/outline";
import { useMessageDialogStore } from '@/stores/messageDialog';
import { updateOutlet } from "@/composables/api/brandManagementApi";

const dialog = useMessageDialogStore();

console.log("Current user email:", localStorage.getItem("email"));
console.log("Current user client_id:", localStorage.getItem("client_id"));

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
      client_id:  localStorage.getItem("client_id"),
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
  console.log("Toolbar action:", action);
  if (action.action === "add_outlets") {
    console.log("Adding new outlet");
    showAddOutletPopup();
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

watch(editDialogVisible, (newValue) => {
  if (!newValue) {
    updateApiError.value = null;
    updateApiSuccess.value = false;
  }
});

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
  {
    name: "Edit",
    action: "edit",
    icon: PencilIcon, // Add the PencilIcon
    class: "text-blue-600 hover:text-blue-800",
    tooltip: "Edit Outlet",
  },
  {
    name: "Delete",
    action: "delete",
    icon: TrashIcon, // Add the TrashIcon
    class: "text-red-600 hover:text-red-800",
    tooltip: "Delete Outlet",
  },
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

const showPopup = ref(false);

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

function closePopup() {
  console.log("Closing popup");
  showPopup.value = false;
}

function showAddOutletPopup() {
  console.log("Opening popup");
  showPopup.value = true;
}

// Outlet form state
const isExpanded = ref(false);
const outletsReview = ref([]);
const outletForm = reactive({
  aggregator: "",
  resid: "",
  subzone: "",
  city: "",
  outletnumber: "",
  is_active: true,
  clientid: localStorage.getItem("client_id")
});

// Add outlet to review list
const addOutletToReview = () => {
  // Only check visible fields
  for (const field of visibleOutletInputFields.value) {
    if (
      outletForm[field.key] === "" ||
      outletForm[field.key] === null ||
      outletForm[field.key] === undefined
    ) {
      showMessage("Please fill all the fields.", "Error", "error");
      return;
    }
  }
  outletsReview.value.unshift({ ...outletForm });
  // Reset only visible fields
  visibleOutletInputFields.value.forEach(field => {
    outletForm[field.key] = "";
  });
  isExpanded.value = false;
};

// Remove outlet from review list
const deleteOutletReview = (index) => {
  outletsReview.value.splice(index, 1);
};

// Submit all outlets in review list
const submitOutlets = async () => {
  if (!outletsReview.value.length) {
    showMessage("No outlets to submit.", "Error", "error");
    return;
  }
  try {
    await addOutlet(outletsReview.value);
    showMessage("Outlets added successfully!", "Success", "success");
    outletsReview.value = [];
    fetchOutlets();
    showPopup.value = false;
  } catch (err) {
    showMessage(err.message || "Failed to add outlets.", "Error", "error");
  }
};

function toggleDropdown() {
  isExpanded.value = !isExpanded.value;
}

const allowedOutletInputs = {
  aggregator: true,
  resid: true,
  subzone: true,
  city: true,
  outletnumber: true,
  is_active: false,
  clientid: false,
  brandid:  false,
}

const outletInputFields = [
  { key: "aggregator", placeholder: "Aggregator", type: "text" },
  { key: "resid", placeholder: "Res ID", type: "text" },
  { key: "subzone", placeholder: "Subzone", type: "text" },
  { key: "city", placeholder: "City", type: "text" },
  { key: "outletnumber", placeholder: "Outlet Number", type: "text" },
  // Add more fields here if needed
];

import { computed } from "vue";

const visibleOutletInputFields = computed(() =>
  outletInputFields.filter(f => allowedOutletInputs[f.key])
);
const isOddVisibleFields = computed(() => visibleOutletInputFields.value.length % 2 === 1);

watch(
  outletsReview,
  (newList) => {
    if (newList.length === 0) {
      isExpanded.value = true;
    }
  },
  { immediate: true }
);

function showError(message, title = "Error") {
  dialog.show({
    message: message,
    title: title,
    icon: "error"
  });
}

const updateApiError = ref(null);
const updateApiSuccess = ref(false);

async function handleUpdateApi(payload) {
  loading.value = true;
  updateApiError.value = null;
  updateApiSuccess.value = false;

  console.log("Edit row:", editRow.value);
  payload['client_id'] = editRow.value.client_id;
  console.log("Submitting update with params:", payload);

  try {
    const params = { outlet_id: editRow.value.id, payload };
    console.log("Updating outlet with params:", params);
    const response = await updateOutlet(params);

    if (response.status === 200) {
      updateApiSuccess.value = true;
      console.log("Update successful:", response.data);
      handleEditSave(response.data);
    } else {
      showError(response?.data?.message || "Unexpected response from server.");
    }
  } catch (err) {
    // Handle network or API errors
    let errorMsg = "Failed to update. Please try again.";
    if (err?.response?.data?.message) {
      errorMsg = err.response.data.message;
    } else if (err?.message) {
      errorMsg = err.message;
    }
    updateApiError.value = errorMsg;
    showError(errorMsg);
  } finally {
    loading.value = false;
  }
}
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
    :action_buttons=" [
      {
        name: 'Add Outlets',
        onClick: showAddOutletPopup,
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

  <EditDialog
    :visible="editDialogVisible"
    :row="editRow"
    :edit-allowed="editAllowed"
    :map-headers="mapHeaders"
    @close="editDialogVisible = false"
    @save="handleEditSave"
    @submit="handleUpdateApi"
    :loading="loading"
    :api-error="updateApiError"
    :api-success="updateApiSuccess"
    :function-call="handleUpdateApi"
  />

  <AddUsersPopup
    v-if="showPopup"
    title="Add Outlets"
    :closeBtnBar="true"
    :action_buttons=" [
      { name: 'Submit', onClick: submitOutlets }
    ]"
    @close="closePopup"
  >
    <div class="my-3 mx-2 h-full overflow-y-auto no-scrollbar">
      <!-- Dropdown Add Form -->
      <div id="dropdown" class="sticky top-0 z-10 bg-white pb-2">
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
            <line x1="12" y1="5" x2="12" y2="19" stroke-linecap="round" />
            <line x1="5" y1="12" x2="19" y2="12" stroke-linecap="round" />
          </svg>
          <span>{{ isExpanded ? 'Hide Form' : 'Add Outlets' }}</span>
        </button>
        <transition name="slide-expand-tr">
          <div
            v-if="isExpanded"
            class="bg-white shadow-sm rounded-lg p-3 border border-gray-200 space-y-2.5"
          >
            <button @click="toggleDropdown" class="w-full ml-auto rounded-lg bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-500 font-bold py-0.5 hover:text-gray-800 transition-colors">
              Close
            </button>
            <div class="w-full">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-2 items-end">
                <template v-for="(field, idx) in visibleOutletInputFields" :key="field.key">
                  <template v-if="field.key === 'aggregator'">
                    <select
                      v-model="outletForm.aggregator"
                      class="w-full border border-gray-300 rounded-md p-1.5 px-3 mb-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                    >
                      <option value="" disabled>Aggregator</option>
                      <option value="Zomato">Zomato</option>
                      <option value="Swiggy">Swiggy</option>
                    </select>
                  </template>
                  <template v-else>
                    <input
                      :type="field.type"
                      v-model="outletForm[field.key]"
                      :placeholder="field.placeholder"
                      class="w-full border border-gray-300 rounded-md p-1.5 px-3 mb-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </template>
                  <!-- If odd number of fields and this is the last field, place Confirm button in the right cell -->
                  <template v-if="isOddVisibleFields && idx === visibleOutletInputFields.length - 1">
                    <button
                      @click="addOutletToReview"
                      class="px-4 py-1.5 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors shadow mb-2 ml-auto block w-auto"
                      style="min-width: 90px;"
                    >
                      Add
                    </button>
                  </template>
                </template>
                <!-- If even number of fields, show Confirm button in a new row, right side -->
                <template v-if="!isOddVisibleFields">
                  <div></div>
                  <button
                    @click="addOutletToReview"
                    class="px-4 py-1.5 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors shadow mb-2 ml-auto block w-auto"
                    style="min-width: 90px;"
                  >
                    Add
                  </button>
                </template>
              </div>
            </div>
          </div>
        </transition>
      </div>
      <!-- Review List -->
      <div class="overflow-y-auto flex-grow min-h-0 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
        <ul class="space-y-2 mt-2">
          <li
            v-for="(outlet, index) in outletsReview"
            :key="index"
            class="flex justify-between items-center border border-gray-200 rounded-md px-3 py-2 bg-white shadow-sm text-sm"
          >
            <div class="text-gray-800">
              <div class="font-medium">
                {{ outlet.aggregator }} • {{ outlet.resid }} • {{ outlet.city }}
              </div>
              <div class="text-gray-600 text-xs">
                Subzone: {{ outlet.subzone }} • Outlet #: {{ outlet.outletnumber }}
              </div>
            </div>
            <button
              @click="deleteOutletReview(index)"
              class="text-red-500 hover:text-red-700 ml-4"
              title="Delete outlet"
            >
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
</template>
