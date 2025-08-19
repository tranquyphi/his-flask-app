"""
User Images FastAPI router
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from models_main import get_db
from models import Staff
import base64
import io
from PIL import Image

router = APIRouter(prefix="/api", tags=["user_images"])

@router.get("/user/image/{user_id}")
async def get_user_image(user_id: int, db: Session = Depends(get_db)):
    """Get user profile image"""
    try:
        # For now, assume user_id corresponds to staff
        staff = db.query(Staff).filter(Staff.StaffId == user_id).first()
        
        if not staff:
            raise HTTPException(status_code=404, detail="User not found")
            
        # If no image stored, return placeholder or error
        if not hasattr(staff, 'StaffImage') or not staff.StaffImage:
            raise HTTPException(status_code=404, detail="No image available for this user")
        
        # Return the image as a streaming response
        return StreamingResponse(
            io.BytesIO(staff.StaffImage),
            media_type="image/jpeg"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image retrieval error: {str(e)}")

@router.post("/user/image/{user_id}", response_model=dict)
async def upload_user_image(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload user profile image"""
    try:
        # For now, assume user_id corresponds to staff
        staff = db.query(Staff).filter(Staff.StaffId == user_id).first()
        
        if not staff:
            raise HTTPException(status_code=404, detail="User not found")
            
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read the file content
        file_content = await file.read()
        
        # For now, just return success without actually storing
        # since Staff model might not have StaffImage field
        return {
            "message": "User image upload functionality not yet implemented",
            "user_id": user_id,
            "filename": file.filename,
            "size": len(file_content)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

@router.delete("/user/image/{user_id}", response_model=dict)
async def delete_user_image(user_id: int, db: Session = Depends(get_db)):
    """Delete user profile image"""
    try:
        # For now, assume user_id corresponds to staff
        staff = db.query(Staff).filter(Staff.StaffId == user_id).first()
        
        if not staff:
            raise HTTPException(status_code=404, detail="User not found")
        
        # For now, just return success without actually deleting
        return {
            "message": "User image deletion functionality not yet implemented",
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion error: {str(e)}")
