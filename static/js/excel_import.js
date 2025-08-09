// Excel Import functionality
$(document).ready(function() {
    // Add "Import Excel" button to the page header
    $('.col-md-3:first').append(`
        <a href="/excel/upload" class="btn btn-primary ms-2" title="Import data from Excel file">
            <i class="fas fa-file-excel me-1"></i> Import Excel
        </a>
    `);
    
    // Get current page type
    let currentPage = '';
    if (window.location.pathname.includes('body_sites')) {
        currentPage = 'body_sites';
    } else if (window.location.pathname.includes('body_parts')) {
        currentPage = 'body_parts';
    } else if (window.location.pathname.includes('departments')) {
        currentPage = 'departments';
    } else if (window.location.pathname.includes('drugs')) {
        currentPage = 'drugs';
    } else if (window.location.pathname.includes('staff')) {
        currentPage = 'staff';
    } else if (window.location.pathname.includes('patients')) {
        currentPage = 'patients';
    } else if (window.location.pathname.includes('procedures')) {
        currentPage = 'procedures';
    } else if (window.location.pathname.includes('signs')) {
        currentPage = 'signs';
    } else if (window.location.pathname.includes('tests')) {
        currentPage = 'tests';
    }
    
    // Add direct parameter to Excel upload if we know the current page
    if (currentPage) {
        $('a[href="/excel/upload"]').attr('href', `/excel/upload?table=${currentPage}`);
    }
});
