/**
 * Staff Department History JavaScript
 * Handles loading and displaying staff department history
 */

// Define history table variable
let historyTable;

$(document).ready(function() {
    // Staff ID is defined in the HTML inline script
    if (!staffId || isNaN(staffId)) {
        showErrorState('Invalid staff ID');
        return;
    }
    
    // Show loading overlay
    $('#loading-overlay').show();
    
    // Load staff details
    loadStaffInformation();
    
    // Load department assignment history
    loadAssignmentHistory();
});

/**
 * Load staff information
 */
function loadStaffInformation() {
    $.ajax({
        url: `/api/staff/${staffId}`,
        method: 'GET',
        success: function(response) {
            const staff = response.staff;
            
            // Update staff name in header
            $('#staff-name').text(staff.StaffName);
            
            // Update staff info text
            $('#staffInfo').html(`
                <i class="fas fa-id-badge me-2"></i> ID: <strong>${staff.StaffId}</strong>
                ${staff.DepartmentName ? 
                    ` | <i class="fas fa-hospital me-2"></i> Current Department: <strong>${staff.DepartmentName}</strong>` : 
                    ' | <i class="fas fa-info-circle me-2"></i> <em>No current department assignment</em>'
                }
            `);
            
            // Update role badge
            $('#staff-role-text').text(staff.StaffRole);
            $('#staff-role-badge').removeClass('d-none');
        },
        error: function(error) {
            console.error('Error loading staff details:', error);
            $('#staffInfo').html(
                '<span class="text-danger"><i class="fas fa-exclamation-triangle me-2"></i> ' +
                'Error loading staff information. Please try again.</span>'
            );
            
            // Show error state
            showErrorState('Failed to load staff details');
        }
    });
}

/**
 * Load department assignment history
 */
function loadAssignmentHistory() {
    $.ajax({
        url: `/api/staff/${staffId}/history`,
        method: 'GET',
        success: function(response) {
            // Hide loading overlay
            $('#loading-overlay').hide();
            
            if (response.history.length === 0) {
                showEmptyState();
            } else {
                initializeHistoryTable(response.history);
            }
        },
        error: function(error) {
            console.error('Error loading assignment history:', error);
            
            // Hide loading overlay
            $('#loading-overlay').hide();
            
            // Show error state
            showErrorState('Failed to load assignment history');
        }
    });
}

/**
 * Initialize history data table 
 */
function initializeHistoryTable(data) {
    const positionLabels = {
        'NV': 'Nhân viên',
        'TK': 'Trưởng khoa',
        'PK': 'Phó khoa',
        'DDT': 'Điều dưỡng trưởng',
        'KTVT': 'Kỹ thuật viên trưởng',
        'KHAC': 'Khác'
    };
    
    historyTable = $('#history-table').DataTable({
        data: data,
        columns: [
            { 
                data: 'DepartmentName',
                title: 'Department'
            },
            {
                data: 'Position',
                title: 'Position',
                render: function(data, type, row) {
                    if (type === 'sort' || type === 'type') {
                        return data || '';
                    }
                    return data ? `${data} - ${positionLabels[data] || ''}` : 'N/A';
                }
            },
            {
                data: 'Current',
                title: 'Status',
                render: function(data, type, row) {
                    if (type === 'sort' || type === 'type') {
                        return data ? 1 : 0;
                    }
                    return data ? 
                        '<span class="badge bg-success">Current</span>' : 
                        '<span class="badge bg-secondary">Previous</span>';
                }
            }
        ],
        createdRow: function(row, data, dataIndex) {
            if (data.Current) {
                $(row).addClass('current-assignment');
            } else {
                $(row).addClass('history-assignment');
            }
        },
        order: [[2, 'desc'], [0, 'asc']],
        responsive: true,
        language: {
            emptyTable: "No department assignments found",
            zeroRecords: "No matching assignments found"
        },
        dom: 'Bfrtip',
        buttons: [
            {
                text: '<i class="fas fa-print"></i> Print',
                className: 'btn btn-sm btn-secondary',
                action: function(e, dt, node, config) {
                    window.print();
                }
            }
        ]
    });
}

/**
 * Format position for display
 */
function formatPosition(position) {
    if (!position) return 'N/A';
    
    const positionLabels = {
        'NV': 'Nhân viên',
        'TK': 'Trưởng khoa',
        'PK': 'Phó khoa',
        'DDT': 'Điều dưỡng trưởng',
        'KTVT': 'Kỹ thuật viên trưởng',
        'KHAC': 'Khác'
    };
    
    return `${position} - ${positionLabels[position] || ''}`;
}

/**
 * Show empty state
 */
function showEmptyState() {
    $('#history-table').closest('.card').addClass('d-none');
    $('#empty-state').removeClass('d-none');
}

/**
 * Show error state
 */
function showErrorState(errorMessage) {
    $('#history-table').closest('.card').addClass('d-none');
    $('#error-state').removeClass('d-none');
    $('#error-message').text(errorMessage || 'An error occurred while loading data.');
}
