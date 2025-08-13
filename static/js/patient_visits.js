/**
 * Patient Visit History Management
 * Provides functionality for managing patient visits, viewing visit history,
 * and summarizing visit data.
 */

// HIS global namespace for shared utilities and configuration
const HIS = HIS || {};
HIS.apiUrl = '/api';

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM content loaded - initializing Patient Visits page');
    
    // Elements - defined in global scope for the function
    let patientSearchInput;
    let searchBtn;
    let patientInfoContainer;
    let visitDataContainer;
    let createVisitBtn;
    let createVisitModal;
    let saveVisitBtn;
    
    try {
        // Initialize elements
        patientSearchInput = document.getElementById('patient-search');
        console.log('Patient search input element:', patientSearchInput);
        
        searchBtn = document.getElementById('search-btn');
        console.log('Search button element:', searchBtn);
        
        patientInfoContainer = document.getElementById('patient-info-container');
        visitDataContainer = document.getElementById('visit-data-container');
        createVisitBtn = document.getElementById('create-visit-btn');
        
        // Check if modal element exists before creating bootstrap modal
        const createVisitModalElement = document.getElementById('create-visit-modal');
        console.log('Create visit modal element:', createVisitModalElement);
        createVisitModal = createVisitModalElement ? new bootstrap.Modal(createVisitModalElement) : null;
        
        saveVisitBtn = document.getElementById('save-visit-btn');
    } catch (err) {
        console.error('Error initializing elements:', err);
        alert('Error initializing the patient visits page. Check the console for details.');
    }
    
    // Patient info elements
    const patientIdElement = document.getElementById('patient-id');
    const patientNameElement = document.getElementById('patient-name');
    const patientGenderElement = document.getElementById('patient-gender');
    const patientAgeElement = document.getElementById('patient-age');
    const patientAddressElement = document.getElementById('patient-address');
    const totalVisitsBadge = document.getElementById('total-visits-badge');
    const firstVisitDateElement = document.getElementById('first-visit-date');
    const latestVisitDateElement = document.getElementById('latest-visit-date');
    
    // Current patient data
    let currentPatientId = null;
    
    // Initialize Tabulator for visits table
    let visitsTable = new Tabulator("#visits-table", {
        height: "400px",
        layout: "fitColumns",
        placeholder: "No visit data found",
        columns: [
            {title: "Visit ID", field: "VisitId", headerFilter: "input", width: 120},
            {title: "Date & Time", field: "VisitTime", headerFilter: "input", sorter: "datetime", formatter: formatDateTime},
            {title: "Department", field: "DepartmentName", headerFilter: "input"},
            {title: "Purpose", field: "VisitPurpose", headerFilter: "select", headerFilterParams: {
                values: ["Thường quy", "Cấp cứu", "Phòng khám", "Nhận bệnh", "Bệnh án", "Đột xuất", "Hội chẩn", "Xuất viện", "Tái khám", "Khám chuyên khoa"]
            }},
            {title: "Attending Staff", field: "StaffName", headerFilter: "input"},
            {title: "Diagnoses", field: "diagnoses", formatter: formatDiagnoses, headerFilter: false},
            {title: "Actions", formatter: formatActions, headerFilter: false, width: 120}
        ]
    });
    
    // Initialize tables for summary tab
    let departmentVisitsTable = new Tabulator("#department-visits", {
        height: "300px",
        layout: "fitColumns",
        placeholder: "No department data found",
        columns: [
            {title: "Department", field: "department", headerFilter: "input"},
            {title: "Visit Count", field: "count", headerFilter: "input", sorter: "number"}
        ]
    });
    
    let purposeVisitsTable = new Tabulator("#purpose-visits", {
        height: "300px",
        layout: "fitColumns",
        placeholder: "No purpose data found",
        columns: [
            {title: "Visit Purpose", field: "purpose", headerFilter: "input"},
            {title: "Visit Count", field: "count", headerFilter: "input", sorter: "number"}
        ]
    });
    
    let commonDiagnosesTable = new Tabulator("#common-diagnoses", {
        height: "300px",
        layout: "fitColumns",
        placeholder: "No diagnosis data found",
        columns: [
            {title: "Diagnosis", field: "diagnosis", headerFilter: "input"},
            {title: "Occurrence Count", field: "count", headerFilter: "input", sorter: "number"}
        ]
    });
    
    // Event Listeners
    console.log('Setting up event listeners');
    
    if (searchBtn) {
        console.log('Search button found, adding click event');
        searchBtn.addEventListener('click', function() {
            console.log('Search button clicked');
            searchPatient();
        });
    } else {
        console.error('Search button not found!');
    }
    
    if (patientSearchInput) {
        console.log('Patient search input found, adding keypress event');
        patientSearchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                console.log('Enter key pressed in search input');
                searchPatient();
            }
        });
    } else {
        console.error('Patient search input not found!');
    }
    
    createVisitBtn.addEventListener('click', openCreateVisitModal);
    saveVisitBtn.addEventListener('click', saveNewVisit);
    
    // Tab switching event to refresh data when switching to summary tab
    const summaryTab = document.getElementById('summary-tab');
    summaryTab.addEventListener('shown.bs.tab', function (e) {
        if (currentPatientId) {
            loadPatientVisitSummary(currentPatientId);
        }
    });
    
    // On page load, populate patients, departments, and staff dropdowns
    populatePatientDropdown();
    populateDepartmentDropdown();
    populateStaffDropdown();
    
    // Check URL for patient ID parameter
    const urlParams = new URLSearchParams(window.location.search);
    const patientIdParam = urlParams.get('patient_id');
    
    // Add a test button for our test patient
    const container = document.querySelector('.container-fluid');
    if (container) {
        const testButton = document.createElement('button');
        testButton.className = 'btn btn-warning mb-3';
        testButton.innerHTML = 'Test Patient 2500073746';
        testButton.onclick = function() {
            console.log('Test button clicked');
            loadPatientData('2500073746');
        };
        container.insertBefore(testButton, container.firstChild);
    }
    
    // Automatically load test patient data for debugging
    setTimeout(function() {
        console.log('Auto-loading test patient data');
        if (patientIdParam) {
            console.log('Loading patient from URL param:', patientIdParam);
            loadPatientData(patientIdParam);
        } else {
            console.log('Loading default test patient');
            // Uncomment the line below to auto-load the test patient
            // loadPatientData('2500073746');
        }
    }, 1000);
    
    /**
     * Search for patient by ID or name
     */
    function searchPatient() {
        const searchValue = patientSearchInput.value.trim();
        console.log('Search value:', searchValue);
        
        if (!searchValue) {
            showToast('Please enter a patient ID or name', 'warning');
            return;
        }
        
        console.log('Checking for test patient ID match with:', searchValue);
        showToast('Searching for patient: ' + searchValue, 'info');
        
        // Since we know the ID, load directly using the patient_visits API
        if (searchValue === '2500073746') {
            console.log('Match found! Loading test patient data');
            showToast('Loading test patient data', 'success');
            loadPatientData(searchValue);
            return;
        }
        
        // First try exact ID match
        fetch(`${HIS.apiUrl}/patient/${searchValue}`)
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else if (response.status === 404) {
                    // If not found by ID, try searching by name
                    return fetch(`${HIS.apiUrl}/patients?name=${encodeURIComponent(searchValue)}`)
                        .then(nameResponse => {
                            if (nameResponse.ok) {
                                return nameResponse.json();
                            } else {
                                throw new Error('Patient not found');
                            }
                        });
                } else {
                    throw new Error('Error fetching patient');
                }
            })
            .then(data => {
                if (data.patients && data.patients.length > 0) {
                    // If multiple patients found by name, use the first one
                    const patient = data.patients[0];
                    loadPatientData(patient.PatientId);
                } else if (data.patient) {
                    // Single patient found by ID
                    loadPatientData(data.patient.PatientId);
                } else {
                    showToast('No patients found with that ID or name', 'warning');
                }
            })
            .catch(error => {
                console.error('Error searching patient:', error);
                showToast('Error searching for patient: ' + error.message, 'danger');
            });
    }
    
    /**
     * Load patient data and visits
     * @param {string} patientId - The patient ID
     */
    function loadPatientData(patientId) {
        currentPatientId = patientId;
        
        console.log(`Loading patient data for ID: ${patientId}`);
        
        // For our test patient, create some mock data since the API might not be ready
        if (patientId === '2500073746') {
            console.log('Using mock data for test patient');
            
            // Create mock patient data
            const mockPatient = {
                PatientId: '2500073746',
                PatientName: 'Nguyễn Văn A',
                PatientGender: 'Nam',
                PatientAge: '45',
                PatientAddress: 'Hà Nội'
            };
            
            // Create mock visit data
            const mockVisits = [
                {
                    VisitId: '10001',
                    PatientId: '2500073746',
                    DepartmentId: '1',
                    DepartmentName: 'Khoa Nội',
                    VisitPurpose: 'Khám chuyên khoa',
                    VisitTime: '2025-08-10T09:30:00',
                    StaffId: '1',
                    StaffName: 'BS. Nguyễn Thị B',
                    StaffRole: 'Bác sĩ',
                    diagnoses: [
                        {
                            ICDCode: 'I10',
                            ActualDiagnosis: 'Tăng huyết áp'
                        }
                    ]
                },
                {
                    VisitId: '10002',
                    PatientId: '2500073746',
                    DepartmentId: '2',
                    DepartmentName: 'Khoa Tim mạch',
                    VisitPurpose: 'Thường quy',
                    VisitTime: '2025-07-15T10:15:00',
                    StaffId: '2',
                    StaffName: 'BS. Trần C',
                    StaffRole: 'Bác sĩ',
                    diagnoses: [
                        {
                            ICDCode: 'I20',
                            ActualDiagnosis: 'Đau thắt ngực'
                        }
                    ]
                }
            ];
            
            // Display mock data
            displayPatientInfo(mockPatient);
            totalVisitsBadge.textContent = `${mockVisits.length} visits`;
            visitsTable.setData(mockVisits);
            
            // Show containers
            patientInfoContainer.classList.remove('d-none');
            visitDataContainer.classList.remove('d-none');
            
            // Auto-switch to first tab
            const firstTab = document.querySelector('#visit-tabs .nav-link');
            new bootstrap.Tab(firstTab).show();
            
            // Create mock summary data
            mockSummaryData(patientId);
            
            return;
        }
        
        // Regular API flow for other patients
        fetch(`${HIS.apiUrl}/patient_visits/${patientId}`)
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('Failed to load patient visits');
                }
            })
            .then(data => {
                // Display patient info
                displayPatientInfo(data.patient);
                
                // Update visits count badge
                totalVisitsBadge.textContent = `${data.total_visits} visits`;
                
                // Load visit data into table
                visitsTable.setData(data.visits);
                
                // Show containers
                patientInfoContainer.classList.remove('d-none');
                visitDataContainer.classList.remove('d-none');
                
                // Auto-switch to first tab
                const firstTab = document.querySelector('#visit-tabs .nav-link');
                new bootstrap.Tab(firstTab).show();
                
                // Also load the summary data
                loadPatientVisitSummary(patientId);
            })
            .catch(error => {
                console.error('Error loading patient data:', error);
                showToast('Error: ' + error.message, 'danger');
            });
    }
    
    /**
     * Display patient information
     * @param {Object} patient - Patient data object
     */
    function displayPatientInfo(patient) {
        patientIdElement.textContent = patient.PatientId || 'N/A';
        patientNameElement.textContent = patient.PatientName || 'N/A';
        patientGenderElement.textContent = patient.PatientGender || 'N/A';
        patientAgeElement.textContent = patient.PatientAge || 'N/A';
        patientAddressElement.textContent = patient.PatientAddress || 'N/A';
    }
    
    /**
     * Load patient visit summary data
     * @param {string} patientId - The patient ID
     */
    function loadPatientVisitSummary(patientId) {
        // Skip API call for our test patient as we're using mock data
        if (patientId === '2500073746') {
            return;
        }
        
        fetch(`${HIS.apiUrl}/patient_visits/${patientId}/summary`)
            .then(response => response.json())
            .then(data => {
                // Update first and latest visit dates
                firstVisitDateElement.textContent = data.visit_summary.first_visit.time ? 
                    formatDateTime(null, null, null, data.visit_summary.first_visit.time) : 'No visits';
                
                latestVisitDateElement.textContent = data.visit_summary.latest_visit.time ? 
                    formatDateTime(null, null, null, data.visit_summary.latest_visit.time) : 'No visits';
                
                // Update summary tables
                departmentVisitsTable.setData(data.department_visits || []);
                purposeVisitsTable.setData(data.purpose_visits || []);
                commonDiagnosesTable.setData(data.common_diagnoses || []);
            })
            .catch(error => {
                console.error('Error loading visit summary:', error);
                showToast('Error loading visit summary', 'danger');
            });
    }
    
    /**
     * Open the create visit modal
     */
    function openCreateVisitModal() {
        // If we have a current patient, select them in the dropdown
        if (currentPatientId) {
            const patientSelect = document.getElementById('patient-select');
            patientSelect.value = currentPatientId;
        }
        
        // Show the modal
        createVisitModal.show();
    }
    
    /**
     * Save a new visit
     */
    function saveNewVisit() {
        const form = document.getElementById('create-visit-form');
        const patientId = document.getElementById('patient-select').value;
        const departmentId = document.getElementById('department-select').value;
        const staffId = document.getElementById('staff-select').value;
        const visitPurpose = document.getElementById('purpose-select').value;
        const diagnosis = document.getElementById('diagnosis-input').value;
        const icdCode = document.getElementById('icd-input').value;
        
        // Validate required fields
        if (!patientId || !departmentId || !staffId || !visitPurpose) {
            showToast('Please fill in all required fields', 'warning');
            return;
        }
        
        // Create visit data object
        const visitData = {
            DepartmentId: departmentId,
            StaffId: staffId,
            VisitPurpose: visitPurpose
        };
        
        // Add optional diagnosis if provided
        if (diagnosis) {
            visitData.diagnosis = diagnosis;
            if (icdCode) {
                visitData.ICDCode = icdCode;
            }
        }
        
        // Send API request
        fetch(`${HIS.apiUrl}/patient_visits/${patientId}/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(visitData)
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Failed to create visit');
            }
        })
        .then(data => {
            showToast('Visit created successfully', 'success');
            createVisitModal.hide();
            form.reset();
            
            // If we're currently viewing the same patient, refresh the data
            if (currentPatientId === patientId) {
                loadPatientData(patientId);
            } else {
                // If it's a different patient, load that patient's data
                loadPatientData(patientId);
            }
        })
        .catch(error => {
            console.error('Error creating visit:', error);
            showToast('Error: ' + error.message, 'danger');
        });
    }
    
    /**
     * Populate the patient dropdown with all patients
     */
    function populatePatientDropdown() {
        const patientSelect = document.getElementById('patient-select');
        
        fetch(`${HIS.apiUrl}/patient`)
            .then(response => response.json())
            .then(data => {
                if (data.patient && Array.isArray(data.patient)) {
                    // Clear existing options
                    patientSelect.innerHTML = '<option value="">Select Patient</option>';
                    
                    // Sort patients by name
                    const sortedPatients = data.patient.sort((a, b) => 
                        a.PatientName.localeCompare(b.PatientName)
                    );
                    
                    // Add options
                    sortedPatients.forEach(patient => {
                        const option = document.createElement('option');
                        option.value = patient.PatientId;
                        option.textContent = `${patient.PatientName} (ID: ${patient.PatientId})`;
                        patientSelect.appendChild(option);
                    });
                }
            })
            .catch(error => {
                console.error('Error loading patients:', error);
                showToast('Error loading patients', 'danger');
            });
    }
    
    /**
     * Populate the department dropdown with all departments
     */
    function populateDepartmentDropdown() {
        const departmentSelect = document.getElementById('department-select');
        
        fetch(`${HIS.apiUrl}/department`)
            .then(response => response.json())
            .then(data => {
                if (data.department && Array.isArray(data.department)) {
                    // Clear existing options
                    departmentSelect.innerHTML = '<option value="">Select Department</option>';
                    
                    // Add options
                    data.department.forEach(dept => {
                        const option = document.createElement('option');
                        option.value = dept.DepartmentId;
                        option.textContent = dept.DepartmentName;
                        departmentSelect.appendChild(option);
                    });
                }
            })
            .catch(error => {
                console.error('Error loading departments:', error);
                showToast('Error loading departments', 'danger');
            });
    }
    
    /**
     * Populate the staff dropdown with all staff
     */
    function populateStaffDropdown() {
        const staffSelect = document.getElementById('staff-select');
        
        fetch(`${HIS.apiUrl}/staff`)
            .then(response => response.json())
            .then(data => {
                if (data.staff && Array.isArray(data.staff)) {
                    // Clear existing options
                    staffSelect.innerHTML = '<option value="">Select Staff</option>';
                    
                    // Sort staff by name and role
                    const sortedStaff = data.staff.sort((a, b) => {
                        if (a.StaffRole === b.StaffRole) {
                            return a.StaffName.localeCompare(b.StaffName);
                        }
                        return a.StaffRole.localeCompare(b.StaffRole);
                    });
                    
                    // Add options
                    sortedStaff.forEach(staff => {
                        const option = document.createElement('option');
                        option.value = staff.StaffId;
                        option.textContent = `${staff.StaffName} (${staff.StaffRole})`;
                        staffSelect.appendChild(option);
                    });
                }
            })
            .catch(error => {
                console.error('Error loading staff:', error);
                showToast('Error loading staff', 'danger');
            });
    }
    
    /**
     * Format date and time for display
     * @param {Object|null} cell - Tabulator cell object or null for direct string
     * @param {Object|null} formatterParams - Tabulator formatter params
     * @param {function|null} onRendered - Tabulator onRendered callback
     * @param {string|null} directDateStr - Direct date string to format (when not using as Tabulator formatter)
     * @returns {string} - Formatted date and time
     */
    function formatDateTime(cell, formatterParams, onRendered, directDateStr) {
        const dateTimeStr = directDateStr || (cell ? cell.getValue() : null);
        if (!dateTimeStr) return 'N/A';
        
        try {
            const date = new Date(dateTimeStr);
            return date.toLocaleString('vi-VN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (e) {
            return dateTimeStr;
        }
    }
    
    /**
     * Format diagnoses for display
     * @param {Object} cell - Tabulator cell object
     * @returns {string} - HTML string for diagnoses
     */
    function formatDiagnoses(cell, formatterParams, onRendered) {
        const diagnoses = cell.getValue();
        if (!diagnoses || !diagnoses.length) return 'N/A';
        
        return diagnoses.map(d => 
            `<div>${d.ActualDiagnosis}${d.ICDCode ? ` (${d.ICDCode})` : ''}</div>`
        ).join('');
    }
    
    /**
     * Format action buttons for each row
     * @param {Object} cell - Tabulator cell object
     * @returns {string} - HTML string for action buttons
     */
    function formatActions(cell, formatterParams, onRendered) {
        const row = cell.getRow();
        const visitId = row.getData().VisitId;
        
        return `
            <div class="d-flex gap-1">
                <button class="btn btn-sm btn-info view-visit-btn" data-id="${visitId}" title="View">
                    <i class="bi bi-eye"></i>
                </button>
                <button class="btn btn-sm btn-warning edit-visit-btn" data-id="${visitId}" title="Edit">
                    <i class="bi bi-pencil"></i>
                </button>
            </div>
        `;
    }
    
    /**
     * Create mock summary data for our test patient
     * @param {string} patientId - The patient ID
     */
    function mockSummaryData(patientId) {
        // Mock department visits data
        const mockDeptVisits = [
            { department: 'Khoa Nội', count: 1 },
            { department: 'Khoa Tim mạch', count: 1 }
        ];
        
        // Mock purpose visits data
        const mockPurposeVisits = [
            { purpose: 'Khám chuyên khoa', count: 1 },
            { purpose: 'Thường quy', count: 1 }
        ];
        
        // Mock diagnoses data
        const mockDiagnoses = [
            { diagnosis: 'Tăng huyết áp', count: 1 },
            { diagnosis: 'Đau thắt ngực', count: 1 }
        ];
        
        // Update first and latest visit dates
        firstVisitDateElement.textContent = formatDateTime(null, null, null, '2025-07-15T10:15:00');
        latestVisitDateElement.textContent = formatDateTime(null, null, null, '2025-08-10T09:30:00');
        
        // Update summary tables
        departmentVisitsTable.setData(mockDeptVisits);
        purposeVisitsTable.setData(mockPurposeVisits);
        commonDiagnosesTable.setData(mockDiagnoses);
    }
    
    /**
     * Show a toast notification
     * @param {string} message - Message to display
     * @param {string} type - Type of notification (success, warning, danger)
     */
    function showToast(message, type = 'info') {
        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast element
        const toastId = 'toast-' + Date.now();
        const toast = document.createElement('div');
        toast.className = `toast text-white bg-${type}`;
        toast.id = toastId;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        // Create toast content
        toast.innerHTML = `
            <div class="toast-header">
                <strong class="me-auto">HIS Notification</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        
        // Add to container
        toastContainer.appendChild(toast);
        
        // Initialize and show the toast
        const toastInstance = new bootstrap.Toast(toast);
        toastInstance.show();
        
        // Remove after it's hidden
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    }
    
    // Add event delegation for dynamic buttons
    document.addEventListener('click', function(e) {
        // View visit button
        if (e.target.closest('.view-visit-btn')) {
            const button = e.target.closest('.view-visit-btn');
            const visitId = button.getAttribute('data-id');
            viewVisit(visitId);
        }
        
        // Edit visit button
        if (e.target.closest('.edit-visit-btn')) {
            const button = e.target.closest('.edit-visit-btn');
            const visitId = button.getAttribute('data-id');
            editVisit(visitId);
        }
    });
    
    /**
     * View visit details
     * @param {string} visitId - Visit ID
     */
    function viewVisit(visitId) {
        // Find the visit data in the table
        const visit = visitsTable.getData().find(v => v.VisitId == visitId);
        if (!visit) {
            showToast('Visit details not found', 'warning');
            return;
        }
        
        // TODO: Implement view visit details
        alert(`View visit details for Visit ID: ${visitId}`);
        console.log('Visit details:', visit);
    }
    
    /**
     * Edit visit details
     * @param {string} visitId - Visit ID
     */
    function editVisit(visitId) {
        // Find the visit data in the table
        const visit = visitsTable.getData().find(v => v.VisitId == visitId);
        if (!visit) {
            showToast('Visit details not found', 'warning');
            return;
        }
        
        // TODO: Implement edit visit details
        alert(`Edit visit details for Visit ID: ${visitId}`);
        console.log('Visit details to edit:', visit);
    }
});
