// frontend/src/config.js
const isLocalhost = window.location.hostname === 'localhost';

const apiBaseUrl = isLocalhost
  ? 'http://localhost:8000/api/v1'
  : 'https://client.advancex.ai/api/v1';

export default {
    api: {
        baseUrl: apiBaseUrl,
    }
};