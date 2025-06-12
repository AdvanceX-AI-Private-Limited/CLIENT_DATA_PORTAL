// src/composables/api/authApi.js
import get, { post } from '@/composables/useApiClient'

export async function login(payload) {
  return await post('/auth/login', payload)
}

export async function logout() {
  return await post('/auth/logout')
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

export async function protectedProfile() {
  return await post('/auth/protected/profile')
}

export async function verifygstin(payload) {
  return await post('/auth/verify-gstin', payload)
}

export async function clientsRegister(payload) {
  return await post('/auth/clients/register', payload)
}

export async function brandsRegister(payload) {
  return await post('/auth/brands/register', payload)
}
