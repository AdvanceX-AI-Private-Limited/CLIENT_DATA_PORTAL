<script setup>
import { ref } from 'vue';

const showChangePassword = ref(false);
const showChangeUsername = ref(false);
const showChangeBrand = ref(false);

function openChangePassword() {
  showChangePassword.value = true;
}
function openChangeUsername() {
  showChangeUsername.value = true;
}
function openChangeBrand() {
  showChangeBrand.value = true;
}
function closeAll() {
  showChangePassword.value = false;
  showChangeUsername.value = false;
  showChangeBrand.value = false;
}
</script>
<template>
  <div class="settings-container p-8 max-w-xl mx-auto">
    <h2 class="text-2xl font-bold mb-6">Settings</h2>
    <div class="space-y-4">
      <button class="w-full py-2 px-4 bg-blue-600 text-white rounded hover:bg-blue-700" @click="openChangePassword">Change Password</button>
      <button class="w-full py-2 px-4 bg-green-600 text-white rounded hover:bg-green-700" @click="openChangeUsername">Change Username</button>
      <button class="w-full py-2 px-4 bg-purple-600 text-white rounded hover:bg-purple-700" @click="openChangeBrand">Change Brand Details</button>
    </div>

    <!-- Change Password Dialog -->
    <div v-if="showChangePassword" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50">
      <div class="bg-white p-6 rounded shadow-lg w-full max-w-sm">
        <h3 class="text-lg font-semibold mb-4">Change Password</h3>
        <form @submit.prevent="closeAll">
          <input type="password" placeholder="Current Password" class="w-full mb-2 p-2 border rounded" required />
          <input type="password" placeholder="New Password" class="w-full mb-2 p-2 border rounded" required />
          <input type="password" placeholder="Confirm New Password" class="w-full mb-4 p-2 border rounded" required />
          <div class="flex justify-end space-x-2">
            <button type="button" class="px-4 py-2 bg-gray-300 rounded" @click="closeAll">Cancel</button>
            <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded">Save</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Change Username Dialog -->
    <div v-if="showChangeUsername" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50">
      <div class="bg-white p-6 rounded shadow-lg w-full max-w-sm">
        <h3 class="text-lg font-semibold mb-4">Change Username</h3>
        <form @submit.prevent="closeAll">
          <input type="text" placeholder="New Username" class="w-full mb-4 p-2 border rounded" required />
          <div class="flex justify-end space-x-2">
            <button type="button" class="px-4 py-2 bg-gray-300 rounded" @click="closeAll">Cancel</button>
            <button type="submit" class="px-4 py-2 bg-green-600 text-white rounded">Save</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Change Brand Details Dialog -->
    <div v-if="showChangeBrand" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50">
      <div class="bg-white p-6 rounded shadow-lg w-full max-w-sm">
        <h3 class="text-lg font-semibold mb-4">Change Brand Details</h3>
        <form @submit.prevent="closeAll">
          <input type="text" placeholder="Brand Name" class="w-full mb-2 p-2 border rounded" required />
          <input type="text" placeholder="Brand Description" class="w-full mb-4 p-2 border rounded" />
          <div class="flex justify-end space-x-2">
            <button type="button" class="px-4 py-2 bg-gray-300 rounded" @click="closeAll">Cancel</button>
            <button type="submit" class="px-4 py-2 bg-purple-600 text-white rounded">Save</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>