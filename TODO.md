# TODO - HIS Project

## High Priority

### Configuration & Security
- [x] Update `config.py` with security improvements
- [x] Generate secure SECRET_KEY
- [x] Update `his.service` with environment variables
- [x] Remove hardcoded credentials
- [ ] Test configuration validation
- [ ] Verify CORS settings work correctly

### Service & Infrastructure
- [x] Service running on port 8000
- [x] Environment variables configured
- [x] Test service restart scenarios
- [ ] Verify log rotation works
- [x ] Check nginx proxy configuration

## Medium Priority

### API & Endpoints
- [x ] Review all API endpoints
- [ ] Test API functionality
- [ ] Verify JSON response formats
- [ ] Check error handling
- [ ] Test pagination for DataTables

### Database & Models
- [x ] Review database schema
- [ ] Check model relationships
- [ ] Verify foreign key constraints
- [ ] Test database connections
- [ ] Review DDL files in `docs/db/ddl/`
- [ ] **IMPORTANT: Update junction table models to use surrogate primary keys**

  - [x] VisitDiagnosis: Add `id` primary key, make (VisitId, ICDCode) unique
  - [x] VisitTest: Add `id` primary key, make (VisitId, TestId) unique
  - [x] VisitDrug: Add `id` primary key, make (VisitId, DrugId) unique
  - [x] VisitProc: Add `id` primary key, make (VisitId, ProcId) unique
  - [x] VisitSign: Add `id` primary key, make (VisitId, SignId) unique
  - [x] VisitStaff: Add `id` primary key, make (VisitId, StaffId) unique
  - [x] StaffDepartment: Add `id` primary key, make (StaffId, DepartmentId) unique
  - [x] SignTemplateDetail: Add `id` primary key, make (SignTemplateId, SignId) unique
  - [x] DrugTemplateDetail: Already has `id` primary key
  - [x] TestTemplate: Already has `TestTemplateId` primary key
- [x] VisitDocument
### Frontend & UI
- [ ] Test frontend pages
- [ ] Verify DataTables integration
- [ ] Check static asset loading
- [ ] Test file upload functionality
- [ ] Validate form submissions

## Low Priority

### Documentation
- [x] Create session tracking files
- [x] Create README.md
- [x] Create CHANGELOG.md
- [x] Create TODO.md
- [ ] Add API documentation
- [ ] Document database schema
- [ ] Add deployment guide

### Testing & Quality
- [ ] Run linting tools
- [ ] Check for syntax errors
- [ ] Test error scenarios
- [ ] Verify security settings
- [ ] Performance testing

## Completed ✅

- [x] Enhanced `config.py` with validation
- [x] Updated `his.service` configuration
- [x] Generated secure SECRET_KEY
- [x] Service running and healthy
- [x] Created documentation files
- [x] Configuration validation implemented

## Notes

- Service is currently running on port 8000
- All critical environment variables are set
- Configuration validation is active
- Log directory auto-creation is implemented
- Next focus should be on testing functionality
