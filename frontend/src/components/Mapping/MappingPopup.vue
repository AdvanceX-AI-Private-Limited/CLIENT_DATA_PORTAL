// MappingPopup.vue
<script setup>
import { ref, computed, watch, toRaw, onMounted } from 'vue'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  tabs: Array,
  title: { type: String, default: 'Bulk Assign Mappings' },
  selections: { type: Object, required: true }
})

const emit = defineEmits(['close', 'update:selections', 'submit'])

const displayedTabs = computed(() => [
  ...props.tabs,
  { label: "Review", key: "review" }
])

const activeTab = ref(displayedTabs.value[0]?.key)
const tabData = ref([])
const searchQuery = ref('')
const sortDirection = ref('asc')

// --- make a local copy of selections, sync with prop ---
const localSelections = ref(JSON.parse(JSON.stringify(toRaw(props.selections))))

watch(() => props.selections, (newVal) => {
  // deep copy for safety
  localSelections.value = JSON.parse(JSON.stringify(newVal))
}, { deep: true })

function emitSelections() {
  emit('update:selections', JSON.parse(JSON.stringify(localSelections.value)))
}

// --- Loading data for tab ---
watch(activeTab, async (newTab) => {
  searchQuery.value = ''
  sortDirection.value = 'asc'
  const t = props.tabs.find(tab => tab.key === newTab)
  if (t?.fetchData) {
    const data = await t.fetchData()
    // Add unique identifiers if not present
    data.forEach((item, index) => {
      if (!item.hasOwnProperty('id')) {
        const heading = item[t.displayMapping.heading] || '';
        const sub = item[t.displayMapping.sub] || '';
        item.id = `${heading.toString().substring(0, 10)}_${sub.toString().substring(0, 10)}_${index}`;
      }
    });
    tabData.value = data || [];
  } else {
    tabData.value = []
  }
}, { immediate: true })

function getTabSelections(tabKey) {
  if (!localSelections.value[tabKey]) localSelections.value[tabKey] = []
  return localSelections.value[tabKey]
}

function getItemIdentifier(item) {
  return item.id || `${JSON.stringify(item)}`;
}

function isSelected(tabKey, item) {
  const itemId = getItemIdentifier(item);
  return getTabSelections(tabKey).some(x => getItemIdentifier(x) === itemId)
}

function toggleSelection(tabKey, item) {
  const arr = getTabSelections(tabKey)
  const itemId = getItemIdentifier(item);
  const idx = arr.findIndex(x => getItemIdentifier(x) === itemId)
  if (idx > -1) {
    arr.splice(idx, 1)
  } else {
    arr.push(item)
  }
  emitSelections()
}

// Select all per tab
function isAllSelected(tabKey, items) {
  if (!items.length) return false
  return items.every(i => isSelected(tabKey, i))
}

function toggleAll(tabKey, items) {
  if (isAllSelected(tabKey, items)) {
    localSelections.value[tabKey] = []
  } else {
    localSelections.value[tabKey] = [...items]
  }
  emitSelections()
}

const currentTab = computed(() =>
  displayedTabs.value.find(tab => tab.key === activeTab.value)
)

// Filtered and sorted data
const processedData = computed(() => {
  if (!currentTab.value || !tabData.value.length) return []
  
  let filtered = tabData.value
  
  // Apply search filter
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    const tab = currentTab.value
    filtered = filtered.filter(item => {
      const heading = item[tab.displayMapping.heading]?.toString().toLowerCase() || ''
      const sub = item[tab.displayMapping.sub]?.toString().toLowerCase() || ''
      return heading.includes(query) || sub.includes(query)
    })
  }
  
  // Apply sorting if we have a current tab with display mapping
  if (currentTab.value?.displayMapping?.heading) {
    const field = currentTab.value.displayMapping.heading
    filtered = [...filtered].sort((a, b) => {
      const valA = (a[field] || '').toString().toLowerCase()
      const valB = (b[field] || '').toString().toLowerCase()
      return sortDirection.value === 'asc' 
        ? valA.localeCompare(valB) 
        : valB.localeCompare(valA)
    })
  }
  
  return filtered
})

