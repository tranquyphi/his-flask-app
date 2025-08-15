/**
 * User Profile Image Upload Implementation
 * Example of using ImageUtils for a different use case
 */

$(document).ready(function() {
    console.log('User profile image upload component loaded');
    
    // Check if the profile image container exists
    if ($('#user-profile-container').length) {
        // Initialize the user profile image uploader
        const profileImageUploader = ImageUtils.initImageUploader({
            uploadUrl: '/api/user/image', // Different endpoint for user profile images
            triggerSelector: '#profile-upload-btn',
            fileInputSelector: '#profile-image-upload',
            previewSelector: '#user-profile-image',
            containerSelector: '#user-profile-container',
            enableImageViewer: true,
            imageViewerTitle: 'Ảnh hồ sơ người dùng',
            showAlert: function(message, type) {
                // Custom alert implementation for user profile
                const alertHtml = `
                    <div class="alert alert-${type} alert-dismissible fade show mt-2" role="alert">
                        ${message}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                `;
                
                $('#profile-alerts').html(alertHtml);
                
                // Auto dismiss after 5 seconds
                setTimeout(() => {
                    $('.alert').alert('close');
                }, 5000);
            },
            getUploadId: function() {
                // Get the current user ID from the data attribute
                return $('#user-profile-container').data('user-id');
            }
        });
        
        // Load initial user image
        const userId = $('#user-profile-container').data('user-id');
        if (userId) {
            profileImageUploader.loadImage(userId);
        }
        
        // Handle view image button click
        $('#view-profile-image-btn').on('click', function() {
            if (userId) {
                profileImageUploader.viewImage();
            }
        });
        
        // Example of adding a delete image button functionality
        $('#delete-profile-image').on('click', function(e) {
            e.preventDefault();
            
            const userId = $('#user-profile-container').data('user-id');
            if (!userId) return;
            
            if (confirm('Bạn có chắc chắn muốn xóa ảnh hồ sơ?')) {
                $.ajax({
                    url: `/api/user/image/${userId}`,
                    type: 'DELETE',
                    success: function(response) {
                        // Show success message
                        $('#profile-alerts').html(`
                            <div class="alert alert-success alert-dismissible fade show mt-2" role="alert">
                                Ảnh hồ sơ đã được xóa thành công.
                                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                            </div>
                        `);
                        
                        // Reset to default image
                        $('#user-profile-image').attr('src', ImageUtils.DEFAULT_IMAGE);
                        
                        // Auto dismiss after 5 seconds
                        setTimeout(() => {
                            $('.alert').alert('close');
                        }, 5000);
                    },
                    error: function(xhr, status, error) {
                        // Show error message
                        $('#profile-alerts').html(`
                            <div class="alert alert-danger alert-dismissible fade show mt-2" role="alert">
                                Lỗi khi xóa ảnh: ${error}
                                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                            </div>
                        `);
                    }
                });
            }
        });
    }
});
