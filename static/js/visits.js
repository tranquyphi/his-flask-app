// Visits Management with Tabulator
let visitsTable;
let patients = [];
let staff = [];

document.addEventListener('DOMContentLoaded', function() {
    initializeVisitsTable();
    loadPatients();
    loadStaff();
    setDefaultDateTime();
});

function initializeVisitsTable() {
    visitsTable = new Tabulator("#visits-table", {
        layout: "fitColumns",
        responsiveLayout: "hide",
        pagination: "local",
        paginationSize: 10,
        paginationSizeSelector: [5, 10, 25, 50],
        placeholder: "No visits found",
        columns: [
            {
                title: "ID", 
                field: "visit_id", 
                width: 80,
                sorter: "number"
            },
            {
                title: "Patient", 
                field: "patient_name", 
                minWidth: 150,
                formatter: function(cell) {
                    const data = cell.getRow().getData();
                    return `<strong>${data.patient_name}</strong><br><small class="text-muted">${data.patient_id}</small>`;
                }
            },
            {
                title: "Staff", 
                field: "staff_name", 
                minWidth: 120,
                formatter: function(cell) {
                    const data = cell.getRow().getData();
                    return data.staff_name || '<span class="text-muted">Not assigned</span>';
                }
            },
            {
                title: "Visit Date", 
                field: "visit_date", 
                minWidth: 130,
                sorter: "datetime",
                formatter: function(cell) {
                    const value = cell.getValue();
                    if (value) {
                        const date = new Date(value);
                        return `${date.toLocaleDateString()}<br><small class="text-muted">${date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</small>`;
                    }
                    return '';
                }
            },
            {
                title: "Type", 
                field: "visit_type", 
                width: 120,
                formatter: function(cell) {
                    const value = cell.getValue();
                    if (!value) return '';
                    const colors = {
                        'Consultation': 'primary',
                        'Follow-up': 'info',
                        'Emergency': 'danger',
                        'Surgery': 'warning',
                        'Check-up': 'success'
                    };
                    const color = colors[value] || 'secondary';
                    return `<span class="badge bg-${color}">${value}</span>`;
                }
            },
            {
                title: "Status", 
                field: "status", 
                width: 120,
                formatter: function(cell) {
                    const value = cell.getValue();
                    const colors = {
                        'Scheduled': 'warning',
                        'In Progress': 'info',
                        'Completed': 'success',
                        'Cancelled': 'danger'
                    };
                    const color = colors[value] || 'secondary';
                    return `<span class="badge bg-${color}">${value}</span>`;
                }
            },
            {
                title: "Chief Complaint", 
                field: "chief_complaint", 
                minWidth: 200,
                formatter: function(cell) {
                    const value = cell.getValue();
                    if (!value) return '<span class="text-muted">Not specified</span>';
                    return value.length > 50 ? value.substring(0, 50) + '...' : value;
                }
            },
            {
                title: "Actions", 
                field: "actions", 
                width: 120,
                hozAlign: "center",
                formatter: function(cell) {
                    return `
                        <div class="btn-group btn-group-sm" role="group">
                            <button class="btn btn-outline-primary btn-sm" onclick="editVisit(${cell.getRow().getData().visit_id})" title="Edit">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-outline-info btn-sm" onclick="viewVisit(${cell.getRow().getData().visit_id})" title="View Details">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-outline-danger btn-sm" onclick="deleteVisit(${cell.getRow().getData().visit_id})" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    `;
                }
            }
        ]
    });

    // Load data
    loadVisits();
}