// Mapping: create combinations of all tab selections
const mappingPairs = computed(() => {
  if (props.tabs.length < 2) return []
  
  // Get selections from all tabs
  const tabSelections = props.tabs.map(tab => getTabSelections(tab.key))
  
  // Return empty array if any tab has no selections
  if (tabSelections.some(selections => selections.length === 0)) return []
  
  // Create combinations of selections from all tabs (cartesian product)
  const generateCombinations = (index = 0, currentCombination = []) => {
    if (index >= tabSelections.length) {
      return [currentCombination];
    }
    
    const combinations = [];
    for (const item of tabSelections[index]) {
      combinations.push(
        ...generateCombinations(index + 1, [...currentCombination, item])
      );
    }
    return combinations;
  };
  
  return generateCombinations();
})

function toggleSort() {
  sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
}

function getTabIndex() {
  return displayedTabs.value.findIndex(tab => tab.key === activeTab.value)
}

function nextTab() {
  const currentIndex = getTabIndex()
  if (currentIndex < displayedTabs.value.length - 1) {
    activeTab.value = displayedTabs.value[currentIndex + 1].key
  }
}

function prevTab() {
  const currentIndex = getTabIndex()
  if (currentIndex > 0) {
    activeTab.value = displayedTabs.value[currentIndex - 1].key
  }
}

// ---- Submit -----
function submit() {
  emit('submit', mappingPairs.value);
  close();
}

function close() { emit('close') }

// Get selection counts
function getSelectionCount(tabKey) {
  return getTabSelections(tabKey).length
}

// Toggle summary panel
const showSummary = ref(false)

// Handle edge case of no data
const noDataAvailable = computed(() => {
  return processedData.value.length === 0 && !searchQuery.value.trim()
})

// Handle edge case of no search results
const noSearchResults = computed(() => {
  return processedData.value.length === 0 && searchQuery.value.trim() !== ''
})

// Compute maximum items to display at once for better performance
const maxItemsToShow = ref(50)
onMounted(() => {
  // Adjust based on screen size
  const height = window.innerHeight
  maxItemsToShow.value = Math.floor(height / 16) // approximate row height
})

// Virtual scrolling support - only render visible items for performance
const displayedItems = computed(() => {
  return processedData.value.slice(0, maxItemsToShow.value)
})

// Keep track if we need to load more items
function loadMoreItems() {
  maxItemsToShow.value += 30
}
</script>

