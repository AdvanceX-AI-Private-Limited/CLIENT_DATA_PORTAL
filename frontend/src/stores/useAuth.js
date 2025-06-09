<script>
import { ref } from 'vue';
const user = ref(null);
const loaded = ref(false);

export function useAuthStore() {
    const isSignedIn = ref(false);
    
    return {
        user,
        isSignedIn,
        loaded
    }
}
</script>