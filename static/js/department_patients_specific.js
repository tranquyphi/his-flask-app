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
            // Use the utility to update all images of this patient
            PatientImageUtils.loadAllPatientImages(`.patient-image[data-patient-id="${currentPatientId}"]`);
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
                        
                        // Use the patient image utility to generate the HTML
                        return `
                            <div class="d-flex justify-content-center">
                                <div class="patient-row-image" data-patient-id="${patientId}" style="width: 40px; height: 40px; border-radius: 50%; overflow: hidden; background-color: #f5f5f5; position: relative;">
                                    ${PatientImageUtils.getPatientImageHtml(patientId, 'thumbnail', {
                                        imageClass: 'patient-thumbnail'
                                    }).trim()}
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
        
        // First, remove any existing spinners to avoid duplicates
        $('.modal-image-spinner').remove();
        
        // Add loading indicator to the specific container that holds the modal patient image
        // Using a unique class name for the spinner to make it easier to select later
        $('#modal-patient-image').parent().append(
            '<div class="modal-image-spinner position-absolute top-50 start-50 translate-middle">' +
            '<div class="spinner-border text-primary" role="status" style="width: 1.5rem; height: 1.5rem;">' +
            '<span class="visually-hidden">Loading...</span></div></div>'
        );
        
        // Use the utility to load the patient image
        PatientImageUtils.loadPatientImage(patientId, '#modal-patient-image', 
            // Success callback
            function($img) {
                // Remove loading spinner for this specific image
                $('.modal-image-spinner').remove();
                // Show the loaded image
                $img.css('opacity', '1');
            },
            // Error callback
            function($img) {
                // Remove loading spinner for this specific image
                $('.modal-image-spinner').remove();
                // Keep the default image
                $img.css('opacity', '1');
            }
        );
    }
    
    // Function to upload patient image with preview
    function uploadPatientImage(patientId, imageFile) {
        // Use the utility to handle image upload
        PatientImageUtils.uploadPatientImage(patientId, imageFile, {
            // Configure preview element
            previewElement: '#modal-patient-image',
            
            // Configure loading button
            loadingElement: '#upload-image-btn',
            loadingElementContent: '<i class="fas fa-upload"></i> Tải ảnh',
            
            // Update all images of this patient in the table
            updateElements: [
                `.patient-image[data-patient-id="${patientId}"]`
            ],
            
            // Success callback
            onSuccess: function(response) {
                showAlert('Hình ảnh bệnh nhân đã được cập nhật', 'success');
                
                // Apply highlight effect to the table image
                setTimeout(function() {
                    const $container = $(`.patient-row-image[data-patient-id="${patientId}"]`);
                    $container.css('border-color', '#28a745');
                    $container.animate({borderWidth: '3px'}, 300)
                             .animate({borderWidth: '2px'}, 300);
                }, 500);
            },
            
            // Error callback
            onError: function(error) {
                showAlert('Lỗi khi tải lên hình ảnh. Vui lòng thử lại', 'danger');
                // Reload original image on error
                loadPatientImage(patientId);
            },
            
            // Complete callback
            onComplete: function() {
                $('#patient-image-upload').val(''); // Reset file input
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
    
    // Function to load all patient thumbnails in the table
    function loadPatientThumbnails() {
        console.log('Loading patient thumbnails for table rows...');
        
        // Use the utility to load all patient images in the table
        PatientImageUtils.loadAllPatientImages('.patient-image');
    }
    
    // The updatePatientTableImage function has been replaced by PatientImageUtils.uploadPatientImage
    
    // All camera-related functions have been removed for simplicity and reliability
    // The system now only supports file upload functionality
});
