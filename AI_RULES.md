## Assistant Rules for This HIS Project

These rules guide the AI assistant (pair programmer) working on the Health Information System (HIS). They complement team documents like `CONTRIBUTING.md` and deployment configs.

### Role and Scope
- Act as a pragmatic, detail-oriented pair programmer.
- Domain: patients, departments, staff, and visits (clinical signs, drugs, tests, procedures).
- Stack: Flask API (Python) + MariaDB; UI: Jinja2 + DataTables; Ubuntu + nginx + gunicorn + systemd.

### Priorities (highest first)
1. Data safety and correctness (constraints, transactions, migrations).
2. Follow existing patterns; keep lints/tests green when configured.
3. Minimal diffs; no drive-by refactors.
4. Concise communication; show only necessary code/commands.

### Inputs/Outputs
- Use backticks for `files`, `dirs`, and `functions`.
- Provide fenced blocks only for code edits, commands, or configs.
- Default to concise bullets + targeted edits; avoid verbose narration.

### Tooling and Autonomy
- May read/search code, propose edits, and run non-interactive commands.
- Do not execute destructive DB ops or apply migrations without stating assumptions and rollback.
- Prefer parallel discovery operations; ask only when blocked by missing decisions or credentials.

### Code and Quality Gates
- Python 3.11+ recommended. If configured, obey `ruff`, `black`, `isort`, and `mypy`.
- Database changes use direct SQL for schema changes; enforce FKs, NOT NULL, proper indexes.
- API design: predictable JSON, correct HTTP statuses, error codes; paginate endpoints consumed by DataTables (server-side mode for large datasets).

### Workflow
- Discovery pass to find relevant files and patterns.
- Implement minimal, focused edits. After edits, run lints/tests; fix new issues.
- End with a brief summary of changes and impact.

### Security and Privacy
- Treat patient data as sensitive (PHI). Avoid logging PII/PHI; redact where needed.
- Validate inputs; use least-privilege DB accounts; avoid exposing internal errors to clients.

### Stack Details
- Flask entrypoint: `his.py` exposes `app`.
- Gunicorn: `gunicorn -c gunicorn.conf.py his:app` (port 8000, nginx backend).
- Systemd: `his.service` manages the app (Gunicorn service on port 8000).
- nginx: site `his` in `sites-available`, symlink to `sites-enabled`, proxying to gunicorn on 127.0.0.1:8000.
- Frontend: `frontend/` directory for UI pages; assets: `static/`; DataTables used for UI.

### Success Criteria (Rubric)
- Must: preserve data integrity and API compatibility; no new lints/test failures; minimal diff.
- Should: clear naming, guard clauses, transactions; efficient queries with indexes.
- Avoid: silent schema/API changes, broad refactors, formatting-only diffs.

### Efficiency Rules (Prevent Delays)
- ALWAYS check existing routes/endpoints BEFORE making changes: `python3 -c "from his import app; [print(f'{rule.rule} -> {rule.endpoint}') for rule in app.url_map.iter_rules()]"`
- ALWAYS verify database schema BEFORE API changes: check if required columns exist
- ALWAYS test ONE endpoint at a time to isolate issues
- NEVER restart services multiple times - fix all issues in one go
- ALWAYS verify blueprint registration matches URL patterns in JavaScript
- ALWAYS check for syntax errors: `python3 -m py_compile filename.py`
- ALWAYS verify import paths and circular dependencies before blueprint changes
- ALWAYS test API endpoints with `curl` before testing in browser
- ALWAYS check service status: `sudo systemctl status his.service`
- ALWAYS verify file paths match between API and frontend expectations
- DELETE all temporary files after successfully testing
- ALWAYS check `config.py` for database connection and environment settings before making DB changes
- ALWAYS use `frontend/` directory for actual UI pages (not `templates/`)
- ALWAYS use `/static/templates/` for base templates and reusable components (when implemented)
- ALWAYS check `docs/db/ddl/` for database schema before implementing model changes
- ALWAYS review DDL files to identify missing tables/columns before implementation
- NEVER run DDL files in terminal - user manually adds missing schema elements

### Database Schema Documentation
- Schema DDL files are stored in `docs/db/ddl/`
- File names align with entities (e.g., `staff_documents` for Staff, StaffDocuments, DocumentType tables)
- ALWAYS review DDL files before implementing model changes
- Report missing tables/columns to user - they manually add schema elements
- NEVER execute DDL files in terminal

### Gunicorn Service Configuration
- Service file: `his.service` (systemd service)
- Port: 8000 (not conventional Flask 5000)
- Gunicorn runs as nginx backend service
- Bind: 127.0.0.1:8000 (localhost only, nginx proxies external requests)
- Service management: `sudo systemctl restart/stop/status his.service`

### Folder Structure (Project Architecture)
- `/frontend/` = Actual application UI pages (staff_documents.html, body_sites.html, index.html)
- `/static/templates/` = Base templates, reusable components, samples (not yet implemented)
- `/static/` = Assets (CSS, JS, images, document storage)
- `/api/` = Flask API blueprints
- `/models/` = SQLAlchemy models
- This structure separates UI pages from reusable templates for better maintainability

### Good vs. Bad Output (Example)
- Good: "Add server-side pagination to `GET /api/patients`. Edits: `api/patients.py` (paginate query), `templates/patients.html` (DataTables serverSide). Added tests in `tests/test_patients.py`."
- Bad: A long narrative with no concrete file references or code edits.

Note: The canonical set the assistant reads is `.cursor/rules`. This file is a human-readable mirror for the team that has been updated with current best practices and lessons learned from development.
