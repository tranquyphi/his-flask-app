from flask import Blueprint, jsonify, send_file, Response, request
from models import db, Patient
import base64
import io

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
            
        # Read image data and save to database
        image_data = image_file.read()
        patient.PatientImage = image_data
        
        # Commit the changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Image for patient {patient_id} has been updated'
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
