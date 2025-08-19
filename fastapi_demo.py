"""
FastAPI demonstration with a simplified BodyPart model
"""
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import uvicorn
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

# Database configuration
DB_CONNECTION_STRING = os.environ.get('DB_CONNECTION_STRING', 'mysql+pymysql://bvthanghoa:57PhanKeBinh@localhost/examdb')
engine = create_engine(DB_CONNECTION_STRING)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Simple BodyPart model
class BodyPart(Base):
    __tablename__ = "BodyPart"
    BodyPartId = Column(Integer, primary_key=True)
    BodyPartName = Column(String(50))

# Pydantic models
class BodyPartBase(BaseModel):
    BodyPartName: str

class BodyPartCreate(BodyPartBase):
    pass

class BodyPartResponse(BodyPartBase):
    BodyPartId: int
    
    class Config:
        orm_mode = True

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI app
app = FastAPI(
    title="HIS FastAPI Demo",
    description="Simplified FastAPI Demo for HIS",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to HIS FastAPI Demo"}

@app.get("/api/body_parts", response_model=List[BodyPartResponse])
def get_body_parts(db: Session = Depends(get_db)):
    body_parts = db.query(BodyPart).all()
    return body_parts

@app.get("/api/body_parts/{part_id}", response_model=BodyPartResponse)
def get_body_part(part_id: int, db: Session = Depends(get_db)):
    body_part = db.query(BodyPart).filter(BodyPart.BodyPartId == part_id).first()
    if body_part is None:
        raise HTTPException(status_code=404, detail="Body part not found")
    return body_part

@app.post("/api/body_parts", response_model=BodyPartResponse, status_code=201)
def create_body_part(body_part: BodyPartCreate, db: Session = Depends(get_db)):
    db_body_part = BodyPart(BodyPartName=body_part.BodyPartName)
    db.add(db_body_part)
    db.commit()
    db.refresh(db_body_part)
    return db_body_part

@app.put("/api/body_parts/{part_id}", response_model=BodyPartResponse)
def update_body_part(part_id: int, body_part: BodyPartCreate, db: Session = Depends(get_db)):
    db_body_part = db.query(BodyPart).filter(BodyPart.BodyPartId == part_id).first()
    if db_body_part is None:
        raise HTTPException(status_code=404, detail="Body part not found")
    
    db_body_part.BodyPartName = body_part.BodyPartName
    db.commit()
    db.refresh(db_body_part)
    return db_body_part

@app.delete("/api/body_parts/{part_id}")
def delete_body_part(part_id: int, db: Session = Depends(get_db)):
    db_body_part = db.query(BodyPart).filter(BodyPart.BodyPartId == part_id).first()
    if db_body_part is None:
        raise HTTPException(status_code=404, detail="Body part not found")
    
    db.delete(db_body_part)
    db.commit()
    return {"message": "Body part deleted successfully"}

# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
