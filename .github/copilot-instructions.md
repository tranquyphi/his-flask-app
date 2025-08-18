# HIS (Hospital Information System) - AI Coding Agent Instructions
## Architecture Overview
This is a **Flask-based Hospital Information System** with MariaDB backend, using SQLAlchemy ORM and a modern web UI built with Bootstrap 5, DataTables.js
### Core Components
- **`models/`**: Directory containing individual ORM model files for each entity
- **`models_main.py`**: Central database setup, configuration, and app factory
- **`his.py`**: Main Flask app that registers blueprints for API and UI routes
- **`api/`**: Directory containing Flask blueprints for all API endpoints
- **`config.py`**: Environment-aware configuration (development/production/testing)
- **`frontend/`**: The UI html pages (template directory)
- **`static/js/`**: Frontend logic for data tables with CRUD operations
- **`schema/`**: Database schemas and views DDL
- **`authorization_audit/`**: Authorization framework (future implementation)
## Database Patterns
### ORM Views (Key Pattern)
Instead of raw SQL, this project uses **ORM models for database views**:
```python
E.g:
class PatientWithDepartment(db.Model):
    __tablename__ = 'patients_with_department'
    __table_args__ = {'info': dict(is_view=True)}
    # ... columns match view structure
    
    def to_dict(self):  # Always include for JSON serialization
        return {'PatientId': self.PatientId, ...}
```
### Enum Types
The database uses ENUM types for fields with predetermined values, such as 'Reason' in PatientDepartment table ('DT','PT','KCK','CLS','KH') representing different types of department transfers.
### CHECK The table structure by DESCRIBE MYSQL statement
### Use schema in folder /schema
### Database Connection
- Connection string: `mysql+pymysql://bvthanghoa:57PhanKeBinh@localhost/examdb`
- Environment variable: `DB_CONNECTION_STRING` 
- Use `python3` (not `python`) for all commands
- Database views in `schema/database_views_enhanced.sql` provide denormalized data
## Frontend Architecture
### UI File Organization (Strict Convention)
- HTML templates: `/frontend/`
- CSS files: `/static/css/`
- JS files: `/static/js/`
- Images: `/static/images/`
- Document storage: `/static/documents/`
### Key Features
- **Patient Management**: Basic patient information and department assignments
- **Department Management**: Assign patients and staff to departments with history tracking
- **Document Management**: Upload and view patient documents including portraits
- **Visit Management**: Track patient visits, diagnoses, and procedures
## Development Workflow
### Service Management
```bash
# Restart HIS service
sudo systemctl daemon-reload #if needed
sudo systemctl restart his.service

# The service runs on port 8000 (not the Flask default of 5000)
# View logs
gunicorn -w 4 -b 0.0.0.0:8000 his:app
journalctl -xeu his.service
```
### Database Views Creation
```python
# Create views using ORM session
from models_main import create_app, db
app = create_app('development')
with app.app_context():
    with open('schema/database_views_enhanced.sql', 'r') as f:
        sql = f.read()
    # Execute view creation statements
```
### Adding New Entities
1. Create ORM model in `models/[EntityName].py`
2. Create view model (if joins needed) following `PatientsWithDepartment` pattern
3. Create API blueprint in `api/[entity_name].py` with CRUD endpoints
4. Register blueprint in `his.py` with appropriate URL prefix
5. Add UI route to `his.py` (`/entity`)
6. Create template in `frontend/entity.html`
7. Create JavaScript in `static/js/entity.js` 
## Critical Conventions
### API Response Format
```python
# Always wrap data in named key
return jsonify({'patients': patients_data})  # Not just patients_data
return jsonify({'error': str(e)}), 500       # Consistent error format
```
### Blueprint Registration
API endpoints are organized as Flask blueprints in the `api/` directory and registered in `his.py` with the appropriate URL prefixes:
```python
app.register_blueprint(entity_bp, url_prefix='/api')
```
### Environment Configuration
- Use `config.py` classes, not direct environment variables
- Three environments: `development`, `production`, `testing`
- Set via `FLASK_ENV` environment variable
### Foreign Key Display
- **Never show IDs in UI** - always show related entity names
- Use database views to join related data (e.g., Department name instead of DepartmentId)
### Error Handling Pattern
```python
def get_entities():
    try:
        entities = EntityWithRelations.query.all()
        return [entity.to_dict() for entity in entities]
    except Exception as e:
        print(f"Error querying view: {e}")
        # Always provide fallback to base table
        return fallback_query()
```
## Front-end Expectations
Use icons instead of text for action buttons.
DataTables integration is required for all tabular data.
Search box
Filters dropdown for the table columns which could acting as category.
### DataTables Integration Requirements
- Download CSS/JS files locally to `/static/`
- All tables must show related entity names (not IDs)
- Action buttons as small icons for each row
- Search and filter capabilities
- Responsive design with Bootstrap 5
## Production Deployment
- Systemd service: `/etc/systemd/system/his.service`
- Uses Gunicorn WSGI server
- Runs on port 8000
- Logs to `/var/log/his/`
- Database connection via environment variables
- Service dependencies: `mysql.service`