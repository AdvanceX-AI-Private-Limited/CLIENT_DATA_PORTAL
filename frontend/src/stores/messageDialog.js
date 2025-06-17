// stores/messageDialog.js
import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useMessageDialogStore = defineStore('messageDialog', () => {
  const visible = ref(false);
  const title = ref('');
  const message = ref('');
  const icon = ref('');

  function show({ message: msg, title: t = 'Message', icon: i = '' }) {
    title.value = t;
    message.value = msg;
    icon.value = i;
    visible.value = true;
  }
  function close() {
    visible.value = false;
  }

  return { visible, title, message, icon, show, close };
});