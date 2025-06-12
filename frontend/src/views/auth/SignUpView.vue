<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue';
import { EyeIcon, EyeSlashIcon } from '@heroicons/vue/24/outline'
import { clientsRegister, verifygstin, brandsRegister } from '@/composables/api/authApi';
import Confetti from '@/components/Confetti.vue';

// Form state
const currentStep = ref(1);
const confirmationPhase = ref(1);
const otpInput = ref('');
const showConfetti = ref(false); 
const isVerifying = ref(false);
const gstVerified = ref(false);
const gstError = ref(false);
const showStatesDropdown = ref(false);
const stateSearchQuery = ref('');
const dropdownPosition = ref('bottom');
const statesDropdownContainer = ref(null);
const statesDropdown = ref(null);
const showFormUi = ref(true);// ...


const showPassword = ref(false);
const showConfirmPassword = ref(false);
const loading = ref(false);
const gstData = ref(null);

// Form data
const formData = reactive({
  brandName: '',
  legalEntityName: '',
  companyEmail: '',
  contactNumber: '',
  password: '',
  confirmPassword: '',

  clientId: '',
  gstNumber: '',
  dateOfregistration: '',

  termsAccepted: false,
  sendTerms: false,

  gstObj: null
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
    
    // Set GST data only if verification is successful
    gstData.value = result ? {
      reference_id: 1364072,
      GSTIN: "27ABBCA2714N1ZN",
      legal_name_of_business: "ADVANCEX AI PRIVATE LIMITED",
      center_jurisdiction: "RANGE-I",
      state_jurisdiction: "CHAKALA_701",
      date_of_registration: "2024-10-24",
      constitution_of_business: "Private Limited",
      taxpayer_type: "Regular",
      gst_in_status: "Active",
      last_update_date: "2024-11-11",
      nature_of_business_activities: ["Supplier of Services"],
      principal_place_address: "7TH FLOOR, INNOV8 SOLITAIRE CORPORATE PARK, S-11, UNIT NO.1171,1172, Mumbai, ANDHERI EAST, Maharashtra, 400093",
      principal_place_split_address: {
        building_name: "INNOV8 SOLITAIRE CORPORATE PARK",
        street: "ANDHERI EAST",
        location: "Mumbai",
        building_number: "S-11, UNIT NO.1171,1172",
        district: "Mumbai Suburban",
        state: "Maharashtra",
        city: "",
        flat_number: "7TH FLOOR",
        latitude: "19.117449",
        longitude: "72.8651080000001",
        pincode: "400093"
      },
      valid: true,
      message: "GSTIN Exists"
    } : null;
  }, 1500);
};

// const verifyGST = async () => {
//   console.log(formData);
//   gstError.value = null;

//   if (!formData.gstNumber) {
//     return;
//   }

//   const brandName = formData.brandName?.toString().trim() || '';
//   const gstNumber = formData.gstNumber?.toString().toUpperCase().trim() || '';

//   isVerifying.value = true;
//   console.log(`name: ${typeof brandName}, number: ${typeof gstNumber}`);
//   console.log(`Verifying GST for ${brandName} with number ${gstNumber}`);
//   try {
//     const payload = {
//       business_name: brandName,
//       GSTIN: gstNumber
//     }
//     console.log("payload: ", payload);
//     const response = await verifygstin(payload);
//     // handle the response as needed
//     console.log('GST verification result:', JSON.stringify(response.data));
//     gstData.value = response.data.data;
//     if (response.data.data.message != "GSTIN Doesn't Exist") {
//       gstVerified.value = response.data.success;
//       gstError.value = !response.data.success;
//     }else{
//       gstVerified.value = false;
//       gstError.value = true;
//     }

//   } catch (error) {
//     gstError.value = error.response?.data?.message || error.message || "GST verification failed";
//     console.error("Error verifying GST:", error);
//   } finally {
//     isVerifying.value = false;
//   }
// };

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

const logThings = () => {
  console.log("hre", formData.gstNumber);
  console.log("gstError", gstError.value);
}

watch(
  [currentStep, confirmationPhase],
  ([step, phase]) => {
    if (step === 3 && phase === 2) {
      console.log('Trigger: currentStep is 3 and confirmationPhase is 2')

    }
  }
);

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

// Button actions
function handleBack() {
  if (currentStep.value > 1) currentStep.value--
}

async function handleNext() {
  if (currentStep.value === 1) {
    gstVerification();
    if (currentStep.value < 5) currentStep.value++;
  } else if (currentStep.value === 2) {
    loading.value = true;
    const result = await brandDetails();  // Wait for API to finish
    loading.value = false;
    // Only move to next step if creation was successful (no error):
    if (result === true) {
      if (currentStep.value < 5) currentStep.value++;
    }
    // Otherwise: show error, DO NOT move forward
  } else if (currentStep.value === 3) {
    otpVerification();
    if (currentStep.value < 5) currentStep.value++;
  }
}

