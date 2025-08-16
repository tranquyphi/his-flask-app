// Patient Documents JavaScript
$(document).ready(function() {
    console.log('Patient Documents script loaded');
    
    let documentsTable = null;
    let allDocuments = [];
    let allPatients = [];
    let allDocumentTypes = [];
    let deleteDocumentId = null;
    
    // Show loading overlay initially
    $('#loading-overlay').show();
    
    // Initialize the UI
    initializeUI();
    
    // Event handlers
    $('#search-document').on('keyup', function() {
        if (documentsTable) {
            documentsTable.search($(this).val()).draw();
        }
    });
    
    $('#patient-filter').on('change', function() {
        filterByPatient($(this).val());
    });
    
    $('#document-type-filter').on('change', function() {
        filterByDocumentType($(this).val());
    });
    
    $('#refresh-data').on('click', function() {
        loadDocumentsData();
    });
    
    // File drop area functionality
    const fileDropArea = $('.file-drop-area');
    const fileInput = $('#document-file');
    
    fileDropArea.on('dragover', function(e) {
        e.preventDefault();
        fileDropArea.addClass('drag-over');
    });
    
    fileDropArea.on('dragleave', function(e) {
        e.preventDefault();
        fileDropArea.removeClass('drag-over');
    });
    
    fileDropArea.on('drop', function(e) {
        e.preventDefault();
        fileDropArea.removeClass('drag-over');
        if (e.originalEvent.dataTransfer.files.length) {
            fileInput[0].files = e.originalEvent.dataTransfer.files;
            updateFileName();
        }
    });
    
    fileInput.on('change', function() {
        updateFileName();
    });
    
    // Handle document upload
    $('#submit-upload').on('click', function() {
        uploadDocument();
    });
    
    // Handle document deletion
    $('#confirm-delete').on('click', function() {
        if (deleteDocumentId) {
            deleteDocument(deleteDocumentId);
        }
    });
    
    // Initialize the UI components
    function initializeUI() {
        Promise.all([
            loadDocumentsData(),
            loadPatientsData(),
            loadDocumentTypesData()
        ]).then(() => {
            console.log('All data loaded');
        }).catch(error => {
            console.error('Error initializing UI:', error);
            showAlert('danger', 'Lỗi khi khởi tạo giao diện: ' + error.message);
        });
    }
    
    // Load documents data
    function loadDocumentsData() {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: '/api/patient_documents',
                method: 'GET',
                success: function(response) {
                    allDocuments = response.patient_documents || [];
                    initializeDocumentsTable();
                    $('#loading-overlay').hide();
                    resolve(allDocuments);
                },
                error: function(xhr, status, error) {
                    console.error('Error loading documents:', error);
                    $('#loading-overlay').hide();
                    showAlert('danger', 'Không thể tải dữ liệu tài liệu: ' + error);
                    reject(error);
                }
            });
        });
    }
    
    // Load patients data
    function loadPatientsData() {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: '/api/patients',
                method: 'GET',
                success: function(response) {
                    allPatients = response.patients || [];
                    populatePatientsDropdowns();
                    resolve(allPatients);
                },
                error: function(xhr, status, error) {
                    console.error('Error loading patients:', error);
                    showAlert('danger', 'Không thể tải dữ liệu bệnh nhân: ' + error);
                    reject(error);
                }
            });
        });
    }
    
    // Load document types data
    function loadDocumentTypesData() {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: '/api/document_types',
                method: 'GET',
                success: function(response) {
                    allDocumentTypes = response.document_types || [];
                    populateDocumentTypesDropdowns();
                    resolve(allDocumentTypes);
                },
                error: function(xhr, status, error) {
                    console.error('Error loading document types:', error);
                    showAlert('danger', 'Không thể tải dữ liệu loại tài liệu: ' + error);
                    reject(error);
                }
            });
        });
    }
    
    // Initialize documents data table
    function initializeDocumentsTable() {
        if (documentsTable) {
            documentsTable.destroy();
        }
        
        documentsTable = $('#documents-table').DataTable({
            data: allDocuments,
            columns: [
                { data: 'DocumentId' },
                { 
                    data: null,
                    render: function(data, type, row) {
                        return `<div>
                            <strong>${data.PatientName || 'N/A'}</strong>
                            <div class="small text-muted">ID: ${data.PatientId || 'N/A'}</div>
                        </div>`;
                    }
                },
                { 
                    data: null,
                    render: function(data, type, row) {
                        return data.DocumentTypeName || 'Không xác định';
                    }
                },
                { 
                    data: 'original_filename',
                    render: function(data, type, row) {
                        return data || 'Không có tên file';
                    }
                },
                { 
                    data: 'file_type',
                    render: function(data, type, row) {
                        return formatFileType(data);
                    }
                },
                { 
                    data: 'file_size',
                    render: function(data, type, row) {
                        return formatFileSize(data);
                    }
                },
                { 
                    data: 'upload_date',
                    render: function(data, type, row) {
                        return formatDate(data);
                    }
                },
                {
                    data: null,
                    orderable: false,
                    className: 'dt-body-center',
                    responsivePriority: 1, // Make sure action buttons have high priority in responsive mode
                    render: function(data, type, row) {
                        return `
                            <div class="btn-group btn-group-sm">
                                <button class="btn btn-info view-document" data-document-id="${data.DocumentId}" title="Xem tài liệu">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <a href="/api/patient_documents/${data.DocumentId}?download=true" class="btn btn-primary" title="Tải xuống">
                                    <i class="fas fa-download"></i>
                                </a>
                                <button class="btn btn-danger delete-document" data-document-id="${data.DocumentId}" title="Xóa">
                                    <i class="fas fa-trash-alt"></i>
                                </button>
                            </div>
                        `;
                    }
                }
            ],
            responsive: {
                details: {
                    display: $.fn.dataTable.Responsive.display.childRowImmediate,
                    type: 'none',
                    target: ''
                }
            },
            dom: '<"row"<"col-md-6"l><"col-md-6 text-end"f>>rtip',
            language: {
                search: "Tìm kiếm:",
                lengthMenu: "Hiển thị _MENU_ mục",
                info: "Hiển thị _START_ đến _END_ trong _TOTAL_ mục",
                infoEmpty: "Hiển thị 0 đến 0 trong 0 mục",
                infoFiltered: "(lọc từ _MAX_ mục)",
                zeroRecords: "Không tìm thấy tài liệu nào",
                paginate: {
                    first: "Đầu tiên",
                    last: "Cuối cùng",
                    next: "Tiếp",
                    previous: "Trước"
                }
            },
            order: [[0, 'desc']], // Sort by DocumentId descending by default
            drawCallback: function() {
                // Attach event handlers after table draw
                attachDocumentEventHandlers();
            }
        });
    }
    
    // Attach event handlers for document actions
    function attachDocumentEventHandlers() {
        // Use document delegation to handle both original and responsive-created elements
        // First remove any existing handlers to prevent duplicates
        $(document).off('click', '.view-document');
        $(document).off('click', '.delete-document');
        
        // View document handler with delegation
        $(document).on('click', '.view-document', function() {
            const documentId = $(this).data('document-id');
            viewDocument(documentId);
        });
        
        // Delete document handler with delegation
        $(document).on('click', '.delete-document', function() {
            deleteDocumentId = $(this).data('document-id');
            $('#deleteDocumentModal').modal('show');
        });
    }
    
    // Populate patient dropdowns
    function populatePatientsDropdowns() {
        const patientFilter = $('#patient-filter');
        const patientSelect = $('#patient-select');
        
        // Clear existing options (except first one)
        patientFilter.find('option:not(:first)').remove();
        patientSelect.find('option:not(:first)').remove();
        
        // Add patient options
        allPatients.forEach(function(patient) {
            const optionText = `${patient.PatientName} (${patient.PatientId})`;
            patientFilter.append(new Option(optionText, patient.PatientId));
            patientSelect.append(new Option(optionText, patient.PatientId));
        });
    }
    
    // Populate document type dropdowns
    function populateDocumentTypesDropdowns() {
        const typeFilter = $('#document-type-filter');
        const typeSelect = $('#document-type-select');
        
        // Clear existing options (except first one)
        typeFilter.find('option:not(:first)').remove();
        typeSelect.find('option:not(:first)').remove();
        
        // Add document type options
        allDocumentTypes.forEach(function(docType) {
            typeFilter.append(new Option(docType.DocumentTypeName, docType.DocumentTypeId));
            typeSelect.append(new Option(docType.DocumentTypeName, docType.DocumentTypeId));
        });
    }
    
    // Filter by patient
    function filterByPatient(patientId) {
        if (!patientId) {
            // If no patient is selected, show all documents
            documentsTable.search('').columns(1).search('').draw();
        } else {
            // Filter by patient ID
            documentsTable.columns(1).search(patientId).draw();
        }
    }
    
    // Filter by document type
    function filterByDocumentType(typeId) {
        if (!typeId) {
            // If no type is selected, show all documents
            documentsTable.columns(2).search('').draw();
        } else {
            // Find the type name
            const typeName = allDocumentTypes.find(t => t.DocumentTypeId == typeId)?.DocumentTypeName || '';
            
            // Filter by document type name
            documentsTable.columns(2).search(typeName).draw();
        }
    }
    
    // View document
    function viewDocument(documentId) {
        // Find the document in allDocuments
        const document = allDocuments.find(d => d.DocumentId == documentId);
        
        if (!document) {
            showAlert('danger', 'Không thể tìm thấy tài liệu');
            return;
        }
        
        const previewContent = $('#document-preview-content');
        previewContent.empty();
        
        // Set the modal title
        $('#documentPreviewModalLabel').text(`Xem tài liệu: ${document.original_filename || 'Tài liệu'}`);
        
        // Set download link
        $('#download-document').attr('href', `/api/patient_documents/${documentId}?download=true`);
        
        // Create preview based on file type
        if (document.file_type) {
            if (document.file_type.startsWith('image/')) {
                // Image preview
                const imgElement = $('<img>')
                    .addClass('preview-image')
                    .attr('src', `/api/patient_documents/${documentId}?download=true`)
                    .attr('alt', document.original_filename || 'Document image');
                    
                previewContent.append(imgElement);
            } else if (document.file_type.includes('pdf')) {
                // PDF preview
                const iframeElement = $('<iframe>')
                    .addClass('preview-iframe')
                    .attr('src', `/api/patient_documents/${documentId}?download=true`);
                    
                previewContent.append(iframeElement);
            } else {
                // For other file types, show an icon and information
                const fileInfoElement = $('<div>')
                    .addClass('text-center p-5')
                    .html(`
                        <div class="mb-3">
                            <i class="fas ${getFileIcon(document.file_type)} fa-5x text-secondary"></i>
                        </div>
                        <h5>${document.original_filename || 'Tài liệu'}</h5>
                        <p>Loại file: ${document.file_type}</p>
                        <p>Kích thước: ${formatFileSize(document.file_size)}</p>
                        <p>Tải lên: ${formatDate(document.upload_date)}</p>
                        <div class="alert alert-info">
                            Không thể xem trước loại tài liệu này. Vui lòng tải xuống để xem.
                        </div>
                    `);
                    
                previewContent.append(fileInfoElement);
            }
        } else {
            // If file type is unknown
            previewContent.html('<div class="alert alert-warning">Không thể xác định loại tài liệu.</div>');
        }
        
        // Show the modal
        $('#documentPreviewModal').modal('show');
    }
    
    // Upload document
    function uploadDocument() {
        const patientId = $('#patient-select').val();
        const documentTypeId = $('#document-type-select').val();
        const description = $('#document-description').val();
        const file = $('#document-file')[0].files[0];
        
        // Validate inputs
        if (!patientId) {
            showAlert('danger', 'Vui lòng chọn bệnh nhân');
            return;
        }
        
        if (!file) {
            showAlert('danger', 'Vui lòng chọn tệp tài liệu');
            return;
        }
        
        // Validate file type
        const allowedExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', 
                                 '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf', '.csv', '.zip'];
        const fileName = file.name.toLowerCase();
        const fileExt = '.' + fileName.split('.').pop();
        
        if (!allowedExtensions.includes(fileExt)) {
            showAlert('danger', `Định dạng tệp không được hỗ trợ. Vui lòng chọn: ${allowedExtensions.join(', ')}`);
            return;
        }
        
        // Validate file size (max 20MB)
        const maxSize = 20 * 1024 * 1024; // 20MB in bytes
        if (file.size > maxSize) {
            showAlert('danger', 'Kích thước tệp không được vượt quá 20MB');
            return;
        }
        
        // Create form data
        const formData = new FormData();
        formData.append('patient_id', patientId);
        formData.append('file', file);
        
        if (documentTypeId) {
            formData.append('document_type_id', documentTypeId);
        }
        
        if (description) {
            formData.append('description', description);
        }
        
        // Show loading overlay
        $('#loading-overlay').show();
        
        // Submit the form
        $.ajax({
            url: '/api/patient_documents',
            method: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
                // Hide the modal
                $('#uploadDocumentModal').modal('hide');
                
                // Reset form
                $('#upload-document-form')[0].reset();
                $('#file-name').text('');
                
                // Reload documents data
                loadDocumentsData();
                
                // Show success message
                showAlert('success', 'Tài liệu đã được tải lên thành công');
            },
            error: function(xhr, status, error) {
                $('#loading-overlay').hide();
                console.error('Error uploading document:', error);
                showAlert('danger', 'Lỗi khi tải lên tài liệu: ' + (xhr.responseJSON?.error || error));
            }
        });
    }
    
    // Delete document
    function deleteDocument(documentId) {
        // Show loading overlay
        $('#loading-overlay').show();
        
        // Hide the modal
        $('#deleteDocumentModal').modal('hide');
        
        $.ajax({
            url: `/api/patient_documents/${documentId}`,
            method: 'DELETE',
            success: function(response) {
                // Reload documents data
                loadDocumentsData();
                
                // Show success message
                showAlert('success', 'Tài liệu đã được xóa thành công');
            },
            error: function(xhr, status, error) {
                $('#loading-overlay').hide();
                console.error('Error deleting document:', error);
                showAlert('danger', 'Lỗi khi xóa tài liệu: ' + (xhr.responseJSON?.error || error));
            }
        });
    }
    
    // Update file name display
    function updateFileName() {
        const fileName = $('#document-file')[0].files[0]?.name || '';
        $('#file-name').text(fileName ? `File: ${fileName}` : '');
    }
    
    // Helper function to format file size
    function formatFileSize(bytes) {
        if (!bytes || bytes === 0) return 'N/A';
        
        const units = ['B', 'KB', 'MB', 'GB'];
        let size = bytes;
        let unitIndex = 0;
        
        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }
        
        return `${size.toFixed(1)} ${units[unitIndex]}`;
    }
    
    // Helper function to format date
    function formatDate(dateString) {
        if (!dateString) return 'N/A';
        
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return dateString;
        
        return date.toLocaleDateString('vi-VN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    // Helper function to format file type
    function formatFileType(mimeType) {
        if (!mimeType) return 'N/A';
        
        // Map common MIME types to user-friendly names
        const mimeTypeMap = {
            'application/pdf': 'PDF',
            'image/jpeg': 'JPEG Image',
            'image/png': 'PNG Image',
            'image/gif': 'GIF Image',
            'image/bmp': 'BMP Image',
            'image/tiff': 'TIFF Image',
            'application/msword': 'Word Document',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word Document',
            'application/vnd.ms-excel': 'Excel Spreadsheet',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Excel Spreadsheet',
            'application/vnd.ms-powerpoint': 'PowerPoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'PowerPoint',
            'text/plain': 'Text Document',
            'application/zip': 'ZIP Archive',
            'application/x-rar-compressed': 'RAR Archive',
            'application/x-7z-compressed': 'Archive',
            'video/mp4': 'MP4 Video',
            'video/quicktime': 'Video',
            'audio/mpeg': 'Audio'
        };
        
        return mimeTypeMap[mimeType] || mimeType;
    }
    
    // Helper function to get file icon class
    function getFileIcon(mimeType) {
        if (!mimeType) return 'fa-file';
        
        if (mimeType.startsWith('image/')) {
            return 'fa-file-image';
        } else if (mimeType.includes('pdf')) {
            return 'fa-file-pdf';
        } else if (mimeType.includes('word') || mimeType.includes('document')) {
            return 'fa-file-word';
        } else if (mimeType.includes('excel') || mimeType.includes('sheet')) {
            return 'fa-file-excel';
        } else if (mimeType.includes('powerpoint') || mimeType.includes('presentation')) {
            return 'fa-file-powerpoint';
        } else if (mimeType.startsWith('video/')) {
            return 'fa-file-video';
        } else if (mimeType.startsWith('audio/')) {
            return 'fa-file-audio';
        } else if (mimeType.includes('zip') || mimeType.includes('compressed') || mimeType.includes('archive')) {
            return 'fa-file-archive';
        } else if (mimeType.includes('text')) {
            return 'fa-file-alt';
        } else {
            return 'fa-file';
        }
    }
    
    // Helper function to show alerts
    function showAlert(type, message) {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        // Insert alert at the top of the container
        const firstElement = $('.container-fluid').children().first();
        $(alertHtml).insertBefore(firstElement);
        
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            $('.alert').alert('close');
        }, 5000);
    }
});
