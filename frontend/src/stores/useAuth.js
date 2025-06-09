import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { logout as apiLogout } from '@/composables/api/authApi';

const user = ref(null);
const loaded = ref(false);
const isSignedIn = ref(false);
// console.log("useAuth isSignedIn: ", isSignedIn.value);

function setCookie(name, value, expiresAt) {
    let cookie = `${name}=${value}; path=/;`;
    if (expiresAt) {
        cookie += ` expires=${new Date(expiresAt).toUTCString()};`;
    }
    document.cookie = cookie;
}

function deleteCookie(name) {
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
}

// Helper to check if token is valid
function isTokenValid() {
    const token = sessionStorage.getItem('session_token');
    const expiresAt = sessionStorage.getItem('expires_at');
    if (!token || !expiresAt) return false;
    const now = new Date();
    const expiry = new Date(expiresAt);
    return now < expiry;
}

// Set token and expiry from API response
function setAuthFromApiResponse(response) {
    // Accept if session_token and expires_at are present, regardless of is_signed_in
    if (response.session_token && response.expires_at) {
        sessionStorage.setItem('session_token', response.session_token);
        sessionStorage.setItem('expires_at', response.expires_at);
        setCookie('session_token', response.session_token, response.expires_at);
        setCookie('expires_at', response.expires_at, response.expires_at);
        user.value = response.user || null;
        isSignedIn.value = true;
    } else {
        console.warn('setAuthFromApiResponse: Missing session_token or expires_at in response', response);
    }
}

// Clear token and expiry (logout)
function clearAuth() {
    sessionStorage.removeItem('session_token');
    sessionStorage.removeItem('expires_at');
    deleteCookie('session_token');
    deleteCookie('expires_at');
    user.value = null;
    isSignedIn.value = false;
}

// Logout and redirect
// async function logout() {
//     const token = sessionStorage.getItem('session_token');
//     const headers = token ? { Authorization: `Bearer ${token}` } : {};
//     console.log("authApi headers: ", headers);
//     return await apiLogout(headers);
// }

async function logout() {
    const token = sessionStorage.getItem('session_token');
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    console.log("authApi headers: ", headers);

    try {
        await apiLogout(headers);
    } catch (error) {
        console.warn("Logout API failed or returned error, proceeding with frontend logout", error);
    }

    clearAuth();
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