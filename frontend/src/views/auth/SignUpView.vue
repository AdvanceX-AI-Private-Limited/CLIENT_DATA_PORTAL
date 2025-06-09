<template>
  <div class="min-h-screen bg-gradient-to-br from-white via-blue-100 to-purple-200 py-5 px-4 sm:px-6 lg:px-8">
    <!-- Confetti container - positioned absolutely to cover the entire screen -->
    <div v-if="showConfetti" class="confetti-container">
      <div v-for="n in 50" :key="n" class="confetti" :style="{
        '--fall-delay': `${Math.random() * 3}s`,
        '--fall-duration': `${Math.random() * 3 + 2}s`,
        '--left-pos': `${Math.random() * 100}vw`,
        '--bg-color': `hsl(${Math.random() * 360}, 100%, 50%)`,
        '--size': `${Math.random() * 0.5 + 0.2}rem`
      }"></div>
    </div>
    <div class="flex justify-between items-center mb-6">
      <div class="flex items-center">
        <img class="w-40 md:w-39" src="/logo-advancex.png" alt="">
      </div>
      <div>
        <span class="text-md">Already a member? </span>
        <a href="#" class="text-blue-600 font-semibold text-md hover:underline">Sign In</a>
      </div>
    </div>
    <div class="max-w-3xl mx-auto">
      <!-- Progress Steps -->
      <div class="flex items-center justify-center mb-5 max-w-6xl mx-auto">
        <!-- Step 1 -->
        <div class="flex items-center">
          <div
            :class="[
              'rounded-full h-8 w-8 flex items-center justify-center text-sm font-medium transition-all duration-200 border-2',
              currentStep >= 1 ? 'bg-white text-blue-600 border-blue-500 shadow-md' : 'bg-gray-100 text-gray-600 border-gray-300'
            ]"
          >
            1
          </div>
          <div class="ml-1 mr-1">
            <p :class="[
              'text-xs md:text-sm font-medium',
              currentStep >= 1 ? 'text-blue-600' : 'text-gray-500'
            ]">Restaurant Details</p>
          </div>
        </div>

        <!-- Connector -->
        <div class="h-0.5 w-10 md:w-16 mx-1 md:mx-2 bg-gray-200" :class="currentStep >= 2 ? 'bg-blue-600' : 'bg-gray-200'"></div>

        <!-- Step 2 -->
        <div class="flex items-center">
          <div
            :class="[
              'rounded-full h-8 w-8 flex items-center justify-center text-sm font-medium transition-all duration-200 border-2',
              currentStep >= 2 ? 'bg-white text-blue-600 border-blue-500 shadow-md' : 'bg-gray-100 text-gray-600 border-gray-300'
            ]"
          >
            2
          </div>
          <div class="ml-1 mr-1">
            <p :class="[
              'text-xs md:text-sm font-medium',
              currentStep >= 2 ? 'text-blue-600' : 'text-gray-500'
            ]">GST Verification</p>
          </div>
        </div>

        <!-- Connector -->
        <div class="h-0.5 w-10 md:w-16 mx-1 md:mx-2 bg-gray-200" :class="currentStep >= 3 ? 'bg-blue-600' : 'bg-gray-200'"></div>

        <!-- Step 3 -->
        <div class="flex items-center">
          <div
            :class="[
              'rounded-full h-8 w-8 flex items-center justify-center text-sm font-medium transition-all duration-200 border-2',
              currentStep >= 3 ? 'bg-white text-blue-600 border-blue-500 shadow-md' : 'bg-gray-100 text-gray-600 border-gray-300'
            ]"
          >
            3
          </div>
          <div class="ml-1">
            <p :class="[
              'text-xs md:text-sm font-medium',
              currentStep >= 3 ? 'text-blue-600' : 'text-gray-500'
            ]">Confirmation</p>
          </div>
        </div>
      </div>

      <!-- Form Card -->
      <div class="bg-white/80 shadow-xl rounded-lg overflow-hidden backdrop-blur-md border border-white/30 ring-1 ring-blue-100/50 px-4">
        <!-- Step 1: Restaurant Details -->
        <div v-if="currentStep === 1" class="px-6 py-8">          
          <div class="space-y-6">
            <div>
              <label for="restaurantName" class="block text-sm font-medium text-gray-700 mb-1">Restaurant Name<span class="text-red-500">*</span></label>
              <input 
                type="text" 
                id="restaurantName" 
                v-model="formData.restaurantName" 
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                placeholder="Enter restaurant name"
                required
              />
            </div>

            <div>
              <label for="legalEntityName" class="block text-sm font-medium text-gray-700 mb-1">Legal Entity Name<span class="text-red-500">*</span></label>
              <input 
                type="text" 
                id="legalEntityName" 
                v-model="formData.legalEntityName" 
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                placeholder="Can be same as Restaurant Name"
                required
              />
            </div>

            <div>
              <label for="companyEmail" class="block text-sm font-medium text-gray-700 mb-1">Company Email Address<span class="text-red-500">*</span></label>
              <input 
                type="email" 
                id="companyEmail" 
                v-model="formData.companyEmail" 
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                placeholder="Enter company email address"
                required
              />
            </div>

            <div>
              <label for="createPassword" class="block text-sm font-medium text-gray-700 mb-1">Create Password<span class="text-red-500">*</span></label>
              <input 
                type="text" 
                id="createPassword" 
                v-model="formData.password" 
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                placeholder="Create Password"
                required
              />
            </div>

            <div>
              <label for="contactNumber" class="block text-sm font-medium text-gray-700 mb-1">Company Contact Number<span class="text-red-500">*</span></label>
              <input 
                type="tel" 
                id="contactNumber" 
                v-model="formData.contactNumber" 
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                placeholder="Enter company contact number"
                required
              />
            </div>

            <div>
              <label for="alternateContactNumber" class="block text-sm font-medium text-gray-700 mb-1">Alternate Contact Number <span class="text-gray-400 text-xs">(Optional)</span></label>
              <input 
                type="tel" 
                id="alternateContactNumber" 
                v-model="formData.alternateContactNumber" 
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                placeholder="Enter alternate contact number (optional)"
              />
            </div>
          </div>
        </div>

        <!-- Step 2: GST Verification -->
        <div v-if="currentStep === 2" class="px-6 py-8">
          <div class="space-y-6">
            <div>
              <label for="gstNumber" class="block text-sm font-medium text-gray-700 mb-1">State Level Company GST<span class="text-red-500">*</span></label>
              <div class="mt-1 flex rounded-md shadow-sm">
                <input 
                  type="text" 
                  id="gstNumber" 
                  v-model="formData.gstNumber" 
                  class="flex-1 block w-full border border-gray-300 rounded-l-md shadow-sm py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  placeholder="Enter GST number"
                  :disabled="gstVerified"
                  required
                />
                <button 
                  @click="verifyGST" 
                  class="flex-shrink-0 inline-flex items-center px-4 py-2.5 border border-transparent text-sm font-medium rounded-r-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
                  :disabled="!formData.gstNumber || gstVerified"
                >
                  <span v-if="isVerifying">
                    <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  </span>
                  Verify
                </button>
              </div>
            </div>

            <div v-if="gstVerified" class="bg-green-50 border border-green-200 rounded-md p-4">
              <div class="flex">
                <div class="flex-shrink-0">
                  <svg class="h-5 w-5 text-green-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div class="ml-3">
                  <h3 class="text-sm font-medium text-green-800">GST verified successfully</h3>
                  <div class="mt-2 text-sm text-green-700">
                    <p>Your GST number has been verified. You can now proceed to the next step.</p>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="gstError" class="bg-red-50 border border-red-200 rounded-md p-4">
              <div class="flex">
                <div class="flex-shrink-0">
                  <svg class="h-5 w-5 text-red-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div class="ml-3">
                  <h3 class="text-sm font-medium text-red-800">GST verification failed</h3>
                  <div class="mt-2 text-sm text-red-700">
                    <p>Please check your GST number and try again.</p>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="gstVerified">
              <div class="flex items-center">
                <input 
                  type="checkbox" 
                  id="termsAccepted" 
                  v-model="formData.termsAccepted" 
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  required
                />
                <label for="termsAccepted" class="ml-2 text-sm text-gray-700">
                  I consent to use my company information and accept the 
                  <a href="#" class="text-blue-600 hover:text-blue-500">Terms of Service</a> and 
                  <a href="#" class="text-blue-600 hover:text-blue-500">Privacy Policy</a>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 3: Confirmation -->
        <div v-if="currentStep === 3" class="px-6 py-8">
          <!-- Phase 1: Terms Agreement -->
          <div v-if="confirmationPhase === 1" class="space-y-6">
            <h3 class="text-lg font-medium text-gray-900">Terms and Conditions</h3>
            <div class="bg-gray-50 p-4 rounded-md border border-gray-200 h-48 overflow-y-auto">
              <p class="text-sm text-gray-700">
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam euismod, nisi vel consectetur
                euismod, nisl nisi consectetur nisl, euismod nisl nisi euismod nisl. Nullam euismod, nisi vel
                consectetur euismod, nisl nisi consectetur nisl, euismod nisl nisi euismod nisl.
                lorem1000
                <!-- Terms content would go here -->
              </p>
            </div>
            <div class="flex items-center">
              <input 
                type="checkbox" 
                id="sendTerms" 
                v-model="formData.sendTerms" 
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label for="sendTerms" class="ml-2 text-sm text-gray-700">
                Send copy to email
              </label>
            </div>
          </div>

          <!-- Phase 2: OTP Verification -->
          <div v-if="confirmationPhase === 2" class="space-y-6">
            <div class="text-center">
              <h3 class="text-lg font-medium text-gray-900">Verify Your Email</h3>
              <p class="mt-2 text-sm text-gray-500">
                We've sent a verification code to your email address. Please enter the code below to complete your registration.
              </p>
            </div>
            <div class="mt-4">
              <label for="otp" class="block text-sm font-medium text-gray-700 mb-1">Verification Code</label>
              <input 
                type="text" 
                id="otp" 
                v-model="otpInput" 
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                placeholder="Enter 4-digit code"
                maxlength="4"
              />
            </div>
          </div>

          <!-- Phase 3: Success Message -->
          <div v-if="confirmationPhase === 3" class="text-center">
            <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100">
              <svg class="h-10 w-10 text-green-600 animate-checkmark" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h3 class="mt-3 text-lg font-medium text-gray-900">Registration Successful!</h3>
            <p class="mt-2 text-sm text-gray-500">
              Thank you for registering your restaurant. Your details have been submitted successfully. Our team will contact you very soon.
            </p>
          </div>
        </div>

        <!-- Form Navigation Buttons -->
        <div v-if="currentStep !== 3 || (currentStep === 3 && confirmationPhase < 3)" class="px-6 pb-6 mx-auto flex justify-between">
          <button 
            v-if="currentStep > 1 && !(currentStep === 3 && confirmationPhase > 1)" 
            @click="currentStep--" 
            type="button" 
            class="inline-flex items-center px-10 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
          >
            Back
          </button>
          <div v-else></div>
          
          <!-- Step 1 Next button -->
          <button 
            v-if="currentStep === 1"
            @click="goToStep2"
            type="button" 
            class="inline-flex items-center px-10 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
          >
            Next
          </button>
          
          <!-- Step 2 Submit button -->
          <button 
            v-else-if="currentStep === 2"
            @click="submitForm"
            type="button" 
            class="inline-flex items-center px-10 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
            :disabled="!canSubmit"
          >
            Submit
          </button>
          
          <!-- Confirmation Phase 1 button -->
          <button 
            v-else-if="currentStep === 3 && confirmationPhase === 1"
            @click="proceedToPhase2" 
            type="button" 
            class="inline-flex items-center px-10 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
          >
            I Agree
          </button>
          
          <!-- Confirmation Phase 2 button -->
          <button 
            v-else-if="currentStep === 3 && confirmationPhase === 2"
            @click="verifyOTP" 
            type="button" 
            class="inline-flex items-center px-10 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
          >
            Submit
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue';