function handleSubmit() {
  showFormUi.value = false;
  currentStep.value = 5;
  showConfetti.value = true;
  setTimeout(() => showConfetti.value = false, 3000);
  
  console.log("pritty form data: ", JSON.stringify(formData));
}

const passwordMatchStatus = computed(() => {
  if (!formData.confirmPassword) return ""; // Blank, user hasn't typed confirm password yet
  if (formData.password === formData.confirmPassword) return "match";
  return "no-match";
});

const passwordLengthStatus = computed(() => {
  if (!formData.password) return '';
  return formData.password.length >= 8 ? 'valid' : 'invalid';
});

const clientApiData = ref(null);
const brandApiData = ref(null);

const clientBrandLoading = ref(false);
const clientBrandError = ref(false);
const clientBrandErrorMessage = ref('');

async function createClient() {
  clientBrandLoading.value = true;
  clientBrandError.value = false;

  const payload = {
    username: formData.companyEmail?.split('@')[0] || '',
    password: formData.password,
    email: formData.companyEmail,
    is_active: false,
    google_linked: false,
  };

  try {
    console.log("Payload being sent:", payload);
    const response = await clientsRegister(payload);
    clientApiData.value = response.data;
    
    if (response.status === 200) {
      formData.clientId = clientApiData.value.client_id;
      clientBrandLoading.value = false;
      return true; 
    }else if(response.status === 400){
      clientBrandLoading.value = false;
      clientBrandError.value = true;
      clientBrandErrorMessage.value = "Client already exists";
      return false;
    }else {
      clientBrandError.value = true;
      clientBrandErrorMessage.value = "Failed to create client";
      return false;
    }
  } catch (error) {
    console.error("Error registering client:", error);
    clientBrandError.value = true;
    if(response.status === 400){
      clientBrandLoading.value = false;
      clientBrandError.value = true;
      clientBrandErrorMessage.value = "Client already exists";
      return false;
    }
    clientBrandErrorMessage.value = error.response?.data?.message || error.message || "Failed to create client";
    return false;
  } finally {
    clientBrandLoading.value = false;
  }
}

// {
//   "brandname": "CoolBrand_2025",
//   "client_id": 1,
//   "gstin": "22ABCDE1234F1Z5",
//   "legal_name_of_business": "CoolBrand Private Limited",
//   "date_of_registration": "2022-07-15",
//   "gstdoc": {
//     "address": "123 Market Street, Bangalore, KA",
//     "gstin": "22ABCDE1234F1Z5",
//     "legalName": "CoolBrand Private Limited",
//     "registrationDate": "2022-07-15",
//     "stateCode": "22",
//     "status": "Active",
//     "tradeName": "CoolBrand"
//   }
// }

async function createBrand() {
  clientBrandLoading.value = true;
  clientBrandError.value = false;
  clientBrandErrorMessage.value = '';

  try {
    const payload = {
      brandname: formData.brandName,
      client_id: formData.clientId,
      gstin: formData.gstNumber,
      legal_name_of_business: formData.legalEntityName,
      date_of_registration: formData.dateOfregistration,
      gstdoc: gstData.value
    };

    console.log("Brand payload being sent:", payload);
    const response = await brandsRegister(payload);
    brandApiData.value = response.data;
    console.log("Brand API Data:", brandApiData.value);

    if (response.status === 200 || response.status === 201) {
      brandApiData.value = response.data;
      clientBrandLoading.value = false;
      return true;
    } else {
      clientBrandError.value = true;
      clientBrandErrorMessage.value = response.detail || "Failed to create brand";
      return false;
    }
  } catch (error) {
    console.error("Error registering brand:", error);
    clientBrandError.value = true;
    clientBrandErrorMessage.value = error.response?.data?.message || error.message || "Failed to create brand";
    return false;
  } finally {
    clientBrandLoading.value = false;
  }
}

function gstVerification() {
  formData.legalEntityName = gstData.value.legal_name_of_business;
  formData.gstNumber = gstData.value.GSTIN;
  formData.dateOfregistration = gstData.value.date_of_registration;
  formData.gstObj = gstData.value;
  console.log('Step 1 Next!', formData);
}

async function brandDetails() {
  loading.value = true;
  try {
    // First API request: Create client
    let createClientVar = await createClient();
    console.log("client created data: ", clientApiData.value);
    
    if (createClientVar) {
      formData.clientId = clientApiData.value.client_id;
      console.log('Client created successfully:', formData);
      
      let createBrandVar = await createBrand();
      
      if (createBrandVar) {
        console.log('Brand created successfully');
        return true; 
      } else {
        console.error('Failed to create brand');
        return false;
      }
    } else {
      console.error('Failed to create client');
      return false;
    }
  } catch (error) {
    console.error('Error in brandDetails:', error);
    clientBrandError.value = true;
    clientBrandErrorMessage.value = "Failed to complete registration";
    return false;
  } finally {
    loading.value = false;
  }
}

