import './assets/main.css'
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia';
import { clerkPlugin } from '@clerk/vue'

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!PUBLISHABLE_KEY) {
  throw new Error('Add your Clerk Publishable Key to the .env file')
}

const pinia = createPinia();
const app = createApp(App)

app.use(clerkPlugin, { 
  publishableKey: PUBLISHABLE_KEY,
  appearance: {
    layout: {
      socialButtonsVariant: 'iconButton',
    },
  },
  routerPush: router.push.bind(router),
  signInUrl: import.meta.env.VITE_CLERK_SIGN_IN_URL,
  signUpUrl: import.meta.env.VITE_CLERK_SIGN_UP_URL,
  afterSignInUrl: import.meta.env.VITE_CLERK_AFTER_SIGN_IN_URL,
  afterSignUpUrl: import.meta.env.VITE_CLERK_AFTER_SIGN_UP_URL,
})
app.use(router)
app.use(pinia)

app.mount('#app')
