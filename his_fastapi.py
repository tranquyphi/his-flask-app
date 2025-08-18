"""
FastAPI main application for HIS
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import API routers
from api.body_parts_fastapi import router as body_parts_router

# Create FastAPI app
app = FastAPI(
    title="Hospital Information System",
    description="API for Hospital Information System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(body_parts_router)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to Hospital Information System API"}

# For direct execution
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

# To run the application with uvicorn:
# uvicorn his_fastapi:app --reload --port 8001
