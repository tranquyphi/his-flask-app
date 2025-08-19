"""
FastAPI main application for HIS - Migration from Flask
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

# Import FastAPI routers from the new FastApi directory
from FastApi.body_parts_fastapi import router as body_parts_router
from FastApi.frontend_routes import router as frontend_router
from FastApi.staff_fastapi import router as staff_router
from FastApi.departments_fastapi import router as departments_router
from FastApi.patients_with_department_fastapi import router as patients_with_department_router
from FastApi.signs_fastapi import router as signs_router
from FastApi.body_sites_fastapi import router as body_sites_router
from FastApi.drugs_fastapi import router as drugs_router
from FastApi.drug_groups_fastapi import router as drug_groups_router
from FastApi.procedures_fastapi import router as procedures_router
from FastApi.tests_fastapi import router as tests_router
from FastApi.patients_fastapi import router as patients_router
from FastApi.patient_visits_fastapi import router as patient_visits_router
from FastApi.visits_fastapi import router as visits_router
# from FastApi.patient_documents_fastapi import router as patient_documents_router  # Disabled - using Flask version
from FastApi.document_types_fastapi import router as document_types_router
from FastApi.patient_images_fastapi import router as patient_images_router
from FastApi.drug_template_fastapi import router as drug_template_router
from FastApi.drug_template_detail_fastapi import router as drug_template_detail_router
from FastApi.department_patients_fastapi import router as department_patients_router
from FastApi.user_images_fastapi import router as user_images_router

# Create FastAPI app
app = FastAPI(
    title="Hospital Information System - FastAPI",
    description="HIS API migrated from Flask to FastAPI",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (equivalent to Flask's static folder)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers (equivalent to Flask blueprints)
app.include_router(body_parts_router)
app.include_router(staff_router)
app.include_router(departments_router)
app.include_router(patients_with_department_router)
app.include_router(signs_router)
app.include_router(body_sites_router)
app.include_router(drugs_router)
app.include_router(drug_groups_router)
app.include_router(procedures_router)
app.include_router(tests_router)
app.include_router(patients_router)
app.include_router(patient_visits_router)
app.include_router(visits_router)
# app.include_router(patient_documents_router)  # Disabled - using Flask version
app.include_router(document_types_router)
app.include_router(patient_images_router)
app.include_router(drug_template_router)
app.include_router(drug_template_detail_router)
app.include_router(department_patients_router)
app.include_router(user_images_router)
app.include_router(frontend_router)

# Root endpoint - now served by frontend_router
# This will be overridden by the HTML route

# For direct execution
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

# To run the application with uvicorn:
# uvicorn his_fastapi:app --reload --port 8001
