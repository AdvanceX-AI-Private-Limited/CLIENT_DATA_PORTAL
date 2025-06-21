<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from "vue";
import { useWindowSize } from '@vueuse/core'; // Add this package if not already installed

const props = defineProps({
  title: {
    type: String,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: null,
  },
  table_data: {
    type: Array,
    default: () => [],
  },
  table_headers: {
    type: Object,
    default: () => ({}),
  },
  data_action_buttons: {
    type: Array,
    default: () => [],
    // Example item: { name: 'Edit', onClick: 'editRow', icon: 'PencilIcon' }
  },
  action_buttons: {
    type: Array,
    default: () => [],
    // Example item: { name: 'Add New', onClick: 'addNewEntry', icon: 'PlusIcon' }
  },
  csv_download: {
    type: Boolean,
    default: false,
  },
  show_all_rows_option: {
    type: Boolean,
    default: true,
  },
  empty_state_message: {
    type: String,
    default: "No data available",
  },
});

// Track window size for responsiveness
const { width } = useWindowSize();
const isSmallScreen = computed(() => width.value < 640);
const isMediumScreen = computed(() => width.value >= 640 && width.value < 1024);

// Table headers
const tableHeaders = computed(() => {
  // If the user provides a table_headers object with keys, use those
  if (props.table_headers && Object.keys(props.table_headers).length > 0) {
    return Object.keys(props.table_headers);
  }
  // Else fallback to data keys from the first row (if any)
  else if (props.table_data && props.table_data.length > 0) {
    return Object.keys(props.table_data[0]);
  }
  return [];
});

// Responsive columns - hide less important columns on small screens
const visibleColumns = computed(() => {
  if (!isSmallScreen.value) return tableHeaders.value;
  // On mobile, show only the first 2-3 columns
  return tableHeaders.value.slice(0, Math.min(3, tableHeaders.value.length));
});

// Cell formatting with better type handling
const formatCell = (value) => {
  if (value === null || value === undefined) return "—";

  // If value is an array, join with comma
  if (Array.isArray(value)) {
    return value.join(", ");
  }

  // If value is a string that looks like an array, parse & join
  if (typeof value === "string" && value.startsWith("[") && value.endsWith("]")) {
    try {
      const parsed = JSON.parse(value.replace(/'/g, '"'));
      if (Array.isArray(parsed)) {
        return parsed.join(", ");
      }
    } catch (e) {
      // Fallback...
    }
  }

  // Dates
  if (typeof value === "string" && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(value)) {
    try {
      return new Date(value).toLocaleString();
    } catch (e) {}
  }

  // Numbers
  if (typeof value === "number") {
    return value;
  }

  // Booleans
  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }

  return value;
};

// Get cell class based on value type
const getCellClass = (value) => {
  if (value === null || value === undefined) return "text-gray-400 italic";
  if (typeof value === "boolean") return value ? "text-green-600" : "text-red-600";
  if (typeof value === "number") return "font-mono";
  return "";
};

// Filters state
const filters = ref({});

const initFilters = () => {
  filters.value = {};
  tableHeaders.value.forEach((header) => {
    filters.value[header] = {
      search: "",
      selected: new Set(),
      expanded: false,
    };
  });
};

watch(tableHeaders, initFilters, { immediate: true });

// Global search with debounce
const globalSearch = ref("");
const debouncedSearch = ref("");
let searchTimeout = null;

watch(globalSearch, (val) => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    debouncedSearch.value = val;
  }, 300);
});

// Pagination
const currentPage = ref(1);
const rowsPerPageOptions = [15, 25, 50, 100];
const rowsPerPage = ref(rowsPerPageOptions[0]);

// Parse and handle array values
function parsePossibleArray(val) {
  if (val === null || val === undefined) return [];

  if (typeof val === "string") {
    const trimmed = val.trim();
    if (trimmed.startsWith("[") && trimmed.endsWith("]")) {
      try {
        const jsonReady = trimmed.replace(/'/g, '"');
        return JSON.parse(jsonReady);
      } catch (e) {
        return [val];
      }
    }
    return [val];
  } else if (Array.isArray(val)) {
    return val;
  } else {
    return [val];
  }
}

function flattenDeep(arr) {
  return Array.isArray(arr)
    ? arr.reduce((acc, val) => acc.concat(flattenDeep(val)), [])
    : [arr];
}

// Apply column filters with error handling
const filteredByColumnData = computed(() => {
  try {
    return props.table_data.filter((row) => {
      return tableHeaders.value.every((header) => {
        const selected = filters.value?.[header]?.selected;
        if (!selected || selected.size === 0) return true;

        let cellValues = parsePossibleArray(row[header]);
        return [...selected].some((sel) =>
          cellValues.some((val) =>
            String(val).toLowerCase().includes(String(sel).toLowerCase())
          )
        );
      });
    });
  } catch (error) {
    console.error("Filter error:", error);
    return props.table_data; // Fallback to unfiltered data
  }
});

// Apply global search on top of column filters
const searchFilteredData = computed(() => {
  if (!debouncedSearch.value) return filteredByColumnData.value;

  const searchTerm = debouncedSearch.value.toLowerCase();

  try {
    return filteredByColumnData.value.filter((row) => {
      // Check all columns for the search term
      return tableHeaders.value.some((header) => {
        const cellValues = parsePossibleArray(row[header]);
        return cellValues.some(
          (val) =>
            val !== null &&
            val !== undefined &&
            String(val).toLowerCase().includes(searchTerm)
        );
      });
    });
  } catch (error) {
    console.error("Search error:", error);
    return filteredByColumnData.value; // Fallback
  }
});

// Final filtered data with pagination
const filteredData = computed(() => {
  if (rowsPerPage.value === "all") {
    return searchFilteredData.value;
  }

  const start = (currentPage.value - 1) * rowsPerPage.value;
  const end = start + rowsPerPage.value;

  return searchFilteredData.value.slice(start, end);
});

// Pagination calculations
const totalPages = computed(() => {
  if (rowsPerPage.value === "all") return 1;
  return Math.max(1, Math.ceil(searchFilteredData.value.length / rowsPerPage.value));
});

const canGoPrevious = computed(() => currentPage.value > 1);
const canGoNext = computed(() => currentPage.value < totalPages.value);

// Page navigation
const nextPage = () => {
  if (canGoNext.value) {
    currentPage.value++;
  }
};

const previousPage = () => {
  if (canGoPrevious.value) {
    currentPage.value--;
  }
};

// Specific page navigation
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
};

