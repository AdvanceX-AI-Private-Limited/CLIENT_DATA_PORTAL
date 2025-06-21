<script setup>
import { ref, onMounted, reactive, watch, computed } from "vue";
import Breadcrumb from "@/components/Breadcrumb.vue";
import DataTable from "@/components/DataTables/DataTable.vue";
import MessageDialog from "@/components/MessageDialog.vue";
import EditDialog from "@/components/OutletManagement/EditDialog.vue";
import AddUsersPopup from "@/components/Mapping/AddUsersPopup.vue";
import { fetchServices as fetchServicesApi, deleteService, addService, updateService } from "@/composables/api/brandManagementApi";
import { PencilIcon, TrashIcon } from "@heroicons/vue/24/outline";

const services = ref([]);
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

const updateApiError = ref(null);
const updateApiSuccess = ref(false);

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

async function fetchServices() {
  loading.value = true;
  error.value = null;
  try {
    const params = {
      skip: 0,
      limit: 100,
    };
    const response = await fetchServicesApi(params);
    services.value = response?.data || [];
    console.log("Fetched services:", services.value);
  } catch (err) {
    error.value = err.message || "Failed to fetch";
  } finally {
    loading.value = false;
  }
}

async function deleteServiceById(userId, username) {
  try {
    await deleteService(userId);
    showMessage(`User ${username} deleted successfully.`, "Success", "success");
    fetchServices();
  } catch (err) {
    showMessage(`Failed to delete user ID ${userId}: ${err.message}`, "Error", "error");
  }
}

function handleToolbarAction(action) {
  if (action.action === "add_users") {
    showaddServicePopup();
  }
}

function handleRowAction({ action, row }) {
  if (action.action === "edit") {
    editRow.value = { ...row };
    editDialogVisible.value = true;
  } else if (action.action === "delete") {
    deleteServiceById(row.id, row.username);
  }
}

function handleEditSave(editedData) {
  console.log("Edited data:", editedData);
  editDialogVisible.value = false;
  fetchServices();
}

watch(editDialogVisible, (newValue) => {
  if (!newValue) {
    updateApiError.value = null;
    updateApiSuccess.value = false;
  }
});

// Add this function to handle update API call
async function handleUpdateApi(data) {
  const payload = { ...data };

  loading.value = true;
  updateApiError.value = null;
  updateApiSuccess.value = false;
  
  try {
    // const params = { user_id: editRow.value.id, payload };
    console.log("Edit row: ", editRow.value);
    console.log("Update params:", payload);
    payload.id = editRow.value.id
    const response = await updateService(editRow.value.id, payload);

    if (response.status === 200) {
      updateApiSuccess.value = true;
      handleEditSave(response.data);
    } else {
      showMessage(response?.data?.message || "Unexpected response from server.", "Error", "error");
    }
  } catch (err) {
    let errorMsg = "Failed to update. Please try again.";
    if (err?.response?.data?.message) {
      errorMsg = err.response.data.message;
    } else if (err?.message) {
      errorMsg = err.message;
    }
    updateApiError.value = errorMsg;
    showMessage(errorMsg, "Error", "error");
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  fetchServices();
});

const columns = [
  { label: "ID", key: "id" },
  { label: "Active", key: "is_active" },
  { label: "Email", key: "useremail" },
  { label: "Username", key: "username" },
  { label: "User Number", key: "usernumber" }
];

const dataActionButtons = [
  {
    name: "Edit",
    action: "edit",
    icon: PencilIcon,
    class: "text-blue-600 hover:text-blue-800",
    tooltip: "Edit user",
  },
  {
    name: "Delete",
    action: "delete",
    icon: TrashIcon,
    class: "text-red-600 hover:text-red-800",
    tooltip: "Delete user",
  },
];

const mapHeaders = {
  servicename: "Service",
  servicevariant: "Variant",
  created_at: "Created At",
  updated_at: "Updated At",
};

const showPopup = ref(false);

function closePopup() {
  showPopup.value = false;
}

function showaddServicePopup() {
  showPopup.value = true;
}

// User form state
const isExpanded = ref(false);
const servicesReview = ref([]);
const servicesForm = reactive({
  servicename: "",
  servicevariant: "",
});

