/**
 * Staff Management JavaScript
 * Handles staff CRUD operations and department assignments
 * Using DataTables for data display
 */

// Global variables
let staffTable;
let departments = [];
let currentStaffId = null;

$(document).ready(function() {
    // Show loading overlay
    $('#loading-overlay').show();
    
    // Initialize the staff table
    initStaffTable();
    
    // Load departments for dropdown
    loadDepartments();
    
    // Set up event listeners
    $('#add-staff-btn').on('click', showAddStaffModal);
    
    // Form submission handlers
    $('#staff-form').on('submit', function(e) {
        e.preventDefault();
        saveStaff();
    });
    
    $('#assignment-form').on('submit', function(e) {
        e.preventDefault();
        saveDepartmentAssignment();
    });
    
    // Delete confirmation handler
    $('#confirm-delete-btn').on('click', deleteStaff);
    
    // Table button handlers (delegated)
    $('#staff-table').on('click', '.btn-edit', function() {
        const staffId = $(this).data('staff-id');
        editStaff(staffId);
    });
    
    $('#staff-table').on('click', '.btn-delete', function() {
        const staffId = $(this).data('staff-id');
        confirmDelete(staffId);
    });
    
    $('#staff-table').on('click', '.btn-history', function() {
        const staffId = $(this).data('staff-id');
        viewHistory(staffId);
    });
    
    $('#staff-table').on('click', '.btn-assign', function() {
        const staffId = $(this).data('staff-id');
        showDepartmentAssignmentModal(staffId);
    });
});

/**
 * Initialize DataTables for displaying staff data
 */
function initStaffTable() {
    // Define position labels
    const positionLabels = {
        'NV': 'Nhân viên',
        'TK': 'Trưởng khoa',
        'PK': 'Phó khoa',
        'DDT': 'Điều dưỡng trưởng',
        'KTVT': 'Kỹ thuật viên trưởng',
        'KHAC': 'Khác'
    };
    
    // Initialize DataTable
    staffTable = $('#staff-table').DataTable({
        ajax: {
            url: "/api/staff",
            method: "GET",
            dataSrc: "staff"
        },
        columns: [
            { 
                data: "StaffId",
                title: "ID", 
                width: "5%"
            },
            { 
                data: "StaffName", 
                title: "Name",
                width: "20%"
            },
            { 
                data: "StaffRole", 
                title: "Role",
                width: "15%"
            },
            { 
                data: "DepartmentName", 
                title: "Department",
                width: "20%",
                render: function(data, type, row) {
                    return data || '<em class="text-muted">Not assigned</em>';
                }
            },
            { 
                data: "Position",
                title: "Position",
                width: "15%", 
                render: function(data, type, row) {
                    if (type === 'sort' || type === 'type') {
                        return data || '';
                    }
                    return data ? `${data} - ${positionLabels[data] || ''}` : 'N/A';
                }
            },
            { 
                data: "StaffAvailable", 
                title: "Availability",
                width: "10%",
                render: function(data, type, row) {
                    if (type === 'sort' || type === 'type') {
                        return data ? 1 : 0;
                    }
                    return data ? 
                        '<span class="badge bg-success">Available</span>' : 
                        '<span class="badge bg-danger">Not Available</span>';
                }
            },
            { 
                data: null, 
                title: "Actions",
                width: "15%",
                orderable: false,
                className: 'text-center',
                render: function(data, type, row) {
                    return `
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-info btn-history" data-staff-id="${row.StaffId}" title="View History">
                            <i class="fas fa-history"></i>
                        </button>
                        <button class="btn btn-outline-primary btn-edit" data-staff-id="${row.StaffId}" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-success btn-assign" data-staff-id="${row.StaffId}" title="Assign Department">
                            <i class="fas fa-hospital"></i>
                        </button>
                        <button class="btn btn-outline-danger btn-delete" data-staff-id="${row.StaffId}" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>`;
                }
            }
        ],
        responsive: true,
        lengthMenu: [5, 10, 25, 50],
        pageLength: 10,
        language: {
            emptyTable: "No staff records found",
            zeroRecords: "No matching staff records found"
        },
        drawCallback: function() {
            $('#loading-overlay').hide();
        }
    });
}

/**
 * Load departments for the dropdown menu
 */
function loadDepartments() {
    $.ajax({
        url: '/api/departments',
        method: 'GET',
        success: function(response) {
            departments = response.departments;
            const departmentSelect = $('#department-id');
            
            // Clear existing options
            departmentSelect.empty().append('<option value="">Select a department</option>');
            
            // Add department options
            departments.forEach(function(dept) {
                departmentSelect.append(
                    `<option value="${dept.DepartmentId}">${dept.DepartmentName} (${dept.DepartmentType || 'N/A'})</option>`
                );
            });
        },
        error: function(error) {
            console.error('Error loading departments:', error);
            showAlert('danger', 'Failed to load departments. Please refresh the page.');
            
            // Hide loading overlay if visible
            $('#loading-overlay').hide();
        }
    });
}

