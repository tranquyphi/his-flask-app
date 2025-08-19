#!/bin/bash

# Script to check API response structure mismatches
echo "=== Checking API Response Structure Mismatches ==="

echo ""
echo "1. Checking signs.js endpoints..."
echo "   - /api/body_system: expecting body_system, body_systems, or bodySystems"
curl -s "http://localhost:8001/api/body_system" | jq 'keys'

echo "   - /api/signs: checking response structure"
curl -s "http://localhost:8001/api/signs" | head -n 1 | jq 'keys' 2>/dev/null || echo "   Failed or invalid JSON"

echo ""
echo "2. Checking patients_with_departments.js endpoints..."
echo "   - /api/patients_with_department: expecting patients_with_department"
curl -s "http://localhost:8001/api/patients_with_department" | jq 'keys'

echo ""
echo "3. Checking image-related endpoints..."
echo "   - /api/patient/image: checking if exists"
curl -s -w "\nStatus: %{http_code}\n" "http://localhost:8001/api/patient/image" | head -n 5

echo "   - /api/user/image: checking if exists"
curl -s -w "\nStatus: %{http_code}\n" "http://localhost:8001/api/user/image" | head -n 5

echo ""
echo "=== Analysis Complete ==="
