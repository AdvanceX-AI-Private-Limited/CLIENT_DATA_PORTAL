import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useSidebarStore = defineStore('sidebar', () => {
    const isLocked = ref(false);

    const toggleLock = () => {
        isLocked.value = !isLocked.value;
    };

    return { isLocked, toggleLock };
});
