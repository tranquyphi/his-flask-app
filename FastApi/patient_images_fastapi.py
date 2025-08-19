"""
Patient Images API endpoints - FastAPI version
CRUD operations for managing patient images with blob data
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
import base64
import io
from PIL import Image

# Import database models and session
from models_main import get_db
from models.Patient import Patient

# Create router with /api prefix
router = APIRouter(prefix="/api", tags=["Patient Images"])

# Pydantic models
class ImageResponse(BaseModel):
    patient_id: str
    image: str  # base64 encoded
    size_mb: Optional[float] = None

class ImageUploadResponse(BaseModel):
    success: bool
    message: str
    size: str

@router.get("/patient/image/{patient_id}")
async def get_patient_image(
    patient_id: str, 
    format_type: str = Query("binary", alias="format"),
    db: Session = Depends(get_db)
):
    """Get patient image as binary data or base64 encoded string"""
    try:
        # Query the patient image
        patient = db.query(Patient).get(patient_id)
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
            
        if not patient.PatientImage:
            raise HTTPException(status_code=404, detail="No image available for this patient")
        
        # Check if base64 format is requested
        if format_type == 'base64':
            # Return base64 encoded image
            encoded_image = base64.b64encode(patient.PatientImage).decode('utf-8')
            size_mb = len(patient.PatientImage) / (1024 * 1024)
            return {
                'patient_id': patient_id,
                'image': encoded_image,
                'size_mb': round(size_mb, 2)
            }
        else:
            # Return binary image as streaming response
            return StreamingResponse(
                io.BytesIO(patient.PatientImage),
                media_type="image/jpeg",
                headers={"Content-Disposition": f"inline; filename=patient_{patient_id}.jpg"}
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image retrieval error: {str(e)}")

@router.post("/patient/image/{patient_id}", response_model=dict)
async def upload_patient_image(
    patient_id: str, 
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a new patient image"""
    try:
        patient = db.query(Patient).get(patient_id)
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
            
        if not image.filename:
            raise HTTPException(status_code=400, detail="No image selected")
        
        # Read image data
        image_data = await image.read()
        size_mb = len(image_data) / (1024 * 1024)
        
        # Check file size (limit to 5MB)
        if size_mb > 5:
            raise HTTPException(
                status_code=413, 
                detail=f"Image too large ({size_mb:.1f}MB). Maximum size is 5MB"
            )
        
        # Always optimize images to ensure consistency
        try:
            print(f"Processing image for patient {patient_id}, original size: {size_mb:.2f}MB")
            
            # Create an image object from bytes
            img = Image.open(io.BytesIO(image_data))
            
            # Get original dimensions
            original_width, original_height = img.size
            print(f"Original image dimensions: {original_width}x{original_height}")
            
            # Determine if we need to resize based on dimensions and file size
            max_size = (800, 800)  # Reduced max dimensions for better performance
            resize_needed = (original_width > max_size[0] or original_height > max_size[1])
            
            # More aggressive optimization for larger files
            quality = 80  # Default quality
            if size_mb > 1.5:
                quality = 70  # More compression for very large files
            elif size_mb > 0.8:
                quality = 75  # Medium compression for large files
                
            # Apply resizing if needed
            if resize_needed:
                print(f"Resizing image from {original_width}x{original_height} to fit within {max_size}")
                img.thumbnail(max_size, Image.LANCZOS)
                print(f"New dimensions after resize: {img.width}x{img.height}")
            
            # Standardize format to JPEG for consistent handling
            output_format = 'JPEG'
            if img.mode == 'RGBA':
                # Convert transparent images to RGB with white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Create a BytesIO object for the optimized image
            optimized_buffer = io.BytesIO()
            
            # Save with optimization
            print(f"Saving with quality={quality}, format={output_format}")
            img.save(optimized_buffer, format=output_format, optimize=True, quality=quality)
            optimized_buffer.seek(0)
            optimized_data = optimized_buffer.getvalue()
            
            # Use the optimized data if it's actually smaller
            new_size_mb = len(optimized_data) / (1024 * 1024)
            if len(optimized_data) < len(image_data):
                image_data = optimized_data
                print(f"Optimized image for patient {patient_id}, new size: {new_size_mb:.2f}MB (saved {size_mb - new_size_mb:.2f}MB)")
            else:
                print(f"Optimization did not reduce size ({new_size_mb:.2f}MB vs {size_mb:.2f}MB), using original")
                
        except Exception as e:
            print(f"Error optimizing image: {e}. Using original.")
        
        # Save image data to database
        patient.PatientImage = image_data
        
        # Commit the changes
        db.commit()
        
        final_size_mb = len(image_data) / (1024 * 1024)
        
        return {
            'success': True,
            'message': f'Image for patient {patient_id} has been updated',
            'size': f'{final_size_mb:.2f}MB'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Image upload error: {str(e)}")

@router.delete("/patient/image/{patient_id}", response_model=dict)
async def delete_patient_image(patient_id: str, db: Session = Depends(get_db)):
    """Delete a patient's image"""
    try:
        patient = db.query(Patient).get(patient_id)
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
            
        # Set image to None
        patient.PatientImage = None
        
        # Commit the changes
        db.commit()
        
        return {
            'success': True,
            'message': f'Image for patient {patient_id} has been deleted'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Image deletion error: {str(e)}")
