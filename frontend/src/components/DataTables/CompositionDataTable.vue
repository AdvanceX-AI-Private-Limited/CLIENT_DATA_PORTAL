<template>
    <div class="w-full">
      <!-- Top controls section -->
      <div class="flex justify-between items-center mb-6">
        <div>
          <slot name="table-top-left"></slot>
        </div>
        <div class="flex items-center gap-4">
          <slot name="table-top-right">
            <div v-if="showGlobalSearch" class="relative">
              <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input 
                type="text" 
                v-model="globalSearch" 
                :placeholder="searchPlaceholder" 
                class="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-64"
              />
            </div>
          </slot>
        </div>
      </div>
  
      <!-- Table -->
      <div class="overflow-x-auto bg-white rounded-lg shadow w-full" style="min-height: 400px;">
        <table class="w-full table-auto">
          <thead>
            <tr :class="headerClasses">
              <th 
                v-for="(column, index) in visibleColumns" 
                :key="column.key"
                :class="[defaultColumnHeaderClass, column.headerClass]"
              >
                <div class="flex flex-col gap-2">
                  <div class="flex items-center justify-between">
                    <span>{{ column.label || formatColumnName(column.key) }}</span>
                    <div v-if="column.filterable !== false" class="relative" v-click-outside="() => closeFilterDropdown(column.key)">
                      <button 
                        @click="toggleFilterDropdown(column.key)" 
                        class="p-1 rounded-full hover:bg-gray-200"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                        </svg>
                      </button>
                      <div 
                        v-if="openFilterColumn === column.key" 
                        class="absolute z-50 mt-1 right-0 bg-white rounded-md shadow-lg p-3 w-64"
                        style="max-height: 300px; overflow-y: auto;"
                      >
                        <div class="mb-2">
                          <input
                            v-model="filterSearches[column.key]"
                            class="border border-gray-300 rounded px-3 py-2 text-sm w-full"
                            :placeholder="`Search in ${column.label || formatColumnName(column.key)}...`"
                            @input="filterColumnValues(column.key)"
                            @click.stop
                          />
                        </div>
                        <div class="max-h-60 overflow-y-auto">
                          <div class="flex items-center mb-2">
                            <input 
                              type="checkbox" 
                              :id="`select-all-${column.key}`" 
                              v-model="selectAllFilters[column.key]"
                              @change="toggleAllFilterValues(column.key)"
                              class="form-checkbox h-4 w-4 text-blue-600 transition duration-150 ease-in-out"
                            />
                            <label :for="`select-all-${column.key}`" class="ml-2 text-sm text-gray-700">Select All</label>
                          </div>
                          <div v-for="(value, idx) in filteredColumnValues[column.key]" :key="`${column.key}-${idx}`" class="flex items-center mb-1">
                            <input 
                              type="checkbox" 
                              :id="`${column.key}-${idx}`" 
                              v-model="selectedFilterValues[column.key][value]"
                              @change="updateFilters(column.key)"
                              class="form-checkbox h-4 w-4 text-blue-600 transition duration-150 ease-in-out"
                            />
                            <label :for="`${column.key}-${idx}`" class="ml-2 text-sm text-gray-700 truncate">{{ value || '(Empty)' }}</label>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </th>
              <th v-if="showActions" :class="[defaultColumnHeaderClass, 'w-16']">
                {{ actionsColumnTitle }}
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr 
              v-for="(row, rowIndex) in paginatedData" 
              :key="getRowKey(row, rowIndex)"
              :class="rowClasses"
              @click="handleRowClick(row, rowIndex)"
            >
              <td 
                v-for="column in visibleColumns" 
                :key="`${getRowKey(row, rowIndex)}-${column.key}`"
                :class="[defaultCellClass, column.cellClass]"
              >
                <slot :name="`cell-${column.key}`" :row="row" :value="row[column.key]" :index="rowIndex">
                  {{ formatCellValue(row[column.key], column.formatter) }}
                </slot>
              </td>
              <td v-if="showActions" :class="[defaultCellClass, 'relative']">
                <div class="relative" v-click-outside="() => (openActionMenu !== rowIndex ? null : openActionMenu = null)">
                  <button 
                    @click.stop="toggleActionMenu(rowIndex)" 
                    class="p-1 rounded-full hover:bg-gray-200"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-500" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                    </svg>
                  </button>
                  <div 
                    v-if="openActionMenu === rowIndex" 
                    class="absolute z-10 mt-1 right-0 bg-white rounded-md shadow-lg w-36"
                  >
                    <button 
                      v-for="(action, actionIndex) in availableActions" 
                      :key="actionIndex"
                      @click.stop="handleAction(action, row, rowIndex)"
                      :class="getActionButtonClass(action)"
                    >
                      <div class="flex items-center">
                        <span v-if="action.icon" v-html="action.icon" class="mr-2"></span>
                        {{ action.label }}
                      </div>
                    </button>
                  </div>
                </div>
              </td>
            </tr>
            <tr v-if="paginatedData.length === 0">
              <td 
                :colspan="showActions ? visibleColumns.length + 1 : visibleColumns.length" 
                class="px-4 py-16 text-center"
              >
                <div class="flex flex-col items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-gray-300 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span class="text-gray-500 font-medium">{{ noDataText }}</span>
                  <span class="text-gray-400 text-sm mt-1">{{ noDataSubtext }}</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
  
      <!-- Pagination and info section -->
      <div v-if="showPagination" class="flex flex-col md:flex-row justify-between items-center mt-6 gap-4">
        <div class="flex items-center gap-4 order-2 md:order-1">
          <div v-if="showPageSizeSelector" class="flex items-center">
            <label v-if="pageSizeSelectorLabel" class="text-sm text-gray-600 mr-2">{{ pageSizeSelectorLabel }}</label>
            <select 
              v-model="pageSize" 
              class="border rounded px-3 py-1 text-sm bg-white shadow-sm min-w-[70px]"
            >
              <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }}</option>
            </select>
          </div>
          
          <div v-if="showRecordInfo" class="text-sm text-gray-600 ml-2">
            {{ recordInfoText }}
          </div>
        </div>
        
        <div class="flex gap-2 order-1 md:order-2">
          <button 
            @click="prevPage" 
            :disabled="currentPage === 1"
            :class="paginationButtonClass"
          >
            <span class="flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
              {{ prevPageText }}
            </span>
          </button>
          
          <div class="flex items-center gap-1">
            <button 
              v-for="page in displayedPages" 
              :key="page" 
              @click="goToPage(page)"
              class="w-8 h-8 flex items-center justify-center rounded-md"
              :class="currentPage === page ? 'bg-blue-500 text-white' : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'"
            >
              {{ page }}
            </button>
          </div>
          
          <button 
            @click="nextPage" 
            :disabled="currentPage >= totalPages"
            :class="paginationButtonClass"
          >
            <span class="flex items-center">
              {{ nextPageText }}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </span>
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, computed, watch, onMounted } from 'vue';
  
  export default {
    name: 'DataTable',
    props: {
      // Core data props
      data: {
        type: Array,
        required: true,
        default: () => []
      },
      // Column configuration
      columns: {
        type: Array,
        default: () => []
      },
      // Unique identifier for rows
      rowKey: {
        type: String,
        default: 'id'
      },
      
      // Actions configuration
      showActions: {
        type: Boolean,
        default: false
      },
      actions: {
        type: Array,
        default: () => [
          { 
            label: 'Edit', 
            action: 'edit', 
            icon: '<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>'
          },
          { 
            label: 'Delete', 
            action: 'delete', 
            icon: '<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>',
            class: 'text-red-600 hover:bg-red-50'
          }
        ]
      },
      actionsColumnTitle: {
        type: String,
        default: 'Actions'
      },
      
      // UI Configuration
      headerClasses: {
        type: String,
        default: 'bg-gradient-to-r from-blue-50 to-blue-100 border-b'
      },
      rowClasses: {
        type: String,
        default: 'hover:bg-blue-50 transition-colors duration-150'
      },
      defaultColumnHeaderClass: {
        type: String,
        default: 'px-4 py-3 text-left text-sm font-medium text-gray-700 uppercase tracking-wider'
      },
      defaultCellClass: {
        type: String,
        default: 'px-4 py-3 text-sm text-gray-700 border-b border-gray-100'
      },
      
      // Search Configuration
      showGlobalSearch: {
        type: Boolean,
        default: true
      },
      searchPlaceholder: {
        type: String,
        default: 'Search in all columns...'
      },
      
      // Pagination configuration
      showPagination: {
        type: Boolean,
        default: true
      },
      pageSizeOptions: {
        type: Array,
        default: () => [5, 10, 25, 50]
      },
      defaultPageSize: {
        type: Number,
        default: 10
      },
      prevPageText: {
        type: String,
        default: 'Prev'
      },
      nextPageText: {
        type: String,
        default: 'Next'
      },
      pageSizeSelectorLabel: {
        type: String,
        default: 'Show'
      },
      showPageSizeSelector: {
        type: Boolean,
        default: true
      },
      showRecordInfo: {
        type: Boolean,
        default: true
      },
      paginationButtonClass: {
        type: String,
        default: 'px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed'
      },
      
      // Empty state
      noDataText: {
        type: String,
        default: 'No matching records found'
      },
      noDataSubtext: {
        type: String,
        default: 'Try adjusting your filters'
      }
    },
    emits: [
      'row-click',
      'action',
      'edit',
      'delete',
      'page-change',
      'filter-change'
    ],
    setup(props, { emit }) {
      // State
      const filters = ref({});
      const currentPage = ref(1);
      const pageSize = ref(props.defaultPageSize);
      const openFilterColumn = ref(null);
      const openActionMenu = ref(null);
      const globalSearch = ref('');
      const filterSearches = ref({});
      const selectedFilterValues = ref({});
      const selectAllFilters = ref({});
      const filteredColumnValues = ref({});
      const uniqueColumnValues = ref({});
      
      // Row click handler
      const handleRowClick = (row, rowIndex) => {
        emit('row-click', row, rowIndex);
      };
      
      // Action handlers
      const handleAction = (action, row, rowIndex) => {
        openActionMenu.value = null;
        
        // Emit both generic and specific action events
        emit('action', { action, row, rowIndex });
        emit(action, row, rowIndex);
      };
      
      // Toggle action menu
      const toggleActionMenu = (rowIndex) => {
        openActionMenu.value = openActionMenu.value === rowIndex ? null : rowIndex;
      };
      
      // Get class for action button
      const getActionButtonClass = (action) => {
        const baseClass = 'block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-blue-50';
        return action.class ? `${baseClass} ${action.class}` : baseClass;
      };
      
      // Generate unique key for row
      const getRowKey = (row, fallbackIndex) => {
        return props.rowKey && row[props.rowKey] !== undefined ? row[props.rowKey] : fallbackIndex;
      };
      
      // Close filter dropdown when clicking outside
      const closeFilterDropdown = (column) => {
        if (openFilterColumn.value === column) {
          openFilterColumn.value = null;
        }
      };
      
      const toggleFilterDropdown = (column) => {
        if (openFilterColumn.value !== column) {
          // Before opening a filter dropdown, update filtered values to reflect current state
          updateFilteredColumnValues();
        }
        openFilterColumn.value = openFilterColumn.value === column ? null : column;
      };
      
      // Click outside directive
      const clickOutside = {
        mounted(el, binding) {
          el._clickOutside = (event) => {
            if (!(el === event.target || el.contains(event.target))) {
              binding.value(event);
            }
          };
          document.addEventListener('click', el._clickOutside);
        },
        unmounted(el) {
          document.removeEventListener('click', el._clickOutside);
        }
      };
      
      // Register directive
      const vClickOutside = clickOutside;
      
      // Process column definitions
      const visibleColumns = computed(() => {
        // If columns are explicitly defined, use them
        if (props.columns.length > 0) {
          return props.columns.filter(col => col.visible !== false);
        }
        
        // Otherwise, derive from first data item
        if (props.data && props.data.length > 0) {
          return Object.keys(props.data[0]).map(key => ({
            key,
            label: formatColumnName(key)
          }));
        }
        
        return [];
      });
      
      // Available actions for dropdown
      const availableActions = computed(() => {
        return props.actions;
      });
  
      // Initialize filters and unique values for each column
      onMounted(() => {
        initializeColumns();
      });
      
      // Re-initialize when data changes
      watch(() => props.data, () => {
        initializeColumns();
      }, { deep: true });
      
      // Initialize column filters
      const initializeColumns = () => {
        if (!props.data || props.data.length === 0) return;
        
        // Process each column
        visibleColumns.value.forEach(column => {
          const columnKey = column.key;
          
          // Initialize filter objects
          filters.value[columnKey] = '';
          filterSearches.value[columnKey] = '';
          selectedFilterValues.value[columnKey] = {};
          selectAllFilters.value[columnKey] = true;
          
          // Get unique values for each column
          const values = new Set();
          props.data.forEach(row => {
            const val = row[columnKey] !== null && row[columnKey] !== undefined ? row[columnKey].toString() : '';
            values.add(val);
          });
          uniqueColumnValues.value[columnKey] = Array.from(values);
          filteredColumnValues.value[columnKey] = [...uniqueColumnValues.value[columnKey]];
          
          // Initialize all values as selected
          uniqueColumnValues.value[columnKey].forEach(value => {
            selectedFilterValues.value[columnKey][value] = true;
          });
        });
      };
  
      // Filter column values based on search
      const filterColumnValues = (column) => {
        const search = filterSearches.value[column].toLowerCase();
        if (search) {
          filteredColumnValues.value[column] = uniqueColumnValues.value[column].filter(
            value => value.toLowerCase().includes(search)
          );
        } else {
          filteredColumnValues.value[column] = [...uniqueColumnValues.value[column]];
        }
      };
      
      // Toggle all filter values
      const toggleAllFilterValues = (column) => {
        const isSelected = selectAllFilters.value[column];
        filteredColumnValues.value[column].forEach(value => {
          selectedFilterValues.value[column][value] = isSelected;
        });
        updateFilters(column);
      };
      
      // Update filtered column values based on currently filtered data
      // This ensures each column's filter options only show values from the currently filtered data
      const updateFilteredColumnValues = () => {
        visibleColumns.value.forEach(column => {
          const columnKey = column.key;
          const search = filterSearches.value[columnKey] || '';
          
          // Get unique values only from the currently filtered data
          const values = new Set();
          filteredData.value.forEach(row => {
            const val = row[columnKey] !== null && row[columnKey] !== undefined ? row[columnKey].toString() : '';
            values.add(val);
          });
          
          // Convert to array and filter by search if needed
          let filteredValues = Array.from(values);
          if (search) {
            filteredValues = filteredValues.filter(value => 
              value.toLowerCase().includes(search.toLowerCase())
            );
          }
          
          // Update the filtered values
          filteredColumnValues.value[columnKey] = filteredValues;
          
          // Update "select all" state
          if (filteredValues.length > 0) {
            const allSelected = filteredValues.every(value => 
              selectedFilterValues.value[columnKey][value]
            );
            selectAllFilters.value[columnKey] = allSelected;
          }
        });
      };
  
      // Update filters based on selected values
      const updateFilters = (column) => {
        // Check if all filtered values are selected
        const allSelected = filteredColumnValues.value[column].every(
          value => selectedFilterValues.value[column][value]
        );
        selectAllFilters.value[column] = allSelected;
        
        // Reset to page 1 when filters change
        currentPage.value = 1;
        
        // After filter has been applied, update available values for other columns
        updateFilteredColumnValues();
        
        // Emit filter change event
        emit('filter-change', { column, filters: selectedFilterValues.value });
      };
  
      // Format column name for display (capitalize, convert snake_case to spaces)
      const formatColumnName = (column) => {
        return column
          .replace(/_/g, ' ')
          .replace(/\b\w/g, char => char.toUpperCase());
      };
  
      // Format cell value for display
      const formatCellValue = (value, formatter) => {
        // Apply custom formatter if provided
        if (formatter && typeof formatter === 'function') {
          return formatter(value);
        }
        
        // Default formatting
        if (value === null || value === undefined) {
          return '-';
        }
        if (typeof value === 'object') {
          return JSON.stringify(value);
        }
        return value;
      };
  
      // Total number of records
      const totalRecords = computed(() => props.data.length);
  
      // Apply filters to get filtered data
      const filteredData = computed(() => {
        return props.data.filter(row => {
          // Global search filter
          if (globalSearch.value) {
            const searchTerm = globalSearch.value.toLowerCase();
            const matchesGlobalSearch = visibleColumns.value.some(column => {
              const cellValue = row[column.key];
              if (cellValue === null || cellValue === undefined) return false;
              return String(cellValue).toLowerCase().includes(searchTerm);
            });
            
            if (!matchesGlobalSearch) return false;
          }
          
          // Column filters
          return visibleColumns.value.every(column => {
            const columnKey = column.key;
            const filterValues = selectedFilterValues.value[columnKey];
            if (!filterValues) return true;
            
            const hasActiveFilter = Object.values(filterValues).some(val => !val);
            
            if (!hasActiveFilter) return true;
            
            const cellValue = row[columnKey];
            const strValue = cellValue !== null && cellValue !== undefined ? cellValue.toString() : '';
            return selectedFilterValues.value[columnKey][strValue];
          });
        });
      });
  
      // Calculate total pages
      const totalPages = computed(() => {
        return Math.max(1, Math.ceil(filteredData.value.length / pageSize.value));
      });
  
      // Get paginated data slice
      const paginatedData = computed(() => {
        const start = (currentPage.value - 1) * pageSize.value;
        const end = start + pageSize.value;
        return filteredData.value.slice(start, end);
      });
  
      // Calculate displayed page numbers
      const displayedPages = computed(() => {
        if (totalPages.value <= 7) {
          return Array.from({ length: totalPages.value }, (_, i) => i + 1);
        }
        
        // Complex pagination with ellipsis logic
        const pages = [];
        if (currentPage.value <= 3) {
          for (let i = 1; i <= 5; i++) pages.push(i);
          pages.push(totalPages.value);
        } else if (currentPage.value >= totalPages.value - 2) {
          pages.push(1);
          for (let i = totalPages.value - 4; i <= totalPages.value; i++) pages.push(i);
        } else {
          pages.push(1);
          for (let i = currentPage.value - 1; i <= currentPage.value + 1; i++) pages.push(i);
          pages.push(totalPages.value);
        }
        
        return pages;
      });
      
      // Record info text
      const recordInfoText = computed(() => {
        return `Showing ${paginatedData.value.length} of ${filteredData.value.length} records (${totalRecords.value} total)`;
      });
  
      // Navigation functions
      const goToPage = (page) => {
        currentPage.value = page;
        emit('page-change', page);
      };
  
      const nextPage = () => {
        if (currentPage.value < totalPages.value) {
          currentPage.value++;
          emit('page-change', currentPage.value);
        }
      };
  
      const prevPage = () => {
        if (currentPage.value > 1) {
          currentPage.value--;
          emit('page-change', currentPage.value);
        }
      };
  
      // Reset page when page size changes
      watch(pageSize, () => {
        const maxPage = Math.max(1, Math.ceil(filteredData.value.length / pageSize.value));
        currentPage.value = Math.min(currentPage.value, maxPage);
        emit('page-change', currentPage.value);
      });
  
      // Watch filtered data to update the filter options
      watch(filteredData, () => {
        updateFilteredColumnValues();
      }, { deep: true });
  
      return {
        // Computed properties
        visibleColumns,
        totalRecords,
        filteredData,
        paginatedData,
        totalPages,
        displayedPages,
        availableActions,
        recordInfoText,
        
        // State refs
        filters,
        currentPage,
        pageSize,
        openFilterColumn,
        openActionMenu,
        globalSearch,
        filterSearches,
        selectedFilterValues,
        selectAllFilters,
        filteredColumnValues,
        
        // Functions
        formatColumnName,
        formatCellValue,
        goToPage,
        nextPage,
        prevPage,
        toggleFilterDropdown,
        closeFilterDropdown,
        filterColumnValues,
        toggleAllFilterValues,
        updateFilters,
        toggleActionMenu,
        handleAction,
        handleRowClick,
        getRowKey,
        getActionButtonClass,
        
        // Directives
        vClickOutside
      };
    },
    directives: {
      'click-outside': {
        mounted(el, binding) {
          el._clickOutside = (event) => {
            if (!(el === event.target || el.contains(event.target))) {
              binding.value(event);
            }
          };
          document.addEventListener('click', el._clickOutside);
        },
        unmounted(el) {
          document.removeEventListener('click', el._clickOutside);
        }
      }
    }
  }
  </script>