// Form state
const currentStep = ref(1);
const confirmationPhase = ref(1); // Track the current phase within Step 3
const otpInput = ref(''); // For OTP verification in phase 2
const showConfetti = ref(false); // Control confetti visibility
const isVerifying = ref(false);
const gstVerified = ref(false);
const gstError = ref(false);
const showStatesDropdown = ref(false);
const stateSearchQuery = ref('');
const dropdownPosition = ref('bottom');
const dropdownWidth = ref(0);
const statesDropdownContainer = ref(null);
const statesDropdown = ref(null);
const searchInput = ref(null);

// Form data
const formData = reactive({
  restaurantName: '',
  legalEntityName: '',
  companyEmail: '',
  contactNumber: '',
  password: '',
  alternateContactNumber: '',
  businessType: '',
  operatingStores: null,
  platforms: {
    swiggy: false,
    zomato: false,
    other: {
      selected: false,
      value: ''
    }
  },
  operatingStates: [],
  gstNumber: '',
  termsAccepted: false,
  sendTerms: false
});

// List of Indian states
const indianStates = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 
  'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 
  'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 
  'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
  'Andaman and Nicobar Islands', 'Chandigarh', 'Dadra and Nagar Haveli and Daman and Diu', 
  'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Lakshadweep', 'Puducherry'
];