function loadVisits() {
    // For now, create some sample data since we don't have visit API endpoints yet
    const sampleVisits = [
        {
            visit_id: 1,
            patient_id: 'P001',
            patient_name: 'John Doe',
            staff_id: 'S001',
            staff_name: 'Dr. Jane Smith',
            visit_date: '2024-01-15T10:30:00',
            visit_type: 'Consultation',
            status: 'Completed',
            chief_complaint: 'Chest pain and shortness of breath',
            diagnosis: 'Mild angina',
            treatment: 'Prescribed medication and lifestyle changes',
            follow_up_date: '2024-02-15',
            notes: 'Patient responded well to treatment'
        },
        {
            visit_id: 2,
            patient_id: 'P002',
            patient_name: 'Jane Smith',
            staff_id: 'S002',
            staff_name: 'Dr. Mike Johnson',
            visit_date: '2024-01-16T14:00:00',
            visit_type: 'Follow-up',
            status: 'Scheduled',
            chief_complaint: 'Follow-up for diabetes management',
            diagnosis: 'Type 2 Diabetes Mellitus',
            treatment: 'Continue current medication, dietary counseling',
            follow_up_date: '2024-03-16',
            notes: 'Blood sugar levels improving'
        }
    ];

    visitsTable.setData(sampleVisits);
    
    // TODO: Replace with actual API call
    /*
    fetch('/api/visits')
        .then(response => response.json())
        .then(data => {
            visitsTable.setData(data.visits || []);
        })
        .catch(error => {
            console.error('Error loading visits:', error);
            showAlert('Error loading visits', 'danger');
        });
    */
}

