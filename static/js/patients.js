// Patients Page JavaScript

let patientsTable;
let departments = [];

// Initialize patients page
document.addEventListener('DOMContentLoaded', function() {
    initializePatientsTable();
    loadDepartments();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Search input
    document.getElementById('searchInput').addEventListener('input', function() {
        patientsTable.setFilter("PatientName", "like", this.value);
    });
    
    // Gender filter
    document.getElementById('genderFilter').addEventListener('change', function() {
        if (this.value) {
            patientsTable.setFilter("PatientGender", "=", this.value);
        } else {
            patientsTable.removeFilter("PatientGender");
        }
    });
    
    // Department filter
    document.getElementById('departmentFilter').addEventListener('change', function() {
        if (this.value) {
            patientsTable.setFilter("DepartmentName", "=", this.value);
        } else {
            patientsTable.removeFilter("DepartmentName");
        }
    });
}

// Initialize Tabulator table
function initializePatientsTable() {
    patientsTable = new Tabulator("#patients-table", {
        ...TabulatorConfig.defaultOptions,
        ajaxURL: HIS.apiUrl + "/patients",
        ajaxConfig: "GET",
        ajaxResponse: function(url, params, response) {
            return response.patients || [];
        },
        columns: [
            {
                title: "Patient ID",
                field: "PatientId",
                width: 120,
                frozen: true,
                headerFilter: "input"
            },
            {
                title: "Full Name",
                field: "PatientName",
                width: 200,
                frozen: true,
                headerFilter: "input",
                formatter: function(cell) {
                    const value = cell.getValue();
                    const rowData = cell.getRow().getData();
                    return `<strong>${value}</strong>`;
                }
            },
            {
                title: "Gender",
                field: "PatientGender",
                width: 100,
                headerFilter: "select",
                headerFilterParams: {
                    "": "All",
                    "Nam": "Nam",
                    "Nữ": "Nữ",
                    "Khác": "Khác"
                },
                formatter: function(cell) {
                    const value = cell.getValue();
                    const colors = {
                        'Nam': 'primary',
                        'Nữ': 'danger',
                        'Khác': 'secondary'
                    };
                    return `<span class="badge bg-${colors[value] || 'secondary'}">${value}</span>`;
                }
            },
            {
                title: "Age",
                field: "PatientAge",
                width: 80,
                hozAlign: "center"
            },
            {
                title: "Address",
                field: "PatientAddress",
                width: 250,
                formatter: function(cell) {
                    const value = cell.getValue();
                    return value ? value.substring(0, 50) + (value.length > 50 ? '...' : '') : '';
                },
                tooltip: true
            },
            {
                title: "Allergies",
                field: "Allergy",
                width: 150,
                formatter: function(cell) {
                    const value = cell.getValue();
                    if (!value) return '<span class="text-muted">None</span>';
                    return value.length > 30 ? value.substring(0, 30) + '...' : value;
                },
                tooltip: true
            },
            {
                title: "Medical History",
                field: "History",
                width: 150,
                formatter: function(cell) {
                    const value = cell.getValue();
                    if (!value) return '<span class="text-muted">None</span>';
                    return value.length > 30 ? value.substring(0, 30) + '...' : value;
                },
                tooltip: true
            },
            {
                title: "Notes",
                field: "PatientNote",
                width: 150,
                formatter: function(cell) {
                    const value = cell.getValue();
                    if (!value) return '<span class="text-muted">None</span>';
                    return value.length > 30 ? value.substring(0, 30) + '...' : value;
                },
                tooltip: true
            },
            {
                title: "Current Department",
                field: "DepartmentName",
                width: 180,
                headerFilter: "select",
                headerFilterParams: function() {
                    // This will be populated by loadDepartments()
                    return {"": "All Departments"};
                },
                formatter: function(cell) {
                    const value = cell.getValue();
                    const rowData = cell.getRow().getData();
                    if (!value) return '<span class="text-muted">No Department</span>';
                    
                    const typeColors = {
                        'Nội trú': 'primary',
                        'Cấp cứu': 'danger', 
                        'Phòng khám': 'success'
                    };
                    const color = typeColors[rowData.DepartmentType] || 'secondary';
                    
                    return `
                        <div>
                            <span class="badge bg-${color}">${value}</span>
                            ${rowData.DepartmentType ? `<br><small class="text-muted">${rowData.DepartmentType}</small>` : ''}
                        </div>
                    `;
                }
            },
            {
                title: "Actions",
                field: "actions",
                width: 120,
                hozAlign: "center",
                headerSort: false,
                formatter: function(cell) {
                    const rowData = cell.getRow().getData();
                    return `
                        <div class="action-buttons">
                            <button class="action-btn btn-view" onclick="viewPatient('${rowData.PatientId}')" title="View Details">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="action-btn btn-edit" onclick="editPatient('${rowData.PatientId}')" title="Edit">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="action-btn btn-add" onclick="viewPatientVisits('${rowData.PatientId}')" title="View Visits">
                                <i class="fas fa-calendar-check"></i>
                            </button>
                            <button class="action-btn btn-delete" onclick="deletePatient('${rowData.PatientId}')" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    `;
                }
            }
        ],
        rowClick: function(e, row) {
            // Highlight selected row
            patientsTable.getRows().forEach(r => r.getElement().classList.remove('table-active'));
            row.getElement().classList.add('table-active');
        }
    });
    
    // Store reference for global use
    window.currentTable = patientsTable;
}

// Load departments for filter
function loadDepartments() {
    fetch(HIS.apiUrl + '/departments')
        .then(response => response.json())
        .then(data => {
            departments = data.departments || [];
            const select = document.getElementById('departmentFilter');
            departments.forEach(dept => {
                const option = document.createElement('option');
                option.value = dept.DepartmentName;
                option.textContent = dept.DepartmentName;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading departments:', error);
        });
}

// Clear all filters
function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('genderFilter').value = '';
    document.getElementById('departmentFilter').value = '';
    patientsTable.clearFilter();
}

// Add new patient
function addPatient() {
    resetPatientForm();
    document.getElementById('modalTitleText').textContent = 'Add New Patient';
    document.getElementById('saveButtonText').textContent = 'Save Patient';
    const modal = new bootstrap.Modal(document.getElementById('patientModal'));
    modal.show();
}

// View patient details
function viewPatient(patientId) {
    window.location.href = `/patients/${patientId}`;
}

// Edit patient
function editPatient(patientId) {
    fetch(`${HIS.apiUrl}/patients/${patientId}`)
        .then(response => response.json())
        .then(data => {
            if (data.patient) {
                populatePatientForm(data.patient);
                document.getElementById('modalTitleText').textContent = 'Edit Patient';
                document.getElementById('saveButtonText').textContent = 'Update Patient';
                const modal = new bootstrap.Modal(document.getElementById('patientModal'));
                modal.show();
            }
        })
        .catch(error => {
            HIS.showAlert('Error loading patient data', 'danger');
        });
}

// View patient visits
function viewPatientVisits(patientId) {
    window.location.href = `/patients/${patientId}/visits`;
}

// Delete patient
function deletePatient(patientId) {
    if (HIS.confirmDelete('Are you sure you want to delete this patient? This action cannot be undone.')) {
        fetch(`${HIS.apiUrl}/patients/${patientId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                HIS.showAlert('Patient deleted successfully', 'success');
                patientsTable.replaceData();
            } else {
                HIS.showAlert(data.error || 'Failed to delete patient', 'danger');
            }
        })
        .catch(error => {
            HIS.showAlert('Error deleting patient', 'danger');
        });
    }
}

// Save patient (create or update)
function savePatient() {
    const form = document.getElementById('patientForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    // Validation
    if (!data.PatientName) {
        HIS.showAlert('Patient name is required', 'warning');
        return;
    }
    
    if (!data.PatientGender) {
        HIS.showAlert('Gender is required', 'warning');
        return;
    }
    
    const isEdit = !!data.PatientId;
    const url = isEdit ? `${HIS.apiUrl}/patients/${data.PatientId}` : `${HIS.apiUrl}/patients`;
    const method = isEdit ? 'PUT' : 'POST';
    
    // Generate patient ID if creating new
    if (!isEdit) {
        data.PatientId = generatePatientId();
    }
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.patient_id || result.message) {
            HIS.showAlert(isEdit ? 'Patient updated successfully' : 'Patient created successfully', 'success');
            const modal = bootstrap.Modal.getInstance(document.getElementById('patientModal'));
            modal.hide();
            patientsTable.replaceData();
        } else {
            HIS.showAlert(result.error || 'Failed to save patient', 'danger');
        }
    })
    .catch(error => {
        HIS.showAlert('Error saving patient', 'danger');
    });
}

// Generate patient ID
function generatePatientId() {
    const timestamp = Date.now().toString().slice(-6);
    const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
    return 'P' + timestamp + random;
}

// Reset patient form
function resetPatientForm() {
    document.getElementById('patientForm').reset();
    document.getElementById('patientId').value = '';
}

// Populate patient form with data
function populatePatientForm(patient) {
    document.getElementById('patientId').value = patient.PatientId;
    document.getElementById('patientName').value = patient.PatientName || '';
    document.getElementById('patientGender').value = patient.PatientGender || '';
    document.getElementById('patientAge').value = patient.PatientAge || '';
    document.getElementById('patientAddress').value = patient.PatientAddress || '';
    document.getElementById('allergy').value = patient.Allergy || '';
    document.getElementById('history').value = patient.History || '';
    document.getElementById('patientNote').value = patient.PatientNote || '';
}