// Filtered states based on search query
const filteredStates = computed(() => {
  if (!stateSearchQuery.value) return indianStates;
  return indianStates.filter(state => 
    state.toLowerCase().includes(stateSearchQuery.value.toLowerCase())
  );
});

// Toggle states dropdown
const toggleStatesDropdown = async () => {
  showStatesDropdown.value = !showStatesDropdown.value;
  
  if (showStatesDropdown.value) {
    await nextTick();
    positionDropdown();
    // Focus the search input
    if (searchInput.value) {
      searchInput.value.focus();
    }
  }
};

// Position the dropdown
const positionDropdown = () => {
  if (!statesDropdownContainer.value) return;
  
  // Check if there's enough space below
  const containerRect = statesDropdownContainer.value.getBoundingClientRect();
  const spaceBelow = window.innerHeight - containerRect.bottom;
  const requiredSpace = 240; // Max dropdown height
  
  if (spaceBelow < requiredSpace && containerRect.top > requiredSpace) {
    // Position above if not enough space below but enough space above
    dropdownPosition.value = 'top';
  } else {
    // Position below
    dropdownPosition.value = 'bottom';
  }
};

// Toggle state selection
const toggleState = (state) => {
  const index = formData.operatingStates.indexOf(state);
  if (index === -1) {
    formData.operatingStates.push(state);
  } else {
    formData.operatingStates.splice(index, 1);
  }
};

