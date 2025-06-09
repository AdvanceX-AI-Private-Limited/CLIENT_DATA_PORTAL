import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { logout as apiLogout } from '@/composables/api/authApi';

const user = ref(null);
const loaded = ref(false);
const isSignedIn = ref(false);
// console.log("useAuth isSignedIn: ", isSignedIn.value);

// Helper to check if token is valid
function isTokenValid() {
    const token = localStorage.getItem('session_token');
    const expiresAt = localStorage.getItem('expires_at');
    if (!token || !expiresAt) return false;
    const now = new Date();
    const expiry = new Date(expiresAt);
    return now < expiry;
}

// Set token and expiry from API response
function setAuthFromApiResponse(response) {
    if (response.session_token && response.expires_at) {
        localStorage.setItem('session_token', response.session_token);
        localStorage.setItem('expires_at', response.expires_at);
        user.value = response.user || null;
        isSignedIn.value = true;
    }
}

// Clear token and expiry (logout)
function clearAuth() {
    localStorage.removeItem('session_token');
    localStorage.removeItem('expires_at');
    user.value = null;
    isSignedIn.value = false;
}

// Logout and redirect
async function logout() {
    const token = localStorage.getItem('session_token');
    console.log()
    if (token) {
        try {
            const response = await apiLogout();
            if (response?.status === 200) {
                console.log('Logged out successfully:', response.data?.message);
            } else {
                console.warn('Logout error (possibly already logged out):', response?.data?.detail || response?.statusText);
            }
        } catch (e) {
            console.warn('Logout API error (possibly already logged out):', e?.response?.data?.detail || e.message || e);
        }
    } else {
        console.log('No session token found, skipping logout API call.');
    }
    clearAuth();
    // Always redirect after logout
    window.location.href = '/login';
}

// On load, check if token is valid
if (isTokenValid()) {
    isSignedIn.value = true;
    // Optionally, you can load user info from localStorage if you store it
} else {
    isSignedIn.value = false;
    clearAuth();
}
loaded.value = true;

// Periodically check token validity
setInterval(() => {
    if (!isTokenValid() && isSignedIn.value) {
        clearAuth();
        // Use window.location to force redirect if router is not available
        window.location.href = '/login';
    }
}, 30000);

export function useAuth() {
    return {
        user,
        isSignedIn,
        loaded,
        setAuthFromApiResponse,
        clearAuth,
        logout
    }
}