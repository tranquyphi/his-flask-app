/**
 * Patient Image Utilities
 * A reusable module for handling patient images throughout the HIS application.
 * Features:
 * - Loading patient images with proper error handling
 * - Displaying patient images in thumbnails, profiles, etc.
 * - Uploading patient images
 * - Managing default images and placeholders
 */

const PatientImageUtils = (function() {
    // Configuration
    const config = {
        apiEndpoint: '/api/patient/image',
        defaultImage: '/static/images/default-patient.png',
        uploadEndpoint: '/api/patient/image',
        imageStyles: {
            thumbnail: {
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                objectFit: 'cover'
            },
            profile: {
                width: '150px',
                height: '150px',
                borderRadius: '5px',
                objectFit: 'cover'
            },
            fullsize: {
                maxWidth: '100%',
                height: 'auto',
                borderRadius: '5px'
            }
        }
    };

    /**
     * Generate HTML for a patient image with proper error handling
     * @param {string} patientId - The patient's ID
     * @param {string} size - Size variant: 'thumbnail', 'profile', 'fullsize'
     * @param {Object} options - Additional options
     * @returns {string} HTML string for the patient image
     */
    function getPatientImageHtml(patientId, size = 'thumbnail', options = {}) {
        const styles = config.imageStyles[size] || config.imageStyles.thumbnail;
        const styleString = Object.entries(styles)
            .map(([key, value]) => `${key}: ${value}`)
            .join('; ');
        
        // Container class handling
        const containerClass = options.containerClass || '';
        const imageClass = options.imageClass || '';
        
        // Additional data attributes
        const dataAttrs = options.dataAttributes 
            ? Object.entries(options.dataAttributes)
                .map(([key, value]) => `data-${key}="${value}"`)
                .join(' ')
            : '';

        return `
            <div class="patient-image-container ${containerClass}" ${dataAttrs}>
                <img src="${config.defaultImage}" 
                     data-patient-id="${patientId}"
                     class="patient-image ${size} ${imageClass}" 
                     alt="Patient" 
                     style="${styleString}"
                     onerror="this.onerror=null; this.src='${config.defaultImage}'">
            </div>
        `;
    }

    /**
     * Load a patient's image
     * @param {string} patientId - The patient's ID
     * @param {HTMLImageElement|jQuery|string} imgElement - The image element or selector
     * @param {function} onSuccess - Optional callback for successful load
     * @param {function} onError - Optional callback for failed load
     */
    function loadPatientImage(patientId, imgElement, onSuccess, onError) {
        // Handle different types of image element inputs
        const $img = imgElement instanceof jQuery 
            ? imgElement 
            : (typeof imgElement === 'string' ? $(imgElement) : $(imgElement));

        if (!$img.length) {
            console.error('Invalid image element provided to loadPatientImage');
            return;
        }

        const imageUrl = `${config.apiEndpoint}/${patientId}`;
        
        // Create a new Image object to check if the image exists
        const imageChecker = new Image();
        
        // Define what happens on successful load
        imageChecker.onload = function() {
            // Add cache-busting parameter to avoid browser caching
            $img.attr('src', `${imageUrl}?t=${new Date().getTime()}`);
            
            // Call success callback if provided
            if (typeof onSuccess === 'function') {
                onSuccess($img);
            }
        };
        
        // Define what happens on error
        imageChecker.onerror = function() {
            // Keep/set default image
            $img.attr('src', config.defaultImage);
            
            // Call error callback if provided
            if (typeof onError === 'function') {
                onError($img);
            }
        };
        
        // Start loading the image (with cache-busting to ensure fresh check)
        imageChecker.src = `${imageUrl}?check=${new Date().getTime()}`;
    }

    /**
     * Load patient images in bulk for multiple elements
     * @param {string} selector - The selector for images to load
     */
    function loadAllPatientImages(selector = '.patient-image') {
        console.log('Loading all patient images for selector:', selector);
        
        $(selector).each(function() {
            const $img = $(this);
            const patientId = $img.data('patient-id');
            
            if (patientId) {
                loadPatientImage(patientId, $img);
            } else {
                console.warn('Patient image element missing data-patient-id attribute:', $img);
            }
        });
    }

    /**
     * Upload a patient image with preview
     * @param {string} patientId - The patient's ID
     * @param {File} imageFile - The image file to upload
     * @param {Object} options - Configuration options
     */
    function uploadPatientImage(patientId, imageFile, options = {}) {
        if (!patientId || !imageFile) {
            console.error('Invalid parameters for uploadPatientImage');
            if (options.onError) options.onError('Invalid parameters');
            return;
        }

        console.log('Starting upload for patient:', patientId);
        console.log('Image file:', imageFile.name, 'Size:', imageFile.size, 'Type:', imageFile.type);
        
        // Check if file is valid
        if (!imageFile || imageFile.size === 0) {
            console.error('Invalid image file:', imageFile);
            if (options.onError) options.onError('Invalid image file');
            return;
        }
        
        // Check file size (max 5MB)
        if (imageFile.size > 5 * 1024 * 1024) {
            console.error('File too large:', imageFile.size);
            if (options.onError) options.onError('File too large');
            return;
        }
        
        // Check file type
        const validImageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/jpg'];
        if (!validImageTypes.includes(imageFile.type)) {
            console.error('Invalid file type:', imageFile.type);
            if (options.onError) options.onError('Invalid file type');
            return;
        }
        
        // Show preview if a preview element is provided
        if (options.previewElement) {
            const reader = new FileReader();
            reader.onload = function(e) {
                $(options.previewElement).attr('src', e.target.result);
            };
            reader.readAsDataURL(imageFile);
        }
        
        // Prepare upload
        const formData = new FormData();
        formData.append('image', imageFile);
        
        // If a loadingElement is provided, show loading state
        if (options.loadingElement) {
            const $loadingElement = $(options.loadingElement);
            const originalContent = $loadingElement.html();
            $loadingElement.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i>');
        }
        
        // Perform the upload
        $.ajax({
            url: `${config.uploadEndpoint}/${patientId}`,
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            timeout: 120000, // Increase timeout to 120 seconds (2 minutes) for larger files
            xhr: function() {
                // Create an XMLHttpRequest instance
                const xhr = $.ajaxSettings.xhr();
                
                // Add progress event listener to show upload progress
                if (xhr.upload) {
                    xhr.upload.addEventListener('progress', function(evt) {
                        if (evt.lengthComputable && options.loadingElement) {
                            const percentComplete = Math.round((evt.loaded / evt.total) * 100);
                            const $loadingElement = $(options.loadingElement);
                            
                            if (percentComplete < 95) {
                                $loadingElement.html(`<i class="fas fa-spinner fa-spin"></i> ${percentComplete}%`);
                            } else {
                                // Once we hit 95%, show a processing message that doesn't make it look like it's stuck
                                $loadingElement.html(`<i class="fas fa-cog fa-spin"></i> Processing image...`);
                                
                                // Log to console for debugging
                                console.log(`Upload at ${percentComplete}%, processing on server...`);
                            }
                        }
                    }, false);
                }
                
                // Add upload complete listener
                xhr.addEventListener('loadend', function() {
                    console.log('Upload network transmission completed');
                });
                
                return xhr;
            },
            success: function(response) {
                console.log('Upload successful response received:', response);
                
                // If image elements are provided, update them with a delay for server processing
                if (options.updateElements && Array.isArray(options.updateElements)) {
                    // For larger files, add a longer delay to allow server processing to complete
                    // Scale the delay based on file size (larger files need more processing time)
                    const fileSizeMB = imageFile.size / (1024 * 1024);
                    const updateDelay = Math.min(2000, Math.max(500, Math.round(fileSizeMB * 500)));
                    
                    console.log(`Waiting ${updateDelay}ms before updating UI for ${fileSizeMB.toFixed(2)}MB image`);
                    
                    if (options.loadingElement) {
                        // Show processing message during the wait
                        const $loadingElement = $(options.loadingElement);
                        $loadingElement.html(`<i class="fas fa-check-circle"></i> Success! Updating...`);
                    }
                    
                    setTimeout(function() {
                        options.updateElements.forEach(function(element) {
                            // Create a timestamp to force image reload from server (avoid cache)
                            const timestamp = new Date().getTime();
                            const serverUrl = `${config.apiEndpoint}/${patientId}?t=${timestamp}`;
                            
                            console.log(`Updating image element with URL: ${serverUrl}`);
                            
                            // Update the image source with the new image from server
                            $(element).attr('src', serverUrl);
                            
                            // Add load event to confirm the image loaded successfully
                            $(element).one('load', function() {
                                console.log('Image loaded successfully from server');
                            }).one('error', function() {
                                console.error('Failed to load updated image from server');
                                // Try one more time with another timestamp
                                const retryTimestamp = new Date().getTime() + 1000;
                                $(this).attr('src', `${config.apiEndpoint}/${patientId}?t=${retryTimestamp}`);
                            });
                        });
                    }, updateDelay);
                }
                
                // Call success callback if provided
                if (options.onSuccess) options.onSuccess(response);
            },
            error: function(xhr, status, error) {
                console.error('Error uploading image:', error);
                console.error('Status:', status);
                console.error('Response:', xhr.responseText || 'No response text');
                
                // Provide more descriptive error messages
                let errorMessage = 'Upload failed';
                if (status === 'timeout') {
                    errorMessage = 'Upload timed out. The server took too long to process the image. Please try with a smaller image.';
                } else if (xhr.status === 413) {
                    errorMessage = 'Image too large. Please use an image under 2MB.';
                } else if (xhr.status === 504 || xhr.status === 502) {
                    errorMessage = 'Server gateway timeout. The image is likely too large for the server to process.';
                } else if (xhr.responseText) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        errorMessage = response.error || errorMessage;
                    } catch (e) {
                        // If can't parse, use status text as message
                        errorMessage = `Upload error: ${status || 'Unknown error'}`;
                    }
                }
                
                console.log('Showing error message to user:', errorMessage);
                
                // Call error callback if provided
                if (options.onError) options.onError(errorMessage);
            },
            complete: function() {
                // If a loadingElement is provided, restore its original state
                if (options.loadingElement) {
                    const $loadingElement = $(options.loadingElement);
                    $loadingElement.prop('disabled', false).html(options.loadingElementContent || '<i class="fas fa-upload"></i> Upload');
                }
                
                // Call complete callback if provided
                if (options.onComplete) options.onComplete();
                
                console.log('Upload request complete handler executed');
            }
        });
    }

    // Public API
    return {
        getPatientImageHtml,
        loadPatientImage,
        loadAllPatientImages,
        uploadPatientImage,
        config
    };
})();