// Close dropdown when clicking outside
const closeDropdown = (event) => {
  if (!showStatesDropdown.value) return;
  
  // Check if click is outside dropdown
  if (statesDropdownContainer.value && 
      !statesDropdownContainer.value.contains(event.target) &&
      statesDropdown.value && 
      !statesDropdown.value.contains(event.target)) {
    showStatesDropdown.value = false;
  }
};

// Event listeners for dropdown
onMounted(() => {
  document.addEventListener('mousedown', closeDropdown);
  window.addEventListener('resize', () => {
    if (showStatesDropdown.value) {
      positionDropdown();
    }
  });
  window.addEventListener('scroll', () => {
    if (showStatesDropdown.value) {
      positionDropdown();
    }
  });
});

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', closeDropdown);
  window.removeEventListener('resize', positionDropdown);
  window.removeEventListener('scroll', positionDropdown);
});

// Check if Step 1 is valid
const isStep1Valid = computed(() => {
  return formData.restaurantName && 
         formData.legalEntityName && 
         formData.companyEmail && 
         formData.contactNumber && 
         formData.businessType && 
         formData.operatingStores && 
         (formData.platforms.swiggy || formData.platforms.zomato || 
          (formData.platforms.other.selected && formData.platforms.other.value)) && 
         formData.operatingStates.length > 0;
});