<template>
  <div class="fixed inset-0 bg-black/50 flex justify-center items-center z-50 overflow-hidden">
    <div class="bg-white rounded-lg shadow-xl w-[90%] max-w-3xl relative h-[85vh] flex flex-col">
      <!-- Header - Modernized -->
      <div class="p-4 pb-3 border-b bg-gradient-to-r from-gray-50 to-white">
        <div class="flex justify-between items-center">
          <h2 class="text-lg font-bold text-gray-800">{{ props.title }}</h2>
          <button @click="close" class="w-6 h-6 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-600 hover:text-gray-800 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <p class="text-gray-500 text-xs mt-1">Create multiple mappings between users, outlets, and services simultaneously.</p>
      </div>

      <!-- Progress Tabs - Modern Style -->
      <div class="px-4 py-3 border-b bg-white">
        <div class="flex">
          <div 
            v-for="(tab, index) in displayedTabs" 
            :key="tab.key" 
            class="flex items-center text-sm relative"
          >
            <div class="flex items-center">
              <div 
                class="w-6 h-6 rounded-full flex items-center justify-center mr-2 text-xs shadow-sm transition-all"
                :class="{
                  'bg-gradient-to-r from-blue-500 to-indigo-600 text-white': activeTab === tab.key,
                  'bg-white text-gray-500 border border-gray-200': activeTab !== tab.key && index < getTabIndex(),
                  'bg-gray-100 text-gray-400 border border-gray-200': activeTab !== tab.key && index > getTabIndex()
                }"
              >
                <svg 
                  v-if="activeTab !== tab.key && index < getTabIndex()" 
                  xmlns="http://www.w3.org/2000/svg" 
                  class="h-3 w-3 text-blue-500" 
                  viewBox="0 0 20 20" 
                  fill="currentColor"
                >
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                <span v-else>{{ index + 1 }}</span>
              </div>
              <span 
                :class="{
                  'font-medium text-gray-900': activeTab === tab.key,
                  'text-blue-500': activeTab !== tab.key && index < getTabIndex(),
                  'text-gray-400': activeTab !== tab.key && index > getTabIndex()
                }"
                class="text-sm"
              >
                {{ tab.label }}
              </span>
            </div>
            <div v-if="index < displayedTabs.length - 1" class="mx-2 text-gray-300 flex items-center">
              <div class="h-px w-4 bg-gray-300"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content Area -->
      <div class="flex-1 overflow-hidden flex flex-col p-2">
        <!-- Data Selection Tab -->
        <div v-if="currentTab && currentTab.key !== 'review'" class="flex flex-col h-full">
          <!-- Search and Sort - Modern UI -->
          <div class="flex justify-between items-center mb-3 px-1">
            <div class="relative w-full max-w-xs">
              <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <svg class="w-3.5 h-3.5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
                </svg>
              </div>
              <input 
                type="text" 
                class="bg-white border border-gray-200 text-gray-900 text-xs rounded-lg shadow-sm block w-full pl-10 p-2 focus:ring-2 focus:ring-blue-100 focus:border-blue-300 transition-all" 
                :placeholder="`Search ${currentTab.label.toLowerCase()}...`"
                v-model="searchQuery"
              >
            </div>
            
            <button 
              @click="toggleSort" 
              class="px-2 py-1.5 bg-white border border-gray-200 shadow-sm text-gray-700 hover:bg-gray-50 rounded-lg text-xs flex items-center transition-colors ml-2"
            >
              <span class="mr-1.5">{{ sortDirection === 'asc' ? 'A→Z' : 'Z→A' }}</span>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                <path v-if="sortDirection === 'asc'" d="M3 3a1 1 0 000 2h11a1 1 0 100-2H3zM3 7a1 1 0 000 2h7a1 1 0 100-2H3zM3 11a1 1 0 100 2h4a1 1 0 100-2H3zM15 8a1 1 0 10-2 0v5.586l-1.293-1.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L15 13.586V8z" />
                <path v-else="true" d="M3 3a1 1 0 000 2h11a1 1 0 100-2H3zM3 7a1 1 0 000 2h7a1 1 0 100-2H3zM3 11a1 1 0 100 2h4a1 1 0 100-2H3zM15 8a1 1 0 10-2 0v5.586l-1.293-1.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L15 13.586V8z" />
              </svg>
            </button>
          </div>

          <!-- Select All + Selection info - Modern Style -->
          <div class="flex justify-between items-center mb-2 px-1">
            <div 
              class="flex items-center px-2 py-1 rounded-md cursor-pointer hover:bg-gray-50"
              @click="toggleAll(currentTab.key, processedData)"
            >
              <div 
                class="w-4 h-4 flex-shrink-0 rounded flex items-center justify-center border transition-colors"
                :class="{
                  'bg-blue-500 border-blue-500': isAllSelected(currentTab.key, processedData),
                  'bg-white border-gray-300': !isAllSelected(currentTab.key, processedData)
                }"
              >
                <svg 
                  v-if="isAllSelected(currentTab.key, processedData)" 
                  xmlns="http://www.w3.org/2000/svg" 
                  class="h-3 w-3 text-white" 
                  viewBox="0 0 20 20" 
                  fill="currentColor"
                >
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </div>
              <label class="ml-2 text-xs font-medium text-gray-700 cursor-pointer">
                Select all
              </label>
              <!-- Hidden real checkbox for accessibility -->
              <input
                type="checkbox"
                :id="currentTab.key + '_selectall'"
                :checked="isAllSelected(currentTab.key, processedData)"
                @change="toggleAll(currentTab.key, processedData)"
                class="sr-only"
              />
            </div>
            <div class="bg-blue-50 text-blue-600 text-xs font-medium px-2 py-1 rounded-full shadow-sm">
              {{ getSelectionCount(currentTab.key) }} selected
            </div>
          </div>

          <!-- List of items - compact design -->
          <div 
            class="overflow-y-auto flex-grow min-h-0 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100" 
            @scroll="e => {
              if (e.target.scrollHeight - e.target.scrollTop < e.target.clientHeight + 100) loadMoreItems()
            }"
          >
            <!-- Empty state when no data -->
            <div v-if="noDataAvailable" class="py-8 flex flex-col items-center justify-center text-gray-400">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
              <p class="text-sm">No data available</p>
            </div>
            
            <!-- No search results -->
            <div v-else-if="noSearchResults" class="py-8 flex flex-col items-center justify-center text-gray-400">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <p class="text-sm">No results for "{{ searchQuery }}"</p>
            </div>
            
            <!-- List items with modern styling -->
            <div v-else class="px-1">
              <div 
                v-for="(item, index) in displayedItems"
                :key="getItemIdentifier(item)"
                class="mb-1.5 flex items-center shadow-sm hover:shadow transition-all duration-200 rounded-md overflow-hidden"
                :class="{
                  'bg-white border-l-4 border-l-transparent': !isSelected(currentTab.key, item),
                  'bg-blue-50 border-l-4 border-l-blue-500': isSelected(currentTab.key, item)
                }"
              >
                <div 
                  class="flex items-center flex-1 pl-3 pr-2 py-2 cursor-pointer"
                  @click="toggleSelection(currentTab.key, item)"
                >
                  <!-- Custom checkbox -->
                  <div 
                    class="w-4 h-4 flex-shrink-0 rounded flex items-center justify-center border"
                    :class="{
                      'bg-blue-500 border-blue-500': isSelected(currentTab.key, item),
                      'bg-white border-gray-300': !isSelected(currentTab.key, item)
                    }"
                  >
                    <svg 
                      v-if="isSelected(currentTab.key, item)" 
                      xmlns="http://www.w3.org/2000/svg" 
                      class="h-3 w-3 text-white" 
                      viewBox="0 0 20 20" 
                      fill="currentColor"
                    >
                      <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                    </svg>
                  </div>
                  
                  <!-- Avatar with updated styling -->
                  <!-- <div class="ml-3 w-7 h-7 rounded-full overflow-hidden flex items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200 text-gray-600 flex-shrink-0 border border-white shadow-sm">
                    <svg v-if="!item.avatar" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    <img v-else :src="item.avatar" :alt="item[currentTab.displayMapping.heading]" class="w-full h-full object-cover" />
                  </div> -->
                  
                  <!-- Content with improved typography -->
                  <div class="flex-1 ml-4 truncate">
                    <div class="font-medium text-xs text-gray-800">
                      {{ item[currentTab.displayMapping.heading] || '' }}
                    </div>
                    <div class="text-xs text-gray-500 truncate">
                      {{ item[currentTab.displayMapping.sub] || '' }}
                    </div>
                  </div>
                  
                  <!-- Hidden real checkbox for accessibility -->
                  <input
                    type="checkbox"
                    :checked="isSelected(currentTab.key, item)"
                    @change="toggleSelection(currentTab.key, item)"
                    class="sr-only"
                    :id="`${currentTab.key}_${index}`"
                  />
                </div>
              </div>
              
              <!-- Loading more indicator -->
              <div v-if="processedData.length > displayedItems.length" class="flex justify-center py-3">
                <div class="px-4 py-1 bg-gray-100 rounded-full text-xs text-gray-500 animate-pulse">
                  Loading more...
                </div>
              </div>
            </div>
          </div>

          <!-- Current Selection Summary - Modern Collapsible Panel -->
          <div class="mt-3">
            <div 
              @click="showSummary = !showSummary" 
              class="bg-white px-3 py-2 rounded-lg flex justify-between items-center cursor-pointer hover:bg-gray-50 shadow-sm border border-gray-100 transition-all"
              :class="{'shadow-md': showSummary}"
            >
              <div class="text-xs font-medium text-gray-700 flex items-center flex-wrap gap-2">
                <span class="text-gray-500">Current Selection:</span>
                <div class="flex flex-wrap gap-1">
                  <span 
                    v-for="tab in props.tabs" 
                    :key="tab.key" 
                    class="px-2 py-0.5 rounded-full text-xs inline-flex items-center"
                    :class="getSelectionCount(tab.key) > 0 ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-500'"
                  >
                    <span class="font-medium mr-1">{{ getSelectionCount(tab.key) }}</span>
                    <span>{{ tab.label }}</span>
                  </span>
                </div>
              </div>
              <div
                class="w-5 h-5 rounded-full bg-gray-100 flex items-center justify-center transition-transform duration-200"
                :class="{'rotate-180': showSummary}"
              >
                <svg 
                  xmlns="http://www.w3.org/2000/svg" 
                  class="h-3 w-3 text-gray-500" 
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
            
            <!-- Expanded summary -->
            <div 
              v-if="showSummary" 
              class="mt-1 rounded-lg bg-white shadow-md text-xs overflow-hidden transition-all duration-200 border border-gray-100"
            >
              <div class="grid grid-cols-3 divide-x divide-gray-100">
                <div 
                  v-for="tab in props.tabs" 
                  :key="tab.key"
                  class="p-3"
                >
                  <div class="font-medium text-gray-800 mb-1">{{ tab.label }}</div>
                  <div class="flex justify-between items-center">
                    <span class="text-gray-500">Selected:</span>
                    <span 
                      class="font-medium px-2 py-0.5 rounded-full"
                      :class="getSelectionCount(tab.key) > 0 ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-500'"
                    >
                      {{ getSelectionCount(tab.key) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Review Tab - more compact -->
        <div v-if="currentTab && currentTab.key === 'review'" class="overflow-auto h-full px-1">
          <h3 class="font-medium text-sm mb-3">Review Selections</h3>
          
          <!-- Empty state -->
          <div v-if="!mappingPairs.length" class="py-10 flex flex-col items-center justify-center text-gray-400">
            <ExclamationTriangleIcon class="h-8 w-8 mb-2" />
            <p class="text-sm">Nothing to map. Please select items in both tabs.</p>
          </div>
          
          <!-- Mapping table -->
          <table v-else class="w-full text-left mb-4 text-sm">
            <thead class="bg-gray-50 text-gray-700">
              <tr>
                <th v-for="tab in props.tabs" :key="tab.key" class="px-3 py-1.5 text-xs font-medium">{{ tab.label }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(combination, i) in mappingPairs" :key="i" class="border-b hover:bg-gray-50">
                <td v-for="(tab, index) in props.tabs" :key="tab.key" class="px-3 py-2">
                  <div class="font-medium text-xs">{{ combination[index][tab.displayMapping.heading] }}</div>
                  <div v-if="tab.displayMapping.sub" class="text-xs text-gray-500">{{ combination[index][tab.displayMapping.sub] }}</div>
                </td>
              </tr>
            </tbody>
          </table>
          
          <!-- Mapping Options Warning -->
          <!-- <div class="mt-4 bg-yellow-50 border border-yellow-200 p-2 rounded">
            <div class="flex items-start">
              <ExclamationTriangleIcon class="h-4 w-4 text-yellow-600 mr-1.5 mt-0.5 flex-shrink-0" />
              <div>
                <h4 class="font-medium text-yellow-800 text-xs">Mapping Options</h4>
                <p class="text-xs text-yellow-700 mt-0.5">Choose whether to append new mappings or overwrite existing ones. Conflicts will be highlighted for review.</p>
              </div>
            </div>
          </div> -->
        </div>
      </div>

      <!-- Footer Actions -->
      <div class="p-3 border-t flex justify-between gap-2 bg-gray-50">
        <button @click="close" class="text-xs text-gray-700 py-2 px-4 border rounded-lg hover:bg-gray-100 cursor-pointer">Cancel</button>
        
        <div class="flex gap-2">
          <!-- Back button - only show if not on first tab -->
          <button 
            v-if="getTabIndex() > 0"
            @click="prevTab" 
            class="px-4 py-2 text-xs text-gray-700 border rounded-lg hover:bg-gray-100 cursor-pointer"
          >
            Back
          </button>
          <button 
            v-if="currentTab.key === 'review'"
            @click="submit" 
            class="px-4 py-2 text-xs bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-blue-300 disabled:cursor-not-allowed"
            :disabled="!mappingPairs.length"
          >
            Submit Mapping
          </button>
          <button 
            v-else
            @click="nextTab" 
            class="px-4 py-2 text-xs bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            Next: {{ displayedTabs[getTabIndex() + 1]?.label || 'Review' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Custom scrollbar */
.scrollbar-thin::-webkit-scrollbar {
  width: 4px;
}
.scrollbar-thin::-webkit-scrollbar-track {
  background: #f1f1f1;
}
.scrollbar-thin::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 4px;
}
.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: #999;
}
.scrollbar-thin {
  scrollbar-width: thin;
  scrollbar-color: #ccc #f1f1f1;
}
</style>