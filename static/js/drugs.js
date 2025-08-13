/**
 * Drugs Management JavaScript
 * Handles CRUD operations for drugs using DataTables
 */

$(document).ready(function() {
    let drugsTable;
    let currentDrugId = null;
    let deleteModal;
    let drugModal;
    let drugGroups = new Set();
    let formulations = new Set();
    
    // Initialize modals
    deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));
    drugModal = new bootstrap.Modal(document.getElementById('drugModal'));
    
    // Initialize DataTable
    initializeDrugsTable();
    
    // Event Handlers
    setupEventHandlers();
    
    // Initialize filters
    initializeFilters();
    
    function initializeDrugsTable() {
        drugsTable = $('#drugsTable').DataTable({
            ajax: {
                url: '/api/drugs',
                type: 'GET',
                dataSrc: function(json) {
                    // Populate filter options from data
                    populateFilterOptions(json.drugs);
                    return json.drugs;
                },
                error: function(xhr, error, thrown) {
                    console.error('Error loading drugs:', error);
                    showError('Failed to load drugs data');
                }
            },
            columns: [
                { 
                    data: 'DrugId',
                    width: '70px'
                },
                { 
                    data: 'DrugName',
                    render: function(data, type, row) {
                        if (type === 'display') {
                            return `<strong>${data}</strong>`;
                        }
                        return data;
                    }
                },
                { 
                    data: 'DrugChemical',
                    defaultContent: '-',
                    render: function(data, type, row) {
                        return data || '-';
                    }
                },
                { 
                    data: 'DrugContent',
                    defaultContent: '-',
                    render: function(data, type, row) {
                        return data || '-';
                    }
                },
                { 
                    data: 'DrugGroup',
                    defaultContent: '-',
                    render: function(data, type, row) {
                        if (data) {
                            return `<span class="badge bg-info">${data}</span>`;
                        }
                        return '-';
                    }
                },
                { 
                    data: 'DrugAvailable',
                    render: function(data, type, row) {
                        if (data) {
                            return `<span class="badge bg-success">Available</span>`;
                        } else {
                            return `<span class="badge bg-danger">Not Available</span>`;
                        }
                    }
                },
                { 
                    data: 'DrugFormulation',
                    defaultContent: '-',
                    render: function(data, type, row) {
                        if (data) {
                            return `<span class="badge bg-outline-secondary border">${data}</span>`;
                        }
                        return '-';
                    }
                },
                { 
                    data: 'DrugRemains',
                    defaultContent: '0',
                    render: function(data, type, row) {
                        const remains = data || 0;
                        let badgeClass = 'bg-success';
                        if (remains === 0) badgeClass = 'bg-danger';
                        else if (remains < 10) badgeClass = 'bg-warning text-dark';
                        
                        return `<span class="badge ${badgeClass}">${remains}</span>`;
                    }
                },
                {
                    data: null,
                    orderable: false,
                    searchable: false,
                    width: '120px',
                    render: function(data, type, row) {
                        return `
                            <div class="btn-group btn-group-sm" role="group">
                                <button type="button" class="btn btn-outline-primary btn-sm" 
                                        onclick="editDrug('${row.DrugId}')" title="Edit">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button type="button" class="btn btn-outline-danger btn-sm" 
                                        onclick="deleteDrug('${row.DrugId}', '${row.DrugName}')" title="Delete">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        `;
                    }
                }
            ],
            order: [[1, 'asc']], // Order by Drug Name
            pageLength: 25,
            responsive: true,
            dom: '<"d-flex justify-content-between align-items-center mb-3"<"d-flex align-items-center"l><"d-flex align-items-center"f>>rtip',
            language: {
                search: "Search drugs:",
                lengthMenu: "Show _MENU_ drugs per page",
                info: "Showing _START_ to _END_ of _TOTAL_ drugs",
                infoEmpty: "No drugs found",
                infoFiltered: "(filtered from _MAX_ total drugs)",
                emptyTable: "No drugs available",
                zeroRecords: "No matching drugs found"
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
        const groupSelect = $('#drugGroupFilter');
        groupSelect.find('option:not(:first)').remove();
        Array.from(drugGroups).sort().forEach(group => {
            groupSelect.append(`<option value="${group}">${group}</option>`);
        });
        
        // Populate Formulation filter
        const formulationSelect = $('#formulationFilter');
        formulationSelect.find('option:not(:first)').remove();
        Array.from(formulations).sort().forEach(formulation => {
            formulationSelect.append(`<option value="${formulation}">${formulation}</option>`);
        });
    }
    
    function setupEventHandlers() {
        // Add Drug Button
        $('#addDrugBtn').on('click', function() {
            showDrugModal();
        });
        
        // Save Drug Button
        $('#saveDrugBtn').on('click', function() {
            saveDrug();
        });
        
        // Confirm Delete Button
        $('#confirmDeleteBtn').on('click', function() {
            confirmDelete();
        });
        
        // Form validation on input
        $('#drugForm input, #drugForm select').on('blur', function() {
            validateField($(this));
        });
        
        // Clear validation on input
        $('#drugForm input, #drugForm select').on('input change', function() {
            $(this).removeClass('is-invalid');
            $(this).next('.invalid-feedback').text('');
        });
        
        // Export button
        $('#exportBtn').on('click', function() {
            exportDrugs();
        });
        
        // Clear filters button
        $('#clearFiltersBtn').on('click', function() {
            clearFilters();
        });
    }
    
    function initializeFilters() {
        // Search input
        $('#searchInput').on('keyup', function() {
            drugsTable.search(this.value).draw();
        });
        
        // Filter dropdowns
        $('#drugGroupFilter, #availableFilter, #formulationFilter').on('change', function() {
            applyFilters();
        });
    }
    
    function applyFilters() {
        const groupFilter = $('#drugGroupFilter').val();
        const availableFilter = $('#availableFilter').val();
        const formulationFilter = $('#formulationFilter').val();
        
        // Apply column-specific filters
        drugsTable
            .column(4).search(groupFilter) // Group column
            .column(5).search(availableFilter === '1' ? 'Available' : availableFilter === '0' ? 'Not Available' : '') // Available column
            .column(6).search(formulationFilter) // Formulation column
            .draw();
    }
    
    function clearFilters() {
        $('#searchInput').val('');
        $('#drugGroupFilter, #availableFilter, #formulationFilter').val('');
        
        drugsTable
            .search('')
            .column(4).search('')
            .column(5).search('')
            .column(6).search('')
            .draw();
    }
    
    function showDrugModal(drug = null) {
        const isEdit = drug !== null;
        
        // Set modal title
        $('#drugModalTitle').text(isEdit ? 'Edit Drug' : 'Add New Drug');
        
        // Reset form
        $('#drugForm')[0].reset();
        $('#drugForm .form-control, #drugForm .form-select').removeClass('is-invalid');
        $('#drugForm .invalid-feedback').text('');
        
        if (isEdit) {
            // Populate form with drug data
            $('#drugId').val(drug.DrugId);
            $('#drugName').val(drug.DrugName);
            $('#drugChemical').val(drug.DrugChemical || '');
            $('#drugContent').val(drug.DrugContent || '');
            $('#drugFormulation').val(drug.DrugFormulation || '');
            $('#drugGroup').val(drug.DrugGroup || '');
            $('#drugRoute').val(drug.DrugRoute || '');
            $('#drugRemains').val(drug.DrugRemains || 0);
            $('#drugAvailable').val(drug.DrugAvailable ? 'true' : 'false');
            $('#drugPriceBHYT').val(drug.DrugPriceBHYT || 0);
            $('#drugPriceVP').val(drug.DrugPriceVP || 0);
            $('#drugNote').val(drug.DrugNote || '');
        } else {
            $('#drugId').val('');
            $('#drugAvailable').val('true');
            $('#drugRemains').val(0);
            $('#drugPriceBHYT').val(0);
            $('#drugPriceVP').val(0);
        }
        
        drugModal.show();
        
        // Focus on first input
        setTimeout(() => {
            $('#drugName').focus();
        }, 500);
    }
    
    function validateField(field) {
        const value = field.val().trim();
        const fieldName = field.attr('name');
        let isValid = true;
        let errorMessage = '';
        
        // Required field validation
        if (field.prop('required') && !value) {
            isValid = false;
            errorMessage = 'This field is required.';
        }
        
        // Specific field validations
        if (value && fieldName === 'DrugName' && value.length > 255) {
            isValid = false;
            errorMessage = 'Drug name must be 255 characters or less.';
        }
        
        if (value && fieldName === 'DrugChemical' && value.length > 255) {
            isValid = false;
            errorMessage = 'Chemical name must be 255 characters or less.';
        }
        
        // Update UI
        if (isValid) {
            field.removeClass('is-invalid').addClass('is-valid');
            field.next('.invalid-feedback').text('');
        } else {
            field.removeClass('is-valid').addClass('is-invalid');
            field.next('.invalid-feedback').text(errorMessage);
        }
        
        return isValid;
    }
    
    function validateForm() {
        let isValid = true;
        
        // Validate all required fields
        $('#drugForm [required]').each(function() {
            if (!validateField($(this))) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    function saveDrug() {
        if (!validateForm()) {
            showError('Please correct the validation errors before saving.');
            return;
        }
        
        const formData = new FormData($('#drugForm')[0]);
        const drugData = Object.fromEntries(formData.entries());
        const isEdit = drugData.DrugId !== '';
        
        // Convert boolean and numeric fields
        drugData.DrugAvailable = drugData.DrugAvailable === 'true';
        drugData.DrugRemains = parseInt(drugData.DrugRemains) || 0;
        drugData.DrugPriceBHYT = parseInt(drugData.DrugPriceBHYT) || 0;
        drugData.DrugPriceVP = parseInt(drugData.DrugPriceVP) || 0;
        
        // Remove empty DrugId for new records
        if (!isEdit) {
            delete drugData.DrugId;
        }
        
        // Show loading state
        const saveBtn = $('#saveDrugBtn');
        const spinner = saveBtn.find('.spinner-border');
        
        spinner.removeClass('d-none');
        saveBtn.prop('disabled', true);
        
        // Make AJAX request
        $.ajax({
            url: isEdit ? `/api/drugs/${drugData.DrugId}` : '/api/drugs',
            type: isEdit ? 'PUT' : 'POST',
            contentType: 'application/json',
            data: JSON.stringify(drugData),
            success: function(response) {
                drugModal.hide();
                drugsTable.ajax.reload();
                showSuccess(isEdit ? 'Drug updated successfully!' : 'Drug created successfully!');
            },
            error: function(xhr) {
                const errorMsg = xhr.responseJSON?.error || 'An error occurred while saving the drug.';
                showError(errorMsg);
            },
            complete: function() {
                spinner.addClass('d-none');
                saveBtn.prop('disabled', false);
            }
        });
    }
    
    function deleteDrug(drugId, drugName) {
        currentDrugId = drugId;
        $('#deleteItemName').text(drugName);
        deleteModal.show();
    }
    
    function confirmDelete() {
        if (!currentDrugId) return;
        
        const deleteBtn = $('#confirmDeleteBtn');
        const spinner = deleteBtn.find('.spinner-border');
        
        spinner.removeClass('d-none');
        deleteBtn.prop('disabled', true);
        
        $.ajax({
            url: `/api/drugs/${currentDrugId}`,
            type: 'DELETE',
            success: function(response) {
                deleteModal.hide();
                drugsTable.ajax.reload();
                showSuccess('Drug deleted successfully!');
                currentDrugId = null;
            },
            error: function(xhr) {
                const errorMsg = xhr.responseJSON?.error || 'An error occurred while deleting the drug.';
                showError(errorMsg);
            },
            complete: function() {
                spinner.addClass('d-none');
                deleteBtn.prop('disabled', false);
            }
        });
    }
    
    function exportDrugs() {
        // Get current table data
        const data = drugsTable.rows({search: 'applied'}).data().toArray();
        
        if (data.length === 0) {
            showError('No data to export.');
            return;
        }
        
        // Create CSV content
        const headers = ['ID', 'Drug Name', 'Chemical Name', 'Content', 'Group', 'Available', 'Formulation', 'Remains', 'Route', 'Price BHYT', 'Price VP', 'Note'];
        const csvContent = [
            headers.join(','),
            ...data.map(row => [
                `"${row.DrugId}"`,
                `"${row.DrugName}"`,
                `"${row.DrugChemical || ''}"`,
                `"${row.DrugContent || ''}"`,
                `"${row.DrugGroup || ''}"`,
                row.DrugAvailable ? 'Available' : 'Not Available',
                `"${row.DrugFormulation || ''}"`,
                row.DrugRemains || 0,
                `"${row.DrugRoute || ''}"`,
                row.DrugPriceBHYT || 0,
                row.DrugPriceVP || 0,
                `"${row.DrugNote || ''}"`
            ].join(','))
        ].join('\n');
        
        // Download CSV
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `drugs_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showSuccess('Drug data exported successfully!');
    }
    
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
    
    // Global functions for button clicks
    window.editDrug = function(drugId) {
        // Get drug data from table
        const drug = drugsTable.rows().data().toArray().find(d => d.DrugId === drugId);
        if (drug) {
            showDrugModal(drug);
        } else {
            showError('Drug not found.');
        }
    };
    
    window.deleteDrug = deleteDrug;
});