const userInputFields = [
  { key: "servicename", type: "text", placeholder: "Service Name" },
  { key: "servicevariant", type: "text", placeholder: "Service Variant" },
];

const allowedUserInputs = {
  servicename: true,
  servicevariant: true,
};

const editAllowed = {
  servicename: true,
  servicevariant: true,
};

const visibleUserInputFields = computed(() =>
  userInputFields.filter(f => allowedUserInputs[f.key])
);
const isOddVisibleFields = computed(() => visibleUserInputFields.value.length % 2 === 1);

// Add user to review list
const addServiceToReview = () => {
  for (const field of visibleUserInputFields.value) {
    if (
      servicesForm[field.key] === "" ||
      servicesForm[field.key] === null ||
      servicesForm[field.key] === undefined
    ) {
      showMessage("Please fill all the fields.", "Error", "error");
      return;
    }
  }
  servicesReview.value.unshift({ ...servicesForm });
  visibleUserInputFields.value.forEach(field => {
    servicesForm[field.key] = field.key === "is_active" ? true : "";
  });
  isExpanded.value = false;
};

// Remove user from review list
const deleteServiceReview = (index) => {
  servicesReview.value.splice(index, 1);
};

// Submit all services in review list
const submitServices = async () => {
  if (!servicesReview.value.length) {
    showMessage("No services to submit.", "Error", "error");
    return;
  }
  try {
    servicesReview.value.map((service) => (service.clientid = Number(localStorage.getItem("client_id"))));
    console.log("servicesReview.value: ", servicesReview.value);
    await addService(servicesReview.value);
    showMessage("services added successfully!", "Success", "success");
    servicesReview.value = [];
    fetchServices();
    showPopup.value = false;
  } catch (err) {
    showMessage(err.message || "Failed to add services.", "Error", "error");
  }
};

function toggleDropdown() {
  isExpanded.value = !isExpanded.value;
}

watch(
  servicesReview,
  (newList) => {
    if (newList.length === 0) {
      isExpanded.value = true;
    }
  },
  { immediate: true }
);
</script>

<template>
  <Breadcrumb />

    <!-- title="services Management" -->
  <DataTable
    :table_data="services"
    :columns="columns"
    :loading="loading"
    :error="error"
    :table_headers="mapHeaders"
    :action_buttons=" [
      {
        name: 'Add&nbsp;services',
        onClick: showaddServicePopup,
        action: 'add_users',
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
    :title="`Edit User`"
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
    title="Add services"
    :closeBtnBar="true"
    :action_buttons=" [
      { name: 'Submit', onClick: submitServices }
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
          <span>{{ isExpanded ? 'Hide Form' : 'Add User' }}</span>
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
                <template v-for="(field, idx) in visibleUserInputFields" :key="field.key">
                  <input
                    v-if="field.key !== 'is_active'"
                    :type="field.type"
                    v-model="servicesForm[field.key]"
                    :placeholder="field.placeholder"
                    class="w-full border border-gray-300 rounded-md p-1.5 px-3 mb-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                  <div v-else class="flex items-center">
                    <input
                      type="checkbox"
                      v-model="servicesForm.is_active"
                      class="mr-2"
                    />
                    <label>Active</label>
                  </div>
                  <template v-if="isOddVisibleFields && idx === visibleUserInputFields.length - 1">
                    <button
                      @click="addServiceToReview"
                      class="px-4 py-1.5 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors shadow mb-2 ml-auto block w-auto"
                      style="min-width: 90px;"
                    >
                      Add
                    </button>
                  </template>
                </template>
                <template v-if="!isOddVisibleFields">
                  <div></div>
                  <button
                    @click="addServiceToReview"
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
            v-for="(user, index) in servicesReview"
            :key="index"
            class="flex justify-between items-center border border-gray-200 rounded-md px-3 py-2 bg-white shadow-sm text-sm"
          >
            <div class="text-gray-800">
              <div class="font-medium">
                {{ user.servicename }}
              </div>
              <div class="text-gray-600 text-xs">
                {{ user.servicevariant }}
              </div>
            </div>
            <button
              @click="deleteServiceReview(index)"
              class="text-red-500 hover:text-red-700 ml-4"
              title="Delete user"
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
