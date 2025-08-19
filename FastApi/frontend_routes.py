"""
Frontend/UI routes for FastAPI - Converted from Flask
Serves HTML templates and static content
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import time

# Create router for UI routes
router = APIRouter(tags=["Frontend/UI"])

# Setup Jinja2 templates
templates = Jinja2Templates(directory="frontend")

# Add Flask-compatible template functions
def url_for(endpoint, **values):
    """
    Flask-compatible url_for function for FastAPI templates
    For static files, return the static URL path
    """
    if endpoint == 'static':
        filename = values.get('filename', '')
        return f"/static/{filename}"
    # For other endpoints, you might need to extend this
    return f"/{endpoint}"

def static_version_filter(filename):
    """
    Flask-compatible static_version filter for cache busting
    Returns current timestamp for cache busting
    """
    return str(int(time.time()))

# Mock config object for templates
class Config:
    STATIC_VERSION = str(int(time.time()))

config = Config()

# Add template globals and filters
templates.env.globals['url_for'] = url_for
templates.env.globals['config'] = config
templates.env.filters['static_version'] = static_version_filter

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Main index page with links to all available pages
    Converted from Flask route: @app.route('/')
    """
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/departments", response_class=HTMLResponse) 
async def departments_page(request: Request):
    """
    Departments page - Currently empty template
    Converted from Flask route: @app.route('/departments')
    """
    # Note: departments.html is currently empty, needs to be created
    try:
        return templates.TemplateResponse("departments.html", {"request": request})
    except:
        # Fallback if template doesn't exist or is empty
        return HTMLResponse("""
        <!DOCTYPE html>
        <html><head><title>Departments - Under Development</title></head>
        <body><h1>Departments Module</h1><p>Under development. <a href="/">Return to Home</a></p></body>
        </html>
        """)

@router.get("/patients-with-departments", response_class=HTMLResponse)
async def patients_with_departments_page(request: Request):
    """
    Patients with departments page - Has content
    Converted from Flask route: @app.route('/patients-with-departments')
    """
    return templates.TemplateResponse("patients_with_departments.html", {"request": request})

@router.get("/staff", response_class=HTMLResponse)
async def staff_page(request: Request):
    """
    Staff management page - Has content (21K file)
    """
    return templates.TemplateResponse("staff.html", {"request": request})

@router.get("/patient-documents", response_class=HTMLResponse)
async def patient_documents_page(request: Request):
    """
    Patient documents page - Has content (18K file)
    """
    return templates.TemplateResponse("patient_documents.html", {"request": request})

@router.get("/signs", response_class=HTMLResponse)
async def signs_page(request: Request):
    """
    Signs management page - Has content (4.7K file)
    """
    return templates.TemplateResponse("signs.html", {"request": request})

@router.get("/sign-templates", response_class=HTMLResponse)
async def sign_templates_page(request: Request):
    """
    Sign templates page - Has content (4.0K file)
    """
    return templates.TemplateResponse("sign_templates.html", {"request": request})

@router.get("/body-sites", response_class=HTMLResponse)
async def body_sites_page(request: Request):
    """
    Body sites page - Has content (12K file)
    """
    return templates.TemplateResponse("body_sites.html", {"request": request})

@router.get("/drugs", response_class=HTMLResponse)
async def drugs_page(request: Request):
    """
    Drugs management page - Has content (11K file)
    """
    return templates.TemplateResponse("drugs.html", {"request": request})

@router.get("/drug-templates", response_class=HTMLResponse)
async def drug_templates_page(request: Request):
    """
    Drug templates page - Has content (3.9K file)
    """
    return templates.TemplateResponse("drug_templates.html", {"request": request})

@router.get("/drug-groups", response_class=HTMLResponse)
async def drug_groups_page(request: Request):
    """
    Drug groups page - Has content (6.9K file)
    """
    return templates.TemplateResponse("drug_groups.html", {"request": request})

@router.get("/tests", response_class=HTMLResponse)
async def tests_page(request: Request):
    """
    Tests management page - Currently empty template
    """
    try:
        return templates.TemplateResponse("tests.html", {"request": request})
    except:
        return HTMLResponse("""
        <!DOCTYPE html>
        <html><head><title>Tests - Under Development</title></head>
        <body><h1>Tests Module</h1><p>Under development. <a href="/">Return to Home</a></p></body>
        </html>
        """)

@router.get("/procedures", response_class=HTMLResponse)
async def procedures_page(request: Request):
    """
    Procedures management page - Currently empty template
    """
    try:
        return templates.TemplateResponse("procedures.html", {"request": request})
    except:
        return HTMLResponse("""
        <!DOCTYPE html>
        <html><head><title>Procedures - Under Development</title></head>
        <body><h1>Procedures Module</h1><p>Under development. <a href="/">Return to Home</a></p></body>
        </html>
        """)

@router.get("/excel-upload", response_class=HTMLResponse)
async def excel_upload_page(request: Request):
    """
    Excel upload page - Has content (20K file)
    """
    return templates.TemplateResponse("excel_upload.html", {"request": request})

@router.get("/api", response_class=HTMLResponse)
async def api_docs_redirect(request: Request):
    """
    API documentation redirect - Redirect to FastAPI auto-docs
    """
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")

@router.get("/department_patients/{department_id}", response_class=HTMLResponse)
async def department_patients_specific(department_id: int, request: Request):
    """
    Direct access to a specific department's patients
    """
    return templates.TemplateResponse(
        "department_patients_specific.html", 
        {"request": request, "department_id": department_id}
    )
