from flask import Blueprint, jsonify, send_file, Response, request
from models import db, Patient
import base64
import io
from PIL import Image
import tempfile

# Create Blueprint for patient images API routes
patient_images_bp = Blueprint('patient_images', __name__)

@patient_images_bp.route('/patient/image/<patient_id>', methods=['GET'])
def get_patient_image(patient_id):
    """Get patient image as binary data or base64 encoded string"""
    try:
        # Query the patient image
        patient = Patient.query.get(patient_id)
        
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
            
        if not patient.PatientImage:
            return jsonify({'error': 'No image available for this patient'}), 404
        
        # Check if base64 format is requested
        format_type = request.args.get('format', 'binary')
        
        if format_type == 'base64':
            # Return base64 encoded image
            encoded_image = base64.b64encode(patient.PatientImage).decode('utf-8')
            return jsonify({
                'patient_id': patient_id,
                'image': encoded_image
            })
        else:
            # Return binary image
            return send_file(
                io.BytesIO(patient.PatientImage),
                mimetype='image/jpeg',  # Assuming images are stored as JPEG
                as_attachment=False,
                download_name=f'patient_{patient_id}.jpg'
            )
            
    except Exception as e:
        print(f"Error in get_patient_image: {e}")
        return jsonify({'error': f'Image retrieval error: {str(e)}'}), 500

@patient_images_bp.route('/patient/image/<patient_id>', methods=['POST'])
def upload_patient_image(patient_id):
    """Upload a new patient image"""
    try:
        patient = Patient.query.get(patient_id)
        
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
            
        # Check if image data is in the request
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
            
        image_file = request.files['image']
        
        if image_file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        # Check file size (limit to 5MB)
        # Read image data first to get accurate size
        image_data = image_file.read()
        size_mb = len(image_data) / (1024 * 1024)
        
        if size_mb > 5:
            return jsonify({'error': f'Image too large ({size_mb:.1f}MB). Maximum size is 5MB'}), 413
        
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
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Image for patient {patient_id} has been updated',
            'size': f'{size_mb:.2f}MB'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in upload_patient_image: {e}")
        return jsonify({'error': f'Image upload error: {str(e)}'}), 500

@patient_images_bp.route('/patient/image/<patient_id>', methods=['DELETE'])
def delete_patient_image(patient_id):
    """Delete a patient's image"""
    try:
        patient = Patient.query.get(patient_id)
        
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
            
        # Set image to None
        patient.PatientImage = None
        
        # Commit the changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Image for patient {patient_id} has been deleted'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_patient_image: {e}")
        return jsonify({'error': f'Image deletion error: {str(e)}'}), 500
