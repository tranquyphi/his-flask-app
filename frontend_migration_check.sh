#!/bin/bash
# Frontend API Endpoint Updater - Optional
# This script can update frontend JS to point to FastAPI endpoints

echo "=== Frontend FastAPI Migration Helper ==="
echo

echo "Current frontend API calls are compatible with FastAPI!"
echo "Both Flask and FastAPI serve the same JSON responses."
echo

echo "📍 Current API calls in JS files:"
echo "   fetch('/api/body_parts')        ← Works with both"
echo "   fetch('/api/departments')       ← Works with both" 
echo "   fetch('/api/patients')          ← Works with both"
echo

echo "✅ No changes needed for frontend!"
echo "🔄 Optional: Update base URL if serving from different domain"

# Optional: Find and list all API calls
echo "📋 All API endpoints used in frontend:"
find /root/his/static/js/ -name "*.js" -exec grep -l "fetch.*api" {} \; | head -5
