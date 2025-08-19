"""
Body Parts API endpoints using FastAPI - Converted from Flask
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from pydantic import BaseModel
import os

# Create a SQLAlchemy engine and session
DB_CONNECTION_STRING = os.environ.get('DB_CONNECTION_STRING', 'mysql+pymysql://bvthanghoa:57PhanKeBinh@localhost/examdb')
engine = create_engine(DB_CONNECTION_STRING)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import the model from the new modular structure
from models.BodyPart import BodyPart

# Define Pydantic models for request/response validation
class BodyPartBase(BaseModel):
    BodyPartName: str

class BodyPartCreate(BodyPartBase):
    BodyPartId: Optional[int] = None

class BodyPartUpdate(BodyPartBase):
    pass

class BodyPartResponse(BodyPartBase):
    BodyPartId: int
    
    class Config:
        orm_mode = True  # For Pydantic v1.x

# Function to get database session
def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

# Create router (equivalent to Flask Blueprint)
router = APIRouter(prefix="/api", tags=["Body Parts"])

@router.get("/body_parts", response_model=List[BodyPartResponse])
def get_all_body_parts(db: Session = Depends(get_db)):
    """Get all body parts - Converted from Flask route"""
    parts = db.query(BodyPart).all()
    return parts

@router.get("/body_parts/{part_id}", response_model=BodyPartResponse)
def get_body_part(part_id: int, db: Session = Depends(get_db)):
    """Get specific body part by ID - Converted from Flask route"""
    part = db.query(BodyPart).filter(BodyPart.BodyPartId == part_id).first()
    if part is None:
        raise HTTPException(status_code=404, detail="Body part not found")
    return part

@router.post("/body_parts", response_model=BodyPartResponse, status_code=201)
def create_body_part(body_part: BodyPartCreate, db: Session = Depends(get_db)):
    """Create new body part - Converted from Flask route"""
    db_body_part = BodyPart(
        BodyPartId=body_part.BodyPartId,
        BodyPartName=body_part.BodyPartName
    )
    db.add(db_body_part)
    db.commit()
    db.refresh(db_body_part)
    return db_body_part

@body_parts_bp.route('/api/body_parts/<int:part_id>', methods=['PUT'])
def update_body_part(part_id):
    data = request.json
    part = BodyPart.query.get_or_404(part_id)
    if 'BodyPartName' in data:
        part.BodyPartName = data['BodyPartName']
    db.session.commit()
    return jsonify({"message": "Updated"})

@body_parts_bp.route('/api/body_parts/<int:part_id>', methods=['DELETE'])
def delete_body_part(part_id):
    part = BodyPart.query.get_or_404(part_id)
    db.session.delete(part)
    db.session.commit()
    return jsonify({"message": "Deleted"})
