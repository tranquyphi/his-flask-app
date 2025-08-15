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
            
            // Process upload
            uploadPatientImage(currentPatientId, file);
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
            // Find the patient's row and update its image from the server
            const $tableImage = $(`.patient-thumbnail[data-patient-id="${currentPatientId}"]`);
            if ($tableImage.length > 0) {
                // Force reload from server with cache-busting
                const imageUrl = `/api/patient/image/${currentPatientId}?refresh=${new Date().getTime()}`;
                
                // Create a new image to check if it exists
                const img = new Image();
                img.onload = function() {
                    $tableImage.attr('src', this.src);
                };
                img.onerror = function() {
                    // Keep default image
                    $tableImage.attr('src', '/static/images/default-patient.png');
                };
                img.src = imageUrl;
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
                    colIndex = 1; // Updated index for patient name
                    direction = 'asc';
                    break;
                case 'PatientAge': 
                    colIndex = 2; // Updated index for patient age
                    direction = 'asc';
                    break;
                case 'DaysAdmitted': 
                    colIndex = 4; // Updated index for days admitted
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
                        const imageUrl = `/api/patient/image/${patientId}`;
                        
                        return `
                            <div class="d-flex justify-content-center">
                                <div class="patient-row-image" data-patient-id="${patientId}" style="width: 40px; height: 40px; border-radius: 50%; overflow: hidden; background-color: #f5f5f5; position: relative;">
                                    <img src="/static/images/default-patient.png" 
                                         data-patient-id="${patientId}"
                                         class="patient-thumbnail" 
                                         style="width: 100%; height: 100%; object-fit: cover;" 
                                         alt="Patient" 
                                         onerror="this.onerror=null; this.src='/static/images/default-patient.png';">
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
                        return data ? `${data} tuổi` : 'N/A';
                    }
                },
                { 
                    data: 'PatientGender',
                    title: 'Giới tính',
                    render: function(data, type, row) {
                        if (type === 'sort' || type === 'type') {
                            return data || '';
                        }
                        
                        if (!data) return '';
                        const genderIcons = {
                            'Nam': '<i class="fas fa-mars text-primary" title="Nam" style="font-size: 1.2em;"></i>',
                            'Nữ': '<i class="fas fa-venus text-danger" title="Nữ" style="font-size: 1.2em;"></i>',
                            'Khác': '<i class="fas fa-genderless text-secondary" title="Khác" style="font-size: 1.2em;"></i>'
                        };
                        return genderIcons[data] || `<span class="text-muted">${data}</span>`;
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
                { targets: 2, width: '80px' },   // Age
                { targets: 3, width: '80px' },   // Gender
                { targets: 4, width: '100px' },  // Days admitted
                { targets: 5, width: '160px', className: 'text-nowrap' }  // Actions
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
        
        // Load patient image
        loadPatientImage(patient.PatientId);
        
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
    
    // Function to load patient image with loading indicator
    function loadPatientImage(patientId) {
        // Show loading spinner
        $('#modal-patient-image').css('opacity', '0.6');
        const originalImage = $('#modal-patient-image').attr('src');
        
        // Add loading indicator
        $('.patient-image-container').append(
            '<div id="image-loading-spinner" class="position-absolute top-50 start-50 translate-middle">' +
            '<div class="spinner-border text-primary" role="status" style="width: 1.5rem; height: 1.5rem;">' +
            '<span class="visually-hidden">Loading...</span></div></div>'
        );
        
        // Try to load the patient's image
        const imageUrl = `/api/patient/image/${patientId}`;
        
        // Create a new image object to test loading
        const img = new Image();
        img.onload = function() {
            // Remove loading spinner
            $('#image-loading-spinner').remove();
            // Show the loaded image
            $('#modal-patient-image').attr('src', this.src).css('opacity', '1');
        };
        
        img.onerror = function() {
            // Remove loading spinner
            $('#image-loading-spinner').remove();
            // Keep the default image
            $('#modal-patient-image').css('opacity', '1');
            console.log('No custom image available for patient, using default');
        };
        
        // Use the Image object's onload/onerror events to check for image existence
        // This avoids 404 errors in console
        img.src = `${imageUrl}?t=${new Date().getTime()}`;
        
        // Note: We don't need the fetch() call anymore since the Image object
        // will handle loading and errors through its event handlers
    }
    
    // Function to upload patient image with preview
    function uploadPatientImage(patientId, imageFile) {
        console.log('Starting upload for patient:', patientId);
        console.log('Image file:', imageFile.name, 'Size:', imageFile.size, 'Type:', imageFile.type);
        
        // Check if file is valid
        if (!imageFile || imageFile.size === 0) {
            console.error('Invalid image file:', imageFile);
            showAlert('Tệp ảnh không hợp lệ hoặc trống.', 'danger');
            return;
        }
        
        // Check file size (max 5MB)
        if (imageFile.size > 5 * 1024 * 1024) {
            console.error('File too large:', imageFile.size);
            showAlert('Tệp ảnh quá lớn. Giới hạn tối đa 5MB.', 'warning');
            return;
        }
        
        // Check file type
        const validImageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/jpg'];
        if (!validImageTypes.includes(imageFile.type)) {
            console.error('Invalid file type:', imageFile.type);
            showAlert('Định dạng tệp không hợp lệ. Vui lòng sử dụng JPG, PNG hoặc GIF.', 'warning');
            return;
        }
        
        // Show preview before upload
        const reader = new FileReader();
        reader.onload = function(e) {
            // Update the image in the modal
            $('#modal-patient-image').attr('src', e.target.result);
            
            // Proceed with upload
            const formData = new FormData();
            formData.append('image', imageFile);
            
            // Show loading state on upload button
            $('#upload-image-btn').prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i>');
            
            $.ajax({
                url: `/api/patient/image/${patientId}`,
                type: 'POST',
                data: formData,
                contentType: false,
                processData: false,
                beforeSend: function() {
                    console.log('Sending upload request...');
                },
                success: function(response) {
                    console.log('Upload successful:', response);
                    showAlert('Hình ảnh bệnh nhân đã được cập nhật', 'success');
                    
                    // Update the image in the table as well
                    updatePatientTableImage(patientId, imageFile);
                },
                error: function(xhr, status, error) {
                    console.error('Error uploading image:', error);
                    console.error('Status:', status);
                    console.error('Response:', xhr.responseText);
                    showAlert('Lỗi khi tải lên hình ảnh. Vui lòng thử lại', 'danger');
                    // Reload original image on error
                    loadPatientImage(patientId);
                },
                complete: function() {
                    // Reset upload button
                    $('#upload-image-btn').prop('disabled', false).html('<i class="fas fa-upload"></i> Tải ảnh');
                    $('#patient-image-upload').val(''); // Reset file input
                    console.log('Upload request completed');
                }
            });
        };
        
        // Read the image file
        reader.readAsDataURL(imageFile);
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
    
    // Function to load all patient thumbnails in the table
    function loadPatientThumbnails() {
        console.log('Loading patient thumbnails for table rows...');
        
        // Use a custom image checker function to avoid console errors
        $('.patient-thumbnail').each(function() {
            const patientId = $(this).data('patient-id');
            const imageUrl = `/api/patient/image/${patientId}`;
            const img = $(this);
            
            // Create a new Image object to check if the image exists without generating 404 errors in console
            const imageChecker = new Image();
            
            // Define what happens on successful load
            imageChecker.onload = function() {
                // Add cache-busting parameter to avoid browser caching
                img.attr('src', `${imageUrl}?t=${new Date().getTime()}`);
            };
            
            // Define what happens on error (just use default image, which is already set)
            imageChecker.onerror = function() {
                // Keep default image, which is already set in the HTML
                // No console error needed since this is an expected condition
                console.log(`Patient ${patientId} has no custom image, using default`);
            };
            
            // Start loading the image (with cache-busting to ensure fresh check)
            imageChecker.src = `${imageUrl}?check=${new Date().getTime()}`;
        });
    }
    
    // Function to update patient's image in the table after upload
    function updatePatientTableImage(patientId, imageFile) {
        console.log('Updating patient table image for patient:', patientId);
        
        // Find the patient's image in the table
        const $tableImage = $(`.patient-thumbnail[data-patient-id="${patientId}"]`);
        
        if ($tableImage.length > 0) {
            // Create a temporary URL for the uploaded file
            const tempUrl = URL.createObjectURL(imageFile);
            
            // Update the image source with the new image
            $tableImage.attr('src', tempUrl);
            
            // Clean up the temporary URL when the image is loaded
            $tableImage.on('load', function() {
                URL.revokeObjectURL(tempUrl);
                
                // After a short delay (to allow the modal to close), add a highlight effect
                setTimeout(function() {
                    const $container = $tableImage.parent();
                    $container.css('border-color', '#28a745');
                    $container.animate({borderWidth: '3px'}, 300)
                             .animate({borderWidth: '2px'}, 300);
                }, 500);
            });
            
            console.log('Table image updated successfully');
        } else {
            console.log('Could not find patient image in table to update');
        }
    }
    
    // All camera-related functions have been removed for simplicity and reliability
    // The system now only supports file upload functionality
});
