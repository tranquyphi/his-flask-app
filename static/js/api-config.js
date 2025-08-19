/**
 * API Configuration
 * This file provides a consistent API interface regardless of Flask/FastAPI backend
 */

const API_CONFIG = {
    // Base URL for all API calls - both Flask and FastAPI use port 8000
    BASE_URL: 'http://127.0.0.1:8000',
    API_PREFIX: '/api'
};

/**
 * Get the full API URL for an endpoint
 * @param {string} endpoint - The API endpoint path (with or without /api/ prefix)
 * @returns {string} - The full URL
 */
function getApiUrl(endpoint) {
    // Normalize endpoint to start with /api/
    if (!endpoint.startsWith('/api/')) {
        endpoint = '/api/' + endpoint.replace(/^\//, '');
    }
    
    return `${API_CONFIG.BASE_URL}${endpoint}`;
}

/**
 * Enhanced jQuery AJAX wrapper with consistent error handling
 */
function makeApiCall(options) {
    // If URL is provided, ensure it's a full URL
    if (options.url) {
        options.url = getApiUrl(options.url);
    }
    
    // Add default error handling if not provided
    const originalError = options.error;
    options.error = function(xhr, status, error) {
        console.error('API Error:', {
            url: options.url,
            status: xhr.status,
            statusText: xhr.statusText,
            responseText: xhr.responseText
        });
        
        if (originalError) {
            originalError.call(this, xhr, status, error);
        }
    };
    
    return $.ajax(options);
}

// Export for use in other files
if (typeof window !== 'undefined') {
    window.API_CONFIG = API_CONFIG;
    window.getApiUrl = getApiUrl;
    window.makeApiCall = makeApiCall;
}

// Log current configuration
console.log('API Configuration loaded:', {
    'Base URL': API_CONFIG.BASE_URL,
    'API Prefix': API_CONFIG.API_PREFIX
});
