$(document).ready(function() {
    // Initialize DataTable
    const departmentsTable = $('#departmentsTable').DataTable({
        ajax: {
            url: '/api/departments',
            dataSrc: 'departments'
        },
        columns: [
            { data: 'DepartmentId' },
            { data: 'DepartmentName' },
            { data: 'DepartmentType' },
            { 
                data: null,
                render: function(data, type, row) {
                    const count = row.current_staff_count || 0;
                    return `<span class="badge bg-info">${count}</span>`;
                }
            },
            { 
                data: null,
                render: function(data, type, row) {
                    const count = row.current_patient_count || 0;
                    return `<span class="badge bg-warning">${count}</span>`;
                }
            },
            { 
                data: null,
                render: function(data, type, row) {
                    const count = row.total_visits || 0;
                    return `<span class="badge bg-secondary">${count}</span>`;
                }
            },
            {
                data: null,
                render: function(data, type, row) {
                    return `
                        <div class="btn-group btn-group-sm" role="group">
                            <button type="button" class="btn btn-outline-primary btn-sm view-btn" data-id="${row.DepartmentId}" title="View Details">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button type="button" class="btn btn-outline-warning btn-sm edit-btn" data-id="${row.DepartmentId}" title="Edit">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button type="button" class="btn btn-outline-danger btn-sm delete-btn" data-id="${row.DepartmentId}" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    `;
                }
            }
        ],
        order: [[1, 'asc']],
        pageLength: 25,
        responsive: true,
        language: {
            search: "Search:",
            lengthMenu: "Show _MENU_ departments per page",
            info: "Showing _START_ to _END_ of _TOTAL_ departments",
            paginate: {
                first: "First",
                last: "Last",
                next: "Next",
                previous: "Previous"
            }
        }
    });

    // Load department statistics
    function loadStatistics() {
        $.ajax({
            url: '/api/departments',
            method: 'GET',
            success: function(response) {
                const departments = response.departments || [];
                $('#totalDepartments').text(departments.length);
                
                // Calculate totals from all departments
                let totalStaff = 0;
                let totalPatients = 0;
                let totalVisits = 0;
                
                // Load detailed stats for each department
                departments.forEach(function(dept) {
                    $.ajax({
                        url: `/api/departments/${dept.DepartmentId}`,
                        method: 'GET',
                        success: function(deptResponse) {
                            const deptData = deptResponse.department;
                            totalStaff += deptData.current_staff_count || 0;
                            totalPatients += deptData.current_patient_count || 0;
                            totalVisits += deptData.total_visits || 0;
                            
                            // Update table with real data
                            const row = departmentsTable.row(`[data-id="${dept.DepartmentId}"]`);
                            if (row.length) {
                                row.data().current_staff_count = deptData.current_staff_count || 0;
                                row.data().current_patient_count = deptData.current_patient_count || 0;
                                row.data().total_visits = deptData.total_visits || 0;
                                departmentsTable.draw();
                            }
                            
                            // Update statistics display
                            $('#totalStaff').text(totalStaff);
                            $('#totalPatients').text(totalPatients);
                            $('#totalVisits').text(totalVisits);
                        },
                        error: function() {
                            console.log(`Failed to load stats for department ${dept.DepartmentId}`);
                        }
                    });
                });
            },
            error: function() {
                showError('Failed to load department statistics');
            }
        });
    }

    // Search functionality
    $('#searchInput').on('keyup', function() {
        departmentsTable.search(this.value).draw();
    });

    // Department type filter
    $('#departmentTypeFilter').on('change', function() {
        const filterValue = $(this).val();
        if (filterValue) {
            departmentsTable.column(2).search(filterValue).draw();
        } else {
            departmentsTable.column(2).search('').draw();
        }
    });

    // Clear filters
    $('#clearFiltersBtn').on('click', function() {
        $('#searchInput').val('');
        $('#departmentTypeFilter').val('');
        departmentsTable.search('').columns().search('').draw();
    });

    // Export functionality
    $('#exportBtn').on('click', function() {
        const data = departmentsTable.data().toArray();
        const csv = convertToCSV(data);
        downloadCSV(csv, 'departments.csv');
    });

    // Add new department
    $('#addDepartmentBtn').on('click', function() {
        $('#departmentModalTitle').text('Add New Department');
        $('#departmentForm')[0].reset();
        $('#departmentId').val('');
        $('#departmentModal').modal('show');
    });

    // Edit department
    $(document).on('click', '.edit-btn', function() {
        const deptId = $(this).data('id');
        loadDepartmentForEdit(deptId);
    });

    // View department details
    $(document).on('click', '.view-btn', function() {
        const deptId = $(this).data('id');
        viewDepartmentDetails(deptId);
    });

    // Delete department
    $(document).on('click', '.delete-btn', function() {
        const deptId = $(this).data('id');
        const deptName = $(this).closest('tr').find('td:eq(1)').text();
        showDeleteConfirmation(deptId, deptName);
    });

    // Save department
    $('#saveDepartmentBtn').on('click', function() {
        saveDepartment();
    });

    // Confirm delete
    $('#confirmDeleteBtn').on('click', function() {
        const deptId = $('#deleteModal').data('deptId');
        deleteDepartment(deptId);
    });

    // Load department for editing
    function loadDepartmentForEdit(deptId) {
        $.ajax({
            url: `/api/departments/${deptId}`,
            method: 'GET',
            success: function(response) {
                const dept = response.department;
                $('#departmentId').val(dept.DepartmentId);
                $('#departmentName').val(dept.DepartmentName);
                $('#departmentType').val(dept.DepartmentType);
                $('#departmentModalTitle').text('Edit Department');
                $('#departmentModal').modal('show');
            },
            error: function() {
                showError('Failed to load department for editing');
            }
        });
    }

    // View department details
    function viewDepartmentDetails(deptId) {
        // Redirect to department details page or show in modal
        window.location.href = `/department_patients/${deptId}`;
    }

    // Save department
    function saveDepartment() {
        const deptId = $('#departmentId').val();
        const formData = {
            DepartmentName: $('#departmentName').val().trim(),
            DepartmentType: $('#departmentType').val()
        };

        // Validation
        if (!formData.DepartmentName) {
            showFieldError('#departmentName', 'Department name is required');
            return;
        }
        if (!formData.DepartmentType) {
            showFieldError('#departmentType', 'Department type is required');
            return;
        }

        const url = deptId ? `/api/departments/${deptId}` : '/api/departments';
        const method = deptId ? 'PUT' : 'POST';

        // Show loading state
        const $btn = $('#saveDepartmentBtn');
        const $spinner = $btn.find('.spinner-border');
        $btn.prop('disabled', true);
        $spinner.removeClass('d-none');

        $.ajax({
            url: url,
            method: method,
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                $('#departmentModal').modal('hide');
                departmentsTable.ajax.reload();
                loadStatistics();
                showSuccess(deptId ? 'Department updated successfully' : 'Department created successfully');
            },
            error: function(xhr) {
                const error = xhr.responseJSON?.error || 'Failed to save department';
                showError(error);
            },
            complete: function() {
                $btn.prop('disabled', false);
                $spinner.addClass('d-none');
            }
        });
    }

    // Delete department
    function deleteDepartment(deptId) {
        $.ajax({
            url: `/api/departments/${deptId}`,
            method: 'DELETE',
            success: function() {
                $('#deleteModal').modal('hide');
                departmentsTable.ajax.reload();
                loadStatistics();
                showSuccess('Department deleted successfully');
            },
            error: function(xhr) {
                const error = xhr.responseJSON?.error || 'Failed to delete department';
                showError(error);
            }
        });
    }

    // Show delete confirmation
    function showDeleteConfirmation(deptId, deptName) {
        $('#deleteItemName').text(deptName);
        $('#deleteModal').data('deptId', deptId);
        $('#deleteModal').modal('show');
    }

    // Utility functions
    function showSuccess(message) {
        $('#successMessage').text(message);
        const toast = new bootstrap.Toast(document.getElementById('successToast'));
        toast.show();
    }

    function showError(message) {
        $('#errorMessage').text(message);
        const toast = new bootstrap.Toast(document.getElementById('errorToast'));
        toast.show();
    }

    function showFieldError(field, message) {
        $(field).addClass('is-invalid');
        $(field).siblings('.invalid-feedback').text(message);
    }

    function convertToCSV(data) {
        const headers = ['ID', 'Department Name', 'Type', 'Current Staff', 'Current Patients', 'Total Visits'];
        const csvContent = [
            headers.join(','),
            ...data.map(row => [
                row.DepartmentId,
                `"${row.DepartmentName}"`,
                row.DepartmentType,
                row.current_staff_count || 0,
                row.current_patient_count || 0,
                row.total_visits || 0
            ].join(','))
        ].join('\n');
        return csvContent;
    }

    function downloadCSV(csv, filename) {
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', filename);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }

    // Initialize page
    loadStatistics();
});
