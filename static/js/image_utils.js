/**
 * HIS Image Utilities
 * A reusable module for handling image upload, preview, and management throughout the application
 * 
 * @author tranquyphi
 * @version 1.1.0
 */

const ImageUtils = (function() {
    // Constants
    const DEFAULT_IMAGE = '/static/images/default-patient.png';
    const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
    const VALID_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/jpg'];
    
    // Initialize the image viewer modal once
    let imageViewerInitialized = false;
    
    /**
     * Upload an image to a specified endpoint
     * 
     * @param {string} uploadUrl - The API endpoint URL to upload to
     * @param {File} imageFile - The image file to upload
     * @param {Object} options - Configuration options
     * @param {Function} options.onStart - Callback before upload starts
     * @param {Function} options.onSuccess - Callback on successful upload
     * @param {Function} options.onError - Callback on upload error
     * @param {Function} options.onComplete - Callback when upload completes (success or error)
     * @param {Function} options.showAlert - Function to display alerts/notifications
     * @returns {void}
     */
    function uploadImage(uploadUrl, imageFile, options = {}) {
        const {
            onStart = () => {},
            onSuccess = () => {},
            onError = () => {},
            onComplete = () => {},
            showAlert = console.log
        } = options;
        
        console.log('Starting image upload to:', uploadUrl);
        console.log('Image file:', imageFile.name, 'Size:', imageFile.size, 'Type:', imageFile.type);
        
        // Validate file
        if (!imageFile || imageFile.size === 0) {
            console.error('Invalid image file:', imageFile);
            showAlert('Tệp ảnh không hợp lệ hoặc trống.', 'danger');
            onError('Invalid or empty file');
            onComplete();
            return;
        }
        
        // Check file size
        if (imageFile.size > MAX_FILE_SIZE) {
            console.error('File too large:', imageFile.size);
            showAlert('Tệp ảnh quá lớn. Giới hạn tối đa 5MB.', 'warning');
            onError('File size exceeds limit');
            onComplete();
            return;
        }
        
        // Check file type
        if (!VALID_IMAGE_TYPES.includes(imageFile.type)) {
            console.error('Invalid file type:', imageFile.type);
            showAlert('Định dạng tệp không hợp lệ. Vui lòng sử dụng JPG, PNG hoặc GIF.', 'warning');
            onError('Invalid file type');
            onComplete();
            return;
        }
        
        // Prepare form data
        const formData = new FormData();
        formData.append('image', imageFile);
        
        // Call onStart callback
        onStart();
        
        // Send request
        $.ajax({
            url: uploadUrl,
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            beforeSend: function() {
                console.log('Sending upload request...');
            },
            success: function(response) {
                console.log('Upload successful:', response);
                showAlert('Hình ảnh đã được cập nhật thành công.', 'success');
                onSuccess(response);
            },
            error: function(xhr, status, error) {
                console.error('Error uploading image:', error);
                console.error('Status:', status);
                console.error('Response:', xhr.responseText);
                showAlert('Lỗi khi tải lên hình ảnh. Vui lòng thử lại.', 'danger');
                onError(error, xhr.responseText);
            },
            complete: function() {
                console.log('Upload request completed');
                onComplete();
            }
        });
    }
    
    /**
     * Preview an image file before uploading
     * 
     * @param {File} file - The image file to preview
     * @param {string|Element} previewElement - Selector or element where preview should be shown
     * @param {Function} callback - Optional callback after preview is loaded
     * @returns {void}
     */
    function previewImage(file, previewElement, callback = null) {
        if (!file || file.size === 0) {
            console.error('Invalid file for preview');
            return;
        }
        
        // Get the preview element
        const imgElement = typeof previewElement === 'string' ? 
                         $(previewElement)[0] : 
                         previewElement;
        
        if (!imgElement) {
            console.error('Preview element not found');
            return;
        }
        
        // Create file reader
        const reader = new FileReader();
        
        // Set up load event
        reader.onload = function(e) {
            // Update preview
            imgElement.src = e.target.result;
            
            // Call callback if provided
            if (callback && typeof callback === 'function') {
                callback(e.target.result);
            }
        };
        
        // Handle errors
        reader.onerror = function() {
            console.error('Error reading file for preview');
        };
        
        // Read the file
        reader.readAsDataURL(file);
    }
    
    /**
     * Load an image from a URL with loading indicator
     * 
     * @param {string} imageUrl - URL to load the image from
     * @param {string|Element} imgElement - Image element to update
     * @param {string} defaultImage - Default image URL if loading fails
     * @param {Object} options - Additional options
     * @returns {void}
     */
    function loadImage(imageUrl, imgElement, defaultImage = DEFAULT_IMAGE, options = {}) {
        const {
            showLoading = true,
            cacheBuster = true,
            containerSelector = null
        } = options;
        
        // Get the image element
        const $img = typeof imgElement === 'string' ? $(imgElement) : $(imgElement);
        
        if (!$img.length) {
            console.error('Image element not found');
            return;
        }
        
        // Get the container
        const $container = containerSelector ? 
                         $(containerSelector) : 
                         $img.parent();
        
        // Show loading
        if (showLoading) {
            $img.css('opacity', '0.6');
            
            // Add loading spinner if not already present
            if ($container.find('.image-loading-spinner').length === 0) {
                $container.append(
                    '<div class="image-loading-spinner position-absolute top-50 start-50 translate-middle">' +
                    '<div class="spinner-border text-primary" role="status" style="width: 1.5rem; height: 1.5rem;">' +
                    '<span class="visually-hidden">Loading...</span></div></div>'
                );
            }
        }
        
        // Add cache buster to URL if needed
        const finalUrl = cacheBuster ? 
                      `${imageUrl}?t=${new Date().getTime()}` : 
                      imageUrl;
        
        // Create a new image object to test loading
        const img = new Image();
        
        img.onload = function() {
            // Remove loading spinner
            $container.find('.image-loading-spinner').remove();
            // Show the loaded image
            $img.attr('src', this.src).css('opacity', '1');
        };
        
        img.onerror = function() {
            // Remove loading spinner
            $container.find('.image-loading-spinner').remove();
            // Set default image
            $img.attr('src', defaultImage).css('opacity', '1');
            console.log('Image failed to load, using default');
        };
        
        // Check if image exists without directly setting img src
        fetch(imageUrl)
            .then(response => {
                if (response.ok) {
                    img.src = finalUrl;
                } else {
                    // Set default image if no custom image
                    $img.attr('src', defaultImage).css('opacity', '1');
                    $container.find('.image-loading-spinner').remove();
                }
            })
            .catch(error => {
                console.error('Error loading image:', error);
                $img.attr('src', defaultImage).css('opacity', '1');
                $container.find('.image-loading-spinner').remove();
            });
    }
    
    /**
     * Initialize an image uploader on elements
     * 
     * @param {Object} config - Configuration object
     * @param {string} config.uploadUrl - The API endpoint for uploads
     * @param {string} config.triggerSelector - Selector for button that triggers file dialog
     * @param {string} config.fileInputSelector - Selector for file input element
     * @param {string} config.previewSelector - Selector for image preview element
     * @param {string} config.containerSelector - Selector for image container (optional)
     * @param {Function} config.showAlert - Function to show alerts/notifications
     * @param {Function} config.getUploadId - Function that returns the ID to use in upload URL
     * @param {boolean} config.enableImageViewer - Whether to make the image viewable in a larger frame (default: true)
     * @param {string} config.imageViewerTitle - Title for the image viewer modal (default: "Xem ảnh")
     * @returns {Object} - Controller with public methods
     */
    function initImageUploader(config) {
        const {
            uploadUrl,
            triggerSelector,
            fileInputSelector,
            previewSelector,
            containerSelector = null,
            showAlert = console.log,
            getUploadId = () => null,
            enableImageViewer = true,
            imageViewerTitle = 'Xem ảnh'
        } = config;
        
        // Initialize event handlers
        $(triggerSelector).on('click', function() {
            $(fileInputSelector).click();
        });
        
        // If container is specified, make it clickable too
        if (containerSelector) {
            $(containerSelector).on('click', function() {
                $(fileInputSelector).click();
            });
        }
        
        // Handle file selection
        $(fileInputSelector).on('change', function() {
            if (!this.files || !this.files[0]) {
                return;
            }
            
            const file = this.files[0];
            
            // Show filename feedback
            showAlert(`Đã chọn tệp: ${file.name} (${Math.round(file.size/1024)} KB)`, 'info');
            
            // Get the ID needed for upload URL
            const id = getUploadId();
            if (!id) {
                showAlert('Không thể xác định ID để tải lên hình ảnh.', 'danger');
                return;
            }
            
            // Create final upload URL with ID
            const finalUploadUrl = typeof uploadUrl === 'function' ? 
                               uploadUrl(id) : 
                               `${uploadUrl}/${id}`;
            
            // Preview the image
            previewImage(file, previewSelector, () => {
                // After preview is shown, upload the image
                uploadImage(finalUploadUrl, file, {
                    showAlert,
                    onStart: function() {
                        // Disable the upload button
                        $(triggerSelector).prop('disabled', true)
                            .html('<i class="fas fa-spinner fa-spin"></i>');
                    },
                    onComplete: function() {
                        // Reset the upload button
                        $(triggerSelector).prop('disabled', false)
                            .html('<i class="fas fa-upload"></i> Tải ảnh');
                        
                        // Reset file input
                        $(fileInputSelector).val('');
                    }
                });
            });
        });
        
        // Make image viewable in larger frame if enabled
        if (enableImageViewer) {
            try {
                // Wait for DOM to be ready
                $(document).ready(function() {
                    try {
                        // Check if elements exist before setting up handlers
                        if ($(previewSelector).length) {
                            // Set up click handler to view image in larger frame
                            makeImageViewable(previewSelector, null, {
                                title: imageViewerTitle,
                                clickSelector: containerSelector
                            });
                        } else {
                            console.warn('Image preview element not found:', previewSelector);
                        }
                    } catch (readyError) {
                        console.error('Error in image viewer initialization:', readyError);
                    }
                });
            } catch (viewerError) {
                console.error('Error setting up image viewer:', viewerError);
            }
        }
        
        // Return controller with public methods
        return {
            /**
             * Load an image for the configured preview element
             * @param {string} id - The ID to use in the image URL
             */
            loadImage: function(id) {
                if (!id) return;
                
                const imageUrl = typeof uploadUrl === 'function' ? 
                              uploadUrl(id) : 
                              `${uploadUrl}/${id}`;
                
                loadImage(imageUrl, previewSelector, DEFAULT_IMAGE, {
                    containerSelector: containerSelector
                });
            },
            
            /**
             * Manually trigger the file input dialog
             */
            triggerFileDialog: function() {
                $(fileInputSelector).click();
            },
            
            /**
             * View the current image in a larger modal
             */
            viewImage: function() {
                const id = getUploadId();
                if (!id) return;
                
                const imageUrl = typeof uploadUrl === 'function' ? 
                              uploadUrl(id) : 
                              `${uploadUrl}/${id}`;
                
                openImageViewer(imageUrl, imageViewerTitle);
            }
        };
    }
    
    /**
     * Initialize the image viewer modal once
     * Creates a Bootstrap modal for viewing images in a larger frame
     */
    function initImageViewerModal() {
        try {
            if (imageViewerInitialized) return;
            
            // Check if modal already exists
            if ($('#imageViewerModal').length) {
                imageViewerInitialized = true;
                return;
            }
            
            // Create modal HTML
            const modalHTML = `
            <div class="modal fade" id="imageViewerModal" tabindex="-1" aria-labelledby="imageViewerModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-lg modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="imageViewerModalLabel">Xem ảnh</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body text-center p-0">
                            <div class="position-relative">
                                <img id="imageViewerImg" src="" alt="Full size image" class="img-fluid" style="max-height: 70vh;">
                                <div class="position-absolute top-50 start-50 translate-middle" id="imageViewerSpinner">
                                    <div class="spinner-border text-primary" role="status">
                                        <span class="visually-hidden">Loading...</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Đóng</button>
                        </div>
                    </div>
                </div>
            </div>
            `;
            
            try {
                // Append modal to body
                $('body').append(modalHTML);
                
                // Handle modal events
                $('#imageViewerModal').on('hidden.bs.modal', function () {
                    $('#imageViewerImg').attr('src', '');
                });
                
                imageViewerInitialized = true;
            } catch (appendError) {
                console.error('Error appending modal to body:', appendError);
            }
        } catch (error) {
            console.error('Error initializing image viewer modal:', error);
        }
    }
    
    /**
     * Open an image in the image viewer modal
     * 
     * @param {string} imageUrl - URL of the image to display
     * @param {string} title - Optional title for the modal
     */
    function openImageViewer(imageUrl, title = 'Xem ảnh') {
        // Make sure the modal exists
        initImageViewerModal();
        
        // Set the modal title
        $('#imageViewerModalLabel').text(title);
        
        // Show loading spinner
        $('#imageViewerSpinner').show();
        $('#imageViewerImg').css('opacity', '0.3');
        
        // Initialize the modal if not already done
        const viewerModal = new bootstrap.Modal(document.getElementById('imageViewerModal'));
        
        // Set up image load event
        $('#imageViewerImg').on('load', function() {
            // Hide spinner when image is loaded
            $('#imageViewerSpinner').hide();
            $(this).css('opacity', '1');
        }).on('error', function() {
            // If image fails to load
            $('#imageViewerSpinner').hide();
            $(this).css('opacity', '1');
            $(this).attr('src', DEFAULT_IMAGE);
        });
        
        // Set the image source with a timestamp to avoid cache
        const cachedImageUrl = imageUrl.includes('?') ? 
                           imageUrl : 
                           `${imageUrl}?t=${new Date().getTime()}`;
        
        $('#imageViewerImg').attr('src', cachedImageUrl);
        
        // Show the modal
        viewerModal.show();
    }
    
    /**
     * Make an image clickable to open in the image viewer
     * 
     * @param {string|Element} imgElement - Selector or element to make clickable
     * @param {string} imageUrl - URL to load in the viewer (if different from img src)
     * @param {Object} options - Additional options
     */
    function makeImageViewable(imgElement, imageUrl = null, options = {}) {
        try {
            const {
                title = 'Xem ảnh',
                clickSelector = null
            } = options;
            
            // Get the image element
            const $img = typeof imgElement === 'string' ? $(imgElement) : $(imgElement);
            
            if (!$img.length) {
                console.error('Image element not found for viewer');
                return;
            }
            
            // Set click handler on image or specified container
            const $clickElement = clickSelector ? $(clickSelector) : $img;
            
            $clickElement.css('cursor', 'pointer');
            
            $clickElement.on('click', function(e) {
                try {
                    // Prevent default action if it's a link
                    e.preventDefault();
                    
                    // Determine the image URL to use
                    const imgUrl = imageUrl || $img.attr('src');
                    if (!imgUrl || imgUrl === DEFAULT_IMAGE) {
                        console.log('No valid image to view');
                        return;
                    }
                    
                    // Open the image viewer
                    openImageViewer(imgUrl, title);
                } catch (clickError) {
                    console.error('Error in image viewer click handler:', clickError);
                }
            });
        } catch (error) {
            console.error('Error setting up image viewer:', error);
        }
    }
    
    // Public API
    return {
        uploadImage,
        previewImage,
        loadImage,
        initImageUploader,
        makeImageViewable,
        openImageViewer,
        VALID_IMAGE_TYPES,
        MAX_FILE_SIZE,
        DEFAULT_IMAGE
    };
})();
