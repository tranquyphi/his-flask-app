## Contributing Guide

This project is a Health Information System (HIS) built with Flask (Python) and MariaDB, rendered via Jinja2 templates using DataTables. It runs on Ubuntu behind nginx with gunicorn managed by systemd.

### 1) Getting Started
- Prerequisites: Python 3.11+, MariaDB client/server, make (optional).
- Create a virtual environment and install dependencies:
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
# If a requirements file exists; otherwise install packages as needed
[ -f requirements.txt ] && pip install -r requirements.txt || true
```
- Environment: copy `.env.example` to `.env` (if present) and set DB creds.

### 2) Running the App (Dev)
- Flask dev server:
```bash
export FLASK_APP=his.py
export FLASK_ENV=development
flask run
```
- gunicorn (dev):
```bash
gunicorn -c gunicorn.conf.py his:app
```

### 3) Database
- Use Alembic for schema changes. Suggested workflow:
```bash
alembic revision -m "describe change"
alembic upgrade head
```
- Conventions:
  - Tables: `snake_case` plural (e.g., `patients`, `staff_visits`).
  - Primary keys: `id` BIGINT AUTO_INCREMENT.
  - Foreign keys: `*_id` with ON DELETE behavior chosen explicitly.
  - Timestamps: `created_at`, `updated_at` (TIMESTAMP or DATETIME, server default where appropriate).
  - Indexes: add for frequent lookups and joins.

### 4) API Conventions
- Version if needed (e.g., `/api/v1/...`).
- JSON responses: consistent envelope or direct resources; include `error` object with `code` and `message` on failures.
- Pagination: support `start`, `length`, and `search[value]` for DataTables server-side processing.
- Validation: validate/sanitize inputs; return appropriate HTTP status codes.

### 5) UI Conventions (DataTables)
- Initialize DataTables with serverSide mode for large datasets.
- Place pages in `templates/` and assets in `static/`.
- Keep JS initialization code modular (e.g., a small script per table page).

### 6) Coding Standards
- Python style: if configured, use `ruff`, `black`, and `isort`. If not, match existing formatting and avoid style-only diffs.
- Typing: add type hints to new/changed public functions.
- Control flow: prefer guard clauses and minimal nesting; handle edge cases first.
- Naming: descriptive, full words; avoid abbreviations.

### 7) Tests and Quality Gates
- Add/adjust tests for new behavior (pytest recommended).
- Require: tests pass and lints (if configured) are clean before merging.

### 8) Commit and PR Style
- Commits: imperative mood ("Add patients pagination"). Keep diffs focused.
- PR checklist:
  - [ ] Purpose and scope described
  - [ ] Tests added/updated
  - [ ] Lints/formatting clean (if configured)
  - [ ] Migrations included and documented when schema changes
  - [ ] Backward compatibility stated for APIs

### 9) Deployment Notes
- gunicorn config: `gunicorn.conf.py` at repo root (recommended).
- systemd: `/etc/systemd/system/his.service` managing `his:app`.
- nginx: site config `his` in `sites-available` → symlink to `sites-enabled`.
- Logs: ensure no PII/PHI is logged; rotate via `logrotate` as needed.

### 10) Security and Privacy
- Treat patient data as sensitive. Redact PII/PHI in logs and error messages.
- Apply least-privilege DB credentials. Validate all inputs.

Refer also to `AI_RULES.md` and `.cursor/rules` for assistant behavior the team expects.
