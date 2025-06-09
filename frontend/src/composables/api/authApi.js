import get, { post } from '@/composables/useApiClient'

export async function login(payload) {
  return await post('/auth/login', payload)
}

export async function logout() {
  // Send session token in Authorization header if present
  // const token = localStorage.getItem('session_token');
  // const headers = token ? { Authorization: `Bearer ${token}` } : {};
  // console.log("authApi headers: ", headers);
  return await post('/auth/logout');
}

export async function verifyOtp(payload) {
  return await post('/auth/verify-otp', payload)
}

export async function googleLogin() {
  return await get('/auth/google/login')
}

export async function googleCallback() {
  return await get('/auth/google/callback')
}
