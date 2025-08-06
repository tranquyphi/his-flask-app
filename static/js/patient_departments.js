// Patient Departments Management - Working Version
$(document).ready(function() {
    console.log('Patient Departments script loaded');
    console.log('jQuery available:', typeof $);
    console.log('DataTables available:', typeof $.fn.DataTable);
    
    // Test API endpoint first
    $.get('/api/patient_department_detail')
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
                                // Return the actual value for sorting and searching
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
                                // Return the actual value for sorting and searching
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
                        data: null,
                        title: 'Actions',
                        orderable: false,
                        render: function(data, type, row) {
                            return `
                                <div class="btn-group btn-group-sm">
                                    <button class="btn btn-outline-primary btn-sm view-btn" 
                                            data-patient-id="${row.PatientId}" 
                                            title="Xem chi tiết">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    <button class="btn btn-outline-success btn-sm edit-btn" 
                                            data-patient-id="${row.PatientId}" 
                                            data-dept-id="${row.DepartmentId}" 
                                            title="Chỉnh sửa">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button class="btn btn-outline-danger btn-sm delete-btn" 
                                            data-patient-id="${row.PatientId}" 
                                            data-dept-id="${row.DepartmentId}" 
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
                order: [[6, 'desc']], // Order by assigned date
                searching: true, // Ensure search is enabled
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
            
            $('#patient-departments-table tbody').on('click', '.edit-btn', function() {
                const data = table.row($(this).parents('tr')).data();
                showAssignmentModal(data);
            });
            
            $('#patient-departments-table tbody').on('click', '.delete-btn', function() {
                const data = table.row($(this).parents('tr')).data();
                deleteAssignment(data);
            });
            
            // Load dropdown options for filters
            loadDepartments();
            loadPatients();
            
            // Add filter event handlers
            setupFilters(table);
            
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
        
        // Add assignment button
        $('#add-assignment').on('click', function() {
            showAssignmentModal();
        });
        
        // Save assignment button
        $('#save-assignment').on('click', function() {
            saveAssignment();
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
            const select = $('#department-select');
            
            filter.empty().append('<option value="">All Departments</option>');
            select.empty().append('<option value="">Select Department</option>');
            
            departments.forEach(function(dept) {
                filter.append(`<option value="${dept.DepartmentName}">${dept.DepartmentName}</option>`);
                select.append(`<option value="${dept.DepartmentId}">${dept.DepartmentName}</option>`);
            });
        }).fail(function() {
            console.error('Failed to load departments');
        });
    }
    
    function loadPatients() {
        $.get('/api/patient', function(response) {
            const patients = response.patient || [];
            const select = $('#patient-select');
            select.empty().append('<option value="">Select Patient</option>');
            
            patients.forEach(function(patient) {
                select.append(`<option value="${patient.PatientId}">
                    ${patient.PatientName} (${patient.PatientId})
                </option>`);
            });
        }).fail(function() {
            console.error('Failed to load patients');
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
        if (confirm(`Xóa thông tin ${data.PatientName} khỏi khoa ${data.DepartmentName}?`)) {
            $.ajax({
                url: `/api/patient_department_detail/${data.PatientId}/${data.DepartmentId}`,
                type: 'DELETE',
                success: function() {
                    location.reload(); // Simple reload for now
                    showAlert('Xóa thành công!', 'success');
                },
                error: function(xhr) {
                    const error = xhr.responseJSON?.error || 'Không thể xóa';
                    showAlert(error, 'danger');
                }
            });
        }
    }
    
    function showAssignmentModal(data = null) {
        const modal = new bootstrap.Modal(document.getElementById('assignmentModal'));
        const form = document.getElementById('assignment-form');
        
        if (data) {
            // Edit mode
            $('#patient-select').val(data.PatientId);
            $('#department-select').val(data.DepartmentId);
            $('#current-assignment').prop('checked', data.Current);
            
            // Store the original department ID for updates
            form.setAttribute('data-original-dept-id', data.DepartmentId);
            
            // Set the assigned date - convert to local datetime format
            if (data.At) {
                const date = new Date(data.At);
                // Format for datetime-local input (YYYY-MM-DDTHH:mm)
                const localDateTime = new Date(date.getTime() - (date.getTimezoneOffset() * 60000))
                    .toISOString().slice(0, 16);
                $('#assigned-date').val(localDateTime);
            }
            
            $('.modal-title').text('Sửa khoa cho người bệnh');
        } else {
            // Add mode
            form.reset();
            form.removeAttribute('data-original-dept-id');
            $('#current-assignment').prop('checked', true); // Default to current
            
            // Set current date and time as default
            const now = new Date();
            const localDateTime = new Date(now.getTime() - (now.getTimezoneOffset() * 60000))
                .toISOString().slice(0, 16);
            $('#assigned-date').val(localDateTime);
            
            $('.modal-title').text('Cho vào khoa mới');
        }
        
        modal.show();
    }
    
    function saveAssignment() {
        const form = document.getElementById('assignment-form');
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        // Convert checkbox value
        data.Current = $('#current-assignment').is(':checked');
        
        // Handle the assigned date
        const assignedDate = $('#assigned-date').val();
        if (assignedDate) {
            // Convert local datetime to ISO string for the server
            data.At = new Date(assignedDate).toISOString();
        }
        
        // Check if this is an edit and include original department ID
        const isEdit = $('.modal-title').text().includes('Sửa');
        if (isEdit) {
            const originalDeptId = form.getAttribute('data-original-dept-id');
            if (originalDeptId) {
                data.OriginalDepartmentId = originalDeptId;
            }
        }
        
        // Validate required fields
        if (!data.PatientId || !data.DepartmentId) {
            showAlert('Vui lòng chọn người bệnh và khoa', 'warning');
            return;
        }
        
        if (!assignedDate) {
            showAlert('Vui lòng chọn ngày và giờ vào khoa', 'warning');
            return;
        }
        
        // Validate that the date is not in the future
        const selectedDate = new Date(assignedDate);
        const now = new Date();
        if (selectedDate > now) {
            showAlert('Đã chọn thời gian ở tương lai', 'warning');
            return;
        }
        
        const method = isEdit ? 'PUT' : 'POST';
        
        console.log('Saving assignment:', data, 'Method:', method);
        
        $.ajax({
            url: '/api/patient_department_detail',
            type: method,
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(response) {
                bootstrap.Modal.getInstance(document.getElementById('assignmentModal')).hide();
                showAlert(isEdit ? 'Cập nhật thành công!' : 'Lưu thành công!', 'success');
                // Reload the page to refresh data
                setTimeout(() => location.reload(), 1000);
            },
            error: function(xhr) {
                let error = 'Failed to save assignment';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    error = xhr.responseJSON.error;
                } else if (xhr.status === 409) {
                    error = 'Người bệnh này đã được đưa vào khoa này';
                }
                showAlert(error, 'danger');
                console.error('Save assignment error:', xhr.responseJSON);
            }
        });
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
