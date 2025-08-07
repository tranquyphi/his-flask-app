// Patient Departments Management - Working Version with Edit Functionality
$(document).ready(function() {
    console.log('Patient Departments script loaded');
    console.log('jQuery available:', typeof $);
    console.log('DataTables available:', typeof $.fn.DataTable);
    
    // Check for URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const patientFilter = urlParams.get('patient');
    
    // Build API URL with filter if present
    let apiUrl = '/api/patient_department_detail';
    if (patientFilter) {
        apiUrl += `?PatientId=${patientFilter}`;
        console.log('Filtering by patient:', patientFilter);
    }
    
    // Test API endpoint first
    $.get(apiUrl)
        .done(function(data) {
            console.log('API test successful, data received:', data);
            console.log('Data length:', data.length);
            
            // Initialize DataTable with full columns
            const table = $('#patient-departments-table').DataTable({
                data: data,
                destroy: true, // Allow reinitialization
                columns: [
                    { 
                        data: 'PatientId',
                        title: 'Mã'
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
                        title: 'Tuổi'
                    },
                    { 
                        data: 'PatientGender',
                        title: 'Giới',
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
                        data: 'DepartmentName',
                        title: 'Khoa',
                        render: function(data, type, row) {
                            if (type === 'sort' || type === 'type') {
                                return data || '';
                            }
                            return data ? `<span class="badge bg-info text-white">${data}</span>` : '<span class="text-muted">Chưa vào khoa</span>';
                        }
                    },
                    { 
                        data: 'Current',
                        title: 'Đang nằm',
                        render: function(data, type, row) {
                            if (type === 'sort' || type === 'type') {
                                return data === true || data === 1 ? 'Đang nằm' : 'Đã nằm';
                            }
                            
                            if (data === true || data === 1) {
                                return '<i class="fas fa-check-circle text-success" title="Đang nằm" style="font-size: 1.2em;"></i>';
                            } else {
                                return '<i class="fas fa-history text-secondary" title="Đã nằm" style="font-size: 1.2em;"></i>';
                            }
                        }
                    },
                    { 
                        data: 'At',
                        title: 'Ngày vào',
                        render: function(data, type, row) {
                            if (!data) return '';
                            const date = new Date(data);
                            return date.toLocaleDateString() + '<br><small class="text-muted">' + 
                                   date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) + '</small>';
                        }
                    },
            {
                data: 'Reason',
                title: 'Lý do',
                render: function(data, type, row) {
                    if (type === 'display' || type === 'type') {
                        // Map database codes to display names
                        const reasonMap = {
                            'DT': 'Điều trị',
                            'PT': 'Phẫu thuật', 
                            'KCK': 'Khám CK',
                            'CLS': 'CLS',
                            'KH': 'Khác'
                        };
                        const displayName = reasonMap[data] || data || '';
                        return `<span class="badge bg-info">${displayName}</span>`;
                    }
                    return data;
                }
            },
                    {
                        data: null,
                        title: 'Actions',
                        orderable: false,
                        render: function(data, type, row) {
                            const recordId = row.id || `${row.PatientId}-${row.DepartmentId}`;
                            return `
                                <div class="btn-group btn-group-sm">
                                    <button class="btn btn-outline-primary btn-sm view-btn" 
                                            data-patient-id="${row.PatientId}" 
                                            data-record-id="${recordId}"
                                            title="Xem chi tiết">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    <button class="btn btn-outline-success btn-sm add-btn" 
                                            data-patient-id="${row.PatientId}" 
                                            data-dept-id="${row.DepartmentId}"
                                            data-record-id="${recordId}"
                                            title="Thêm vào khoa mới">
                                        <i class="fas fa-plus"></i>
                                    </button>
                                    <button class="btn btn-outline-danger btn-sm delete-btn" 
                                            data-patient-id="${row.PatientId}" 
                                            data-dept-id="${row.DepartmentId}"
                                            data-record-id="${recordId}" 
                                            title="Xóa">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            `;
                        }
                    }
                ],
                pageLength: 25,
                responsive: true,
                scrollX: true, // Enable horizontal scrolling
                scrollCollapse: true,
                order: [[7, 'desc']], // Order by assigned date (now column 7)
                searching: true, // Ensure search is enabled
                autoWidth: false, // Prevent auto width calculation
                columnDefs: [
                    {
                        targets: [8], // Actions column (now column 8)
                        responsivePriority: 1 // Always show actions column
                    },
                    {
                        targets: [0, 1], // Patient ID and Name
                        responsivePriority: 2 // Show these next
                    },
                    {
                        targets: [4, 5], // Department and Current status
                        responsivePriority: 3 // Show these after
                    }
                ],
                language: {
                    emptyTable: "Không tìm thấy thông tin người bệnh ở các khoa",
                    search: "Tìm kiếm:",
                    lengthMenu: "Hiển thị _MENU_ bản ghi mỗi trang",
                    zeroRecords: "Không tìm thấy bản ghi nào"
                }
            });
            
            console.log('DataTable initialized successfully with', data.length, 'records');
            
            // Add event handlers
            $('#patient-departments-table tbody').on('click', '.view-btn', function() {
                const data = table.row($(this).parents('tr')).data();
                viewAssignment(data);
            });
            
            $('#patient-departments-table tbody').on('click', '.add-btn', function() {
                const data = table.row($(this).parents('tr')).data();
                console.log('Add button clicked, data:', data);
                addNewAssignment(data);
            });
            
            $('#patient-departments-table tbody').on('click', '.delete-btn', function() {
                const data = table.row($(this).parents('tr')).data();
                deleteAssignment(data);
            });
            
            // Add filter event handlers
            setupFilters(table);
            
            // Load departments for filter
            loadDepartments();
            
            // Setup modal save handler
            $('#save-assignment').on('click', function() {
                saveAssignment();
            });
        })
        .fail(function(xhr, status, error) {
            console.error('API test failed:', status, error);
            console.error('Response:', xhr.responseText);
            showAlert('Failed to load data: ' + error, 'danger');
        });
    
    // Setup filter functionality with combined filtering
    function setupFilters(table) {
        let currentSearchTerm = '';
        let currentDepartment = '';
        let currentStatus = '';
        
        // Custom search function that combines all filters
        $.fn.dataTable.ext.search.push(
            function(settings, data, dataIndex) {
                // Get the current values
                const patientId = (data[0] || '').toLowerCase();
                const patientName = (data[1] || '').toLowerCase();
                const departmentName = data[4] || '';
                const statusText = data[5] || '';
                
                // Get the actual row data to access the raw Current value
                const rowData = table.row(dataIndex).data();
                const actualCurrentValue = rowData ? rowData.Current : null;
                
                // Check search term (patient ID or name)
                let searchMatch = true;
                if (currentSearchTerm !== '') {
                    searchMatch = patientId.includes(currentSearchTerm) || patientName.includes(currentSearchTerm);
                }
                
                // Check department filter
                let departmentMatch = true;
                if (currentDepartment !== '') {
                    departmentMatch = departmentName.includes(currentDepartment);
                }
                
                // Check status filter
                let statusMatch = true;
                if (currentStatus !== '') {
                    const filterValue = parseInt(currentStatus);
                    const currentValue = actualCurrentValue === true || actualCurrentValue === 1 ? 1 : 0;
                    statusMatch = currentValue === filterValue;
                }
                
                return searchMatch && departmentMatch && statusMatch;
            }
        );
        
        // Patient search
        $('#search-patient').on('keyup', function() {
            currentSearchTerm = $(this).val().toLowerCase();
            console.log('Searching for:', currentSearchTerm);
            table.draw();
            console.log('Search applied, visible rows:', table.rows({search:'applied'}).count());
        });
        
        // Department filter
        $('#filter-department').on('change', function() {
            currentDepartment = $(this).val();
            console.log('Department filter:', currentDepartment);
            table.draw();
        });
        
        // Status filter
        $('#filter-current').on('change', function() {
            currentStatus = $(this).val();
            console.log('Status filter:', currentStatus);
            table.draw();
        });
        
        // Clear filters button
        $('#clear-filters').on('click', function() {
            currentSearchTerm = '';
            currentDepartment = '';
            currentStatus = '';
            
            $('#search-patient').val('');
            $('#filter-department').val('');
            $('#filter-current').val('');
            
            table.draw();
            console.log('All filters cleared');
        });
    }
    
    // Helper functions
    function loadDepartments() {
        $.get('/api/department', function(response) {
            const departments = response.department || [];
            const filter = $('#filter-department');
            
            filter.empty().append('<option value="">All Departments</option>');
            
            departments.forEach(function(dept) {
                filter.append(`<option value="${dept.DepartmentName}">${dept.DepartmentName}</option>`);
            });
        }).fail(function() {
            console.error('Failed to load departments');
        });
    }

    function saveAssignment() {
        const formData = {
            PatientId: parseInt($('#patient-id').val()),
            DepartmentId: parseInt($('#department-id').val()),
            Current: parseInt($('#current-status').val()) === 1,
            At: $('#assigned-at').val() || null,
            Reason: $('#reason').val() || null,
            Notes: $('#notes').val() || null
        };
        
        // For Add functionality, we always create new records (never edit existing)
        const isEditing = false; // Always false for Add button
        
        // Validation
        if (!formData.PatientId || !formData.DepartmentId || formData.Current === null) {
            showAlert('Vui lòng điền đầy đủ thông tin bắt buộc', 'warning');
            return;
        }
        
        // Always use POST for new assignments
        const url = '/api/patient_department_detail';
        const method = 'POST';
        
        // Show loading
        $('#save-assignment').prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Đang lưu...');
        
        $.ajax({
            url: url,
            type: method,
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                $('#assignmentModal').modal('hide');
                showAlert('Thêm bệnh nhân vào khoa thành công!', 'success');
                
                // Reload page to refresh data
                setTimeout(() => location.reload(), 1000);
            },
            error: function(xhr) {
                const error = xhr.responseJSON?.error || 'Có lỗi xảy ra khi lưu dữ liệu';
                showAlert(error, 'danger');
            },
            complete: function() {
                $('#save-assignment').prop('disabled', false).html('<i class="fas fa-save"></i> Lưu');
            }
        });
    }
    
    function addNewAssignment(data) {
        console.log('Add new assignment for patient:', data);
        
        // Load departments for the dropdown
        loadDepartmentsForModal();
        
        // Reset form
        $('#assignment-form')[0].reset();
        
        // Show patient info
        $('#patient-info-display').show();
        $('#display-patient-id').text(data.PatientId);
        $('#display-patient-name').text(data.PatientName || 'N/A');
        $('#display-patient-age').text(data.PatientAge || 'N/A');
        $('#display-patient-gender').text(data.PatientGender || 'N/A');
        
        // Pre-fill form for new assignment for this patient
        $('#patient-id').val(data.PatientId);
        $('#edit-id').val(''); // Always clear for new assignment
        
        // Set default values for new assignment
        $('#current-status').val('1'); // Default to Current
        $('#assigned-at').val(new Date().toISOString().slice(0, 16)); // Current time
        
        // Update modal title for adding new assignment
        $('#assignmentModalLabel').text('Thêm bệnh nhân vào khoa mới');
        
        // Show modal
        $('#assignmentModal').modal('show');
    }
    
    function loadDepartmentsForModal() {
        $.get('/api/department', function(response) {
            const departments = response.department || [];
            const select = $('#department-id');
            
            select.empty().append('<option value="">Chọn khoa...</option>');
            
            departments.forEach(function(dept) {
                select.append(`<option value="${dept.DepartmentId}">${dept.DepartmentName}</option>`);
            });
        }).fail(function() {
            console.error('Failed to load departments for modal');
            showAlert('Không thể tải danh sách khoa', 'danger');
        });
    }
    
    function viewAssignment(data) {
        const assignedDate = data.At ? new Date(data.At) : null;
        const dateDisplay = assignedDate ? 
            `${assignedDate.toLocaleDateString()} lúc ${assignedDate.toLocaleTimeString()}` : 
            'Chưa rõ';
        
        let details = `
            <strong>Người bệnh:</strong> ${data.PatientName} (${data.PatientId})<br>
            <strong>Tuổi:</strong> ${data.PatientAge || 'N/A'}<br>
            <strong>Giới tính:</strong> ${data.PatientGender || 'N/A'}<br>
            <strong>Khoa:</strong> ${data.DepartmentName || 'Chưa vào khoa'}<br>
            <strong>Trạng thái:</strong> ${data.Current ? 'Đang nằm' : 'Đã nằm'}<br>
            <strong>Ngày vào:</strong> ${dateDisplay}
        `;
        
        showAlert(details, 'info', 'Chi tiết thông tin');
    }
    
    function deleteAssignment(data) {
        const recordId = data.id;
        const deleteUrl = recordId ? 
            `/api/patient_department_detail/record/${recordId}` : 
            `/api/patient_department_detail/${data.PatientId}/${data.DepartmentId}`;
            
        if (confirm(`Xóa lịch sử vào khoa: ${data.PatientName} - ${data.DepartmentName}?\n\nLưu ý: Hành động này không thể hoàn tác.`)) {
            $.ajax({
                url: deleteUrl,
                type: 'DELETE',
                success: function() {
                    showAlert('Xóa lịch sử vào khoa thành công!', 'success');
                    setTimeout(() => location.reload(), 1000); // Reload to refresh data
                },
                error: function(xhr) {
                    const error = xhr.responseJSON?.error || 'Không thể xóa lịch sử vào khoa';
                    showAlert(error, 'danger');
                }
            });
        }
    }
    
    function showAlert(message, type = 'info', title = null) {
        const alertDiv = $(`
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${title ? `<h6>${title}</h6>` : ''}
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `);
        
        $('.container-fluid').prepend(alertDiv);
        setTimeout(() => alertDiv.remove(), 5000);
    }
    
    console.log('Patient Departments script setup complete');
});