// Reset pagination when filters or rows per page changes
watch([() => searchFilteredData.value.length, rowsPerPage], () => {
  // Reset to first page when filter results change or rows per page changes
  currentPage.value = 1;
});

// Column filter methods
const getOptionsForColumn = (header) => {
  try {
    const rowsToConsider = props.table_data.filter((row) => {
      return tableHeaders.value.every((h) => {
        if (h === header) return true;
        const selected = filters.value[h]?.selected;
        if (!selected || selected.size === 0) return true;
        return selected.has(row[h]);
      });
    });

    let options = [];
    rowsToConsider.forEach((row) => {
      if (row[header] === null || row[header] === undefined) {
        options.push("(Empty)");
        return;
      }

      const rawVal = row[header];
      const arrVal = parsePossibleArray(rawVal);
      options = options.concat(flattenDeep(arrVal));
    });

    options = options.map((v) => (typeof v === "string" ? v.trim() : v));

    return [...new Set(options)].sort();
  } catch (error) {
    console.error("Error getting column options:", error);
    return [];
  }
};

watch(
  () => props.table_data,
  () => {
    initFilters();
    currentPage.value = 1;
  }
);

const toggleAllInColumn = (header, isCheck) => {
  if (isCheck) {
    getOptionsForColumn(header).forEach((val) => filters.value[header].selected.add(val));
  } else {
    filters.value[header].selected.clear();
  }
};

const toggleOption = (header, value) => {
  const sel = filters.value[header].selected;
  if (sel.has(value)) sel.delete(value);
  else sel.add(value);
};

const isIndeterminate = (header) => {
  const opts = getOptionsForColumn(header);
  const sel = filters.value[header].selected;
  return sel.size > 0 && sel.size < opts.length;
};

const isAllChecked = (header) => {
  const opts = getOptionsForColumn(header);
  return opts.length > 0 && opts.every((val) => filters.value[header].selected.has(val));
};

const filteredOptionsForColumn = (header) => {
  const options = getOptionsForColumn(header);
  const search = filters.value[header]?.search?.toLowerCase() || "";
  return options.filter((opt) => String(opt).toLowerCase().includes(search));
};

// Dropdown management
function closeAllDropdowns(e) {
  // Only close if click was outside any dropdown
  for (const header of tableHeaders.value) {
    const ref = document.getElementById("dropdown-ref-" + header);
    if (ref && ref.contains(e.target)) return; // clicked inside
  }
  // else close
  tableHeaders.value.forEach((header) => (filters.value[header].expanded = false));
}

onMounted(() => {
  window.addEventListener("click", closeAllDropdowns);
});

onBeforeUnmount(() => {
  window.removeEventListener("click", closeAllDropdowns);
  clearTimeout(searchTimeout);
});

function toggleDropdown(header) {
  Object.keys(filters.value).forEach((h) => {
    if (h !== header) filters.value[h].expanded = false;
  });
  filters.value[header].expanded = !filters.value[header].expanded;
}

const openActionMenuRow = ref(null);
const dropdownPosition = ref({});

function toggleRowActionMenu(idx, event) {
  if (openActionMenuRow.value === idx) {
    openActionMenuRow.value = null;
    return;
  }
  openActionMenuRow.value = idx;
  nextTick(() => {
    const rect = event.target.getBoundingClientRect();

    // Find the nearest ancestor table, then get its right edge
    // (If you keep a ref on the table container, this is even easier)
    let tableRect = null;
    // Option 1: If you have a ref (recommended)
    if (tableContainer.value) {
      tableRect = tableContainer.value.getBoundingClientRect();
    } else {
      // Option 2: Try to climb DOM from button
      let el = event.target;
      while (el && el.tagName !== "TABLE") el = el.parentElement;
      tableRect = el ? el.getBoundingClientRect() : null;
    }

    const MENU_WIDTH = 160;

    let left = rect.left + window.scrollX;
    const top = rect.bottom + window.scrollY;

    if (tableRect) {
      const tableRight = tableRect.right + window.scrollX;
      // If overflow, shift left so menu stays within table's right
      if (left + MENU_WIDTH > tableRight) {
        left = tableRight - MENU_WIDTH - 8; // 8px padding so it's not flush
        // Prevent going off the table's left
        if (left < tableRect.left + window.scrollX)
          left = tableRect.left + window.scrollX + 8;
      }
    } else {
      // Fallback: check for window boundary
      if (left + MENU_WIDTH > window.innerWidth - 8)
        left = window.innerWidth - MENU_WIDTH - 8;
    }

    dropdownPosition.value = {
      top: `${top}px`,
      left: `${left}px`,
      minWidth: "10rem",
    };
  });
}

