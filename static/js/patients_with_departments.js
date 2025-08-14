// Patients with Department Information JavaScript
$(document).ready(function() {
    console.log('Patients with Departments script loaded');
    
    let patientsTable = null;
    let allPatients = [];
    
    // Show loading overlay initially
    $('#loading-overlay').show();
    
    // Load data on page load
    loadPatientsData();
    
    // Event handlers
    $('#search-patient').on('keyup', function() {
        if (patientsTable) {
            patientsTable.search($(this).val()).draw();
        }
    });
    
    $('#department-filter').on('change', function() {
        filterByDepartment($(this).val());
    });
    
    $('#gender-filter').on('change', function() {
        filterByGender($(this).val());
    });
    
    $('#sort-by').on('change', function() {
        const sortCol = $(this).val();
        if (patientsTable && sortCol) {
            let colIndex = 1; // Default to patient name
            
            switch(sortCol) {
                case 'PatientName': colIndex = 1; break;
                case 'PatientAge': colIndex = 2; break;
                case 'CurrentDepartment': colIndex = 5; break;
            }
            
            patientsTable.order([colIndex, 'asc']).draw();
        }
    });
    
    $('#refresh-data').on('click', function() {
        loadPatientsData();
    });
    
    $('#export-excel').on('click', function() {
        exportToExcel();
    });
    
    $('#retry-button').on('click', function() {
        loadPatientsData();
    });
    
    // Modal event handlers
    $('#modal-view-visits').on('click', function() {
        const patientId = $('#modal-patient-id').text().trim();
        if (patientId && patientId !== '-') {
            $('#patientModal').modal('hide');
            window.location.href = `/patient-visits/${patientId}`;
        }
    });
    
    $('#modal-edit-patient').on('click', function() {
        const patientId = $('#modal-patient-id').text().trim();
        if (patientId && patientId !== '-') {
            editPatient(patientId);
        }
    });
    
    function loadPatientsData() {
        console.log('Loading patients data...');
        
        // Show loading states
        $('#loading-overlay').show();
        $('#loading-section').show();
        $('#stats-section').hide();
        $('#search-section').hide();
        $('#table-section').hide();
        $('#empty-section').addClass('d-none');
        $('#error-section').addClass('d-none');
        
        // Fetch data from API
        $.ajax({
            url: '/api/patients_with_department',
            method: 'GET',
            dataType: 'json',
            success: function(response) {
                console.log('Patients data loaded:', response);
                
                if (response.patients_with_department && response.patients_with_department.length > 0) {
                    allPatients = response.patients_with_department;
                    updateStatistics(allPatients);
                    populateDepartmentFilter(allPatients);
                    initializePatientsTable(allPatients);
                    updateLastUpdated();
                    showDataSections();
                } else {
                    showEmptyState();
                }
                $('#loading-overlay').hide();
            },
            error: function(xhr, status, error) {
                console.error('Error loading patients data:', error);
                showErrorState(error);
                $('#loading-overlay').hide();
            }
        });
    }
    
    function updateStatistics(patients) {
        const withDepartment = patients.filter(p => p.CurrentDepartment).length;
        const withoutDepartment = patients.length - withDepartment;
        
        // Get unique departments
        const departments = new Set();
        patients.forEach(patient => {
            if (patient.CurrentDepartment) {
                departments.add(patient.CurrentDepartment);
            }
        });
        
        $('#total-patients').text(patients.length);
        $('#with-department').text(withDepartment);
        $('#without-department').text(withoutDepartment);
        $('#unique-departments').text(departments.size);
    }
    
    function populateDepartmentFilter(patients) {
        const departments = new Set();
        patients.forEach(patient => {
            if (patient.CurrentDepartment) {
                departments.add(patient.CurrentDepartment);
            }
        });
        
        const $filter = $('#department-filter');
        $filter.find('option:not(:first)').remove();
        
        Array.from(departments).sort().forEach(dept => {
            $filter.append(`<option value="${dept}">${dept}</option>`);
        });
    }
    
    function initializePatientsTable(patients) {
        console.log('Initializing table with', patients.length, 'patients');
        
        // Destroy existing table if it exists
        if (patientsTable) {
            patientsTable.destroy();
        }
        
        patientsTable = $('#patients-table').DataTable({
            data: patients,
            destroy: true,
            pageLength: 25,
            responsive: true, // Back to responsive
            scrollX: true,
            scrollCollapse: true,
            order: [[1, 'asc']], // Order by patient name
            searching: true,
            autoWidth: false,
            columns: [
                { 
                    data: 'PatientId',
                    title: 'Mã BN',
                    render: function(data, type, row) {
                        return `<strong class="text-primary">${data}</strong>`;
                    }
                },
                { 
                    data: 'PatientName',
                    title: 'Họ tên',
                    render: function(data, type, row) {
                        return data ? `<strong>${data}</strong>` : '<span class="text-muted">N/A</span>';
                    }
                },
                { 
                    data: 'PatientAge',
                    title: 'Tuổi',
                    render: function(data, type, row) {
                        if (type === 'sort' || type === 'type') {
                            return parseInt(data) || 0;
                        }
                        return data ? `${data} tuổi` : '<span class="text-muted">N/A</span>';
                    }
                },
                { 
                    data: 'PatientGender',
                    title: 'Giới tính',
                    render: function(data, type, row) {
                        if (type === 'sort' || type === 'type') {
                            return data || '';
                        }
                        
                        if (!data) return '<span class="text-muted">N/A</span>';
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
                        if (!data) return '<span class="text-muted">Chưa có</span>';
                        return data.length > 30 ? 
                            `<span title="${data}" class="text-truncate d-inline-block" style="max-width: 150px;">${data}</span>` : 
                            `<span>${data}</span>`;
                    }
                },
                { 
                    data: 'CurrentDepartment',
                    title: 'Khoa hiện tại',
                    render: function(data, type, row) {
                        if (type === 'sort' || type === 'type') {
                            return data || '';
                        }
                        return data ? 
                            `<span class="department-badge">${data}</span>` : 
                            '<span class="badge bg-secondary">Chưa phân khoa</span>';
                    }
                },
                { 
                    data: 'Allergy',
                    title: 'Dị ứng',
                    render: function(data, type, row) {
                        if (type === 'sort' || type === 'type') {
                            return data || '';
                        }
                        if (!data || data.trim() === '') {
                            return '<span class="text-muted">Không</span>';
                        }
                        return `<span class="allergy-badge" title="${data}">
                                    <i class="fas fa-exclamation-triangle"></i> Có
                                </span>`;
                    }
                },
                { 
                    data: 'History',
                    title: 'Tiền sử',
                    render: function(data, type, row) {
                        if (type === 'sort' || type === 'type') {
                            return data || '';
                        }
                        if (!data || data.trim() === '') {
                            return '<span class="text-muted">Không</span>';
                        }
                        return `<span class="history-indicator" title="${data}">
                                    <i class="fas fa-history"></i> Có
                                </span>`;
                    }
                },
                { 
                    data: 'PatientNote',
                    title: 'Ghi chú',
                    render: function(data, type, row) {
                        if (type === 'sort' || type === 'type') {
                            return data || '';
                        }
                        if (!data || data.trim() === '') {
                            return '<span class="text-muted">-</span>';
                        }
                        return data.length > 20 ? 
                            `<span title="${data}" class="text-truncate d-inline-block" style="max-width: 100px;">${data}</span>` : 
                            `<span>${data}</span>`;
                    }
                },
                { 
                    data: 'AllDepartments',
                    title: 'Lịch sử khoa',
                    orderable: false,
                    render: function(data, type, row) {
                        if (type === 'sort' || type === 'type') {
                            return data ? data.length : 0;
                        }
                        
                        if (!data || data.length === 0) {
                            return '<span class="text-muted">Chưa có</span>';
                        }
                        
                        if (data.length === 1) {
                            return `<small class="text-muted">1 khoa</small>`;
                        }
                        
                        return `<button class="btn btn-sm btn-outline-info" onclick="showDepartmentHistory('${row.PatientId}')">
                                    <i class="fas fa-history"></i> ${data.length} khoa
                                </button>`;
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
                                <button class="btn btn-outline-success btn-sm visits-btn" 
                                        data-patient-id="${row.PatientId}" 
                                        title="Lượt khám">
                                    <i class="fas fa-calendar-check"></i>
                                </button>
                                <button class="btn btn-outline-info btn-sm edit-btn" 
                                        data-patient-id="${row.PatientId}" 
                                        title="Chỉnh sửa">
                                    <i class="fas fa-edit"></i>
                                </button>
                            </div>
                        `;
                    }
                }
            ],
            pageLength: 25,
            columnDefs: [
                {
                    targets: [10], // Actions column
                    responsivePriority: 1
                },
                {
                    targets: [1], // Patient Name - highest priority after actions
                    responsivePriority: 2
                },
                {
                    targets: [0], // Patient ID
                    responsivePriority: 4
                },
                {
                    targets: [2, 5], // Age and Current Department
                    responsivePriority: 3
                }
            ],
            language: {
                emptyTable: "Không có dữ liệu bệnh nhân",
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
        
        console.log('DataTable initialized successfully with', patients.length, 'patients');
        
        // Add event handlers for table buttons (like in reference file)
        $('#patients-table tbody').on('click', '.view-btn', function() {
            const patientData = $(this).data('patient');
            showPatientDetails(patientData);
        });
        
        $('#patients-table tbody').on('click', '.visits-btn', function() {
            const patientId = $(this).data('patient-id');
            viewPatientVisits(patientId);
        });
        
        $('#patients-table tbody').on('click', '.edit-btn', function() {
            const patientId = $(this).data('patient-id');
            editPatient(patientId);
        });
    }
    
    function filterByDepartment(department) {
        if (!patientsTable) return;
        
        if (department) {
            patientsTable.column(5).search(department).draw();
        } else {
            patientsTable.column(5).search('').draw();
        }
    }
    
    function filterByGender(gender) {
        if (!patientsTable) return;
        
        if (gender) {
            patientsTable.column(3).search(gender).draw();
        } else {
            patientsTable.column(3).search('').draw();
        }
    }
    
    function showDataSections() {
        $('#loading-section').hide();
        $('#stats-section').show();
        $('#search-section').show();
        $('#table-section').show();
        $('#empty-section').addClass('d-none');
        $('#error-section').addClass('d-none');
    }
    
    function showEmptyState() {
        $('#loading-section').hide();
        $('#stats-section').hide();
        $('#search-section').hide();
        $('#table-section').hide();
        $('#empty-section').removeClass('d-none');
        $('#error-section').addClass('d-none');
    }
    
    function showErrorState(error) {
        $('#loading-section').hide();
        $('#stats-section').hide();
        $('#search-section').hide();
        $('#table-section').hide();
        $('#empty-section').addClass('d-none');
        $('#error-section').removeClass('d-none');
        $('#error-message').text('Lỗi tải dữ liệu: ' + error);
    }
    
    // Helper functions for table data formatting
    function getGenderIcon(gender) {
        if (!gender) return '<span class="text-muted">N/A</span>';
        const genderIcons = {
            'Nam': '<i class="fas fa-mars text-primary" title="Nam" style="font-size: 1.2em;"></i>',
            'Nữ': '<i class="fas fa-venus text-danger" title="Nữ" style="font-size: 1.2em;"></i>',
            'Khác': '<i class="fas fa-genderless text-secondary" title="Khác" style="font-size: 1.2em;"></i>'
        };
        return genderIcons[gender] || `<span class="text-muted">${gender}</span>`;
    }
    
    function getAllergyDisplay(allergy) {
        if (!allergy || allergy.trim() === '') {
            return '<span class="text-muted">Không</span>';
        }
        return `<span class="allergy-badge" title="${allergy}">
                    <i class="fas fa-exclamation-triangle"></i> Có
                </span>`;
    }
    
    function getHistoryDisplay(history) {
        if (!history || history.trim() === '') {
            return '<span class="text-muted">Không</span>';
        }
        return `<span class="history-indicator" title="${history}">
                    <i class="fas fa-history"></i> Có
                </span>`;
    }
    
    function getDepartmentHistoryButton(patient) {
        const data = patient.AllDepartments;
        if (!data || data.length === 0) {
            return '<span class="text-muted">Chưa có</span>';
        }
        
        if (data.length === 1) {
            return `<small class="text-muted">1 khoa</small>`;
        }
        
        return `<button class="btn btn-sm btn-outline-info" onclick="showDepartmentHistory('${patient.PatientId}')">
                    <i class="fas fa-history"></i> ${data.length} khoa
                </button>`;
    }
    
    function getActionsButtons(patientId) {
        return `
            <div class="btn-group btn-group-sm">
                <button class="btn btn-outline-primary btn-sm" onclick="viewPatientDetails('${patientId}')" title="Xem chi tiết">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-outline-success btn-sm" onclick="viewPatientVisits('${patientId}')" title="Lượt khám">
                    <i class="fas fa-calendar-check"></i>
                </button>
                <button class="btn btn-outline-info btn-sm" onclick="editPatient('${patientId}')" title="Chỉnh sửa">
                    <i class="fas fa-edit"></i>
                </button>
            </div>
        `;
    }
    
    // Patient interaction functions (like in reference file)
    function showPatientDetails(patient) {
        $('#modal-patient-id').text(patient.PatientId);
        $('#modal-patient-name').text(patient.PatientName || 'N/A');
        $('#modal-patient-age').text(patient.PatientAge ? `${patient.PatientAge} tuổi` : 'N/A');
        $('#modal-patient-gender').text(patient.PatientGender || 'N/A');
        $('#modal-patient-address').text(patient.PatientAddress || 'Chưa có thông tin');
        $('#modal-department').text(patient.CurrentDepartment || 'Chưa phân khoa');
        $('#modal-allergy').text(patient.Allergy || 'Không');
        $('#modal-history').text(patient.History || 'Không');
        $('#modal-notes').text(patient.PatientNote || 'Không có ghi chú');
        
        $('#patientModal').modal('show');
    }
    
    function viewPatientVisits(patientId) {
        window.location.href = `/patient-visits/${patientId}`;
    }
    
    function editPatient(patientId) {
        // Placeholder for edit functionality
        alert(`Chỉnh sửa bệnh nhân ${patientId} - Tính năng sẽ được phát triển`);
    }
    
    function showDepartmentHistory(patientId) {
        // Find patient data and show department history
        const patient = allPatients.find(p => p.PatientId === patientId);
        if (patient && patient.AllDepartments) {
            let historyHtml = '<div class="department-history">';
            patient.AllDepartments.forEach(dept => {
                const date = new Date(dept.AssignedDate).toLocaleDateString('vi-VN');
                historyHtml += `<p><strong>${dept.DepartmentName}</strong> - ${date}</p>`;
            });
            historyHtml += '</div>';
            
            // Show in modal or alert (simple implementation)
            alert(`Lịch sử khoa của bệnh nhân ${patientId}:\n${patient.AllDepartments.map(d => `${d.DepartmentName} (${new Date(d.AssignedDate).toLocaleDateString('vi-VN')})`).join('\n')}`);
        }
    }
    
    function updateLastUpdated() {
        const now = new Date();
        const timeString = now.toLocaleString('vi-VN');
        $('#last-updated').text(timeString);
        $('#table-last-updated').text(timeString);
    }
    
    function exportToExcel() {
        console.log('Exporting to Excel...');
        
        // Get current filtered data from DataTable
        const data = patientsTable ? patientsTable.rows({ search: 'applied' }).data().toArray() : allPatients;
        
        if (data.length === 0) {
            alert('Không có dữ liệu để xuất');
            return;
        }
        
        // Create Excel export
        const ws_data = [
            ['Patient ID', 'Name', 'Age', 'Gender', 'Address', 'Current Department', 'Allergy', 'History', 'Notes']
        ];
        
        data.forEach(patient => {
            ws_data.push([
                patient.PatientId,
                patient.PatientName || '',
                patient.PatientAge || '',
                patient.PatientGender || '',
                patient.PatientAddress || '',
                patient.CurrentDepartment || '',
                patient.Allergy || '',
                patient.History || '',
                patient.PatientNote || ''
            ]);
        });
        
        // Convert to CSV and download
        const csvContent = ws_data.map(row => 
            row.map(field => `"${(field || '').toString().replace(/"/g, '""')}"`).join(',')
        ).join('\n');
        
        const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `patients_with_departments_${new Date().toISOString().split('T')[0]}.csv`;
        link.click();
        
        console.log('Export completed');
    }
});

// Global functions for button actions
function viewPatientDetails(patientId) {
    console.log('Viewing patient details for:', patientId);
    
    // Find patient data
    const patient = allPatients.find(p => p.PatientId === patientId);
    
    if (!patient) {
        alert('Không tìm thấy thông tin bệnh nhân');
        return;
    }
    
    // Populate modal with patient information
    $('#modal-patient-id').text(patient.PatientId);
    $('#modal-patient-name').text(patient.PatientName || 'N/A');
    $('#modal-patient-age').text(patient.PatientAge ? `${patient.PatientAge} tuổi` : 'N/A');
    $('#modal-patient-gender').text(patient.PatientGender || 'N/A');
    $('#modal-patient-address').text(patient.PatientAddress || 'Chưa có thông tin');
    $('#modal-current-department').text(patient.CurrentDepartment || 'Chưa phân khoa');
    $('#modal-allergy').text(patient.Allergy || 'Không có');
    $('#modal-history').text(patient.History || 'Không có');
    $('#modal-notes').text(patient.PatientNote || 'Không có');
    
    // Show the modal
    $('#patientModal').modal('show');
}

function viewPatientVisits(patientId) {
    console.log('Viewing patient visits for:', patientId);
    window.location.href = `/patient-visits/${patientId}`;
}

function editPatient(patientId) {
    console.log('Editing patient:', patientId);
    // TODO: Implement patient edit functionality
    alert(`Chỉnh sửa bệnh nhân ${patientId} - Tính năng đang phát triển!`);
}

function showDepartmentHistory(patientId) {
    console.log('Showing department history for:', patientId);
    
    // Find patient data
    const patient = $('#patients-table').DataTable().data().toArray().find(p => p.PatientId === patientId);
    
    if (!patient || !patient.AllDepartments) {
        alert('Không tìm thấy lịch sử phân khoa');
        return;
    }
    
    // Create modal content
    let historyHtml = '<div class="timeline">';
    patient.AllDepartments.forEach((dept, index) => {
        historyHtml += `
            <div class="timeline-item ${index === 0 ? 'current' : ''}">
                <div class="timeline-marker ${index === 0 ? 'bg-primary' : 'bg-secondary'}"></div>
                <div class="timeline-content">
                    <h6 class="mb-1">${dept.DepartmentName}</h6>
                    <small class="text-muted">${dept.AssignedDate ? new Date(dept.AssignedDate).toLocaleString('vi-VN') : 'N/A'}</small>
                    ${index === 0 ? '<span class="badge bg-primary ms-2">Hiện tại</span>' : ''}
                </div>
            </div>
        `;
    });
    historyHtml += '</div>';
    
    // Show in a modal (you'll need to add the modal HTML to the page)
    const modalHtml = `
        <div class="modal fade" id="departmentHistoryModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Lịch sử phân khoa - ${patient.PatientName}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${historyHtml}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Đóng</button>
                    </div>
                </div>
            </div>
        </div>
        <style>
            .timeline { position: relative; padding: 1rem 0; }
            .timeline-item { position: relative; padding-left: 2rem; margin-bottom: 1rem; }
            .timeline-marker { position: absolute; left: 0; top: 0.25rem; width: 0.75rem; height: 0.75rem; border-radius: 50%; }
            .timeline-item:before { content: ''; position: absolute; left: 0.35rem; top: 1rem; bottom: -1rem; width: 2px; background: #dee2e6; }
            .timeline-item:last-child:before { display: none; }
            .timeline-item.current .timeline-content h6 { color: #0d6efd; }
        </style>
    `;
    
    // Remove existing modal and add new one
    $('#departmentHistoryModal').remove();
    $('body').append(modalHtml);
    
    // Show the modal
    $('#departmentHistoryModal').modal('show');
}
