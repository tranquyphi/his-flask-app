#!/bin/bash

# Script to test the patient documents functionality

echo "Testing the patient documents functionality..."

# Step 1: Verify the service is running
echo "Step 1: Verifying service status..."
systemctl status his.service | grep "active (running)" > /dev/null
if [ $? -eq 0 ]; then
    echo "  ✓ Service is running"
else
    echo "  ✗ Service is not running. Please restart the service."
    exit 1
fi

# Step 2: Verify the patient-documents page is accessible
echo "Step 2: Verifying UI page..."
curl -s -I http://localhost:8000/patient-documents | grep "200 OK" > /dev/null
if [ $? -eq 0 ]; then
    echo "  ✓ Patient documents UI page is accessible"
else
    echo "  ✗ Patient documents UI page is not accessible"
    exit 1
fi

# Step 3: Verify the patients API is working
echo "Step 3: Verifying patients API..."
PATIENTS_RESPONSE=$(curl -s http://localhost:8000/api/patients)
echo "$PATIENTS_RESPONSE" | grep "PatientId" > /dev/null
if [ $? -eq 0 ]; then
    echo "  ✓ Patients API is working"
else
    echo "  ✗ Patients API is not working"
    exit 1
fi

# Step 4: Verify the document_types API is working
echo "Step 4: Verifying document types API..."
DOC_TYPES_RESPONSE=$(curl -s http://localhost:8000/api/document_types)
echo "$DOC_TYPES_RESPONSE" | grep "DocumentTypeId" > /dev/null
if [ $? -eq 0 ]; then
    echo "  ✓ Document types API is working"
else
    echo "  ✗ Document types API is not working"
    exit 1
fi

# Step 5: Verify the patient_documents API is working
echo "Step 5: Verifying patient documents API..."
DOC_RESPONSE=$(curl -s http://localhost:8000/api/patient_documents)
echo "$DOC_RESPONSE" | grep "patient_documents" > /dev/null
if [ $? -eq 0 ]; then
    echo "  ✓ Patient documents API is working"
else
    echo "  ✗ Patient documents API is not working"
    exit 1
fi

echo "All tests passed! The patient documents functionality is working correctly."
echo "You can access the patient documents UI at: http://your-server:8000/patient-documents"
