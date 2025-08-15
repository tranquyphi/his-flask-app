from flask import Blueprint, jsonify, send_file, Response, request
from models import db, User
import base64
import io
import os

# Create Blueprint for user profile images API routes
user_images_bp = Blueprint('user_images', __name__)

@user_images_bp.route('/user/image/<user_id>', methods=['GET'])
def get_user_image(user_id):
    """Get user profile image as binary data or base64 encoded string"""
    try:
        # Query the user image
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        if not user.ProfileImage:
            return jsonify({'error': 'No image available for this user'}), 404
        
        # Check if base64 format is requested
        format_type = request.args.get('format', 'binary')
        
        if format_type == 'base64':
            # Return base64 encoded image
            encoded_image = base64.b64encode(user.ProfileImage).decode('utf-8')
            return jsonify({
                'user_id': user_id,
                'image': encoded_image
            })
        else:
            # Return binary image
            return send_file(
                io.BytesIO(user.ProfileImage),
                mimetype='image/jpeg',  # Assuming images are stored as JPEG
                as_attachment=False,
                download_name=f'user_{user_id}.jpg'
            )
            
    except Exception as e:
        print(f"Error in get_user_image: {e}")
        return jsonify({'error': f'Image retrieval error: {str(e)}'}), 500

@user_images_bp.route('/user/image/<user_id>', methods=['POST'])
def upload_user_image(user_id):
    """Upload a new user profile image"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Check if image data is in the request
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
            
        image_file = request.files['image']
        
        if image_file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
            
        # Read image data and save to database
        image_data = image_file.read()
        user.ProfileImage = image_data
        
        # Commit the changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Profile image for user {user_id} has been updated'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in upload_user_image: {e}")
        return jsonify({'error': f'Image upload error: {str(e)}'}), 500

@user_images_bp.route('/user/image/<user_id>', methods=['DELETE'])
def delete_user_image(user_id):
    """Delete a user's profile image"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Set image to None
        user.ProfileImage = None
        
        # Commit the changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Profile image for user {user_id} has been deleted'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_user_image: {e}")
        return jsonify({'error': f'Image deletion error: {str(e)}'}), 500
