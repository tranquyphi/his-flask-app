// Department Patients Management
$(document).ready(function() {
    console.log('Department Patients script loaded');
    
    let currentDepartmentId = null;
    let patientsTable = null;
    
    // Load departments on page load
    loadDepartments();
    
    // Event handlers
    $('#department-select').on('change', function() {
        const deptId = $(this).val();
        $('#load-department').prop('disabled', !deptId);
    });
    
    $('#load-department').on('click', function() {
        const deptId = $('#department-select').val();
        if (deptId) {
            loadDepartmentPatients(deptId);
        }
    });
    
    $('#refresh-data').on('click', function() {
        if (currentDepartmentId) {
            loadDepartmentPatients(currentDepartmentId);
        }
    });
    
    $('#search-patient').on('keyup', function() {
        if (patientsTable) {
            patientsTable.search($(this).val()).draw();
        }
    });
    
    $('#sort-by').on('change', function() {
        if (patientsTable) {
            const sortCol = $(this).val();
            let colIndex = 5; // Default to admission date
            
            switch(sortCol) {
                case 'PatientName': colIndex = 1; break;
                case 'PatientAge': colIndex = 2; break;
                case 'At': colIndex = 5; break;
            }
            
            patientsTable.order([colIndex, 'desc']).draw();
        }
    });
    
    function loadDepartments() {
        $.get('/api/departments')
            .done(function(response) {
                console.log('Departments loaded:', response);
                const select = $('#department-select');
                select.empty().append('<option value="">-- Chọn Khoa --</option>');
                
                if (response.departments) {
                    response.departments.forEach(function(dept) {
                        select.append(`<option value="${dept.DepartmentId}">${dept.DepartmentName} (${dept.DepartmentType})</option>`);
                    });
                }
            })
            .fail(function(xhr) {
                console.error('Error loading departments:', xhr);
                showAlert('Lỗi khi tải danh sách khoa', 'danger');
            });
    }
    
    function loadDepartmentPatients(departmentId) {
        console.log('Loading patients for department:', departmentId);
        currentDepartmentId = departmentId;
        
        // Show loading state
        $('#load-department').prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Đang tải...');
        
        // Load department data and statistics
        Promise.all([
            $.get(`/api/department_patients/${departmentId}`),
            $.get(`/api/department_stats/${departmentId}`)
        ])
        .then(function(responses) {
            const [patientsResponse, statsResponse] = responses;
            
            console.log('Patients data:', patientsResponse);
            console.log('Stats data:', statsResponse);
            
            // Update department header
            updateDepartmentHeader(patientsResponse.department);
            
            // Update statistics
            updateStatistics(statsResponse);
            
            // Initialize/update patients table
            initializePatientsTable(patientsResponse.patients);
            
            // Show sections
            showDataSections();
            
            // Reset button
            $('#load-department').prop('disabled', false).html('<i class="fas fa-search"></i> Tải danh sách bệnh nhân');
        })
        .catch(function(error) {
            console.error('Error loading department data:', error);
            showAlert('Lỗi khi tải dữ liệu khoa', 'danger');
            $('#load-department').prop('disabled', false).html('<i class="fas fa-search"></i> Tải danh sách bệnh nhân');
        });
    }
    
    function updateDepartmentHeader(department) {
        $('#department-name').text(department.DepartmentName);
        $('#department-type').text(department.DepartmentType);
        $('#department-header').removeClass('d-none');
    }
    
    function updateStatistics(stats) {
        $('#current-count').text(stats.current_patients || 0);
        $('#recent-count').text(stats.recent_admissions || 0);
        $('#total-count').text(stats.total_patients || 0);
        $('#stats-section').removeClass('d-none');
    }
    
    function initializePatientsTable(patients) {
        console.log('Initializing table with', patients.length, 'patients');
        
        // Destroy existing table if it exists
        if (patientsTable) {
            patientsTable.destroy();
        }
        
        if (patients.length === 0) {
            $('#table-section').addClass('d-none');
            $('#empty-state').removeClass('d-none');
            return;
        }
        
        $('#empty-state').addClass('d-none');
        $('#table-section').removeClass('d-none');
        
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
                    title: 'Mã BN'
                },
                { 
                    data: 'PatientName',
                    title: 'Họ tên',
                    render: function(data, type, row) {
                        return data ? `<strong>${data}</strong>` : 'N/A';
                    }
                },
                { 
                    data: 'PatientAge',
                    title: 'Tuổi',
                    render: function(data, type, row) {
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
                    data: 'PatientAddress',
                    title: 'Địa chỉ',
                    render: function(data, type, row) {
                        if (type === 'sort' || type === 'type') {
                            return data || '';
                        }
                        return data ? `<small>${data}</small>` : '<span class="text-muted">Chưa có</span>';
                    }
                },
                { 
                    data: 'At',
                    title: 'Ngày vào khoa',
                    render: function(data, type, row) {
                        if (!data) return '';
                        const date = new Date(data);
                        return date.toLocaleDateString('vi-VN') + '<br><small class="text-muted">' + 
                               date.toLocaleTimeString('vi-VN', {hour: '2-digit', minute:'2-digit'}) + '</small>';
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
                        if (data > 7) badgeClass = 'bg-warning';
                        if (data > 14) badgeClass = 'bg-danger';
                        
                        return `<span class="badge ${badgeClass}">${data} ngày</span>`;
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
                                <button class="btn btn-outline-success btn-sm edit-btn" 
                                        data-patient-id="${row.PatientId}" 
                                        title="Chỉnh sửa">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-outline-info btn-sm history-btn" 
                                        data-patient-id="${row.PatientId}" 
                                        title="Lịch sử khoa">
                                    <i class="fas fa-history"></i>
                                </button>
                            </div>
                        `;
                    }
                }
            ],
            pageLength: 15,
            responsive: true,
            scrollX: true,
            scrollCollapse: true,
            order: [[5, 'desc']], // Order by admission date
            searching: true,
            autoWidth: false,
            columnDefs: [
                {
                    targets: [7], // Actions column
                    responsivePriority: 1
                },
                {
                    targets: [0, 1], // Patient ID and Name
                    responsivePriority: 2
                },
                {
                    targets: [2, 5], // Age and admission date
                    responsivePriority: 3
                }
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
        
        $('#department-patients-table tbody').on('click', '.edit-btn', function() {
            const patientId = $(this).data('patient-id');
            editPatient(patientId);
        });
        
        $('#department-patients-table tbody').on('click', '.history-btn', function() {
            const patientId = $(this).data('patient-id');
            showPatientHistory(patientId);
        });
    }
    
    function showDataSections() {
        $('#search-section').removeClass('d-none');
    }
    
    function showPatientDetails(patient) {
        $('#modal-patient-id').text(patient.PatientId);
        $('#modal-patient-name').text(patient.PatientName || 'N/A');
        $('#modal-patient-age').text(patient.PatientAge ? `${patient.PatientAge} tuổi` : 'N/A');
        $('#modal-patient-gender').text(patient.PatientGender || 'N/A');
        $('#modal-patient-address').text(patient.PatientAddress || 'Chưa có thông tin');
        
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
    
    function showPatientHistory(patientId) {
        // This could open a modal or redirect to history page
        showAlert('Tính năng lịch sử khoa sẽ được phát triển trong phiên bản tiếp theo', 'info');
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
    
    // Global function to reset view
    window.resetView = function() {
        // Hide all sections
        $('#department-header').addClass('d-none');
        $('#stats-section').addClass('d-none');
        $('#search-section').addClass('d-none');
        $('#table-section').addClass('d-none');
        $('#empty-state').addClass('d-none');
        
        // Reset form
        $('#department-select').val('');
        $('#load-department').prop('disabled', true);
        $('#search-patient').val('');
        
        // Destroy table
        if (patientsTable) {
            patientsTable.destroy();
            patientsTable = null;
        }
        
        currentDepartmentId = null;
    };
    
    // Global function for modal edit button
    window.editPatient = function() {
        const patientId = $('#modal-patient-id').text();
        $('#patientModal').modal('hide');
        editPatient(patientId);
    };
});
