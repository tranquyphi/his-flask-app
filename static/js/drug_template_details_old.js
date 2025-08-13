/**
 * Drug Template Details Management JavaScript
 * Based on sign_template_details.js pattern
 */

$(document).ready(function() {
    let drugsTable;
    let templateId;
    let drugGroups = new Set();
    let formulations = new Set();
    
    // Get template ID from URL
    templateId = getTemplateIdFromUrl();
    
    if (templateId) {
        // Load template information
        loadTemplateInfo();
        
        // Initialize table
        initializeDrugsTable();
        
        // Setup event handlers
        setupEventHandlers();
    } else {
        showAlert('Template ID not found', 'danger');
    }
    
    function getTemplateIdFromUrl() {
        const path = window.location.pathname;
        const match = path.match(/\/drug-templates\/(\d+)\/details/);
        return match ? parseInt(match[1]) : null;
    }
    
    function loadTemplateInfo() {
        $.ajax({
            url: `/api/drug-templates/${templateId}`,
            type: 'GET',
            success: function(response) {
                if (response.drug_template) {
                    const template = response.drug_template;
                    $('#template-id').text(template.DrugTemplateId);
                    $('#template-name').text(template.DrugTemplateName);
                    $('#department-name').text(template.DepartmentName || 'N/A');
                    document.title = `Chi tiết mẫu thuốc - ${template.DrugTemplateName}`;
                }
            },
            error: function() {
                showAlert('Failed to load template information', 'danger');
            }
        });
    }
    
    function initializeDrugsTable() {
        drugsTable = $('#drugs-table').DataTable({
            ajax: {
                url: `/api/drug-template-details?template_id=${templateId}`,
                type: 'GET',
                dataSrc: function(json) {
                    // Populate filter options from data
                    populateFilterOptions(json.drug_template_details || []);
                    return json.drug_template_details || [];
                },
                error: function(xhr, error, thrown) {
                    console.error('Error loading drugs:', error);
                    showAlert('Failed to load drugs data', 'danger');
                }
            },
            columns: [
                { data: 'DrugId', width: '80px' },
                { data: 'DrugName' },
                { 
                    data: 'DrugChemical',
                    defaultContent: '-',
                    render: function(data) {
                        return data || '-';
                    }
                },
                { 
                    data: 'DrugGroup',
                    defaultContent: '-',
                    render: function(data) {
                        if (data) {
                            return `<span class="badge bg-info">${data}</span>`;
                        }
                        return '-';
                    }
                },
                { 
                    data: 'DrugFormulation',
                    defaultContent: '-',
                    render: function(data) {
                        if (data) {
                            return `<span class="badge bg-outline-secondary border">${data}</span>`;
                        }
                        return '-';
                    }
                },
                { 
                    data: 'DrugAvailable',
                    render: function(data) {
                        if (data) {
                            return '<span class="badge bg-success">Có sẵn</span>';
                        } else {
                            return '<span class="badge bg-danger">Hết hàng</span>';
                        }
                    }
                },
                {
                    data: null,
                    orderable: false,
                    searchable: false,
                    width: '80px',
                    render: function(data, type, row) {
                        return `
                            <button class="btn btn-outline-danger btn-sm" 
                                    onclick="removeDrugFromTemplate('${row.DrugId}', '${row.DrugName}')" 
                                    title="Xóa khỏi mẫu">
                                <i class="fas fa-trash"></i>
                            </button>
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
                lengthMenu: "Hiển thị _MENU_ thuốc",
                info: "Hiển thị _START_ đến _END_ của _TOTAL_ thuốc",
                infoEmpty: "Không có thuốc nào",
                infoFiltered: "(lọc từ _MAX_ tổng số thuốc)",
                emptyTable: "Chưa có thuốc nào trong mẫu",
                zeroRecords: "Không tìm thấy thuốc nào"
            }
        });
    }
    
    function populateFilterOptions(drugs) {
        drugGroups.clear();
        formulations.clear();
        
        drugs.forEach(drug => {
            if (drug.DrugGroup) drugGroups.add(drug.DrugGroup);
            if (drug.DrugFormulation) formulations.add(drug.DrugFormulation);
        });
        
        // Populate Group filter
        const groupSelect = $('#filter-group');
        groupSelect.find('option:not(:first)').remove();
        Array.from(drugGroups).sort().forEach(group => {
            groupSelect.append(`<option value="${group}">${group}</option>`);
        });
        
        // Populate Formulation filter
        const formulationSelect = $('#filter-formulation');
        formulationSelect.find('option:not(:first)').remove();
        Array.from(formulations).sort().forEach(formulation => {
            formulationSelect.append(`<option value="${formulation}">${formulation}</option>`);
        });
    }
    
    function setupEventHandlers() {
        // Add drug button
        $('#btn-add-drug').on('click', function() {
            $('#drugModal').modal('show');
            $('#drug-search').focus();
        });
        
        // Drug search
        let searchTimeout;
        $('#drug-search').on('input', function() {
            const query = $(this).val().trim();
            
            clearTimeout(searchTimeout);
            
            if (query.length < 2) {
                $('#drug-results').html('<div class="text-muted text-center py-3">Nhập ít nhất 2 ký tự để tìm kiếm</div>');
                return;
            }
            
            searchTimeout = setTimeout(() => {
                searchDrugs(query);
            }, 500);
        });
        
        // Filters
        $('#search-name').on('keyup', function() {
            drugsTable.column(1).search(this.value).draw();
        });
        
        $('#filter-group').on('change', function() {
            drugsTable.column(3).search(this.value).draw();
        });
        
        $('#filter-available').on('change', function() {
            const value = this.value;
            let searchTerm = '';
            if (value === 'true') searchTerm = 'Có sẵn';
            else if (value === 'false') searchTerm = 'Hết hàng';
            drugsTable.column(5).search(searchTerm).draw();
        });
        
        $('#filter-formulation').on('change', function() {
            drugsTable.column(4).search(this.value).draw();
        });
        
        // Refresh button
        $('#btn-refresh').on('click', function() {
            drugsTable.ajax.reload();
        });
        
        // Remove confirmation
        $('#btn-confirm-remove').on('click', function() {
            const drugId = $(this).data('drug-id');
            if (drugId) {
                confirmRemoveDrug(drugId);
            }
        });
    }
    
    function searchDrugs(query) {
        $('#drug-results').html('<div class="text-center py-3"><span class="spinner-border spinner-border-sm me-2"></span>Đang tìm kiếm...</div>');
        
        $.ajax({
            url: `/api/drugs?q=${encodeURIComponent(query)}`,
            type: 'GET',
            success: function(response) {
                if (response.drugs && response.drugs.length > 0) {
                    let resultsHtml = '';
                    response.drugs.slice(0, 20).forEach(drug => { // Limit to first 20 results
                        const availableBadge = drug.DrugAvailable ? 
                            '<span class="badge bg-success">Có sẵn</span>' : 
                            '<span class="badge bg-danger">Hết hàng</span>';
                        
                        resultsHtml += `
                            <div class="border-bottom py-2">
                                <div class="d-flex justify-content-between align-items-start">
                                    <div class="flex-grow-1">
                                        <strong>${drug.DrugName}</strong>
                                        ${drug.DrugChemical ? `<br><small class="text-muted">${drug.DrugChemical}</small>` : ''}
                                        ${drug.DrugGroup ? `<br><span class="badge bg-info me-1">${drug.DrugGroup}</span>` : ''}
                                        ${drug.DrugFormulation ? `<span class="badge bg-secondary">${drug.DrugFormulation}</span>` : ''}
                                    </div>
                                    <div class="ms-3">
                                        ${availableBadge}
                                        <br>
                                        <button class="btn btn-sm btn-outline-primary mt-1" 
                                                onclick="addDrugToTemplate('${drug.DrugId}', '${drug.DrugName}')">
                                            <i class="fas fa-plus"></i> Thêm
                                        </button>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                    $('#drug-results').html(resultsHtml);
                } else {
                    $('#drug-results').html('<div class="text-muted text-center py-3">Không tìm thấy thuốc nào</div>');
                }
            },
            error: function() {
                $('#drug-results').html('<div class="text-danger text-center py-3">Lỗi khi tìm kiếm thuốc</div>');
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
    
    // Global functions
    window.addDrugToTemplate = function(drugId, drugName) {
        $.ajax({
            url: '/api/drug-template-details',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                DrugTemplateId: templateId,
                DrugId: drugId
            }),
            success: function() {
                $('#drugModal').modal('hide');
                drugsTable.ajax.reload();
                showAlert(`Đã thêm "${drugName}" vào mẫu`, 'success');
                $('#drug-search').val('');
                $('#drug-results').html('<div class="text-muted text-center py-3">Nhập từ khóa để tìm kiếm thuốc</div>');
            },
            error: function(xhr) {
                const errorMsg = xhr.responseJSON?.error || 'Có lỗi xảy ra khi thêm thuốc';
                showAlert(errorMsg, 'danger');
            }
        });
    };
    
    window.removeDrugFromTemplate = function(drugId, drugName) {
        $('#remove-drug-name').text(drugName);
        $('#btn-confirm-remove').data('drug-id', drugId);
        $('#removeModal').modal('show');
    };
    
    function confirmRemoveDrug(drugId) {
        $.ajax({
            url: `/api/drug-template-details/${templateId}/${drugId}`,
            type: 'DELETE',
            success: function() {
                $('#removeModal').modal('hide');
                drugsTable.ajax.reload();
                showAlert('Đã xóa thuốc khỏi mẫu', 'success');
            },
            error: function(xhr) {
                const errorMsg = xhr.responseJSON?.error || 'Có lỗi xảy ra khi xóa thuốc';
                showAlert(errorMsg, 'danger');
            }
        });
    }
});
