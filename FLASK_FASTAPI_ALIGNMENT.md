# Flask-to-FastAPI Model Alignment Documentation

## Overview
This document describes the approach taken to ensure FastAPI endpoints match Flask API responses exactly, maintaining frontend compatibility during the migration process.

## Key Principle: Flask as Reference
**The existing Flask models, columns, and API structures serve as the authoritative reference** for FastAPI implementation. FastAPI must match Flask exactly to ensure frontend JavaScript code works without modification.

## Model Alignment Process

### 1. Field Selection Matching
Flask endpoints often return only specific subsets of model fields. FastAPI must match exactly:

**Example: Patients API**
- **Flask returns (7 fields)**: PatientId, PatientName, PatientGender, PatientAge, PatientAddress, PatientPhone, PatientBHYT
- **FastAPI must return identical fields** - not all 13+ available patient fields

### 2. Join Structure Matching
Flask APIs that join multiple tables must be replicated exactly in FastAPI:

**Example: Department Patients API**
```python
# Flask query structure (reference)
results = db.session.query(
    PatientDepartment.PatientId,
    PatientDepartment.DepartmentId, 
    PatientDepartment.Current,
    PatientDepartment.At,
    Patient.PatientAge,
    Patient.PatientAddress,
    # ... all patient fields
    Department.DepartmentName,
    Department.DepartmentType
).join(Patient).join(Department)

# FastAPI must replicate exactly
results = db.query(
    PatientDepartment.PatientId,
    PatientDepartment.DepartmentId,
    PatientDepartment.Current, 
    PatientDepartment.At,
    Patient.PatientAge,
    Patient.PatientAddress,
    # ... same fields in same order
    Department.DepartmentName,
    Department.DepartmentType
).join(Patient).join(Department)
```

### 3. Response Structure Matching
JSON response format must be identical:

**Example: Signs API**
```python
# Flask response structure (reference)
{
  "signs": [
    {
      "SignId": 393,
      "SignDesc": "Ăn không tiêu", 
      "SignType": 0,  # Note: converted from boolean
      "SystemId": 5,
      "Speciality": "Chung",
      "SystemName": "Tiêu hoá"  # From join
    }
  ]
}

# FastAPI must match exactly
return {'signs': data}  # Not {'data': signs} or similar
```

### 4. Data Type Conversion Matching
Flask often applies data transformations that must be preserved:

**Examples:**
- `SignType`: Flask converts boolean to 0/1 integer → FastAPI must do same
- `At` timestamps: Flask converts to ISO format → FastAPI must match
- Null handling: Flask behavior must be preserved

### 5. Query Parameter Matching
All Flask query parameters and filters must work identically in FastAPI:

**Example: Signs API Filters**
```python
# Flask supports these parameters
q = request.args.get('q', type=str)  # Search term
sign_type = request.args.get('type', type=str)  # '0' or '1'
system_id = request.args.get('system_id', type=int)
speciality = request.args.get('speciality', type=str)

# FastAPI must support identical parameters
async def get_all_signs(
    q: Optional[str] = Query(None),
    type: Optional[str] = Query(None),  # Same name: 'type'
    system_id: Optional[int] = Query(None),
    speciality: Optional[str] = Query(None)
):
```

## Service Management

### Single Service Mode
The application runs either Flask OR FastAPI, not both simultaneously:

```bash
# Switch to Flask mode
./service_manager.sh flask

# Switch to FastAPI mode  
./service_manager.sh fastapi

# Check current status
./service_manager.sh status
```

### Frontend API Configuration
The `api-config.js` file provides a unified interface that works with either backend:

```javascript
// Automatically routes to correct backend (port 8000)
makeApiCall({
    url: '/api/patients',
    method: 'GET',
    success: function(data) {
        // Works identically with Flask or FastAPI
        console.log(data.patients);
    }
});
```

## Validation Checklist

When implementing FastAPI endpoints, verify:

1. **Field Count**: Exact same number of fields as Flask
2. **Field Names**: Identical field names and casing  
3. **Data Types**: Same data types and conversions
4. **Join Structure**: Identical table joins and field selection
5. **Response Format**: Same JSON structure (`{key: data}`)
6. **Query Parameters**: All Flask parameters supported
7. **Error Handling**: Similar error response format

## Benefits

1. **Zero Frontend Changes**: JavaScript code works with both backends
2. **Gradual Migration**: Can switch back to Flask if needed
3. **Consistent Behavior**: Users see no difference
4. **Reliable Testing**: Compare Flask vs FastAPI responses directly

## Example Comparison Command

```bash
# Test both backends return identical data
curl -s "http://127.0.0.1:8000/api/patients" > flask_response.json
./service_manager.sh fastapi
sleep 2
curl -s "http://127.0.0.1:8000/api/patients" > fastapi_response.json
diff flask_response.json fastapi_response.json
# Should show no differences
```

This approach ensures a seamless migration where FastAPI provides performance benefits while maintaining complete compatibility with existing frontend code.