function handleDataActionClick(action, row) {
  if (action.action === "delete") {
    // Show confirmation popup for delete
    showDeleteConfirm.value = true;
    deleteRowData.value = { action, row };
  } else {
    // Emit the row-action event for other actions
    openActionMenuRow.value = null;
    emit("row-action", { action, row });
  }
}

function confirmDelete(confirmed) {
  if (confirmed && deleteRowData.value) {
    emit("row-action", {
      action: deleteRowData.value.action,
      row: deleteRowData.value.row,
    });
  }
  showDeleteConfirm.value = false;
  deleteRowData.value = null;
}

const emit = defineEmits(["row-action", "action-click", "row-click"]);

function handleActionClick(action) {
  emit("action-click", action);
}

function handleRowClick(row) {
  emit("row-click", row);
}

function downloadCSV() {
  try {
    const keys = tableHeaders.value;
    const labels = keys.map((key) => props.table_headers?.[key] || key);
    const rows = searchFilteredData.value;

    const csv = [
      labels.map(escapeCSV).join(","),
      ...rows.map((row) => keys.map((key) => escapeCSV(formatCell(row[key]))).join(",")),
    ].join("\r\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = (props.title?.replace(/\s+/g, "_") || "table") + ".csv";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("CSV download error:", error);
    alert("Failed to download CSV. Please try again.");
  }
}

function escapeCSV(val) {
  if (val == null) return "";
  const str = String(val).replace(/"/g, '""');
  if (/[\s,"]/.test(str)) return `"${str}"`;
  return str;
}

const dropdownState = ref({
  openHeader: null,
  position: { top: 0, left: 0 },
});

function openDropdown(header, event) {
  event.stopPropagation();

  const rect = event.target.getBoundingClientRect();
  const DROPDOWN_WIDTH = 192; // matches the w-48 in Tailwind (48*4 px)
  const DROPDOWN_HEIGHT = 250; // approximate max height for dropdown; adjust as needed

  const viewportWidth = window.innerWidth;
  const viewportHeight = window.innerHeight;

  // Calculate initial dropdown position
  let left = rect.left + window.scrollX;
  let top = rect.bottom + window.scrollY + 4;

  // If dropdown would overflow right edge, adjust left to show fully
  if (left + DROPDOWN_WIDTH > window.scrollX + viewportWidth) {
    left = window.scrollX + viewportWidth - DROPDOWN_WIDTH - 8; // 8px padding from edge
    if (left < window.scrollX) left = window.scrollX + 8; // avoid going off left edge
  }

  // Similarly, if dropdown would overflow bottom edge, open above the button
  if (top + DROPDOWN_HEIGHT > window.scrollY + viewportHeight) {
    top = rect.top + window.scrollY - DROPDOWN_HEIGHT - 4; // position above button with small gap
    if (top < window.scrollY) top = window.scrollY + 8; // avoid going off top edge
  }

  if (dropdownState.value.openHeader === header) {
    dropdownState.value.openHeader = null; // toggle off
  } else {
    dropdownState.value = {
      openHeader: header,
      position: {
        top,
        left,
      },
    };
  }
}

function closeTeleportDropdown(e) {
  if (e.target.closest(".dropdown-filter")) return;
  dropdownState.value.openHeader = null;
}

onMounted(() => {
  window.addEventListener("click", closeTeleportDropdown);
});
onBeforeUnmount(() => {
  window.removeEventListener("click", closeTeleportDropdown);
});

// Sorting functionality
const sortConfig = ref({
  key: null,
  direction: "asc",
});

function sortTable(key) {
  if (sortConfig.value.key === key) {
    sortConfig.value.direction = sortConfig.value.direction === "asc" ? "desc" : "asc";
  } else {
    sortConfig.value.key = key;
    sortConfig.value.direction = "asc";
  }
}

// Apply sorting to data
const sortedData = computed(() => {
  if (!sortConfig.value.key) return filteredData.value;

  return [...filteredData.value].sort((a, b) => {
    const aValue = a[sortConfig.value.key];
    const bValue = b[sortConfig.value.key];

    // Handle null/undefined values
    if (aValue === null || aValue === undefined)
      return sortConfig.value.direction === "asc" ? -1 : 1;
    if (bValue === null || bValue === undefined)
      return sortConfig.value.direction === "asc" ? 1 : -1;

    // Compare based on type
    if (typeof aValue === "number" && typeof bValue === "number") {
      return sortConfig.value.direction === "asc" ? aValue - bValue : bValue - aValue;
    }

    // Default string comparison
    const aStr = String(aValue).toLowerCase();
    const bStr = String(bValue).toLowerCase();

    return sortConfig.value.direction === "asc"
      ? aStr.localeCompare(bStr)
      : bStr.localeCompare(aStr);
  });
});

// Track if table has scrollbars
const tableContainer = ref(null);
const hasHorizontalScroll = ref(false);

function checkForScrollbars() {
  nextTick(() => {
    if (tableContainer.value) {
      hasHorizontalScroll.value =
        tableContainer.value.scrollWidth > tableContainer.value.clientWidth;
    }
  });
}

watch([width, () => props.table_data], checkForScrollbars);
onMounted(() => {
  checkForScrollbars();
  window.addEventListener("resize", checkForScrollbars);
});
onBeforeUnmount(() => {
  window.removeEventListener("resize", checkForScrollbars);
});

const showScrollMsg = ref(true);

onMounted(() => {
  setTimeout(() => {
    showScrollMsg.value = false;
  }, 3000);
});

const rowActionDropdownState = ref({
  rowIdx: null, // which row
  position: { top: 0, left: 0 },
});

function openRowActionDropdown(rowIdx, event) {
  // event should be the click event of the button that opens the menu
  const rect = event.target.getBoundingClientRect();
  const MENU_WIDTH = 160;
  const MENU_HEIGHT = 40 + data_action_buttons.length * 40;

  let left = rect.left + window.scrollX;
  let top = rect.bottom + window.scrollY;

  // Make sure the menu does not go off-screen (optional)
  if (left + MENU_WIDTH > window.innerWidth - 8)
    left = window.innerWidth - MENU_WIDTH - 8;
  if (top + MENU_HEIGHT > window.innerHeight) top = window.innerHeight - MENU_HEIGHT - 8;

  rowActionDropdownState.value = {
    rowIdx,
    position: { top, left },
  };
}

const rowActionsMenuRef = ref();

onMounted(() => {
  window.addEventListener("click", handleCloseRowEllipsisMenu);
});
onBeforeUnmount(() => {
  window.removeEventListener("click", handleCloseRowEllipsisMenu);
});

function handleCloseRowEllipsisMenu(e) {
  if (rowActionsMenuRef.value && rowActionsMenuRef.value.contains(e.target)) return;
  openActionMenuRow.value = null;
}

// Confirmation dialog state
const showDeleteConfirm = ref(false);
const deleteRowData = ref(null);
</script>

<template>
  <div class="w-full flex-col" :class="{ 'rounded-xl p-2': !error && !loading }">
    <!-- Header and controls section -->
    <div class="mb-4 flex flex-col">
      <div
        v-if="!loading && !error"
        class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-2"
      >
        <h2 v-if="title" class="text-2xl font-bold text-gray-800 pb-2.5">{{ title }}</h2>
        <!-- Action buttons -->
        <div v-if="action_buttons && title" class="flex flex-wrap items-center gap-2 mt-2 sm:mt-0">
          <button
            v-if="!loading"
            v-for="(action, index) in action_buttons"
            :key="index"
            @click="handleActionClick(action)"
            :class="[
              'px-3 py-1.5 text-sm font-medium text-white rounded-md shadow-sm transition-all duration-150 focus:outline-none',
              action.color
                ? `bg-${action.color}-500 hover:bg-${action.color}-600 focus:ring-${action.color}-500`
                : 'bg-gray-600 hover:bg-gray-700',
              action.class || '',
            ]"
          >
            <span class="flex items-center gap-1.5">
              <component :is="action.icon" v-if="action.icon" class="w-4 h-4" />
              {{ action.name }}
            </span>
          </button>
        </div>
      </div>

      <div
        class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-3"
      >
        <!-- Global Search -->
        <div v-if="!loading && !error" class="relative w-full sm:w-64 md:w-72">
          <input
            type="text"
            v-model="globalSearch"
            placeholder="Search all columns..."
            class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
          />
          <div class="absolute right-3 top-2.5 text-gray-400">
            <svg
              class="h-4 w-4"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fill-rule="evenodd"
                d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                clip-rule="evenodd"
              />
            </svg>
          </div>
        </div>

        <!-- Title and action buttons -->
        <div v-if="!error" class="flex flex-col sm:flex-row sm:items-center gap-2">
          <!-- CSV Download button -->
          <button
            v-if="csv_download && !loading && !error && searchFilteredData.length > 0"
            class="px-3 py-1.5 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-md shadow-sm hover:shadow-md transition-all duration-150 focus:ring-offset-2 focus:outline-none"
            @click="downloadCSV"
          >
            <span class="flex items-center gap-1.5">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fill-rule="evenodd"
                  d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"
                  clip-rule="evenodd"
                />
              </svg>
              Export&nbsp;CSV
            </span>
          </button>

          <div
            v-if="action_buttons && !title"
            class="flex flex-wrap items-center gap-2 mt-2 sm:mt-0"
          >
            <button
              v-if="!loading"
              v-for="(action, index) in action_buttons"
              :key="index"
              @click="handleActionClick(action)"
              :class="[
                'px-3 py-1.5 text-sm font-medium text-white rounded-md shadow-sm transition-all duration-150 focus:outline-none',
                action.color
                  ? `bg-${action.color}-500 hover:bg-${action.color}-600 focus:ring-${action.color}-500`
                  : 'bg-gray-600 hover:bg-gray-700',
                action.class || '',
              ]"
            >
              <span class="flex items-center gap-1.5">
                <component :is="action.icon" v-if="action.icon" class="w-4 h-4" />
                {{ action.name }}
              </span>
            </button>
          </div>
        </div>
      </div>

      <!-- Applied filters summary -->
      <div
        v-if="Object.values(filters).some((f) => f.selected.size > 0)"
        class="flex flex-wrap gap-2 mt-3"
      >
        <div
          v-for="(filter, header) in filters"
          :key="header"
          v-show="filter.selected.size > 0"
          class="inline-flex items-center rounded-full px-3 py-1 text-xs font-medium bg-blue-50 text-blue-700"
        >
          {{ props.table_headers?.[header] || header }}:
          {{ filter.selected.size }} filters
          <button
            @click="filters[header].selected.clear()"
            class="ml-1 text-blue-500 hover:text-blue-700"
            title="Clear filter"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-3 w-3"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fill-rule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clip-rule="evenodd"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Teleport dropdown for filtering -->
    <Teleport to="body">
      <div
        v-if="dropdownState.openHeader"
        class="z-[9999] fixed bg-white rounded-lg shadow-lg p-3 w-56 dropdown-filter"
        :style="{
          top: dropdownState.position.top + 'px',
          left: dropdownState.position.left + 'px',
        }"
        @click.stop
      >
        <!-- Search input -->
        <div class="mb-2">
          <input
            type="text"
            placeholder="Filter options..."
            v-model="filters[dropdownState.openHeader].search"
            class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <!-- Check All box -->
        <label
          class="flex items-center space-x-2 text-sm font-medium mb-2 pb-2 border-b border-gray-200"
        >
          <input
            type="checkbox"
            :checked="isAllChecked(dropdownState.openHeader)"
            ref="el => el && (el.indeterminate = isIndeterminate(dropdownState.openHeader))"
            @change="toggleAllInColumn(dropdownState.openHeader, $event.target.checked)"
            class="rounded text-blue-600 focus:ring-blue-500 border-gray-300"
          />
          <span>Select All</span>
        </label>

        <!-- Option checkboxes -->
        <div
          class="max-h-48 overflow-y-auto space-y-1.5 pr-1"
          style="scrollbar-width: thin"
        >
          <div
            v-if="filteredOptionsForColumn(dropdownState.openHeader).length === 0"
            class="text-sm text-gray-500 italic py-1"
          >
            No options match your filter
          </div>
          <label
            v-for="val in filteredOptionsForColumn(dropdownState.openHeader)"
            :key="val"
            class="flex items-center space-x-2 text-sm hover:bg-gray-50 p-1 rounded"
          >
            <input
              type="checkbox"
              :checked="filters[dropdownState.openHeader].selected.has(val)"
              @change="toggleOption(dropdownState.openHeader, val)"
              class="rounded text-blue-600 focus:ring-blue-500 border-gray-300"
            />
            <span class="truncate max-w-[180px]" :title="val">{{ val }}</span>
          </label>
        </div>
      </div>
    </Teleport>

    <!-- Teleport dropdown for data row actions -->
    <Teleport to="body">
      <div
        v-if="rowActionDropdownState.rowIdx !== null"
        ref="rowActionsMenuRef"
        :style="{
          position: 'absolute',
          top: rowActionDropdownState.position.top + 'px',
          left: rowActionDropdownState.position.left + 'px',
          minWidth: '10rem',
          zIndex: 9999,
        }"
        class="z-[9999] py-1.5 bg-white border border-gray-100 rounded-lg shadow-lg animate-fade-in"
        @click.stop
      >
        <button
          v-for="(action, actionIdx) in data_action_buttons"
          :key="actionIdx"
          @click="
            handleDataActionClick(action, sortedData[rowActionDropdownState.rowIdx]);
            rowActionDropdownState.rowIdx = null;
          "
          class="flex items-center w-full text-left gap-2 px-4 py-2 text-sm text-gray-700 bg-white border-none hover:bg-blue-50 transition duration-75 font-medium cursor-pointer"
          :class="action.class"
        >
          <component v-if="action.icon" :is="action.icon" class="w-4 h-4" />
          {{ action.name }}
        </button>
      </div>
    </Teleport>

    <!-- Main content area -->
    <div
      class="overflow-hidden p-1"
      :class="[
        {
          'min-h-300px flex items-center justify-center':
            loading || error || table_data.length === 0,
        },
        { 'bg-white border border-gray-200 rounded-lg shadow-sm': !error && !loading },
      ]"
    >
      <!-- Loading state -->
      <div
        v-if="loading"
        class="flex flex-col items-center justify-center py-8 text-gray-500"
      >
        <svg
          class="animate-spin h-8 w-8 text-blue-500 mb-3"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            class="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="4"
          ></circle>
          <path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          ></path>
        </svg>
        <p class="text-sm font-medium">Loading Table...</p>
      </div>

      <!-- Error state -->
      <div
        v-else-if="error"
        class="flex flex-col items-center justify-center py-8 text-red-600"
      >
        <svg class="h-12 w-12 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
        <p class="text-sm font-medium">{{ error }}</p>
        <button
          @click="$emit('retry')"
          class="mt-3 px-4 py-2 bg-red-50 text-red-600 rounded-md text-sm font-medium hover:bg-red-100"
        >
          Retry
        </button>
      </div>

      <!-- Empty state -->
      <div
        v-else-if="table_data.length === 0"
        class="flex flex-col items-center justify-center py-10 text-gray-500"
      >
        <svg
          class="h-16 w-16 mb-3 text-gray-300"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
          />
        </svg>
        <p class="text-base font-medium mb-1">{{ empty_state_message }}</p>
        <p class="text-sm text-gray-400">No data is currently available for display</p>
      </div>

      <!-- Empty search/filter results -->
      <div
        v-else-if="searchFilteredData.length === 0"
        class="flex flex-col items-center justify-center py-10 text-gray-500"
      >
        <svg
          class="h-12 w-12 mb-3 text-gray-300"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
          />
        </svg>
        <p class="text-base font-medium mb-1">No matching results</p>
        <p class="text-sm text-gray-400">Try adjusting your search or filters</p>
        <button
          @click="
            () => {
              globalSearch = '';
              Object.keys(filters).forEach((h) => filters[h].selected.clear());
            }
          "
          class="mt-3 px-4 py-2 bg-blue-50 text-blue-600 rounded-md text-sm font-medium hover:bg-blue-100"
        >
          Clear all filters
        </button>
      </div>

      <!-- Table data -->
      <div v-else>
        <!-- Horizontal scroll indicator if needed -->
        <transition name="fade">
          <div
            v-if="hasHorizontalScroll && showScrollMsg"
            class="border-b border-gray-200 bg-blue-50 py-1.5 px-4 text-xs text-blue-700 flex items-center"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-4 w-4 mr-1"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
              />
            </svg>
            Scroll horizontally to see more columns
          </div>
        </transition>

        <div class="overflow-x-auto" ref="tableContainer">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th
                  v-for="header in tableHeaders"
                  :key="header"
                  :class="[
                    'px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sticky top-0 bg-gray-50 align-top',
                    isSmallScreen && !visibleColumns.includes(header) ? 'hidden' : '',
                    sortConfig.key === header ? 'text-blue-600' : '',
                  ]"
                >
                  <div class="flex items-center group">
                    <!-- Sort button -->
                    <button
                      @click="sortTable(header)"
                      class="flex items-center font-bold hover:text-blue-600 focus:outline-none"
                    >
                      <span v-if="props.table_headers && props.table_headers[header]">
                        {{ props.table_headers[header] }}
                      </span>
                      <span v-else>{{ header }}</span>

                      <!-- Sort indicator -->
                      <span class="ml-1 inline-flex flex-none">
                        <svg
                          :class="[
                            'h-4 w-4 transition-opacity duration-150',
                            sortConfig.key === header
                              ? 'opacity-100'
                              : 'opacity-0 group-hover:opacity-50',
                          ]"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            v-if="
                              sortConfig.key === header && sortConfig.direction === 'asc'
                            "
                            fill-rule="evenodd"
                            d="M5.293 7.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L10 4.414 6.707 7.707a1 1 0 01-1.414 0z"
                            clip-rule="evenodd"
                          />
                          <path
                            v-else
                            fill-rule="evenodd"
                            d="M14.707 12.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L10 15.586l3.293-3.293a1 1 0 011.414 0z"
                            clip-rule="evenodd"
                          />
                        </svg>
                      </span>
                    </button>

                    <!-- Filter button -->
                    <button
                      type="button"
                      @click.stop="openDropdown(header, $event)"
                      class="ml-2 focus:outline-none p-0.5 rounded hover:bg-gray-200"
                      :id="'dropdown-ref-' + header"
                      aria-haspopup="true"
                      :class="{ 'text-blue-500': filters[header]?.selected.size > 0 }"
                    >
                      <svg
                        width="16"
                        height="16"
                        viewBox="0 0 15 15"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <path d="M0 2.5H15M3 7.5H12M5 12.5H10" stroke="currentColor" />
                      </svg>
                    </button>
                  </div>
                </th>

                <!-- Actions column -->
                <th
                  v-if="data_action_buttons && data_action_buttons.length > 0"
                  class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider sticky top-0 bg-gray-50 w-20"
                >
                  <div class="font-bold">Actions</div>
                </th>
              </tr>
            </thead>

            <tbody class="bg-white divide-y divide-gray-200">
              <tr
                v-for="(row, rowIdx) in sortedData"
                :key="rowIdx"
                :class="[
                  'hover:bg-blue-50 transition-colors duration-150',
                  rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50',
                ]"
                @click="handleRowClick(row)"
                class="cursor-pointer"
              >
                <td
                  v-for="header in tableHeaders"
                  :key="header"
                  :class="[
                    'px-4 py-3 text-sm text-gray-700 align-middle',
                    getCellClass(row[header]),
                    isSmallScreen && !visibleColumns.includes(header) ? 'hidden' : '',
                  ]"
                >
                  {{ formatCell(row[header]) }}
                </td>

                <!-- Row action buttons -->
                <td
                  v-if="data_action_buttons && data_action_buttons.length > 0"
                  class="px-4 py-3 align-middle whitespace-nowrap"
                  style="position: relative"
                  @click.stop
                >
                  <template v-if="data_action_buttons.length === 1">
                    <button
                      @click="handleDataActionClick(data_action_buttons[0], row)"
                      class="px-2.5 py-1 text-xs font-medium rounded hover:shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-1 transition-all duration-150"
                    >
                      {{ data_action_buttons[0].name }}
                    </button>
                  </template>
                  <template v-else>
                    <button
                      @click="toggleRowActionMenu(rowIdx, $event)"
                      class="mx-auto p-1.5 rounded-full text-gray-500 hover:text-blue-500 hover:bg-blue-50 focus:outline-none transition duration-150 flex items-center justify-center"
                      aria-label="Show row actions"
                    >
                      <svg viewBox="0 0 24 24" fill="none" class="w-5 h-5">
                        <circle cx="6" cy="12" r="2" fill="currentColor" />
                        <circle cx="12" cy="12" r="2" fill="currentColor" />
                        <circle cx="18" cy="12" r="2" fill="currentColor" />
                      </svg>
                    </button>
                    <Teleport to="body">
                      <div
                        v-if="openActionMenuRow === rowIdx"
                        class="fixed z-[9999] mt-1 py-1.5 bg-white border border-gray-100 rounded-lg shadow-lg animate-fade-in"
                        :style="dropdownPosition"
                        @click.stop
                      >
                        <button
                          v-for="(action, actionIdx) in data_action_buttons"
                          :key="actionIdx"
                          @click="
                            handleDataActionClick(action, row);
                            openActionMenuRow = null;
                          "
                          class="flex items-center w-full text-left gap-2 px-4 py-2 text-sm text-gray-700 bg-white border-none hover:bg-blue-50 transition duration-75 font-medium cursor-pointer"
                          :class="action.class"
                        >
                          <component
                            v-if="action.icon"
                            :is="action.icon"
                            class="w-4 h-4"
                          />
                          {{ action.name }}
                        </button>
                      </div>
                    </Teleport>
                  </template>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination section -->
        <div class="border-t border-gray-200 bg-gray-50 px-3 py-2">
          <div class="flex flex-col sm:flex-row justify-between items-center gap-4">
            <!-- Rows per page selector and record count -->
            <div
              class="flex flex-wrap items-center gap-4 text-sm text-gray-600 order-2 sm:order-1"
            >
              <div class="flex items-center gap-2">
                <label for="rows-per-page" class="whitespace-nowrap"
                  >Rows per page:</label
                >
                <select
                  id="rows-per-page"
                  v-model="rowsPerPage"
                  class="px-6 ps-2 block appearance-none bg-white border border-gray-300 py-1 pr-7 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option
                    v-for="option in rowsPerPageOptions"
                    :key="option"
                    :value="option"
                  >
                    {{ option }}
                  </option>
                  <option v-if="show_all_rows_option" value="all">All</option>
                </select>
              </div>

              <div class="text-sm text-gray-600">
                <span class="hidden sm:inline-block">Showing </span>
                <span class="font-medium">
                  {{
                    searchFilteredData.length === 0
                      ? 0
                      : (currentPage - 1) *
                          (rowsPerPage === "all"
                            ? searchFilteredData.length
                            : rowsPerPage) +
                        1
                  }}
                  -
                  {{
                    Math.min(
                      currentPage *
                        (rowsPerPage === "all" ? searchFilteredData.length : rowsPerPage),
                      searchFilteredData.length
                    )
                  }}
                </span>
                <span> of </span>
                <span class="font-medium">{{ searchFilteredData.length }}</span>
                <span class="hidden sm:inline-block"> records</span>
              </div>
            </div>

            <!-- Pagination controls -->
            <div class="flex items-center text-sm text-gray-600 gap-2 order-1 sm:order-2">
              <!-- Page navigation buttons for larger screens -->
              <div class="hidden sm:flex items-center gap-2">
                <button
                  @click="goToPage(1)"
                  :disabled="currentPage === 1"
                  :class="{ 'opacity-50 cursor-not-allowed': currentPage === 1 }"
                  class="p-1 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  aria-label="First page"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-5 w-5"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fill-rule="evenodd"
                      d="M15.707 15.707a1 1 0 01-1.414 0l-5-5a1 1 0 010-1.414l5-5a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 010 1.414z"
                      clip-rule="evenodd"
                    />
                    <path
                      fill-rule="evenodd"
                      d="M9.707 15.707a1 1 0 01-1.414 0l-5-5a1 1 0 010-1.414l5-5a1 1 0 111.414 1.414L5.414 10l4.293 4.293a1 1 0 010 1.414z"
                      clip-rule="evenodd"
                    />
                  </svg>
                </button>

                <button
                  @click="previousPage"
                  :disabled="!canGoPrevious"
                  :class="{ 'opacity-50 cursor-not-allowed': !canGoPrevious }"
                  class="p-1 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  aria-label="Previous page"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-5 w-5"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fill-rule="evenodd"
                      d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
                      clip-rule="evenodd"
                    />
                  </svg>
                </button>
              </div>

              <!-- Page number selector -->
              <div class="flex items-center gap-1.5">
                <select
                  v-if="totalPages > 7"
                  v-model="currentPage"
                  class="pe-5 block appearance-none bg-white border border-gray-300 px-2 py-1 pr-7 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option v-for="page in totalPages" :key="page" :value="page">
                    {{ page }} of {{ totalPages }}
                  </option>
                </select>

                <div v-else class="flex gap-1">
                  <button
                    v-for="page in totalPages"
                    :key="page"
                    @click="goToPage(page)"
                    :class="[
                      'min-w-[2rem] h-8 px-2 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500',
                      currentPage === page
                        ? 'bg-blue-600 text-white'
                        : 'bg-white text-gray-700 hover:bg-gray-100',
                    ]"
                  >
                    {{ page }}
                  </button>
                </div>
              </div>

              <!-- Next page buttons -->
              <div class="hidden sm:flex items-center gap-2">
                <button
                  @click="nextPage"
                  :disabled="!canGoNext"
                  :class="{ 'opacity-50 cursor-not-allowed': !canGoNext }"
                  class="p-1 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  aria-label="Next page"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-5 w-5"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fill-rule="evenodd"
                      d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                      clip-rule="evenodd"
                    />
                  </svg>
                </button>

                <button
                  @click="goToPage(totalPages)"
                  :disabled="currentPage === totalPages"
                  :class="{ 'opacity-50 cursor-not-allowed': currentPage === totalPages }"
                  class="p-1 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  aria-label="Last page"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-5 w-5"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fill-rule="evenodd"
                      d="M4.293 15.707a1 1 0 010-1.414L8.586 10 4.293 6.707a1 1 0 011.414-1.414l5 5a1 1 0 010 1.414l-5 5a1 1 0 01-1.414 0z"
                      clip-rule="evenodd"
                    />
                    <path
                      fill-rule="evenodd"
                      d="M10.293 15.707a1 1 0 010-1.414L14.586 10l-4.293-3.293a1 1 0 011.414-1.414l5 5a1 1 0 010 1.414l-5 5a1 1 0 01-1.414 0z"
                      clip-rule="evenodd"
                    />
                  </svg>
                </button>
              </div>

              <!-- Mobile navigation -->
              <div class="flex sm:hidden items-center gap-2">
                <button
                  @click="previousPage"
                  :disabled="!canGoPrevious"
                  :class="[
                    'px-3 py-1.5 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500',
                    canGoPrevious
                      ? 'border-gray-300 hover:bg-gray-100'
                      : 'opacity-50 cursor-not-allowed border-gray-200',
                  ]"
                >
                  Prev
                </button>
                <button
                  @click="nextPage"
                  :disabled="!canGoNext"
                  :class="[
                    'px-3 py-1.5 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500',
                    canGoNext
                      ? 'border-gray-300 hover:bg-gray-100'
                      : 'opacity-50 cursor-not-allowed border-gray-200',
                  ]"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Confirmation Dialog for Delete -->
    <div
      v-if="showDeleteConfirm"
      class="fixed inset-0 z-[99999] flex items-center justify-center bg-black/50"
    >
      <div
        class="bg-white rounded-lg shadow-lg p-6 w-full max-w-xs flex flex-col items-center"
      >
        <div class="font-semibold text-lg mb-2 text-center">Delete Confirmation</div>
        <!-- <div class="text-gray-700 text-center mb-4">Are you sure you want to delete this item?</div> -->
        <div class="flex gap-3 mt-2">
          <button
            @click="confirmDelete(false)"
            class="px-4 py-1.5 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 font-medium"
          >
            Cancel
          </button>
          <button
            @click="confirmDelete(true)"
            class="px-4 py-1.5 bg-red-600 text-white rounded hover:bg-red-700 font-medium"
          >
            Yes, Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Animations */
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(6px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

.animate-fade-in {
  animation: fade-in 120ms cubic-bezier(0.24, 0.56, 0.63, 0.99);
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

:deep(td) {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  /* white-space: nowrap; */
}

/* Better scrollbars for webkit browsers */
.overflow-y-auto::-webkit-scrollbar,
.overflow-x-auto::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track,
.overflow-x-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb,
.overflow-x-auto::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover,
.overflow-x-auto::-webkit-scrollbar-thumb:hover {
  background: #ccc;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .flex-col-mobile {
    flex-direction: column;
  }

  .w-full-mobile {
    width: 100%;
  }

  .mt-3-mobile {
    margin-top: 0.75rem;
  }
}

/* Tooltip */
.tooltip {
  position: relative;
}

.tooltip:hover::after {
  content: attr(data-tip);
  position: absolute;
  bottom: 125%;
  left: 50%;
  transform: translateX(-50%);
  padding: 4px 8px;
  border-radius: 4px;
  background: rgba(55, 65, 81, 0.9);
  color: white;
  font-size: 12px;
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  animation: fade-in 200ms ease forwards;
}

.tooltip:hover::before {
  content: "";
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 4px solid transparent;
  border-top-color: rgba(55, 65, 81, 0.9);
  pointer-events: none;
  opacity: 0;
  animation: fade-in 200ms ease forwards;
}

/* Focus styles for better accessibility */
:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Print styles */
@media print {
  .no-print {
    display: none !important;
  }

  * {
    box-shadow: none !important;
  }

  table {
    width: 100% !important;
    border-collapse: collapse !important;
  }

  th,
  td {
    border: 1px solid #ddd !important;
    padding: 8px !important;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
.fade-enter-to,
.fade-leave-from {
  opacity: 1;
}
</style>
