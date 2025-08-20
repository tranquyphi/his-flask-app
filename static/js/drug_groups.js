/**
 * Drug Groups Management JavaScript
 * Handles CRUD operations for drug groups
 */

$(document).ready(function() {
    let table;
    let currentGroupId = null;
    
    // Initialize DataTable
    initializeTable();
    
    // Event Handlers
    setupEventHandlers();
    
    function initializeTable() {
        table = $('#drug-groups-table').DataTable({
            ajax: {
                url: '/api/drug-groups',
                type: 'GET',
                dataSrc: 'drug_groups'
            },
            columns: [
                { data: 'DrugGroupId', width: '80px' },
                { data: 'DrugGroupName' },
                { 
                    data: 'DrugGroupDescription',
                    defaultContent: '-',
                    render: function(data) {
                        return data || '-';
                    }
                },
                { 
                    data: 'drug_count',
                    render: function(data, type, row) {
                        const count = data || 0;
                        const badgeClass = count > 0 ? 'bg-primary' : 'bg-secondary';
                        return `<span class="badge ${badgeClass}">${count}</span>`;
                    },
                    orderable: true,
                    searchable: false,
                    width: '100px'
                },
                {
                    data: null,
                    orderable: false,
                    searchable: false,
                    width: '150px',
                    render: function(data, type, row) {
                        return `
                            <div class="btn-group" role="group">
                                <button class="btn btn-sm btn-outline-primary" 
                                        onclick="editGroup(${row.DrugGroupId}, '${row.DrugGroupName}', '${row.DrugGroupDescription || ''}')" 
                                        title="Chỉnh sửa">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger" 
                                        onclick="deleteGroup(${row.DrugGroupId}, '${row.DrugGroupName}')" 
                                        title="Xóa">
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
            dom: '<"d-flex justify-content-between align-items-center mb-3"<"d-flex align-items-center"l><"d-flex align-items-center"f>>rtip',
            language: {
                search: "Tìm kiếm:",
                lengthMenu: "Hiển thị _MENU_ nhóm",
                info: "Hiển thị _START_ đến _END_ của _TOTAL_ nhóm",
                infoEmpty: "Không có nhóm thuốc nào",
                infoFiltered: "(lọc từ _MAX_ tổng số nhóm)",
                emptyTable: "Chưa có nhóm thuốc nào",
                zeroRecords: "Không tìm thấy nhóm thuốc nào"
            }
        });
    }
    
    function setupEventHandlers() {
        // Search functionality
        $('#search-name').on('keyup', function() {
            table.column(1).search(this.value).draw();
        });
        
        // Form submission
        $('#groupForm').on('submit', function(e) {
            e.preventDefault();
            saveGroup();
        });
        
        // Reset form when modal is closed
        $('#groupModal').on('hidden.bs.modal', function() {
            resetForm();
        });
        
        // Delete confirmation
        $('#btn-confirm-delete').on('click', function() {
            if (currentGroupId) {
                confirmDelete();
            }
        });
    }
    
    function saveGroup() {
        const name = $('#groupName').val().trim();
        const description = $('#groupDescription').val().trim();
        
        if (!name) {
            showAlert('Vui lòng nhập tên nhóm thuốc', 'warning');
            return;
        }
        
        const data = {
            DrugGroupName: name,
            DrugGroupDescription: description || null
        };
        
        const url = currentGroupId ? `/api/drug-groups/${currentGroupId}` : '/api/drug-groups';
        const method = currentGroupId ? 'PUT' : 'POST';
        
        $.ajax({
            url: url,
            type: method,
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(response) {
                $('#groupModal').modal('hide');
                table.ajax.reload();
                showAlert(
                    currentGroupId ? 'Cập nhật nhóm thuốc thành công!' : 'Thêm nhóm thuốc thành công!', 
                    'success'
                );
            },
            error: function(xhr) {
                const errorMsg = xhr.responseJSON?.error || 'Có lỗi xảy ra khi lưu nhóm thuốc';
                showAlert(errorMsg, 'danger');
            }
        });
    }
    
    function resetForm() {
        currentGroupId = null;
        $('#groupForm')[0].reset();
        $('#modal-title').text('Thêm nhóm thuốc');
        $('#groupModal .modal-header i').removeClass('fa-edit').addClass('fa-plus');
    }
    
    function confirmDelete() {
        $.ajax({
            url: `/api/drug-groups/${currentGroupId}`,
            type: 'DELETE',
            success: function() {
                $('#deleteModal').modal('hide');
                table.ajax.reload();
                showAlert('Xóa nhóm thuốc thành công!', 'success');
                currentGroupId = null;
            },
            error: function(xhr) {
                const errorMsg = xhr.responseJSON?.error || 'Có lỗi xảy ra khi xóa nhóm thuốc';
                showAlert(errorMsg, 'danger');
            }
        });
    }
    
    function showAlert(message, type = 'info') {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        $('#alert-container').html(alertHtml);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            $('.alert').alert('close');
        }, 5000);
    }
    
    // Global functions for button clicks
    window.editGroup = function(id, name, description) {
        currentGroupId = id;
        $('#groupName').val(name);
        $('#groupDescription').val(description || '');
        $('#modal-title').text('Chỉnh sửa nhóm thuốc');
        $('#groupModal .modal-header i').removeClass('fa-plus').addClass('fa-edit');
        $('#groupModal').modal('show');
    };
    
    window.deleteGroup = function(id, name) {
        currentGroupId = id;
        $('#delete-group-name').text(name);
        $('#deleteModal').modal('show');
    };
});
