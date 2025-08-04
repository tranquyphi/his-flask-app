// HIS - Hospital Information System - Main JavaScript

// Global configuration
const HIS = {
    baseUrl: window.location.origin,
    apiUrl: window.location.origin + '/api',
    currentUser: null,
    
    // Initialize the application
    init: function() {
        this.setupEventListeners();
        this.loadCurrentUser();
    },
    
    // Setup global event listeners
    setupEventListeners: function() {
        // Handle AJAX errors globally
        $(document).ajaxError(function(event, xhr, settings, error) {
            if (xhr.status === 401) {
                window.location.href = '/login';
            } else if (xhr.status >= 500) {
                HIS.showAlert('Server error occurred. Please try again.', 'danger');
            }
        });
        
        // Show loading indicator for AJAX requests
        $(document).ajaxStart(function() {
            HIS.showLoading();
        }).ajaxStop(function() {
            HIS.hideLoading();
        });
    },
    
    // Load current user information
    loadCurrentUser: function() {
        fetch('/test/current-user')
            .then(response => response.json())
            .then(data => {
                this.currentUser = data;
            })
            .catch(error => {
                console.log('No user session found');
            });
    },
    
    // Utility functions
    showAlert: function(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container-fluid');
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    },
    
    showLoading: function() {
        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'global-loading';
        loadingDiv.className = 'loading-overlay';
        loadingDiv.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        `;
        document.body.appendChild(loadingDiv);
    },
    
    hideLoading: function() {
        const loadingDiv = document.getElementById('global-loading');
        if (loadingDiv) {
            loadingDiv.remove();
        }
    },
    
    // Format date for display
    formatDate: function(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    // Format currency
    formatCurrency: function(amount) {
        if (!amount) return '0 VND';
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND'
        }).format(amount);
    },
    
    // Confirm deletion
    confirmDelete: function(message = 'Are you sure you want to delete this item?') {
        return confirm(message);
    }
};

// Tabulator common configurations
const TabulatorConfig = {
    // Common table options
    defaultOptions: {
        layout: "fitColumns",
        pagination: "local",
        paginationSize: 20,
        paginationSizeSelector: [10, 20, 50, 100],
        movableColumns: true,
        resizableRows: true,
        selectable: true,
        responsiveLayout: "hide",
        placeholder: "No data available",
        tooltips: true,
        history: true,
    },
    
    // Common column formatters
    formatters: {
        // Action buttons formatter
        actions: function(cell, formatterParams, onRendered) {
            const rowData = cell.getRow().getData();
            const actions = formatterParams.actions || ['view', 'edit', 'delete'];
            
            let buttons = '<div class="action-buttons">';
            
            if (actions.includes('view')) {
                buttons += `<button class="action-btn btn-view" onclick="HIS.viewRecord('${formatterParams.table}', '${rowData[formatterParams.idField]}')" title="View">
                    <i class="fas fa-eye"></i>
                </button>`;
            }
            
            if (actions.includes('edit')) {
                buttons += `<button class="action-btn btn-edit" onclick="HIS.editRecord('${formatterParams.table}', '${rowData[formatterParams.idField]}')" title="Edit">
                    <i class="fas fa-edit"></i>
                </button>`;
            }
            
            if (actions.includes('delete')) {
                buttons += `<button class="action-btn btn-delete" onclick="HIS.deleteRecord('${formatterParams.table}', '${rowData[formatterParams.idField]}')" title="Delete">
                    <i class="fas fa-trash"></i>
                </button>`;
            }
            
            buttons += '</div>';
            return buttons;
        },
        
        // Status formatter
        status: function(cell, formatterParams, onRendered) {
            const value = cell.getValue();
            const statusClass = value ? 'status-active' : 'status-inactive';
            const statusText = value ? 'Active' : 'Inactive';
            return `<span class="status-badge ${statusClass}">${statusText}</span>`;
        },
        
        // Date formatter
        date: function(cell, formatterParams, onRendered) {
            return HIS.formatDate(cell.getValue());
        },
        
        // Currency formatter
        currency: function(cell, formatterParams, onRendered) {
            return HIS.formatCurrency(cell.getValue());
        }
    },
    
    // Common CRUD operations
    crud: {
        view: function(table, id) {
            window.location.href = `/${table}/${id}`;
        },
        
        edit: function(table, id) {
            window.location.href = `/${table}/${id}/edit`;
        },
        
        delete: function(table, id) {
            if (HIS.confirmDelete()) {
                fetch(`${HIS.apiUrl}/${table}/${id}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        HIS.showAlert('Record deleted successfully', 'success');
                        // Refresh the table
                        if (window.currentTable) {
                            window.currentTable.replaceData();
                        }
                    } else {
                        HIS.showAlert('Failed to delete record', 'danger');
                    }
                })
                .catch(error => {
                    HIS.showAlert('Error deleting record', 'danger');
                });
            }
        }
    }
};

// Global functions for table actions
HIS.viewRecord = TabulatorConfig.crud.view;
HIS.editRecord = TabulatorConfig.crud.edit;
HIS.deleteRecord = TabulatorConfig.crud.delete;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    HIS.init();
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { HIS, TabulatorConfig };
}