/**
 * Show the modal for adding a new staff member
 */
function showAddStaffModal() {
    currentStaffId = null;
    
    // Update modal title
    $('#staff-modal-title').text('Add New Staff');
    
    // Reset form
    $('#staff-form')[0].reset();
    $('#staff-id').val('');
    
    // Show department field for new staff
    $('#department-container').removeClass('d-none');
    
    // Show the modal
    $('#staff-modal').modal('show');
}

/**
 * Show the modal for editing an existing staff member
 */
function editStaff(staffId) {
    currentStaffId = staffId;
    
    // Show loading overlay
    $('#loading-overlay').show();
    
    // Fetch staff data
    $.ajax({
        url: `/api/staff/${staffId}`,
        method: 'GET',
        success: function(response) {
            const staff = response.staff;
            
            // Update modal title
            $('#staff-modal-title').text(`Edit Staff: ${staff.StaffName}`);
            
            // Populate form fields
            $('#staff-id').val(staff.StaffId);
            $('#staff-name').val(staff.StaffName);
            $('#staff-role').val(staff.StaffRole);
            $('#department-id').val(staff.DepartmentId || '');
            $('#position').val(staff.Position || '');
            $('#staff-available').prop('checked', staff.StaffAvailable);
            
            // For editing existing staff, hide department field as it should be managed through assignments
            if (staff.DepartmentId) {
                $('#current-department-text').text(staff.DepartmentName);
                $('#current-department-container').removeClass('d-none');
                $('#department-container').addClass('d-none');
            } else {
                $('#current-department-container').addClass('d-none');
                $('#department-container').removeClass('d-none');
            }
            
            // Hide loading overlay
            $('#loading-overlay').hide();
            
            // Show the modal
            $('#staff-modal').modal('show');
        },
        error: function(error) {
            console.error('Error fetching staff details:', error);
            showAlert('danger', 'Failed to load staff details. Please try again.');
            
            // Hide loading overlay
            $('#loading-overlay').hide();
        }
    });
}

/**
 * Save or update staff member
 */
function saveStaff() {
    // Validate form
    const form = $('#staff-form')[0];
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    // Show loading overlay
    $('#loading-overlay').show();
    
    // Gather form data
    const staffData = {
        StaffName: $('#staff-name').val(),
        StaffRole: $('#staff-role').val(),
        StaffAvailable: $('#staff-available').is(':checked'),
    };
    
    // For new staff, include department information if provided
    if (!currentStaffId) {
        const departmentId = $('#department-id').val();
        const position = $('#position').val();
        
        if (departmentId) {
            staffData.DepartmentId = departmentId;
            staffData.Position = position || null;
        }
    }
    
    // Determine if creating or updating
    const isNewStaff = !currentStaffId;
    const url = isNewStaff ? '/api/staff' : `/api/staff/${currentStaffId}`;
    const method = isNewStaff ? 'POST' : 'PUT';
    
    // If updating, add staff ID to data
    if (!isNewStaff) {
        staffData.StaffId = currentStaffId;
    }
    
    // Send request
    $.ajax({
        url: url,
        method: method,
        contentType: 'application/json',
        data: JSON.stringify(staffData),
        success: function(response) {
            // Hide the modal
            $('#staff-modal').modal('hide');
            
            // Refresh the table
            staffTable.ajax.reload();
            
            // Show success message
            showAlert('success', isNewStaff ? 'Staff created successfully' : 'Staff updated successfully');
            
            // Hide loading overlay
            $('#loading-overlay').hide();
        },
        error: function(error) {
            console.error('Error saving staff:', error);
            showAlert('danger', `Failed to ${isNewStaff ? 'create' : 'update'} staff. Please try again.`);
            
            // Hide loading overlay
            $('#loading-overlay').hide();
        }
    });
}

/**
 * Show confirmation dialog for deleting staff
 */
function confirmDelete(staffId) {
    currentStaffId = staffId;
    
    // Load staff details for confirmation message
    $.ajax({
        url: `/api/staff/${staffId}`,
        method: 'GET',
        success: function(response) {
            const staff = response.staff;
            
            // Set confirmation message
            $('#delete-confirmation-message').html(
                `Are you sure you want to delete <strong>${staff.StaffName}</strong>? ` +
                `This action cannot be undone.`
            );
            
            // Show the confirmation modal
            $('#delete-modal').modal('show');
        },
        error: function(error) {
            console.error('Error loading staff details:', error);
            showAlert('danger', 'Failed to load staff details. Please try again.');
        }
    });
}

