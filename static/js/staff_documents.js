// Staff Documents JavaScript
$(document).ready(function() {
    let documentsTable = null;
    let allDocuments = [];
    let allStaff = [];
    let allDocumentTypes = [];
    let deleteDocumentId = null;

    $('#loading-overlay').show();
    initializeUI();

    // Event handlers
    $('#search-document').on('keyup', function() {
        if (documentsTable) {
            documentsTable.search($(this).val()).draw();
        }
    });

    $('#staff-filter').on('change', function() {
        filterByStaff($(this).val());
    });

    $('#document-type-filter').on('change', function() {
        filterByDocumentType($(this).val());
    });

    $('#refresh-data').on('click', function() {
        loadDocumentsData();
    });

    $('#submit-upload').on('click', function() {
        uploadDocument();
    });

    // File drop area functionality
    setupFileDropArea();

    function initializeUI() {
        Promise.all([
            loadDocumentsData(),
            loadStaffData(),
            loadDocumentTypesData()
        ]).then(() => {
            $('#loading-overlay').hide();
        }).catch(error => {
            $('#loading-overlay').hide();
            alert('Lỗi khi khởi tạo giao diện: ' + error.message);
        });
    }

    function loadDocumentsData() {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: '/api/staff_documents',
                method: 'GET',
                success: function(response) {
                    allDocuments = response.staff_documents || [];
                    initializeDocumentsTable();
                    resolve(allDocuments);
                },
                error: function(xhr, status, error) {
                    console.error('Error loading documents:', error);
                    alert('Không thể tải dữ liệu tài liệu: ' + error);
                    reject(error);
                }
            });
        });
    }

    function loadStaffData() {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: '/api/staff',
                method: 'GET',
                success: function(response) {
                    allStaff = response.staff || [];
                    populateStaffDropdowns();
                    resolve(allStaff);
                },
                error: function(xhr, status, error) {
                    console.error('Error loading staff:', error);
                    alert('Không thể tải dữ liệu nhân viên: ' + error);
                    reject(error);
                }
            });
        });
    }

    function loadDocumentTypesData() {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: '/api/types',
                method: 'GET',
                success: function(response) {
                    allDocumentTypes = response.staff_document_types || [];
                    populateDocumentTypesDropdowns();
                    resolve(allDocumentTypes);
                },
                error: function(xhr, status, error) {
                    console.error('Error loading document types:', error);
                    alert('Không thể tải dữ liệu loại tài liệu: ' + error);
                    reject(error);
                }
            });
        });
    }

    function populateStaffDropdowns() {
        // For filter dropdown
        var filterSelect = $('#staff-filter');
        filterSelect.empty();
        filterSelect.append('<option value="">-- Tất cả Nhân viên --</option>');
        allStaff.forEach(function(staff) {
            filterSelect.append(`<option value="${staff.StaffId}">${staff.StaffName}</option>`);
        });

        // For upload form dropdown
        var uploadSelect = $('#staff-select');
        uploadSelect.empty();
        uploadSelect.append('<option value="">-- Chọn nhân viên --</option>');
        allStaff.forEach(function(staff) {
            uploadSelect.append(`<option value="${staff.StaffId}">${staff.StaffName} (${staff.StaffRole})</option>`);
        });
    }

    function populateDocumentTypesDropdowns() {
        // For filter dropdown
        var filterSelect = $('#document-type-filter');
        filterSelect.empty();
        filterSelect.append('<option value="">-- Tất cả Loại tài liệu --</option>');
        allDocumentTypes.forEach(function(type) {
            filterSelect.append(`<option value="${type.DocumentTypeId}">${type.DocumentTypeName}</option>`);
        });

        // For upload form dropdown
        var uploadSelect = $('#document-type-select');
        uploadSelect.empty();
        uploadSelect.append('<option value="">-- Chọn loại tài liệu --</option>');
        allDocumentTypes.forEach(function(type) {
            uploadSelect.append(`<option value="${type.DocumentTypeId}">${type.DocumentTypeName}</option>`);
        });
    }

    function initializeDocumentsTable() {
        if (documentsTable) {
            documentsTable.destroy();
        }

        documentsTable = $('#documents-table').DataTable({
            data: allDocuments,
            columns: [
                { data: 'DocumentId', title: 'ID', width: '60px' },
                { 
                    data: null, 
                    title: 'Xem trước', 
                    width: '80px',
                    render: function(data, type, row) {
                        return renderThumbnail(data);
                    }
                },
                { data: 'StaffName', title: 'Nhân viên', width: '150px' },
                { data: 'StaffRole', title: 'Vai trò', width: '120px' },
                { 
                    data: 'DocumentTypeName', 
                    title: 'Loại tài liệu', 
                    width: '150px',
                    render: function(data, type, row) {
                        return data ? `<span class="document-type-badge">${data}</span>` : '<span class="text-muted">-</span>';
                    }
                },
                { 
                    data: 'original_filename', 
                    title: 'Tên file gốc', 
                    width: '200px',
                    render: function(data, type, row) {
                        return data ? `<span title="${data}">${data.length > 30 ? data.substring(0, 30) + '...' : data}</span>` : '<span class="text-muted">-</span>';
                    }
                },
                { 
                    data: 'file_type', 
                    title: 'Loại file', 
                    width: '100px',
                    render: function(data, type, row) {
                        if (!data) return '<span class="text-muted">-</span>';
                        const icon = getFileTypeIcon(data);
                        return `<i class="${icon}" title="${data}"></i> ${data.split('/')[1] || data}`;
                    }
                },
                { 
                    data: 'FileSize', 
                    title: 'Kích thước', 
                    width: '100px',
                    render: function(data, type, row) {
                        return data ? formatFileSize(data) : '<span class="text-muted">-</span>';
                    }
                },
                { 
                    data: 'UploadDate', 
                    title: 'Ngày tải lên', 
                    width: '120px',
                    render: function(data, type, row) {
                        return data ? formatDate(data) : '<span class="text-muted">-</span>';
                    }
                },
                { 
                    data: null, 
                    title: 'Thao tác', 
                    width: '120px',
                    orderable: false,
                    render: function(data, type, row) {
                        return renderActionButtons(data);
                    }
                }
            ],
            responsive: true,
            language: {
                url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/vi.json'
            },
            order: [[0, 'desc']],
            pageLength: 25,
            lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
            dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>rtip',
            initComplete: function() {
                // Apply filters after table is initialized
                applyFilters();
            }
        });
    }

    function renderThumbnail(data) {
        if (data.document_links && data.document_links.thumbnail_path) {
            return `<div class="thumbnail-container">
                        <img src="/static/staff_documents/${data.document_links.thumbnail_path}" 
                             class="document-thumbnail" 
                             alt="Thumbnail"
                             onclick="previewDocument(${data.DocumentId})"
                             title="Nhấn để xem">
                        <div class="thumbnail-overlay">Xem</div>
                    </div>`;
        } else {
            return `<div class="thumbnail-placeholder" onclick="previewDocument(${data.DocumentId})" title="Nhấn để xem">
                        <i class="fas fa-file"></i>
                    </div>`;
        }
    }

    function renderActionButtons(data) {
        return `<div class="btn-group btn-group-sm" role="group">
                    <button type="button" class="btn btn-outline-primary" 
                            onclick="previewDocument(${data.DocumentId})" 
                            title="Xem tài liệu">
                        <i class="fas fa-eye"></i>
                    </button>
                                            <a href="/api/staff_documents/${data.DocumentId}?download=true" 
                       class="btn btn-outline-success" 
                       title="Tải xuống">
                        <i class="fas fa-download"></i>
                    </a>
                    <button type="button" class="btn btn-outline-danger" 
                            onclick="deleteDocument(${data.DocumentId})" 
                            title="Xóa tài liệu">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>`;
    }

    function getFileTypeIcon(fileType) {
        if (!fileType) return 'fas fa-file';
        
        if (fileType.startsWith('image/')) return 'fas fa-file-image';
        if (fileType.includes('pdf')) return 'fas fa-file-pdf';
        if (fileType.includes('word') || fileType.includes('document')) return 'fas fa-file-word';
        if (fileType.includes('excel') || fileType.includes('sheet')) return 'fas fa-file-excel';
        if (fileType.includes('powerpoint') || fileType.includes('presentation')) return 'fas fa-file-powerpoint';
        if (fileType.includes('text')) return 'fas fa-file-alt';
        if (fileType.includes('zip')) return 'fas fa-file-archive';
        
        return 'fas fa-file';
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function formatDate(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString('vi-VN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    function filterByStaff(staffId) {
        if (documentsTable) {
            if (staffId) {
                documentsTable.column(2).search(allStaff.find(s => s.StaffId == staffId)?.StaffName || '').draw();
            } else {
                documentsTable.column(2).search('').draw();
            }
        }
    }

    function filterByDocumentType(documentTypeId) {
        if (documentsTable) {
            if (documentTypeId) {
                documentsTable.column(4).search(allDocumentTypes.find(t => t.DocumentTypeId == documentTypeId)?.DocumentTypeName || '').draw();
            } else {
                documentsTable.column(4).search('').draw();
            }
        }
    }

    function applyFilters() {
        const staffFilter = $('#staff-filter').val();
        const documentTypeFilter = $('#document-type-filter').val();
        
        if (staffFilter) filterByStaff(staffFilter);
        if (documentTypeFilter) filterByDocumentType(documentTypeFilter);
    }

    function setupFileDropArea() {
        const dropArea = $('.file-drop-area');
        const fileInput = $('#document-file');
        const fileName = $('#file-name');

        // Handle file selection
        fileInput.on('change', function() {
            const file = this.files[0];
            if (file) {
                fileName.text(file.name);
                dropArea.addClass('has-file');
            }
        });

        // Handle drag and drop
        dropArea.on('dragover', function(e) {
            e.preventDefault();
            $(this).addClass('drag-over');
        });

        dropArea.on('dragleave', function(e) {
            e.preventDefault();
            $(this).removeClass('drag-over');
        });

        dropArea.on('drop', function(e) {
            e.preventDefault();
            $(this).removeClass('drag-over');
            
            const files = e.originalEvent.dataTransfer.files;
            if (files.length > 0) {
                fileInput[0].files = files;
                fileName.text(files[0].name);
                dropArea.addClass('has-file');
            }
        });

        // Click to select file
        dropArea.on('click', function() {
            fileInput.click();
        });
    }

    function uploadDocument() {
        const formData = new FormData();
        const fileInput = $('#document-file')[0];
        const staffSelect = $('#staff-select');
        const documentTypeSelect = $('#document-type-select');
        const descriptionInput = $('#document-description');

        // Validate form
        if (!fileInput.files[0]) {
            alert('Vui lòng chọn một tệp để tải lên.');
            return;
        }

        if (!staffSelect.val()) {
            alert('Vui lòng chọn nhân viên.');
            return;
        }

        if (!documentTypeSelect.val()) {
            alert('Vui lòng chọn loại tài liệu.');
            return;
        }

        // Build form data
        formData.append('file', fileInput.files[0]);
        formData.append('staff_id', staffSelect.val());
        formData.append('document_type_id', documentTypeSelect.val());
        formData.append('description', descriptionInput.val());

        // Show loading state
        $('#submit-upload').prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-2"></i>Đang tải lên...');

        $.ajax({
            url: '/api/staff_documents',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                alert('Tài liệu đã được tải lên thành công!');
                
                // Reset form
                $('#upload-document-form')[0].reset();
                $('#file-name').text('');
                $('.file-drop-area').removeClass('has-file');
                
                // Close modal
                $('#uploadDocumentModal').modal('hide');
                
                // Reload data
                loadDocumentsData();
            },
            error: function(xhr, status, error) {
                let errorMessage = 'Lỗi khi tải lên tài liệu.';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMessage = xhr.responseJSON.error;
                }
                alert(errorMessage);
            },
            complete: function() {
                $('#submit-upload').prop('disabled', false).html('<i class="fas fa-upload me-2"></i>Tải lên');
            }
        });
    }

    // Global functions for onclick handlers
    window.previewDocument = function(documentId) {
        const document = allDocuments.find(d => d.DocumentId == documentId);
        if (!document) {
            alert('Không tìm thấy tài liệu.');
            return;
        }

        // Set download link
        $('#download-document').attr('href', `/api/staff_documents/${documentId}?download=true`);

        // Prepare preview content
        let previewContent = '';
        const fileType = document.file_type;
        const filePath = document.document_links?.file_path;

        if (fileType && fileType.startsWith('image/')) {
            // Image preview
            previewContent = `<img src="/static/staff_documents/${filePath}" class="preview-image" alt="Document Preview">`;
        } else if (fileType && fileType.includes('pdf')) {
            // PDF preview
            previewContent = `<iframe src="/static/staff_documents/${filePath}" class="preview-iframe"></iframe>`;
        } else {
            // Generic preview with file info
            previewContent = `
                <div class="text-center p-5">
                    <i class="fas fa-file fa-5x text-muted mb-3"></i>
                    <h5>Không thể xem trước loại tệp này</h5>
                    <p class="text-muted">Tên tệp: ${document.original_filename || 'Không xác định'}</p>
                    <p class="text-muted">Loại tệp: ${document.file_type || 'Không xác định'}</p>
                    <p class="text-muted">Kích thước: ${formatFileSize(document.FileSize)}</p>
                </div>
            `;
        }

        $('#document-preview-content').html(previewContent);
        $('#documentPreviewModal').modal('show');
    };

    window.deleteDocument = function(documentId) {
        deleteDocumentId = documentId;
        $('#deleteDocumentModal').modal('show');
    };

    // Delete confirmation handler
    $('#confirm-delete').on('click', function() {
        if (!deleteDocumentId) return;

        $.ajax({
            url: `/api/staff_documents/${deleteDocumentId}`,
            method: 'DELETE',
            success: function(response) {
                alert('Tài liệu đã được xóa thành công!');
                $('#deleteDocumentModal').modal('hide');
                loadDocumentsData();
            },
            error: function(xhr, status, error) {
                let errorMessage = 'Lỗi khi xóa tài liệu.';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMessage = xhr.responseJSON.error;
                }
                alert(errorMessage);
            }
        });
    });

    // Modal event handlers
    $('#uploadDocumentModal').on('hidden.bs.modal', function() {
        $('#upload-document-form')[0].reset();
        $('#file-name').text('');
        $('.file-drop-area').removeClass('has-file');
    });

    $('#deleteDocumentModal').on('hidden.bs.modal', function() {
        deleteDocumentId = null;
    });
});
