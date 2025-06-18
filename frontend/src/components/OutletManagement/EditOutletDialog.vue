<script setup>
import { reactive, watch, ref, computed } from "vue";
import { updateOutlet } from "@/composables/api/brandManagementApi";
import { useMessageDialogStore } from '@/stores/messageDialog';

const dialog = useMessageDialogStore();

const props = defineProps({
  visible: Boolean,
  row: Object,
  editAllowed: {
    type: Object,
    default: () => ({}),
  },
  mapHeaders: {
    type: Object,
    default: () => ({}),
  },
});

const emit = defineEmits(["close", "save"]);

const form = reactive({});
const originalRow = ref(null);

watch(
  () => props.row,
  (newRow) => {
    Object.keys(form).forEach(k => delete form[k]);
    if (newRow) {
      Object.assign(form, newRow);
      originalRow.value = { ...newRow };
    }
  },
  { immediate: true }
);

const editableKeys = computed(() =>
  Object.keys(props.mapHeaders)
    .filter(key =>
      props.editAllowed[key] === true && form.hasOwnProperty(key)
    )
);

const updateApiError = ref(null);
const loading = ref(false);
const updateApiSuccess = ref(false);

function validateForm() {
  // Basic validation: check for empty required fields
  for (const key of editableKeys.value) {
    if (form[key] === undefined || form[key] === null || form[key].toString().trim() === "") {
      showError(`"${props.mapHeaders[key]}" cannot be empty.`);
      return false;
    }
    // Add more validation rules here if needed (e.g., type, length)
  }
  return true;
}

function isFormChanged() {
  // Check if any editable field has changed
  return editableKeys.value.some(key => form[key] !== originalRow.value[key]);
}

async function handleUpdateApi() {
  if (!validateForm()) return;

  if (!isFormChanged()) {
    showError("No changes detected. Please modify at least one field before saving.");
    return;
  }

  loading.value = true;
  updateApiError.value = null;
  updateApiSuccess.value = false;

  const payload = {};
  editableKeys.value.forEach(key => {
    payload[key] = form[key];
  });
  payload.client_id = props.row.client_id;
  payload['brand_id'] = props.row.brand_id;

  try {
    const params = { outlet_id: props.row.id, payload };
    console.log("Updating outlet with params:", params);
    const response = await updateOutlet(params);

    if (response.status === 200) {
      updateApiSuccess.value = true;
      console.log("Update successful:", response.data);
      emit("save", response);
      emit("close");
    } else {
      // Handle non-200 but valid responses
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

function showMessage(message, title = "Message", icon = "info") {
  dialog.show({
    message: message,
    title: title,
    icon: icon
  });
}

function showError(message, title = "Error") {
  dialog.show({
    message: message,
    title: title,
    icon: "error"
  });
}

</script>

<template>
  <!-- Enhanced Modal UI -->
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/30 backdrop-blur-x transition-opacity"
    @click.self="$emit('close')"
  >
    <div class="relative w-full max-w-3xl bg-white rounded-2xl shadow-2xl overflow-hidden animate-fade-in">

      <div
        v-if="loading"
        class="absolute inset-0 bg-white/70 flex items-center justify-center z-20"
      >
        <svg class="animate-spin mr-3 h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="text-blue-700 text-lg font-semibold">Loading...</span>
      </div>

      <!-- Modal Header -->
      <div class="flex items-center justify-between px-6 py-4 bg-gradient-to-r from-slate-100 to-slate-200 border-b">
        <h3 class="text-xl font-semibold text-slate-800 tracking-tight">Edit Outlet</h3>
        <button
          @click="$emit('close')"
          class="p-2 hover:bg-slate-300/60 bg-gray-100 rounded-full transition-colors"
          aria-label="Close modal"
        >
          <svg class="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Modal Form -->
      <form @submit.prevent="handleUpdateApi" class="px-6 pt-6 pb-5 space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div
            v-for="key in editableKeys"
            :key="key"
          >
            <label :for="key" class="block text-sm font-medium text-slate-700 mb-1">
              {{ mapHeaders[key] }}
            </label>
            <template v-if="key === 'aggregator'">
              <select
                v-model="form[key]"
                :id="key"
                :name="key"
                class="w-full px-3 py-2 text-sm bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 shadow-sm transition"
                :disabled="loading"
              >
                <option value="" disabled>Aggregator</option>
                <option value="Zomato">Zomato</option>
                <option value="Swiggy">Swiggy</option>
              </select>
            </template>
            <template v-else>
              <input
                v-model="form[key]"
                :id="key"
                :name="key"
                type="text"
                class="w-full px-3 py-2 text-sm bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 shadow-sm transition"
                :placeholder="`Enter ${mapHeaders[key]}`"
                :disabled="loading"
                autocomplete="off"
              />
            </template>
          </div>
        </div>

        <div v-if="updateApiError" class="text-red-600 text-sm mt-2">
          {{ updateApiError }}
        </div>

        <div class="flex justify-end gap-3 pt-4 border-t border-slate-200">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 text-sm font-medium text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg transition"
            :disabled="loading"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow transition"
            :disabled="loading"
          >
            Save
          </button>
        </div>
      </form>
    </div>
  </div>
</template>