/**
 * Delete staff after confirmation
 */
function deleteStaff() {
    if (!currentStaffId) return;
    
    // Show loading overlay
    $('#loading-overlay').show();
    
    $.ajax({
        url: `/api/staff/${currentStaffId}`,
        method: 'DELETE',
        success: function(response) {
            // Hide the confirmation modal
            $('#delete-modal').modal('hide');
            
            // Refresh the table
            staffTable.ajax.reload();
            
            // Show success message
            showAlert('success', 'Staff deleted successfully');
            
            // Hide loading overlay
            $('#loading-overlay').hide();
        },
        error: function(error) {
            console.error('Error deleting staff:', error);
            
            // Hide the confirmation modal
            $('#delete-modal').modal('hide');
            
            // Show error message
            showAlert('danger', 'Failed to delete staff. Please try again.');
            
            // Hide loading overlay
            $('#loading-overlay').hide();
        }
    });
}

/**
 * Navigate to staff history page
 */
function viewHistory(staffId) {
    window.location.href = `/staff/history/${staffId}`;
}

/**
 * Show department assignment modal
 */
function showDepartmentAssignmentModal(staffId) {
    currentStaffId = staffId;
    
    // Reset form
    $('#assignment-form')[0].reset();
    
    // Load staff details
    showLoadingOverlay();
    
    // Load departments for dropdown
    $.ajax({
        url: '/api/departments',
        method: 'GET',
        success: function(response) {
            departments = response.departments;
            const departmentSelect = $('#department');
            
            // Clear existing options
            departmentSelect.empty().append('<option value="">Select a department</option>');
            
            // Add department options
            departments.forEach(function(dept) {
                departmentSelect.append(
                    `<option value="${dept.DepartmentId}">${dept.DepartmentName} (${dept.DepartmentType || 'N/A'})</option>`
                );
            });
            
            // Load staff details
            $.ajax({
                url: `/api/staff/${staffId}`,
                method: 'GET',
                success: function(response) {
                    const staff = response.staff;
                    
                    // Update modal title
                    $('#assignment-modal-title').text(`Assign Department: ${staff.StaffName}`);
                    
                    // Show current department if exists
                    if (staff.DepartmentId) {
                        $('#current-department').text(staff.DepartmentName);
                        $('#current-department-container').removeClass('d-none');
                        
                        // Pre-select current department in dropdown
                        $('#department').val(staff.DepartmentId);
                        $('#position').val(staff.Position || '');
                    } else {
                        $('#current-department-container').addClass('d-none');
                    }
                    
                    // Show modal
                    $('#assignment-modal').modal('show');
                    
                    hideLoadingOverlay();
                },
                error: function(error) {
                    console.error('Error loading staff:', error);
                    showAlert('danger', 'Failed to load staff data. Please try again.');
                    hideLoadingOverlay();
                }
            });
        },
        error: function(error) {
            console.error('Error loading departments:', error);
            showAlert('danger', 'Failed to load departments. Please try again.');
            hideLoadingOverlay();
        }
    });
}

/**
 * Save department assignment
 */
function saveDepartmentAssignment() {
    const departmentId = $('#department').val();
    const position = $('#position').val();
    
    if (!departmentId) {
        showAlert('warning', 'Please select a department.', 'assignment-alert');
        return;
    }
    
    const assignmentData = {
        DepartmentId: departmentId,
        Position: position
    };
    
    // Show loading overlay
    showLoadingOverlay();
    
    $.ajax({
        url: `/api/staff/${currentStaffId}/department`,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(assignmentData),
        success: function(response) {
            // Hide modal
            $('#assignment-modal').modal('hide');
            
            // Refresh data table
            staffTable.ajax.reload();
            
            // Show success message
            showAlert('success', 'Department assignment updated successfully!');
            
            hideLoadingOverlay();
        },
        error: function(error) {
            console.error('Error assigning department:', error);
            showAlert('danger', 'Failed to update department assignment. Please try again.', 'assignment-alert');
            hideLoadingOverlay();
        }
    });
}

/**
 * Show alert message
 */
function showAlert(type, message, targetId = 'main-alert') {
    const alertElement = $(`#${targetId}`);
    
    // Set message and type
    alertElement.html(`
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `);
    
    // Show alert
    alertElement.removeClass('d-none');
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        alertElement.find('.alert').alert('close');
    }, 5000);
}

/**
 * Show loading overlay
 */
function showLoadingOverlay() {
    $('#loading-overlay').show();
}

/**
 * Hide loading overlay
 */
function hideLoadingOverlay() {
    $('#loading-overlay').hide();
}
