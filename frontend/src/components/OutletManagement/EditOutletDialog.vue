<script setup>
import { reactive, watch, computed } from "vue";

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

// On every edit popup, copy row data fresh into form:
watch(
  () => props.row,
  (newRow) => {
    // Clear old keys
    Object.keys(form).forEach(k => delete form[k]);
    // Copy new keys from row
    if (newRow) Object.assign(form, newRow);
  },
  { immediate: true }
);

// Show only keys that are BOTH: in mapHeaders AND editAllowed is true
const editableKeys = computed(() =>
  Object.keys(props.mapHeaders)
    .filter(key =>
      props.editAllowed[key] === true && form.hasOwnProperty(key)
    )
);

function save() {
  // Only save the editable keys (avoid sending extra fields).
  const dataToSend = {};
  editableKeys.value.forEach(key => {
    dataToSend[key] = form[key];
  });
  emit("save", dataToSend);
}
</script>

<template>
  <!-- Enhanced Modal UI -->
  <div 
    v-if="visible" 
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/30 backdrop-blur-x transition-opacity"
    @click.self="$emit('close')"
  >
    <div class="w-full max-w-3xl bg-white rounded-2xl shadow-2xl overflow-hidden animate-fade-in">
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
      <form @submit.prevent="save" class="px-6 pt-6 pb-5 space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div 
            v-for="key in editableKeys" 
            :key="key"
          >
            <label :for="key" class="block text-sm font-medium text-slate-700 mb-1">
              {{ mapHeaders[key] }}
            </label>
            <input
              v-model="form[key]"
              :id="key"
              :name="key"
              type="text"
              class="w-full px-3 py-2 text-sm bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 shadow-sm transition"
              placeholder="Enter value"
            />
          </div>
        </div>

        <div class="flex justify-end gap-3 pt-4 border-t border-slate-200">
          <button 
            type="button" 
            @click="$emit('close')"
            class="px-4 py-2 text-sm font-medium text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg transition"
          >
            Cancel
          </button>
          <button 
            type="submit"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow transition"
          >
            Save
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
