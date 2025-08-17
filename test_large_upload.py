#!/usr/bin/env python3
"""
Test script to verify large file upload improvements
"""
import requests
import io
import os

def test_upload_size_limits():
    """Test different file sizes to verify our limits work correctly"""
    
    # Test endpoint
    url = "http://localhost:8000/api/patient_documents"
    
    # Create test files of different sizes
    test_cases = [
        ("small_file.txt", 1024),           # 1KB
        ("medium_file.txt", 1024 * 1024),   # 1MB  
        ("large_file.txt", 5 * 1024 * 1024), # 5MB
        ("very_large_file.txt", 15 * 1024 * 1024), # 15MB
        ("too_large_file.txt", 25 * 1024 * 1024)   # 25MB (should fail)
    ]
    
    for filename, size in test_cases:
        print(f"\nTesting {filename} ({size // (1024*1024) if size >= 1024*1024 else size // 1024}{'MB' if size >= 1024*1024 else 'KB'})")
        
        # Create file content
        content = b"A" * size
        file_obj = io.BytesIO(content)
        
        # Prepare request
        files = {'file': (filename, file_obj, 'text/plain')}
        data = {
            'patient_id': '1',  # Assuming patient ID 1 exists
            'description': f'Test upload of {filename}'
        }
        
        try:
            response = requests.post(url, files=files, data=data, timeout=60)
            if response.status_code == 201:
                print(f"✓ SUCCESS: {filename} uploaded successfully")
            elif response.status_code == 413:
                print(f"✗ EXPECTED FAILURE: {filename} - File too large (413)")
            else:
                print(f"✗ FAILURE: {filename} - Status {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"✗ TIMEOUT: {filename} - Request timed out")
        except requests.exceptions.RequestException as e:
            print(f"✗ ERROR: {filename} - {str(e)}")

if __name__ == "__main__":
    print("Testing large file upload improvements...")
    test_upload_size_limits()
    print("\nTest completed!")
