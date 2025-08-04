# Environment Variables Usage Guide for HIS Flask Application

## Overview

This guide explains how to use environment variables declared in your `his.service` systemd service file and how they're consumed by your Flask application.

## File Structure

- `config.py` - Configuration classes for different environments
- `environment.py` - Environment variable helper functions and demonstration routes
- `models.py` - Database models with environment-aware configuration
- `his.py` - Main Flask application

## Environment Variables in his.service

Your systemd service file declares environment variables that are available to your Flask application when it runs under systemd:

```ini
[Service]
Environment="DB_CONNECTION_STRING=mysql+pymysql://bvthanghoa:57PhanKeBinh@localhost/examdb"
Environment="FLASK_ENV=production"
Environment="SECRET_KEY=your-production-secret-key-change-this"
Environment="GUNICORN_WORKERS=4"
Environment="LOG_LEVEL=INFO"
```

## How to Use Environment Variables in Flask

### 1. Basic Usage with `os.getenv()`

```python
import os

# Get environment variable with fallback
database_url = os.getenv('DB_CONNECTION_STRING', 'default_connection_string')
log_level = os.getenv('LOG_LEVEL', 'INFO')
secret_key = os.getenv('SECRET_KEY', 'development-key')
```

### 2. Configuration Class Approach (Recommended)

We've implemented a configuration class system in `config.py`:

```python
class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DB_CONNECTION_STRING',
        'mysql+pymysql://bvthanghoa:57PhanKeBinh@localhost/examdb'
    )
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
```

### 3. Using in Flask Application

In your `models.py` and `his.py`:

```python
from config import config
import os

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Determine configuration from environment
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Load configuration
    app.config.from_object(config[config_name])
    return app
```

## Available Environment Variables

| Variable | Purpose | Default | Example |
|----------|---------|---------|---------|
| `DB_CONNECTION_STRING` | Database connection URL | Local MySQL | `mysql+pymysql://user:pass@host/db` |
| `FLASK_ENV` | Flask environment | `development` | `production`, `development`, `testing` |
| `SECRET_KEY` | Flask secret key | Random string | `your-secure-secret-key` |
| `LOG_LEVEL` | Logging level | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_FILE` | Log file path | `/var/log/his/his.log` | `/path/to/logfile.log` |
| `GUNICORN_WORKERS` | Number of Gunicorn workers | `4` | `2`, `4`, `8` |
| `GUNICORN_BIND` | Gunicorn bind address | `127.0.0.1:8000` | `0.0.0.0:8000` |
| `SESSION_LIFETIME_HOURS` | Session timeout | `8` | `4`, `12`, `24` |

## Setting Environment Variables

### 1. In systemd service file:
```ini
Environment="VARIABLE_NAME=value"
```

### 2. In shell (for testing):
```bash
export VARIABLE_NAME=value
```

### 3. In .env file (for development):
```
VARIABLE_NAME=value
```

## Examples

### Using the Environment Module

The `environment.py` module provides helper functions and demonstration routes:

```python
from environment import get_pagination_settings, get_database_pool_settings

# Get pagination settings from environment variables
pagination = get_pagination_settings()
# Returns: {'items_per_page': 20, 'max_per_page': 100}

# Get database pool settings
pool_settings = get_database_pool_settings()
# Returns: {'pool_size': 10, 'max_overflow': 20, 'pool_recycle': 3600}
```

### Available Routes from Environment Module

- `GET /config` - Show current configuration (sanitized)
- `GET /health` - Health check endpoint with database status

### Test Configuration Access

Create a route to view current configuration:

```python
@app.route('/config')
def show_config():
    return jsonify({
        'environment': os.getenv('FLASK_ENV'),
        'log_level': os.getenv('LOG_LEVEL'),
        'workers': os.getenv('GUNICORN_WORKERS'),
        'database_configured': bool(app.config.get('SQLALCHEMY_DATABASE_URI'))
    })
```

### Using in Business Logic

```python
def get_pagination_settings():
    return {
        'items_per_page': int(os.getenv('ITEMS_PER_PAGE', 20)),
        'max_per_page': int(os.getenv('MAX_ITEMS_PER_PAGE', 100))
    }
```

## Security Best Practices

1. **Never commit sensitive values** to version control
2. **Use different values** for different environments
3. **Validate environment variables** at startup
4. **Provide sensible defaults** for non-critical settings
5. **Log configuration** (but not sensitive values) at startup

## Testing Environment Variables

```bash
# Test with specific environment variables
export FLASK_ENV=development
export DB_CONNECTION_STRING="mysql+pymysql://user:pass@localhost/testdb"
export LOG_LEVEL=DEBUG

# Run your application
/root/his/venv/bin/python his.py
```

## Deployment Setup

1. **Update systemd service** with your environment variables
2. **Reload systemd**:
   ```bash
   sudo systemctl daemon-reload
   ```
3. **Start/restart service**:
   ```bash
   sudo systemctl restart his.service
   ```
4. **Check environment variables are loaded**:
   ```bash
   sudo systemctl show his.service --property=Environment
   ```

## Troubleshooting

### Check if environment variables are set:
```bash
# In Python
import os
print(f"DB_CONNECTION_STRING: {os.getenv('DB_CONNECTION_STRING', 'NOT SET')}")

# In systemd service
sudo systemctl show his.service --property=Environment
```

### Common issues:
- Environment variables not quoted properly in service file
- Variables not exported in shell
- Typos in variable names
- Service not reloaded after changes

## Example systemd service with all variables:

```ini
[Unit]
Description=HIS Flask Application
After=network.target mysql.service

[Service]
Type=notify
User=root
Group=www-data
WorkingDirectory=/root/his
Environment="PATH=/root/his/venv/bin"
Environment="DB_CONNECTION_STRING=mysql+pymysql://bvthanghoa:57PhanKeBinh@localhost/examdb"
Environment="FLASK_ENV=production"
Environment="SECRET_KEY=your-production-secret-key"
Environment="LOG_LEVEL=INFO"
Environment="GUNICORN_WORKERS=4"
Environment="GUNICORN_BIND=127.0.0.1:8000"

ExecStart=/root/his/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 his:app
Restart=always

[Install]
WantedBy=multi-user.target
```
