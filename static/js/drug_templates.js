/**
 * Drug Templates Management JavaScript
 * Based on sign_templates.js pattern
 */

$(document).ready(function() {
    let templatesTable;
    let departments = {};
    
    // Initialize DataTable
    initializeTemplatesTable();
    
    // Load departments
    loadDepartments();
    
    // Event handlers
    setupEventHandlers();
    
    function initializeTemplatesTable() {
        templatesTable = $('#templates-table').DataTable({
            ajax: {
                url: '/api/drug-templates',
                type: 'GET',
                dataSrc: 'drug_templates',
                error: function(xhr, error, thrown) {
                    console.error('Error loading drug templates:', error);
                    showAlert('Failed to load drug templates', 'danger');
                }
            },
            columns: [
                { data: 'DrugTemplateId', width: '80px' },
                { 
                    data: 'DrugTemplateName',
                    render: function(data, type, row) {
                        return `<a href="/drug-templates/${row.DrugTemplateId}/details" class="text-decoration-none fw-bold">${data}</a>`;
                    }
                },
                { data: 'DepartmentName', defaultContent: '-' },
                { 
                    data: 'DrugTemplateType',
                    render: function(data, type, row) {
                        const typeLabels = {
                            'BA': '<span class="badge bg-primary">Bệnh án</span>',
                            'TD': '<span class="badge bg-success">Tự động</span>',
                            'PK': '<span class="badge bg-info">Phòng khám</span>',
                            'CC': '<span class="badge bg-warning text-dark">Cấp cứu</span>'
                        };
                        return typeLabels[data] || data;
                    }
                },
                {
                    data: null,
                    orderable: false,
                    searchable: false,
                    width: '120px',
                    render: function(data, type, row) {
                        return `
                            <div class="btn-group btn-group-sm">
                                <button class="btn btn-outline-primary btn-sm" onclick="editTemplate(${row.DrugTemplateId})" title="Sửa">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-outline-danger btn-sm" onclick="deleteTemplate(${row.DrugTemplateId}, '${row.DrugTemplateName}')" title="Xóa">
                                    <i class="fas fa-trash"></i>
                                </button>
                                <a href="/drug-templates/${row.DrugTemplateId}/details" class="btn btn-outline-info btn-sm" title="Chi tiết">
                                    <i class="fas fa-list"></i>
                                </a>
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
                lengthMenu: "Hiển thị _MENU_ mẫu",
                info: "Hiển thị _START_ đến _END_ của _TOTAL_ mẫu",
                infoEmpty: "Không có mẫu nào",
                infoFiltered: "(lọc từ _MAX_ tổng số mẫu)",
                emptyTable: "Không có dữ liệu",
                zeroRecords: "Không tìm thấy mẫu nào"
            }
        });
    }
    
    function loadDepartments() {
        $.ajax({
            url: '/api/departments',
            type: 'GET',
            success: function(response) {
                const deptSelect = $('#DepartmentId');
                const deptFilter = $('#filter-department');
                
                deptSelect.empty().append('<option value="">Chọn khoa</option>');
                deptFilter.empty().append('<option value="">Khoa (tất cả)</option>');
                
                if (response.departments) {
                    response.departments.forEach(function(dept) {
                        departments[dept.DepartmentId] = dept.DepartmentName;
                        deptSelect.append(`<option value="${dept.DepartmentId}">${dept.DepartmentName}</option>`);
                        deptFilter.append(`<option value="${dept.DepartmentId}">${dept.DepartmentName}</option>`);
                    });
                }
            },
            error: function() {
                console.error('Failed to load departments');
            }
        });
    }
    
    function setupEventHandlers() {
        // Add template button
        $('#btn-add-template').on('click', function() {
            showTemplateModal();
        });
        
        // Save template button
        $('#btn-save-template').on('click', function() {
            saveTemplate();
        });
        
        // Search input
        $('#search-name').on('keyup', function() {
            templatesTable.column(1).search(this.value).draw();
        });
        
        // Department filter
        $('#filter-department').on('change', function() {
            const deptId = this.value;
            const deptName = deptId ? departments[deptId] : '';
            templatesTable.column(2).search(deptName).draw();
        });
        
        // Type filter
        $('#filter-type').on('change', function() {
            const typeValue = this.value;
            let searchTerm = '';
            if (typeValue) {
                const typeLabels = {
                    'BA': 'Bệnh án',
                    'TD': 'Tự động', 
                    'PK': 'Phòng khám',
                    'CC': 'Cấp cứu'
                };
                searchTerm = typeLabels[typeValue] || typeValue;
            }
            templatesTable.column(3).search(searchTerm).draw();
        });
        
        // Refresh button
        $('#btn-refresh').on('click', function() {
            templatesTable.ajax.reload();
        });
    }
    
    function showTemplateModal(template = null) {
        const isEdit = template !== null;
        
        $('#modalTitle').text(isEdit ? 'Sửa mẫu thuốc' : 'Thêm mẫu thuốc');
        
        // Reset form
        $('#template-form')[0].reset();
        $('#template-form .form-control, #template-form .form-select').removeClass('is-invalid');
        
        if (isEdit) {
            $('#DrugTemplateId').val(template.DrugTemplateId);
            $('#DrugTemplateName').val(template.DrugTemplateName);
            $('#DepartmentId').val(template.DepartmentId);
            $('#DrugTemplateType').val(template.DrugTemplateType);
        } else {
            $('#DrugTemplateId').val('');
        }
        
        $('#templateModal').modal('show');
        
        // Focus on name input
        setTimeout(() => {
            $('#DrugTemplateName').focus();
        }, 500);
    }
    
    function saveTemplate() {
        const templateId = $('#DrugTemplateId').val();
        const isEdit = templateId !== '';
        
        const templateData = {
            DrugTemplateName: $('#DrugTemplateName').val().trim(),
            DepartmentId: parseInt($('#DepartmentId').val()),
            DrugTemplateType: $('#DrugTemplateType').val()
        };
        
        // Validation
        if (!templateData.DrugTemplateName) {
            showAlert('Vui lòng nhập tên mẫu', 'warning');
            $('#DrugTemplateName').addClass('is-invalid');
            return;
        }
        
        if (!templateData.DepartmentId) {
            showAlert('Vui lòng chọn khoa', 'warning');
            $('#DepartmentId').addClass('is-invalid');
            return;
        }
        
        if (!templateData.DrugTemplateType) {
            showAlert('Vui lòng chọn loại mẫu', 'warning');
            $('#DrugTemplateType').addClass('is-invalid');
            return;
        }
        
        // Show loading state
        const saveBtn = $('#btn-save-template');
        const originalText = saveBtn.html();
        saveBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-2"></span>Đang lưu...');
        
        $.ajax({
            url: isEdit ? `/api/drug-templates/${templateId}` : '/api/drug-templates',
            type: isEdit ? 'PUT' : 'POST',
            contentType: 'application/json',
            data: JSON.stringify(templateData),
            success: function(response) {
                $('#templateModal').modal('hide');
                templatesTable.ajax.reload();
                showAlert(isEdit ? 'Cập nhật mẫu thành công!' : 'Thêm mẫu thành công!', 'success');
            },
            error: function(xhr) {
                const errorMsg = xhr.responseJSON?.error || 'Có lỗi xảy ra khi lưu mẫu';
                showAlert(errorMsg, 'danger');
            },
            complete: function() {
                saveBtn.prop('disabled', false).html(originalText);
            }
        });
    }
    
    function showAlert(message, type = 'info') {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
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
    
    // Global functions for button actions
    window.editTemplate = function(templateId) {
        const template = templatesTable.rows().data().toArray().find(t => t.DrugTemplateId === templateId);
        if (template) {
            showTemplateModal(template);
        }
    };
    
    window.deleteTemplate = function(templateId, templateName) {
        if (confirm(`Bạn có chắc chắn muốn xóa mẫu "${templateName}"?`)) {
            $.ajax({
                url: `/api/drug-templates/${templateId}`,
                type: 'DELETE',
                success: function() {
                    templatesTable.ajax.reload();
                    showAlert('Xóa mẫu thành công!', 'success');
                },
                error: function(xhr) {
                    const errorMsg = xhr.responseJSON?.error || 'Có lỗi xảy ra khi xóa mẫu';
                    showAlert(errorMsg, 'danger');
                }
            });
        }
    };
});
