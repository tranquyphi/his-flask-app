// Staff Documents JavaScript
$(document).ready(function() {
    let documentsTable = null;
    let allDocuments = [];
    let allStaff = [];
    let allDocumentTypes = [];
    let deleteDocumentId = null;

    $('#loading-overlay').show();
    initializeUI();

    $('#search-document').on('keyup', function() {
        if (documentsTable) {
            documentsTable.search($(this).val()).draw();
        }
    });
    $('#staff-filter').on('change', function() {
        filterByStaff($(this).val());
    });
    $('#document-type-filter').on('change', function() {
        filterByDocumentType($(this).val());
    });
    $('#refresh-data').on('click', function() {
        loadDocumentsData();
    });
    $('#submit-upload').on('click', function() {
        uploadDocument();
    });
    // TODO: Add file drop area logic if needed

    function initializeUI() {
        Promise.all([
            loadDocumentsData(),
            loadStaffData(),
            loadDocumentTypesData()
        ]).then(() => {
            $('#loading-overlay').hide();
        }).catch(error => {
            $('#loading-overlay').hide();
            alert('Lỗi khi khởi tạo giao diện: ' + error.message);
        });
    }
    function loadDocumentsData() {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: '/api/staff_documents/',
                method: 'GET',
                success: function(response) {
                    allDocuments = response || [];
                    initializeDocumentsTable();
                    resolve(allDocuments);
                },
                error: function(xhr, status, error) {
                    alert('Không thể tải dữ liệu tài liệu: ' + error);
                    reject(error);
                }
            });
        });
    }
    function loadStaffData() {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: '/api/staff_documents/staff',
                method: 'GET',
                success: function(response) {
                    allStaff = response || [];
                    populateStaffDropdowns();
                    resolve(allStaff);
                },
                error: function(xhr, status, error) {
                    alert('Không thể tải dữ liệu nhân viên: ' + error);
                    reject(error);
                }
            });
        });
    }
    function loadDocumentTypesData() {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: '/api/staff_documents/types',
                method: 'GET',
                success: function(response) {
                    allDocumentTypes = response || [];
                    populateDocumentTypesDropdowns();
                    resolve(allDocumentTypes);
                },
                error: function(xhr, status, error) {
                    alert('Không thể tải dữ liệu loại tài liệu: ' + error);
                    reject(error);
                }
            });
        });
    }
    function populateStaffDropdowns() {
        // For filter dropdown
        var filterSelect = $('#staff-filter');
        filterSelect.empty();
        filterSelect.append('<option value="">-- Tất cả Nhân viên --</option>');
        allStaff.forEach(function(staff) {
            filterSelect.append(`<option value="${staff.StaffId}">${staff.StaffName}</option>`);
        });
        // For upload modal dropdown
        var modalSelect = $('#staff-select');
        modalSelect.empty();
        modalSelect.append('<option value="">-- Chọn nhân viên --</option>');
        allStaff.forEach(function(staff) {
            modalSelect.append(`<option value="${staff.StaffId}">${staff.StaffName}</option>`);
        });
    }
    function populateDocumentTypesDropdowns() {
        // For filter dropdown
        var filterSelect = $('#document-type-filter');
        filterSelect.empty();
        filterSelect.append('<option value="">-- Tất cả Loại tài liệu --</option>');
        allDocumentTypes.forEach(function(type) {
            filterSelect.append(`<option value="${type.DocumentTypeId}">${type.DocumentTypeName}</option>`);
        });
        // For upload modal dropdown
        var modalSelect = $('#document-type-select');
        modalSelect.empty();
        modalSelect.append('<option value="">-- Chọn loại tài liệu --</option>');
        allDocumentTypes.forEach(function(type) {
            modalSelect.append(`<option value="${type.DocumentTypeId}">${type.DocumentTypeName}</option>`);
        });
    }
    function filterByStaff(staffId) {
        if (documentsTable) {
            if (!staffId) {
                documentsTable.search('').draw();
            } else {
                documentsTable.column(2).search(staffId).draw();
            }
        }
    }
    function filterByDocumentType(typeId) {
        if (documentsTable) {
            if (!typeId) {
                documentsTable.search('').draw();
            } else {
                documentsTable.column(3).search(typeId).draw();
            }
        }
    }
    function initializeDocumentsTable() {
        if (documentsTable) {
            documentsTable.destroy();
        }
        documentsTable = $('#documents-table').DataTable({
            data: allDocuments,
            columns: [
                { data: 'DocumentId' },
                { data: 'StaffName' },
                { data: 'StaffId' },
                { data: 'DocumentTypeId' },
                { data: 'DocumentTypeName' },
                { data: 'original_filename' },
                { data: 'FileSize' },
                { data: 'UploadDate' },
                { data: 'LastModified' }
            ]
        });
    }
    function uploadDocument() {
        var staffId = $('#staff-select').val();
        var documentTypeId = $('#document-type-select').val();
        var description = $('#document-description').val();
        var fileInput = $('#document-file')[0];
        if (!staffId || !documentTypeId || fileInput.files.length === 0) {
            alert('Vui lòng chọn nhân viên, loại tài liệu và tệp.');
            return;
        }
        var file = fileInput.files[0];
        var formData = new FormData();
        formData.append('StaffId', staffId);
        formData.append('DocumentTypeId', documentTypeId);
        formData.append('document_metadata', JSON.stringify({ description: description }));
        formData.append('original_filename', file.name);
        formData.append('FileSize', file.size);
        formData.append('document_links', JSON.stringify({ link: 'uploaded' })); // Placeholder, update as needed
        formData.append('file', file);

        $.ajax({
            url: '/api/staff_documents/',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                alert('Tải lên thành công!');
                $('#uploadDocumentModal').modal('hide');
                loadDocumentsData();
            },
            error: function(xhr, status, error) {
                alert('Lỗi khi tải lên: ' + error);
            }
        });
    }
});
