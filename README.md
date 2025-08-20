# Health Information System (HIS)

A Flask-based Health Information System for managing patients, departments, staff, and clinical visits.

## Features

- **Patient Management**: Patient records and information
- **Department Management**: Hospital departments and staff
- **Clinical Visits**: Clinical signs, drugs, tests, and procedures
- **Document Management**: Staff documents and file handling
- **User Authentication**: Secure access control

## Technology Stack

- **Backend**: Flask (Python 3.11+)
- **Database**: MySQL/MariaDB with SQLAlchemy
- **Web Server**: Gunicorn + nginx
- **Process Manager**: systemd
- **Frontend**: Jinja2 templates with DataTables

## Architecture

```
/frontend/          # UI pages (staff_documents.html, body_sites.html, index.html)
/static/templates/  # Base templates and reusable components
/static/            # Assets (CSS, JS, images, document storage)
/api/               # Flask API blueprints
/models/            # SQLAlchemy models
/docs/              # Documentation and database schema
```

## Quick Start

### Prerequisites
- Python 3.11+
- MySQL/MariaDB
- nginx
- systemd

### Installation
1. Clone the repository
2. Create virtual environment: `python3 -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`

### Configuration
1. Set environment variables in `his.service`:
   ```ini
   Environment="DB_CONNECTION_STRING=mysql+pymysql://user:pass@localhost/db"
   Environment="SECRET_KEY=your-secure-secret-key"
   ```

2. Update `config.py` as needed

### Running
- **Development**: `python3 his.py`
- **Production**: `sudo systemctl start his`
- **Check Status**: `sudo systemctl status his`

## Service Management

- **Service File**: `his.service`
- **Port**: 8000 (Gunicorn backend)
- **External Access**: nginx proxy on port 80/443
- **Logs**: `/var/log/his/`

## Database Schema

Schema definitions are stored in `docs/db/ddl/`:
- Review DDL files before making model changes
- Report missing tables/columns to developers
- Never execute DDL files directly

## Security

- Environment-based configuration
- Secure session management
- CSRF protection enabled
- Input validation and sanitization
- Least-privilege database access

## Development

- Follow existing project conventions
- Use transactions for multi-table writes
- Validate API contracts
- Test endpoints before deployment
- Check service status after changes