// Check if form can be submitted
const canSubmit = computed(() => {
  return gstVerified.value && formData.termsAccepted && formData.sendTerms;
});

// Go to Step 2
const goToStep2 = () => {
  if (isStep1Valid.value) {
    currentStep.value = 2;
  } else {
    alert("Please fill all required fields before proceeding.");
  }
};

// Mock GST verification function
const verifyGST = () => {
  if (!formData.gstNumber) {
    return;
  }
  
  isVerifying.value = true;
  gstError.value = false;
  
  // Simulate API call with timeout
  setTimeout(() => {
    // Simple mock - GST numbers starting with '27' will return true, others false
    // You can replace this with your actual API call later
    const result = formData.gstNumber.startsWith('27');
    gstVerified.value = result;
    gstError.value = !result;
    isVerifying.value = false;
  }, 1500);
};

// Submit form
const submitForm = () => {
  if (canSubmit.value) {
    // Here you would typically send the form data to your backend
    console.log('Form submitted:', formData);
    
    // Go to confirmation step
    currentStep.value = 3;
    // Start at phase 1 of confirmation
    confirmationPhase.value = 1;
  }
};

// Move to phase 2 after agreeing to terms
const proceedToPhase2 = () => {
  // Here you would send terms and conditions email
  console.log('Sending terms and conditions email');
  confirmationPhase.value = 2;
};

// Verify OTP and move to final phase
const verifyOTP = () => {
  // Here you would verify the OTP with backend
  // For demo purposes, any 4-digit OTP works
  if (otpInput.value.length === 4) {
    console.log('OTP verified');
    confirmationPhase.value = 3;
    
    // Show confetti when reaching the final phase
    showConfetti.value = true;
    
    // Hide confetti after 5 seconds
    setTimeout(() => {
      showConfetti.value = false;
    }, 5000);
  } else {
    alert('Please enter a valid 4-digit OTP');
  }
};

// Watch for changes to confirmationPhase as an alternative trigger
watch(() => confirmationPhase.value, (newPhase) => {
  if (newPhase === 3 && !showConfetti.value) {
    // Show confetti when reaching the final phase
    showConfetti.value = true;
    
    // Hide confetti after 5 seconds
    setTimeout(() => {
      showConfetti.value = false;
    }, 5000);
  }
});
</script>

<style scoped>
/* Optional: Add transition for smoother dropdown */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

/* Add some extra styling for the dropdown */
.max-h-60 {
  max-height: 240px;
}

/* Add animation for the checkmark */
@keyframes checkmark {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.animate-checkmark {
  animation: checkmark 1.5s ease-in-out forwards; /* Increased from 0.5s to 1.5s for slower animation */
}

/* Confetti styles */
.confetti-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  pointer-events: none;
  z-index: 50;
}

.confetti {
  position: absolute;
  width: var(--size);
  height: var(--size);
  background: var(--bg-color);
  top: -20px;
  left: var(--left-pos);
  opacity: 0.8;
  animation: fall var(--fall-duration) var(--fall-delay) linear forwards, sway 3s ease-in-out infinite alternate;
}

.confetti:nth-child(odd) {
  border-radius: 0 40% 50% 50%;
  transform: rotate(45deg);
}

.confetti:nth-child(even) {
  border-radius: 50%;
  transform: rotate(90deg);
}

.confetti:nth-child(3n) {
  border-radius: 50% 0 50% 50%;
  transform: rotate(135deg);
}

.confetti:nth-child(5n) {
  width: var(--size);
  height: calc(var(--size) * 0.2);
  border-radius: 0;
}

@keyframes fall {
  0% {
    top: -20px;
    transform: translateX(-5px) rotate(0deg);
    opacity: 1;
  }
  80% {
    opacity: 1;
  }
  100% {
    top: 100vh;
    transform: translateX(5px) rotate(360deg);
    opacity: 0;
  }
}

@keyframes sway {
  0% {
    margin-left: -10px;
  }
  100% {
    margin-left: 10px;
  }
}
</style>