function loadPatients() {
    fetch('/api/patients')
        .then(response => response.json())
        .then(data => {
            patients = data.patients || [];
            const select = document.getElementById('patientId');
            select.innerHTML = '<option value="">Select Patient</option>';
            
            patients.forEach(patient => {
                const option = document.createElement('option');
                option.value = patient.patient_id;
                option.textContent = `${patient.first_name} ${patient.last_name} (${patient.patient_id})`;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading patients:', error);
        });
}

function loadStaff() {
    fetch('/api/staff')
        .then(response => response.json())
        .then(data => {
            staff = data.staff || [];
            const select = document.getElementById('staffId');
            select.innerHTML = '<option value="">Select Staff</option>';
            
            staff.forEach(member => {
                const option = document.createElement('option');
                option.value = member.staff_id;
                option.textContent = `${member.first_name} ${member.last_name} - ${member.role}`;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading staff:', error);
        });
}

function setDefaultDateTime() {
    const now = new Date();
    const localDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
    document.getElementById('visitDate').value = localDateTime;
}

function showVisitModal(visitId = null) {
    const modal = document.getElementById('visitModal');
    const modalTitle = document.getElementById('visitModalLabel');
    const form = document.getElementById('visitForm');
    
    // Reset form
    form.reset();
    setDefaultDateTime();
    
    if (visitId) {
        modalTitle.textContent = 'Edit Visit';
        // Load visit data
        const visitData = visitsTable.getRow(visitId).getData();
        populateVisitForm(visitData);
    } else {
        modalTitle.textContent = 'Add New Visit';
        document.getElementById('visitId').value = '';
    }
}

function populateVisitForm(visitData) {
    document.getElementById('visitId').value = visitData.visit_id;
    document.getElementById('patientId').value = visitData.patient_id;
    document.getElementById('staffId').value = visitData.staff_id;
    
    if (visitData.visit_date) {
        const date = new Date(visitData.visit_date);
        const localDateTime = new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
        document.getElementById('visitDate').value = localDateTime;
    }
    
    document.getElementById('visitType').value = visitData.visit_type || '';
    document.getElementById('chiefComplaint').value = visitData.chief_complaint || '';
    document.getElementById('diagnosis').value = visitData.diagnosis || '';
    document.getElementById('treatment').value = visitData.treatment || '';
    document.getElementById('status').value = visitData.status || 'Scheduled';
    document.getElementById('followUpDate').value = visitData.follow_up_date || '';
    document.getElementById('notes').value = visitData.notes || '';
}

function saveVisit() {
    const form = document.getElementById('visitForm');
    const formData = new FormData(form);
    const visitData = Object.fromEntries(formData.entries());
    const visitId = document.getElementById('visitId').value;
    
    // Validate required fields
    if (!visitData.patient_id || !visitData.staff_id || !visitData.visit_date) {
        showAlert('Please fill in all required fields', 'warning');
        return;
    }
    
    // For now, just add to table since we don't have API endpoints
    if (visitId) {
        // Update existing visit
        visitData.visit_id = parseInt(visitId);
        visitData.patient_name = getPatientName(visitData.patient_id);
        visitData.staff_name = getStaffName(visitData.staff_id);
        
        visitsTable.updateRow(visitId, visitData);
        showAlert('Visit updated successfully', 'success');
    } else {
        // Add new visit
        visitData.visit_id = Date.now(); // Temporary ID
        visitData.patient_name = getPatientName(visitData.patient_id);
        visitData.staff_name = getStaffName(visitData.staff_id);
        
        visitsTable.addRow(visitData);
        showAlert('Visit added successfully', 'success');
    }
    
    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('visitModal'));
    modal.hide();
    
    // TODO: Replace with actual API calls
    /*
    const url = visitId ? `/api/visits/${visitId}` : '/api/visits';
    const method = visitId ? 'PUT' : 'POST';
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(visitData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadVisits();
            showAlert(visitId ? 'Visit updated successfully' : 'Visit added successfully', 'success');
            const modal = bootstrap.Modal.getInstance(document.getElementById('visitModal'));
            modal.hide();
        } else {
            showAlert(data.message || 'Error saving visit', 'danger');
        }
    })
    .catch(error => {
        console.error('Error saving visit:', error);
        showAlert('Error saving visit', 'danger');
    });
    */
}

function getPatientName(patientId) {
    const patient = patients.find(p => p.patient_id === patientId);
    return patient ? `${patient.first_name} ${patient.last_name}` : 'Unknown';
}

function getStaffName(staffId) {
    const member = staff.find(s => s.staff_id === staffId);
    return member ? `${member.first_name} ${member.last_name}` : 'Unknown';
}

function editVisit(visitId) {
    showVisitModal(visitId);
}

function viewVisit(visitId) {
    const visitData = visitsTable.getRow(visitId).getData();
    
    // Create a detailed view modal or page
    let detailsHtml = `
        <div class="row">
            <div class="col-md-6">
                <h6>Patient Information</h6>
                <p><strong>Name:</strong> ${visitData.patient_name}</p>
                <p><strong>ID:</strong> ${visitData.patient_id}</p>
            </div>
            <div class="col-md-6">
                <h6>Visit Information</h6>
                <p><strong>Date:</strong> ${new Date(visitData.visit_date).toLocaleString()}</p>
                <p><strong>Type:</strong> ${visitData.visit_type}</p>
                <p><strong>Status:</strong> ${visitData.status}</p>
            </div>
        </div>
        <div class="row mt-3">
            <div class="col-12">
                <h6>Medical Details</h6>
                <p><strong>Chief Complaint:</strong> ${visitData.chief_complaint || 'Not specified'}</p>
                <p><strong>Diagnosis:</strong> ${visitData.diagnosis || 'Not specified'}</p>
                <p><strong>Treatment:</strong> ${visitData.treatment || 'Not specified'}</p>
                <p><strong>Notes:</strong> ${visitData.notes || 'No additional notes'}</p>
            </div>
        </div>
    `;
    
    // Show in a modal or alert for now
    showAlert(detailsHtml, 'info', 'Visit Details');
}

function deleteVisit(visitId) {
    if (confirm('Are you sure you want to delete this visit?')) {
        visitsTable.deleteRow(visitId);
        showAlert('Visit deleted successfully', 'success');
        
        // TODO: Replace with actual API call
        /*
        fetch(`/api/visits/${visitId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadVisits();
                showAlert('Visit deleted successfully', 'success');
            } else {
                showAlert(data.message || 'Error deleting visit', 'danger');
            }
        })
        .catch(error => {
            console.error('Error deleting visit:', error);
            showAlert('Error deleting visit', 'danger');
        });
        */
    }
}

function refreshVisits() {
    loadVisits();
    showAlert('Visits refreshed', 'info');
}

function searchVisits() {
    const searchTerm = document.getElementById('searchInput').value;
    if (searchTerm) {
        visitsTable.setFilter([
            {field: "patient_name", type: "like", value: searchTerm},
            {field: "staff_name", type: "like", value: searchTerm},
            {field: "visit_type", type: "like", value: searchTerm},
            {field: "chief_complaint", type: "like", value: searchTerm},
            {field: "diagnosis", type: "like", value: searchTerm}
        ]);
    } else {
        visitsTable.clearFilter();
    }
}

// Clear search on Enter key
document.getElementById('searchInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        searchVisits();
    }
});

// Clear search when input is empty
document.getElementById('searchInput').addEventListener('input', function(e) {
    if (e.target.value === '') {
        visitsTable.clearFilter();
    }
});

function showAlert(message, type = 'info', title = null) {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${title ? `<h6>${title}</h6>` : ''}
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at top of content
    const content = document.querySelector('.container-fluid');
    content.insertBefore(alertDiv, content.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}
