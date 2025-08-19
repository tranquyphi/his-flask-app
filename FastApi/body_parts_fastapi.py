"""
Body Parts API endpoints using FastAPI
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from pydantic import BaseModel
import os

# Create a SQLAlchemy engine and session
# Use the same connection string as in your Flask app
DB_CONNECTION_STRING = os.environ.get('DB_CONNECTION_STRING', 'mysql+pymysql://bvthanghoa:57PhanKeBinh@localhost/examdb')
engine = create_engine(DB_CONNECTION_STRING)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import the model from the new modular structure
from models.BodyPart import BodyPart

# Define Pydantic models for request/response validation
class BodyPartBase(BaseModel):
    BodyPartName: str

class BodyPartCreate(BodyPartBase):
    pass

class BodyPartUpdate(BodyPartBase):
    pass

class BodyPartResponse(BodyPartBase):
    BodyPartId: int
    
    class Config:
        from_attributes = True  # Using the new attribute name instead of orm_mode

# Function to get database session
def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

# Create router
router = APIRouter(tags=["Body Parts"])

# GET all body parts
@router.get("/api/body_parts", response_model=List[BodyPartResponse])
def get_all_body_parts(db: Session = Depends(get_db)):
    parts = db.query(BodyPart).all()
    return parts

# GET a specific body part
@router.get("/api/body_parts/{part_id}", response_model=BodyPartResponse)
def get_body_part(part_id: int, db: Session = Depends(get_db)):
    part = db.query(BodyPart).filter(BodyPart.BodyPartId == part_id).first()
    if part is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Body part with ID {part_id} not found"
        )
    return part

# CREATE a new body part
@router.post("/api/body_parts", response_model=BodyPartResponse, status_code=status.HTTP_201_CREATED)
def create_body_part(body_part: BodyPartCreate, db: Session = Depends(get_db)):
    new_part = BodyPart(BodyPartName=body_part.BodyPartName)
    db.add(new_part)
    db.commit()
    db.refresh(new_part)
    return new_part

# UPDATE a body part
@router.put("/api/body_parts/{part_id}", status_code=status.HTTP_200_OK)
def update_body_part(part_id: int, body_part: BodyPartUpdate, db: Session = Depends(get_db)):
    db_part = db.query(BodyPart).filter(BodyPart.BodyPartId == part_id).first()
    if db_part is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Body part with ID {part_id} not found"
        )
    
    # Update model attributes
    db_part.BodyPartName = body_part.BodyPartName
    
    db.commit()
    db.refresh(db_part)
    return {"message": "Updated"}

# DELETE a body part
@router.delete("/api/body_parts/{part_id}", status_code=status.HTTP_200_OK)
def delete_body_part(part_id: int, db: Session = Depends(get_db)):
    db_part = db.query(BodyPart).filter(BodyPart.BodyPartId == part_id).first()
    if db_part is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Body part with ID {part_id} not found"
        )
    
    db.delete(db_part)
    db.commit()
    return {"message": "Deleted"}
