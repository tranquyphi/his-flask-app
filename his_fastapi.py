"""
FastAPI main application for HIS - Migration from Flask
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import FastAPI routers from the new FastApi directory
from FastApi.body_parts import router as body_parts_router
# TODO: Import other routers as they are converted:
# from FastApi.departments import router as departments_router
# from FastApi.patients import router as patients_router
# etc.

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

# Include routers (equivalent to Flask blueprints)
app.include_router(body_parts_router)

# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to Hospital Information System API v2.0",
        "version": "2.0.0",
        "framework": "FastAPI", 
        "migration_status": "In Progress"
    }

# For direct execution
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

# To run the application with uvicorn:
# uvicorn his_fastapi:app --reload --port 8001
