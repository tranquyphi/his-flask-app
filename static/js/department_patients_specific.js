// Department Patients Specific - Authorized Staff View
$(document).ready(function() {
    console.log('Department Patients Specific script loaded');
    console.log('Department ID:', DEPARTMENT_ID);
    
    let patientsTable = null;
    let currentPatientId = null;
    
    // Automatically load department data on page load
    loadDepartmentData();
    
    // Handle image upload button click
    $('#upload-image-btn').on('click', function() {
        $('#patient-image-upload').click();
    });
    
    // Handle image container click to also trigger file upload
    $('.patient-image-container').on('click', function() {
        $('#patient-image-upload').click();
    });
    
    // Handle file selection with improved feedback
    $('#patient-image-upload').on('change', function() {
        if (this.files && this.files[0] && currentPatientId) {
            const file = this.files[0];
            
            // Show filename feedback
            showAlert(`Đã chọn tệp: ${file.name} (${Math.round(file.size/1024)} KB)`, 'info');
            
            // Process upload using patient documents API
            uploadPatientDocument(currentPatientId, file);
        }
    });
    
    // Event handlers
    $('#search-patient').on('keyup', function() {
        if (patientsTable) {
            patientsTable.search($(this).val()).draw();
        }
    });
    
        // When the patient modal is hidden, refresh the table image
    $('#patientModal').on('hidden.bs.modal', function() {
        // Only refresh if we have a currentPatientId
        if (currentPatientId) {
            // Refresh the specific patient thumbnail in the table
            const $thumbnail = $(`.patient-thumbnail[data-patient-id="${currentPatientId}"]`);
            if ($thumbnail.length > 0) {
                loadPatientThumbnails();
            }
        }
    });
    
        $('#sort-by').on('change', function() {
        if (patientsTable) {
            const sortCol = $(this).val();
            let colIndex = 1; // Default to patient name
            let direction = 'asc';
            
            switch(sortCol) {
                case 'PatientName': 
                    colIndex = 1; // Patient name column index
                    direction = 'asc';
                    break;
                case 'PatientAge': 
                    colIndex = 2; // Age column index
                    direction = 'asc';
                    break;
                case 'DaysAdmitted': 
                    colIndex = 3; // Days admitted column index
                    direction = 'desc'; // Higher days first
                    break;
                case 'At': 
                    // This is no longer a visible column, but we can sort by data
                    patientsTable.order({
                        column: 'At',
                        dir: 'desc'
                    }).draw();
                    return;
            }
            
            patientsTable.order(colIndex, direction).draw();
        }
    });
    
    $('#export-data').on('click', function() {
        exportToExcel();
    });
    
    function loadDepartmentData() {
        console.log('Loading data for department:', DEPARTMENT_ID);
        
        // Show loading overlay
        $('#loading-overlay').show();
        
        // Load department data and statistics
        Promise.all([
            $.get(`/api/department_patients/${DEPARTMENT_ID}`),
            $.get(`/api/department_stats/${DEPARTMENT_ID}`)
        ])
        .then(function(responses) {
            const [patientsResponse, statsResponse] = responses;
            
            console.log('Patients data:', patientsResponse);
            console.log('Stats data:', statsResponse);
            
            // Update department header
            updateDepartmentHeader(patientsResponse.department);
            
            // Update statistics
            updateStatistics(statsResponse);
            
            // Initialize patients table
            initializePatientsTable(patientsResponse.patients);
            
            // Update last updated time
            updateLastUpdated();
            
            // Hide loading overlay
            $('#loading-overlay').hide();
            
            // Show appropriate content
            if (patientsResponse.patients.length === 0) {
                showEmptyState();
            } else {
                showDataSections();
            }
        })
        .catch(function(error) {
            console.error('Error loading department data:', error);
            $('#loading-overlay').hide();
            showErrorState(error);
        });
    }
    
    function updateDepartmentHeader(department) {
        $('#department-name').text(department.DepartmentName);
        $('#department-type').text(department.DepartmentType || 'Khoa chuyên môn');
    }
    
    function updateStatistics(stats) {
        $('#current-count').text(stats.current_patients || 0);
        $('#recent-count').text(stats.recent_admissions || 0);
        $('#total-count').text(stats.total_patients || 0);
    }
    
    function updateLastUpdated() {
        const now = new Date();
        $('#last-updated').text(now.toLocaleString('vi-VN'));
    }
    
    function initializePatientsTable(patients) {
        console.log('Initializing table with', patients.length, 'patients');
        
        // Destroy existing table if it exists
        if (patientsTable) {
            patientsTable.destroy();
        }
        
        // Calculate days since admission for each patient
        const processedPatients = patients.map(patient => {
            if (patient.At) {
                const admissionDate = new Date(patient.At);
                const today = new Date();
                const daysDiff = Math.floor((today - admissionDate) / (1000 * 60 * 60 * 24));
                patient.DaysAdmitted = daysDiff;
            } else {
                patient.DaysAdmitted = 0;
            }
            return patient;
        });
        
        patientsTable = $('#department-patients-table').DataTable({
            data: processedPatients,
            destroy: true,
            columns: [
                {
                    data: 'PatientId',
                    title: 'Ảnh',
                    orderable: false,
                    render: function(data, type, row) {
                        if (type === 'sort' || type === 'type') {
                            return '';
                        }
                        
                        const patientId = row.PatientId;
                        
                        // Generate thumbnail HTML using patient documents API
                        return `
                            <div class="d-flex justify-content-center">
                                <div class="patient-row-image" data-patient-id="${patientId}" style="width: 40px; height: 40px; border-radius: 50%; overflow: hidden; background-color: #f5f5f5; position: relative;">
                                    <img src="/static/images/default-patient.png" 
                                         class="patient-thumbnail" 
                                         data-patient-id="${patientId}"
                                         style="width: 100%; height: 100%; object-fit: cover; cursor: pointer;" 
                                         alt="Patient ${patientId}"
                                         onload="console.log('Default image loaded for patient ${patientId}')"
                                         onerror="console.error('Failed to load image for patient ${patientId}'); this.src='/static/images/default-patient.png'" />
                                </div>
                            </div>
                        `;
                    }
                },
                { 
                    data: 'PatientName',
                    title: 'Họ tên',
                    render: function(data, type, row) {
                        if (type === 'sort' || type === 'type') {
                            return data || '';
                        }
                        // Include PatientId as a badge after patient name
                        return `<strong>${data || 'N/A'}</strong>
                                <span class="badge bg-light text-dark ms-1" title="Mã BN">${row.PatientId}</span>`;
                    }
                },
                { 
                    data: 'PatientAge',
                    title: 'Tuổi',
                    render: function(data, type, row) {
                        if (type === 'sort' || type === 'type') {
                            return parseInt(data) || 0;
                        }
                        // Include gender icon alongside age for compact display
                        let genderIcon = '';
                        if (row.PatientGender) {
                            const genderIcons = {
                                'Nam': '<i class="fas fa-mars text-primary" title="Nam" style="font-size: 0.9em; margin-left: 5px;"></i>',
                                'Nữ': '<i class="fas fa-venus text-danger" title="Nữ" style="font-size: 0.9em; margin-left: 5px;"></i>',
                                'Khác': '<i class="fas fa-genderless text-secondary" title="Khác" style="font-size: 0.9em; margin-left: 5px;"></i>'
                            };
                            genderIcon = genderIcons[row.PatientGender] || '';
                        }
                        return data ? `${data} tuổi ${genderIcon}` : `N/A ${genderIcon}`;
                    }
                },
                {
                    data: 'DaysAdmitted',
                    title: 'Số ngày nằm',
                    render: function(data, type, row) {
                        if (type === 'sort' || type === 'type') {
                            return data || 0;
                        }
                        
                        let badgeClass = 'bg-success';
                        let icon = 'fas fa-calendar-check';
                        
                        if (data > 14) {
                            badgeClass = 'bg-danger';
                            icon = 'fas fa-exclamation-triangle';
                        } else if (data > 7) {
                            badgeClass = 'bg-warning';
                            icon = 'fas fa-clock';
                        }
                        
                        return `<span class="badge ${badgeClass}">
                                    <i class="${icon}"></i> ${data} ngày
                                </span>`;
                    }
                },
                {
                    data: null,
                    title: 'Thao tác',
                    orderable: false,
                    render: function(data, type, row) {
                        return `
                            <div class="btn-group btn-group-sm">
                                <button class="btn btn-outline-primary btn-sm view-btn" 
                                        data-patient='${JSON.stringify(row)}' 
                                        title="Xem chi tiết">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn btn-outline-info btn-sm visits-btn" 
                                        data-patient-id="${row.PatientId}" 
                                        title="Xem lượt khám">
                                    <i class="fas fa-calendar-check"></i>
                                </button>
                                <button class="btn btn-outline-success btn-sm edit-btn" 
                                        data-patient-id="${row.PatientId}" 
                                        title="Chỉnh sửa">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-outline-secondary btn-sm history-btn" 
                                        data-patient-id="${row.PatientId}" 
                                        title="Lịch sử điều trị">
                                    <i class="fas fa-history"></i>
                                </button>
                                <button class="btn btn-outline-warning btn-sm discharge-btn" 
                                        data-patient-id="${row.PatientId}" 
                                        title="Xuất viện">
                                    <i class="fas fa-sign-out-alt"></i>
                                </button>
                            </div>
                        `;
                    }
                }
            ],
            pageLength: 20,
            responsive: false, // Disable responsive behavior
            scrollX: true,     // Enable horizontal scrolling
            scrollCollapse: true,
            order: [1, 'asc'], // Order by patient name ascending
            searching: true,
            autoWidth: false,
            columnDefs: [
                { targets: 0, width: '60px', className: 'text-center' },  // Image column
                { targets: 1, width: '200px' },  // Patient Name
                { targets: 2, width: '100px' },  // Age with gender icon
                { targets: 3, width: '100px' },  // Days admitted
                { targets: 4, width: '160px', className: 'text-nowrap' }  // Actions
            ],
            language: {
                emptyTable: "Không có bệnh nhân nào đang nằm viện",
                search: "Tìm kiếm:",
                lengthMenu: "Hiển thị _MENU_ bệnh nhân mỗi trang",
                zeroRecords: "Không tìm thấy bệnh nhân nào",
                info: "Hiển thị _START_ đến _END_ trong tổng số _TOTAL_ bệnh nhân",
                infoEmpty: "Hiển thị 0 đến 0 trong tổng số 0 bệnh nhân",
                infoFiltered: "(lọc từ _MAX_ tổng số bệnh nhân)",
                paginate: {
                    first: "Đầu",
                    last: "Cuối",
                    next: "Tiếp",
                    previous: "Trước"
                }
            }
        });
        
        console.log('DataTable initialized successfully with', processedPatients.length, 'patients');
        
        // Add event handlers for table buttons
        $('#department-patients-table tbody').on('click', '.view-btn', function() {
            const patientData = $(this).data('patient');
            showPatientDetails(patientData);
        });
        
        // Add click handler for patient thumbnails (also open details)
        $('#department-patients-table tbody').on('click', '.patient-row-image', function() {
            const patientId = $(this).data('patient-id');
            // Find the related view button and trigger its click event
            $(this).closest('tr').find('.view-btn').click();
        });
        
        // Load thumbnails for all patients after table is initialized
        loadPatientThumbnails();
        
        $('#department-patients-table tbody').on('click', '.visits-btn', function() {
            const patientId = $(this).data('patient-id');
            viewPatientVisits(patientId);
        });
        
        $('#department-patients-table tbody').on('click', '.edit-btn', function() {
            const patientId = $(this).data('patient-id');
            editPatient(patientId);
        });
        
        $('#department-patients-table tbody').on('click', '.history-btn', function() {
            const patientId = $(this).data('patient-id');
            showPatientHistory(patientId);
        });
        
        $('#department-patients-table tbody').on('click', '.discharge-btn', function() {
            const patientId = $(this).data('patient-id');
            dischargePatient(patientId);
        });
    }
    
    function showDataSections() {
        $('#table-section').removeClass('d-none');
        $('#search-section').removeClass('d-none');
        $('#empty-state').addClass('d-none');
        $('#error-state').addClass('d-none');
    }
    
    function showEmptyState() {
        $('#table-section').addClass('d-none');
        $('#search-section').addClass('d-none');
        $('#empty-state').removeClass('d-none');
        $('#error-state').addClass('d-none');
    }
    
    function showErrorState(error) {
        $('#table-section').addClass('d-none');
        $('#search-section').addClass('d-none');
        $('#empty-state').addClass('d-none');
        $('#error-state').removeClass('d-none');
        
        let errorMessage = 'Không thể tải dữ liệu khoa. Vui lòng thử lại.';
        if (error.status === 404) {
            errorMessage = 'Khoa không tồn tại hoặc bạn không có quyền truy cập.';
        } else if (error.status === 403) {
            errorMessage = 'Bạn không có quyền truy cập vào khoa này.';
        }
        
        $('#error-message').text(errorMessage);
    }
    
    function showPatientDetails(patient) {
        $('#modal-patient-id').text(patient.PatientId);
        $('#modal-patient-name').text(patient.PatientName || 'N/A');
        $('#modal-patient-age').text(patient.PatientAge ? `${patient.PatientAge} tuổi` : 'N/A');
        $('#modal-patient-gender').text(patient.PatientGender || 'N/A');
        $('#modal-patient-phone').text(patient.PatientPhone || 'Chưa có');
        $('#modal-patient-address').text(patient.PatientAddress || 'Chưa có thông tin');
        $('#modal-patient-cccd').text(patient.PatientCCCD || 'Chưa có');
        $('#modal-patient-relative').text(patient.PatientRelative || 'Chưa có');
        $('#modal-patient-bhyt').text(patient.PatientBHYT || 'Chưa có');
        $('#modal-patient-bhyt-valid').text(patient.PatientBHYTValid || 'Chưa có');
        $('#modal-patient-allergy').text(patient.Allergy || 'Không có');
        $('#modal-patient-history').text(patient.History || 'Không có');
        $('#modal-patient-note').text(patient.PatientNote || 'Không có');
        
        // Set the current patient ID for image upload
        currentPatientId = patient.PatientId;
        
        // Set the patient ID on the modal image and load it
        $('#modal-patient-image').attr('data-patient-id', patient.PatientId);
        loadPatientDocumentImage(patient.PatientId);
        
        if (patient.At) {
            const admissionDate = new Date(patient.At);
            $('#modal-admission-date').text(admissionDate.toLocaleDateString('vi-VN') + ' ' + 
                                          admissionDate.toLocaleTimeString('vi-VN'));
        } else {
            $('#modal-admission-date').text('N/A');
        }
        
        $('#modal-days-admitted').text(patient.DaysAdmitted ? `${patient.DaysAdmitted} ngày` : '0 ngày');
        
        $('#patientModal').modal('show');
    }
    
    function editPatient(patientId) {
        // Redirect to patient departments page with filter
        window.location.href = `/patient_departments?patient=${patientId}`;
    }
    
    function viewPatientVisits(patientId) {
        // Redirect to patient visits page
        window.location.href = `/patient-visits/${patientId}`;
    }
    
    function showPatientHistory(patientId) {
        showAlert('Tính năng lịch sử điều trị sẽ được phát triển trong phiên bản tiếp theo', 'info');
    }
    
    function dischargePatient(patientId) {
        if (confirm('Bạn có chắc chắn muốn xuất viện cho bệnh nhân này?')) {
            // In a real application, this would call an API to discharge the patient
            showAlert('Tính năng xuất viện sẽ được phát triển trong phiên bản tiếp theo', 'warning');
        }
    }
    
    function exportToExcel() {
        if (patientsTable) {
            // Get current table data
            const data = patientsTable.data().toArray();
            showAlert('Tính năng xuất Excel sẽ được phát triển trong phiên bản tiếp theo', 'info');
        }
    }
    
    function showAlert(message, type = 'info') {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        // Remove existing alerts
        $('.alert').remove();
        
        // Add new alert at top of container
        $('.container-fluid').prepend(alertHtml);
        
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            $('.alert').alert('close');
        }, 5000);
    }
    
    // Global function to refresh data
    window.refreshData = function() {
        loadDepartmentData();
    };
    
    // Function to load patient document image (chân dung) with loading indicator
    function loadPatientDocumentImage(patientId) {
        console.log('Loading patient document image for patient:', patientId);
        
        // Show loading spinner
        $('#modal-patient-image').css('opacity', '0.6');
        
        // First, remove any existing spinners to avoid duplicates
        $('.modal-image-spinner').remove();
        
        // Add loading indicator to the specific container that holds the modal patient image
        $('#modal-patient-image').parent().append(
            '<div class="modal-image-spinner position-absolute top-50 start-50 translate-middle">' +
            '<div class="spinner-border text-primary" role="status" style="width: 1.5rem; height: 1.5rem;">' +
            '<span class="visually-hidden">Loading...</span></div></div>'
        );
        
        // Get patient documents to find the image (DocumentTypeId=1)
        $.ajax({
            url: `/api/patients/${patientId}/documents`,
            type: 'GET',
            success: function(response) {
                console.log('Patient documents response:', response);
                
                // Find the portrait document (DocumentTypeId=1)
                let portraitDocument = null;
                if (response.patient_documents && response.patient_documents.length > 0) {
                    portraitDocument = response.patient_documents.find(doc => 
                        doc.DocumentTypeId == 1 && doc.file_type && doc.file_type.startsWith('image/')
                    );
                }
                
                // Remove loading spinner
                $('.modal-image-spinner').remove();
                
                if (portraitDocument) {
                    // Load the document thumbnail
                    const thumbnailUrl = `/api/patient_documents/${portraitDocument.DocumentId}/thumbnail?t=${new Date().getTime()}`;
                    $('#modal-patient-image').attr('src', thumbnailUrl).css('opacity', '1');
                } else {
                    // No portrait found, use default image
                    $('#modal-patient-image').attr('src', '/static/images/default-patient.png').css('opacity', '1');
                }
            },
            error: function(xhr, status, error) {
                console.error('Failed to load patient documents:', error);
                
                // Remove loading spinner
                $('.modal-image-spinner').remove();
                
                // Use default image on error
                $('#modal-patient-image').attr('src', '/static/images/default-patient.png').css('opacity', '1');
            }
        });
    }
    
    // Function to upload patient document (image) as DocumentTypeId=1
    function uploadPatientDocument(patientId, imageFile) {
        console.log('Starting patient document upload for patient:', patientId);
        
        // Validate file type
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
        if (!allowedTypes.includes(imageFile.type)) {
            showAlert('Chỉ hỗ trợ tệp hình ảnh (JPEG, PNG, GIF)', 'warning');
            return;
        }
        
        // Validate file size (max 5MB)
        const maxSize = 5 * 1024 * 1024;
        if (imageFile.size > maxSize) {
            showAlert('Kích thước tệp không được vượt quá 5MB', 'warning');
            return;
        }
        
        // Show loading state
        const $uploadBtn = $('#upload-image-btn');
        const originalBtnText = $uploadBtn.html();
        $uploadBtn.html('<i class="fas fa-spinner fa-spin"></i> Đang tải...').prop('disabled', true);
        
        // Create form data
        const formData = new FormData();
        formData.append('patient_id', patientId);
        formData.append('document_type_id', '1'); // DocumentTypeId=1 for "Chân dung"
        formData.append('file', imageFile);
        formData.append('description', 'Ảnh chân dung bệnh nhân');
        
        // Upload to patient documents API
        $.ajax({
            url: '/api/patient_documents',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
                console.log('Document upload successful:', response);
                showAlert('Ảnh chân dung đã được cập nhật thành công', 'success');
                
                // Reload patient image in modal
                loadPatientDocumentImage(patientId);
                
                // Update thumbnail in table
                loadPatientThumbnails();
                
                // Reset file input
                $('#patient-image-upload').val('');
            },
            error: function(xhr, status, error) {
                console.error('Document upload failed:', xhr.responseText);
                let errorMessage = 'Lỗi khi tải lên ảnh chân dung';
                
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMessage = xhr.responseJSON.error;
                }
                
                showAlert(errorMessage, 'danger');
            },
            complete: function() {
                // Restore button state
                $uploadBtn.html(originalBtnText).prop('disabled', false);
            }
        });
    }
    // Global function for modal edit button
    window.editPatient = function() {
        const patientId = $('#modal-patient-id').text();
        $('#patientModal').modal('hide');
        editPatient(patientId);
    };
    
    // Auto-refresh every 5 minutes
    setInterval(function() {
        console.log('Auto-refreshing department data...');
        loadDepartmentData();
    }, 5 * 60 * 1000);
    
    // Function to load all patient thumbnails in the table using documents API
    function loadPatientThumbnails() {
        console.log('Loading patient thumbnails for table rows...');
        
        // Find all patient thumbnail images in the table
        $('.patient-thumbnail').each(function() {
            const $img = $(this);
            const patientId = $img.data('patient-id');
            
            if (!patientId) {
                console.log('No patient ID found for thumbnail, setting default');
                $img.attr('src', '/static/images/default-patient.png');
                return;
            }
            
            console.log(`Loading thumbnail for patient ${patientId}`);
            
            // Load patient documents to find portrait
            $.ajax({
                url: `/api/patients/${patientId}/documents`,
                type: 'GET',
                success: function(response) {
                    console.log(`Documents response for patient ${patientId}:`, response);
                    
                    // Find the portrait document (DocumentTypeId=1)
                    let portraitDocument = null;
                    if (response.patient_documents && response.patient_documents.length > 0) {
                        portraitDocument = response.patient_documents.find(doc => 
                            doc.DocumentTypeId == 1 && doc.file_type && doc.file_type.startsWith('image/')
                        );
                    }
                    
                    if (portraitDocument) {
                        // Load the document thumbnail
                        console.log(`Found portrait document ${portraitDocument.DocumentId} for patient ${patientId}`);
                        const thumbnailUrl = `/api/patient_documents/${portraitDocument.DocumentId}/thumbnail?t=${new Date().getTime()}`;
                        $img.attr('src', thumbnailUrl);
                    } else {
                        // No portrait found, set default image explicitly
                        console.log(`No portrait document found for patient ${patientId}, using default`);
                        $img.attr('src', '/static/images/default-patient.png');
                    }
                },
                error: function(xhr, status, error) {
                    console.error(`Failed to load documents for patient ${patientId}:`, error);
                    // Set default image on error
                    $img.attr('src', '/static/images/default-patient.png');
                }
            });
        });
    }
    
    // The updatePatientTableImage function has been replaced by PatientImageUtils.uploadPatientImage
    
    // All camera-related functions have been removed for simplicity and reliability
    // The system now only supports file upload functionality
});