function otpVerification() {
  console.log('Step 3 Next!', formData);
}

const allowNextBtn = computed(() => {
  if (currentStep.value === 1 && !gstVerified.value) return true;
  if (currentStep.value === 2) {
    if (loading.value) return true;
    
    if (
      formData.password === formData.confirmPassword &&
      formData.password.length >= 8 &&
      formData.companyEmail !== '' &&
      formData.contactNumber !== '' &&
      !clientBrandError.value
    ) {
      return false;
    } else {
      return true;
    }
  }
  if (currentStep.value === 3) {
    if (otpInput.value.length === 6) {
      return false;
    } else {
      return true;
    }
  }
  return false;
});


</script>

<template>
  <Confetti :showConfetti="showConfetti" />

  <div class="min-h-screen bg-gradient-to-br from-white via-blue-100 to-purple-200 py-5 px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between items-center mb-6">
      <a href="/">
        <div class="flex items-center">
          <img class="w-40 md:w-39" src="/logo-advancex.png" alt="">
        </div>
      </a>
      <div>
        <span class="text-md">Already a member? </span>
        <a href="#" class="text-blue-600 font-semibold text-md hover:underline">Sign In</a>
      </div>
    </div>
    <div class="max-w-4xl mx-auto">
      
      <!-- Progress Steps -->
      <div v-if="showFormUi" class="flex items-center justify-center mb-5 max-w-6xl mx-auto">
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
            ]">GST Verification</p>
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
            ]">Restaurant Details</p>
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
            ]">OTP Verification</p>
          </div>
        </div>

        <!-- Connector -->
        <div class="h-0.5 w-10 md:w-16 mx-1 md:mx-2 bg-gray-200" :class="currentStep >= 3 ? 'bg-blue-600' : 'bg-gray-200'"></div>

        <!-- Step 4 -->
        <div class="flex items-center">
          <div
            :class="[
              'rounded-full h-8 w-8 flex items-center justify-center text-sm font-medium transition-all duration-200 border-2',
              currentStep >= 4 ? 'bg-white text-blue-600 border-blue-500 shadow-md' : 'bg-gray-100 text-gray-600 border-gray-300'
            ]"
          >
            4
          </div>
          <div class="ml-1">
            <p :class="[
              'text-xs md:text-sm font-medium',
              currentStep >= 4 ? 'text-blue-600' : 'text-gray-500'
            ]">Terms and Conditions</p>
          </div>
        </div>
      </div>

      <!-- Form Card -->
      <!-- Loading State -->
      <div v-if="showFormUi" class="bg-white/80 shadow-xl rounded-lg overflow-hidden backdrop-blur-md border border-white/30 ring-1 ring-blue-100/50 px-4">
        <div v-if="loading" class="absolute inset-0 bg-white/70 flex items-center justify-center z-20">
          <svg class="animate-spin mr-3 h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span class="text-blue-700 text-lg font-semibold">Loading...</span>
        </div>

        <!-- Step 1: GST Verification -->
        <div v-if="currentStep === 1" class="px-6 py-8">
          <div class="space-y-6">
            <div>
              <div class="mb-6">
                <label for="brandName" class="block text-sm font-medium text-gray-700 mb-1">Brand Name<span class="text-red-500">*</span></label>
                <input 
                  type="text"
                  id="brandName" 
                  v-model="formData.brandName" 
                  class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  placeholder="Enter restaurant name"
                  required
                />
              </div>
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
          </div>
        </div>

        <!-- Step 2: Restaurant Details -->
        <div v-if="currentStep === 2" class="px-6 py-8">          
          <div class="space-y-6">
            <!-- Error message -->
            <div v-if="clientBrandError" class="bg-red-50 border border-red-300 text-red-700 px-4 py-2 mb-4 rounded">
              {{ clientBrandErrorMessage }}
            </div>
            <div>
              <label for="companyEmail" class="block text-sm font-medium text-gray-700 mb-1">Email Address<span class="text-red-500">*</span></label>
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
              <label for="contactNumber" class="block text-sm font-medium text-gray-700 mb-1">Contact Number<span class="text-red-500">*</span></label>
              <input 
                type="tel" 
                id="contactNumber" 
                v-model="formData.contactNumber" 
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                placeholder="Enter company contact number"
                required
              />
            </div>

            <!-- Password -->
            <div>
              <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
                Password<span class="text-red-500">*</span>
              </label>
              <div class="relative">
                <input 
                  :type="showPassword ? 'text' : 'password'" 
                  id="password" 
                  v-model="formData.password"
                  :class="[
                    'mt-1 block w-full border rounded-md shadow-sm py-2.5 px-4 pr-12 focus:outline-none transition-all duration-200',
                    passwordLengthStatus === 'valid' ? 'border-green-400 focus:border-green-600 ring-3 ring-green-200' : '',
                    passwordLengthStatus === 'invalid' ? 'border-red-400 focus:border-red-600 ring-3 ring-red-200' : '',
                    passwordLengthStatus === '' ? 'border-gray-300 focus:border-blue-500 ring-2 ring-blue-100' : ''
                  ]"
                  placeholder="Enter password"
                  minlength="8"
                  required
                />
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 focus:outline-none"
                  tabindex="-1"
                  aria-label="Toggle password visibility"
                >
                  <component :is="showPassword ? EyeSlashIcon : EyeIcon" class="h-5 w-5"/>
                </button>
              </div>
              <div v-if="formData.password && passwordLengthStatus === 'invalid'" class="text-red-500 text-xs mt-1">
                Password must be at least 8 characters.
              </div>
            </div>

            <!-- Confirm Password Field -->
            <div class="mt-4">
              <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-1">
                Confirm Password<span class="text-red-500">*</span>
              </label>
              <div class="relative">
                <input 
                  :type="showConfirmPassword ? 'text' : 'password'" 
                  id="confirmPassword" 
                  v-model="formData.confirmPassword" 
                  :class="[
                    'mt-1 block w-full border rounded-md shadow-sm py-2.5 px-4 pr-12 focus:outline-none transition-all duration-200',
                    passwordMatchStatus === 'match' ? 'border-green-400 focus:border-green-600 ring-3 ring-green-200' : '',
                    passwordMatchStatus === 'no-match' ? 'border-red-400 focus:border-red-600 ring-3 ring-red-200' : '',
                    passwordMatchStatus === '' ? 'border-gray-300 focus:border-blue-500 ring-2 ring-blue-100' : ''
                  ]"
                  placeholder="Enter Confirm Password"
                  minlength="8"
                  required
                />
                <button
                  type="button"
                  @click="showConfirmPassword = !showConfirmPassword"
                  class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 focus:outline-none"
                  tabindex="-1"
                  aria-label="Toggle confirm password visibility"
                >
                  <component :is="showConfirmPassword ? EyeSlashIcon : EyeIcon" class="h-5 w-5"/>
                </button>
              </div>
              <div v-if="passwordMatchStatus === 'no-match'" class="text-red-500 text-xs mt-1">
                Passwords do not match.
              </div>
              <div v-else-if="passwordMatchStatus === 'match'" class="text-green-500 text-xs mt-1">
                Passwords match!
              </div>
            </div>
          </div>
        </div>
        
        <!-- <button class="bg-blue-500 px-4 text-white rounded-lg py-2 m-3" @click="logThings" >yo</button> -->

        <!-- Step 3: OTP Verification -->
        <div v-if="currentStep === 3" class="px-6 py-8 space-y-6">
          <div class="text-center">
            <h3 class="text-lg font-medium text-gray-900">Verify Your Email</h3>
            <p class="mt-2 text-sm text-gray-500">
              We've sent a verification code to your email address. Please enter the code below to complete your registration.
            </p>
          </div>
          <div class="mt-4 mx-">
            <!-- <label for="otp" class="block text-sm font-medium text-gray-700 mb-3 mx-0.5">Verification Code</label> -->
            <input 
              type="text" 
              id="otp" 
              v-model="otpInput" 
              class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
              placeholder="Enter 6-digit code"
              maxlength="6"
            />
          </div>
        </div>

        <!-- Step 4: Terms and Conditions -->
        <div v-if="currentStep === 4" class="px-6 py-8 space-y-6">
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

        <!-- Form Navigation Buttons -->
        <div class="px-6 pb-6 mx-auto flex justify-between">
          <button 
            v-if="currentStep > 1"
            @click="handleBack"
            type="button"
            class="inline-flex items-center px-10 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
          >
            Back
          </button>
          <div v-else></div>

          <!-- Next: show if not last step -->
          <button
            v-if="currentStep < 4"
            @click="handleNext"
            type="button"
            class="inline-flex items-center px-10 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
            :disabled="allowNextBtn"
          >
            Next
          </button>

          <!-- Submit: only on last step -->
          <button
            v-else
            @click="handleSubmit"
            type="button"
            class="inline-flex items-center px-10 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
            :disabled="!formData.termsAccepted"
          >
            Submit
          </button>
        </div>
      </div>

      <div v-if="currentStep === 5" class="text-center">
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
  </div>
</template>

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
