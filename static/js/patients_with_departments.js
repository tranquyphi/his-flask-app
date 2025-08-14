// Patients with Department Information JavaScript
$(document).ready(function() {
    console.log('Patients with Departments script loaded');
    
    let patientsTable = null;
    let allPatients = [];
    
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
    
    $('#refresh-data').on('click', function() {
        loadPatientsData();
    });
    
    $('#export-excel').on('click', function() {
        exportToExcel();
    });
    
    function loadPatientsData() {
        console.log('Loading patients data...');
        
        // Show loading state
        $('#loading-section').show();
        $('#stats-section').hide();
        $('#table-section').hide();
        $('#empty-section').hide();
        $('#error-section').hide();
        
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
            },
            error: function(xhr, status, error) {
                console.error('Error loading patients data:', error);
                showErrorState(error);
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
            columns: [
                { 
                    data: 'PatientId',
                    render: function(data, type, row) {
                        return `<strong class="text-primary">${data}</strong>`;
                    }
                },
                { 
                    data: 'PatientName',
                    render: function(data, type, row) {
                        return data ? `<strong>${data}</strong>` : '<span class="text-muted">N/A</span>';
                    }
                },
                { 
                    data: 'PatientAge',
                    render: function(data, type, row) {
                        if (type === 'sort' || type === 'type') {
                            return parseInt(data) || 0;
                        }
                        return data ? `${data} tuổi` : '<span class="text-muted">N/A</span>';
                    }
                },
                { 
                    data: 'PatientGender',
                    render: function(data, type, row) {
                        if (type === 'sort' || type === 'type') {
                            return data || '';
                        }
                        
                        if (!data) return '<span class="text-muted">N/A</span>';
                        const genderIcons = {
                            'Nam': '<i class="fas fa-mars text-primary" title="Nam" style="font-size: 1.2em;"></i> Nam',
                            'Nữ': '<i class="fas fa-venus text-danger" title="Nữ" style="font-size: 1.2em;"></i> Nữ',
                            'Khác': '<i class="fas fa-genderless text-secondary" title="Khác" style="font-size: 1.2em;"></i> Khác'
                        };
                        return genderIcons[data] || `<span class="text-muted">${data}</span>`;
                    }
                },
                { 
                    data: 'PatientAddress',
                    render: function(data, type, row) {
                        if (type === 'sort' || type === 'type') {
                            return data || '';
                        }
                        if (!data) return '<span class="text-muted">Chưa có</span>';
                        return data.length > 50 ? 
                            `<span title="${data}">${data.substring(0, 50)}...</span>` : 
                            `<span>${data}</span>`;
                    }
                },
                { 
                    data: 'CurrentDepartment',
                    render: function(data, type, row) {
                        if (type === 'sort' || type === 'type') {
                            return data || '';
                        }
                        return data ? 
                            `<span class="department-badge">${data}</span>` : 
                            '<span class="text-muted">Chưa phân khoa</span>';
                    }
                },
                { 
                    data: 'AllDepartments',
                    orderable: false,
                    render: function(data, type, row) {
                        if (type === 'sort' || type === 'type') {
                            return data ? data.length : 0;
                        }
                        
                        if (!data || data.length === 0) {
                            return '<span class="text-muted">Chưa có lịch sử</span>';
                        }
                        
                        if (data.length === 1) {
                            return `<small class="text-muted">1 phân khoa</small>`;
                        }
                        
                        return `<button class="btn btn-sm btn-outline-info" onclick="showDepartmentHistory('${row.PatientId}')">
                                    <i class="fas fa-history"></i> ${data.length} phân khoa
                                </button>`;
                    }
                },
                { 
                    data: null,
                    orderable: false,
                    render: function(data, type, row) {
                        return `
                            <div class="btn-group btn-group-sm">
                                <button class="btn btn-outline-primary btn-sm" onclick="viewPatientDetails('${row.PatientId}')" title="Xem chi tiết">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn btn-outline-success btn-sm" onclick="viewPatientVisits('${row.PatientId}')" title="Lượt khám">
                                    <i class="fas fa-calendar-check"></i>
                                </button>
                                <button class="btn btn-outline-info btn-sm" onclick="editPatient('${row.PatientId}')" title="Chỉnh sửa">
                                    <i class="fas fa-edit"></i>
                                </button>
                            </div>
                        `;
                    }
                }
            ],
            pageLength: 25,
            responsive: true,
            scrollX: true,
            scrollCollapse: true,
            order: [[1, 'asc']], // Order by patient name
            searching: true,
            autoWidth: false,
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
        
        console.log('DataTable initialized successfully');
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
        $('#table-section').show();
        $('#empty-section').hide();
        $('#error-section').hide();
    }
    
    function showEmptyState() {
        $('#loading-section').hide();
        $('#stats-section').hide();
        $('#table-section').hide();
        $('#empty-section').show();
        $('#error-section').hide();
    }
    
    function showErrorState(error) {
        $('#loading-section').hide();
        $('#stats-section').hide();
        $('#table-section').hide();
        $('#empty-section').hide();
        $('#error-section').show();
        $('#error-message').text('Error loading data: ' + error);
    }
    
    function updateLastUpdated() {
        const now = new Date();
        $('#last-updated').text(now.toLocaleString('vi-VN'));
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
    // TODO: Implement patient details modal or page
    alert(`Patient details for ${patientId} - Feature coming soon!`);
}

function viewPatientVisits(patientId) {
    console.log('Viewing patient visits for:', patientId);
    window.location.href = `/patient-visits/${patientId}`;
}

function editPatient(patientId) {
    console.log('Editing patient:', patientId);
    // TODO: Implement patient edit functionality
    alert(`Edit patient ${patientId} - Feature coming soon!`);
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
