# HIS (Hospital Information System) - AI Coding Agent Instructions

## Architecture Overview

This is a **Flask-based Hospital Information System** with MariaDB backend, using SQLAlchemy ORM and a modern web UI built with Bootstrap 5 + Tabulator.js.

### Core Components
- **`models.py`**: Central ORM models + database views as ORM classes (e.g., `PatientWithDepartment`)
- **`his.py`**: Main Flask app with both API routes (`/api/*`) and UI routes (`/patients`, `/dashboard`)
- **`config.py`**: Environment-aware configuration (development/production/testing)
- **`frontend/`**: The UI html pages
- **`static/js/`**: Frontend logic using Tabulator.js for data tables with CRUD operations
- **`schema/`**: Database schemas and views DDL
- **`authorization_audit/`**: Complete authorization framework (future implementation)

## Database Patterns

### ORM Views (Key Pattern)
Instead of raw SQL, this project uses **ORM models for database views**:
```python
class PatientWithDepartment(db.Model):
    __tablename__ = 'patients_with_department'
    __table_args__ = {'info': dict(is_view=True)}
    # ... columns match view structure
    
    def to_dict(self):  # Always include for JSON serialization
        return {'PatientId': self.PatientId, ...}
```

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
- Icons: `/static/icons/`
- Images: `/static/images/`

## Development Workflow

### Service Management
```bash
# Restart HIS service
sudo systemctl daemon-reload
sudo systemctl restart his.service
sudo systemctl status his.service

The port: 8000 (not 5000)
# View logs
journalctl -xeu his.service
```

### Database Views Creation
```python
# Create views using ORM session
from models import create_app, db
app = create_app('development')
with app.app_context():
    with open('schema/database_views_enhanced.sql', 'r') as f:
        sql = f.read()
    # Execute view creation statements
```

### Adding New Entities
1. Create ORM model in `models.py`
2. Create view model (if joins needed) following `PatientWithDepartment` pattern
3. Add API routes in `his.py` (`/api/entity` for GET/POST/PUT/DELETE)
4. Add UI route (`/entity`)
5. Create template in `frontend/entity.html`
6. Create JavaScript in `static/js/entity.js` 

## Critical Conventions

### API Response Format
```python
# Always wrap data in named key
return jsonify({'patients': patients_data})  # Not just patients_data
return jsonify({'error': str(e)}), 500       # Consistent error format
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


### DataTables Integration Requirements
- Download CSS/JS files locally to `/static/`
- All tables must show related entity names (not IDs)
- Action buttons as small icons for each row
- Search and filter capabilities
- Responsive design with Bootstrap 5

## Production Deployment

- Systemd service: `/etc/systemd/system/his.service`
- Uses Gunicorn WSGI server
- Logs to `/var/log/his/`
- Database connection via environment variables
- Service dependencies: `mysql.service`

