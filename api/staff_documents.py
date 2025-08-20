"""
Staff Documents API Blueprint
CRUD operations for managing staff documents
"""
from flask import Blueprint, request, jsonify, current_app, send_file
from models import db
from models import StaffDocuments, Staff, DocumentType
import os
import json
import uuid
import datetime
import mimetypes
from werkzeug.utils import secure_filename
import io
from PIL import Image, ImageFile
import pdf2image
import subprocess
import logging

# Enable loading of truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

staff_documents_bp = Blueprint('staff_documents', __name__)

# Path to store staff document files
STAFF_DOCUMENTS_PATH = '/static/staff_documents'

def get_full_staff_documents_path():
    """Get the absolute path to the staff documents directory"""
    # Use the application root path + the staff documents path
    return os.path.join(current_app.root_path, STAFF_DOCUMENTS_PATH.lstrip('/'))

def ensure_staff_documents_dir():
    """Ensure the staff documents directory exists"""
    docs_path = get_full_staff_documents_path()
    if not os.path.exists(docs_path):
        os.makedirs(docs_path, exist_ok=True)
    
    # Also ensure thumbnails directory exists
    thumbs_path = os.path.join(docs_path, 'thumbnails')
    if not os.path.exists(thumbs_path):
        os.makedirs(thumbs_path, exist_ok=True)
    
    return docs_path

def generate_thumbnail(file_path, file_type, original_filename):
    """Generate thumbnail for supported file types"""
    docs_path = get_full_staff_documents_path()
    thumbs_path = os.path.join(docs_path, 'thumbnails')
    
    # Ensure thumbnails directory exists
    if not os.path.exists(thumbs_path):
        os.makedirs(thumbs_path, exist_ok=True)
    
    # Generate thumbnail filename
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    thumb_filename = f"{base_name}_thumb.jpg"
    thumb_path = os.path.join(thumbs_path, thumb_filename)
    
    try:
        if file_type and file_type.startswith('image/'):
            try:
                # Generate thumbnail for images
                with Image.open(file_path) as img:
                    # Convert to RGB if necessary (for PNG with transparency, etc.)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    
                    # Create thumbnail maintaining aspect ratio
                    img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                    img.save(thumb_path, 'JPEG', quality=85, optimize=True)
                    
                    return f"thumbnails/{thumb_filename}"
            except Exception as img_error:
                current_app.logger.error(f"Error processing image: {img_error}")
                return None
                
        elif file_type and 'pdf' in file_type.lower():
            # Generate thumbnail for PDF (first page)
            try:
                # Convert first page of PDF to image
                pages = pdf2image.convert_from_path(file_path, first_page=1, last_page=1, dpi=150)
                if pages:
                    img = pages[0]
                    # Convert to RGB if necessary
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    
                    # Create thumbnail
                    img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                    img.save(thumb_path, 'JPEG', quality=85, optimize=True)
                    
                    return f"thumbnails/{thumb_filename}"
            except Exception as pdf_error:
                print(f"Error generating PDF thumbnail: {pdf_error}")
                
        elif file_type and any(office_type in file_type.lower() for office_type in ['word', 'excel', 'powerpoint', 'document', 'sheet', 'presentation']):
            # For Office documents, we can try to generate a generic thumbnail
            # or use LibreOffice headless mode if available
            try:
                # Try using LibreOffice to convert first page to image
                temp_pdf = os.path.join(thumbs_path, f"{base_name}_temp.pdf")
                result = subprocess.run([
                    'libreoffice', '--headless', '--convert-to', 'pdf', 
                    '--outdir', thumbs_path, file_path
                ], capture_output=True, timeout=30)
                
                if result.returncode == 0 and os.path.exists(temp_pdf):
                    # Convert the PDF to image
                    pages = pdf2image.convert_from_path(temp_pdf, first_page=1, last_page=1, dpi=150)
                    if pages:
                        img = pages[0]
                        if img.mode in ('RGBA', 'LA', 'P'):
                            img = img.convert('RGB')
                        img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                        img.save(thumb_path, 'JPEG', quality=85, optimize=True)
                        
                        # Clean up temp PDF
                        os.remove(temp_pdf)
                        
                        return f"thumbnails/{thumb_filename}"
                        
            except Exception as office_error:
                print(f"Error generating Office document thumbnail: {office_error}")
        
        # Return None if thumbnail generation is not supported or failed
        return None
        
    except Exception as e:
        current_app.logger.error(f"Error generating thumbnail for {original_filename}: {e}")
        return None

def generate_unique_filename(original_filename):
    """Generate a unique filename to avoid conflicts"""
    # Get file extension
    _, ext = os.path.splitext(original_filename)
    # Generate a unique filename with timestamp and UUID
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}{ext}"

@staff_documents_bp.route('/staff_documents', methods=['GET'])
def list_staff_documents():
    """List all staff documents with optional filter by staff ID"""
    try:
        # Get query parameters
        staff_id = request.args.get('staff_id')
        document_type_id = request.args.get('document_type_id')
        
        # Start with base query
        query = db.session.query(
            StaffDocuments, 
            Staff.StaffName, 
            Staff.StaffRole,
            StaffDocumentType.DocumentTypeName
        ).join(
            Staff, StaffDocuments.StaffId == Staff.StaffId
        ).outerjoin(
            StaffDocumentType, StaffDocuments.DocumentTypeId == StaffDocumentType.DocumentTypeId
        )
        
        # Apply filters if provided
        if staff_id:
            query = query.filter(StaffDocuments.StaffId == staff_id)
        if document_type_id:
            query = query.filter(StaffDocuments.DocumentTypeId == document_type_id)
        
        # Execute query
        results = query.all()
        
        # Format response
        documents = []
        for doc, staff_name, staff_role, doc_type_name in results:
            doc_dict = doc.to_dict()
            doc_dict['StaffName'] = staff_name
            doc_dict['StaffRole'] = staff_role
            doc_dict['DocumentTypeName'] = doc_type_name
            documents.append(doc_dict)
            
        return jsonify({'staff_documents': documents})
    except Exception as e:
        print(f"Error listing staff documents: {e}")
        return jsonify({'error': str(e)}), 500

@staff_documents_bp.route('/staff_documents/<int:document_id>/thumbnail', methods=['GET'])
def get_staff_document_thumbnail(document_id):
    """Get thumbnail for a staff document"""
    try:
        # Find the document
        document = StaffDocuments.query.get(document_id)
        if not document:
            return jsonify({'error': 'Staff document not found'}), 404
        
        # Check if thumbnail exists
        if not document.document_links or 'thumbnail_path' not in document.document_links:
            # Try to generate thumbnail on-the-fly if original file exists
            if 'file_path' in document.document_links:
                file_path = os.path.join(get_full_staff_documents_path(), document.document_links['file_path'])
                if os.path.exists(file_path):
                    thumbnail_path = generate_thumbnail(file_path, document.file_type, document.original_filename)
                    if thumbnail_path:
                        try:
                            # Update document with thumbnail info
                            updated_links = dict(document.document_links) if document.document_links else {}
                            updated_links['thumbnail_path'] = thumbnail_path
                            updated_links['thumbnail_url'] = f"{STAFF_DOCUMENTS_PATH}/{thumbnail_path}"
                            
                            document.document_links = updated_links
                            db.session.commit()
                        except Exception as db_error:
                            current_app.logger.error(f"Database update error: {db_error}")
                            db.session.rollback()
                            return jsonify({'error': str(db_error)}), 500
                    else:
                        return jsonify({'error': 'Thumbnail not available for this file type'}), 404
                else:
                    return jsonify({'error': 'Original file not found'}), 404
            else:
                return jsonify({'error': 'No thumbnail available'}), 404
        
        # Serve the thumbnail file
        thumbnail_path = os.path.join(get_full_staff_documents_path(), document.document_links['thumbnail_path'])
        if os.path.exists(thumbnail_path):
            return send_file(thumbnail_path, mimetype='image/jpeg')
        else:
            return jsonify({'error': 'Thumbnail file not found'}), 404
            
    except Exception as e:
        print(f"Error serving thumbnail: {e}")
        return jsonify({'error': str(e)}), 500

@staff_documents_bp.route('/staff_documents/<int:document_id>', methods=['GET'])
def get_staff_document(document_id):
    """Get a specific staff document by ID"""
    try:
        # Query the document with staff and document type info
        result = db.session.query(
            StaffDocuments, 
            Staff.StaffName, 
            Staff.StaffRole,
            StaffDocumentType.DocumentTypeName
        ).join(
            Staff, StaffDocuments.StaffId == Staff.StaffId
        ).outerjoin(
            StaffDocumentType, StaffDocuments.DocumentTypeId == StaffDocumentType.DocumentTypeId
        ).filter(
            StaffDocuments.DocumentId == document_id
        ).first()
        
        if not result:
            return jsonify({'error': 'Staff document not found'}), 404
            
        doc, staff_name, staff_role, doc_type_name = result
        doc_dict = doc.to_dict()
        doc_dict['StaffName'] = staff_name
        doc_dict['StaffRole'] = staff_role
        doc_dict['DocumentTypeName'] = doc_type_name
        
        # Check if file should be returned
        download = request.args.get('download', 'false').lower() == 'true'
        
        if download:
            # Get document path from document_links
            if doc.document_links and 'file_path' in doc.document_links:
                file_path = os.path.join(get_full_staff_documents_path(), doc.document_links['file_path'])
                
                if os.path.exists(file_path):
                    return send_file(
                        file_path,
                        as_attachment=True,
                        download_name=doc.original_filename or os.path.basename(file_path),
                        mimetype=doc.file_type or 'application/octet-stream'
                    )
                else:
                    return jsonify({'error': 'Document file not found on server'}), 404
            else:
                return jsonify({'error': 'Document has no associated file'}), 404
                
        return jsonify({'staff_document': doc_dict})
    except Exception as e:
        print(f"Error getting staff document: {e}")
        return jsonify({'error': str(e)}), 500

@staff_documents_bp.route('/staff_documents', methods=['POST'])
def upload_staff_document():
    """Upload a new staff document"""
    try:
        # Check if we have a file in the request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        
        # Validate file
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        # Validate file type
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', 
                            '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf', '.csv', '.zip']
        file_ext = os.path.splitext(file.filename.lower())[1]
        
        if file_ext not in allowed_extensions:
            return jsonify({'error': f'Unsupported file type. Allowed extensions: {", ".join(allowed_extensions)}'}), 400
            
        # Validate file size (max 20MB) - check both content length and actual file size
        max_size = 20 * 1024 * 1024  # 20MB in bytes
        
        # Check request content length first (if available)
        if request.content_length and request.content_length > max_size:
            return jsonify({
                'error': f'File size ({request.content_length // (1024*1024)}MB) exceeds the limit of 20MB'
            }), 413  # 413 Payload Too Large
        
        # Read and validate actual file size
        file.seek(0, 2)  # Seek to end of file
        file_size_bytes = file.tell()
        file.seek(0)  # Reset file pointer to beginning
        
        if file_size_bytes > max_size:
            return jsonify({
                'error': f'File size ({file_size_bytes // (1024*1024)}MB) exceeds the limit of 20MB'
            }), 413
            
        # Get form data
        staff_id = request.form.get('staff_id')
        document_type_id = request.form.get('document_type_id')
        
        # Validate staff ID
        if not staff_id:
            return jsonify({'error': 'Staff ID is required'}), 400
            
        # Verify staff exists
        staff = Staff.query.get(staff_id)
        if not staff:
            return jsonify({'error': 'Staff not found'}), 404
            
        # Ensure document directory exists
        try:
            docs_path = ensure_staff_documents_dir()
        except Exception as e:
            return jsonify({'error': f'Failed to create documents directory: {str(e)}'}), 500
        
        # Generate a unique filename
        secure_name = secure_filename(file.filename)
        unique_filename = generate_unique_filename(secure_name)
        
        # Save the file
        file_path = os.path.join(docs_path, unique_filename)
        
        try:
            file.save(file_path)
        except Exception as e:
            return jsonify({'error': f'Failed to save file: {str(e)}'}), 500
        
        # Use the file size we already calculated
        file_size = file_size_bytes
        
        # Determine file type
        file_type = file.content_type or mimetypes.guess_type(file.filename)[0] or 'application/octet-stream'
        
        # Generate thumbnail if supported
        thumbnail_path = generate_thumbnail(file_path, file_type, file.filename)
        
        # Create document links JSON
        document_links = {
            'file_path': unique_filename,
            'url': f"{STAFF_DOCUMENTS_PATH}/{unique_filename}"
        }
        
        # Add thumbnail path if generated
        if thumbnail_path:
            document_links['thumbnail_path'] = thumbnail_path
            document_links['thumbnail_url'] = f"{STAFF_DOCUMENTS_PATH}/{thumbnail_path}"
        
        # Create metadata JSON
        metadata_value = {
            'upload_timestamp': datetime.datetime.now().isoformat(),
            'uploader': request.form.get('uploader', 'system'),
            'description': request.form.get('description', '')
        }
        
        # Create document record
        new_document = StaffDocuments(
            StaffId=staff_id,
            DocumentTypeId=document_type_id if document_type_id else None,
            document_links=document_links,
            document_metadata=metadata_value,
            original_filename=file.filename,
            file_type=file_type,
            FileSize=file_size
        )
        
        try:
            db.session.add(new_document)
            db.session.commit()
        except Exception as db_error:
            # If database save fails, clean up the uploaded file
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as cleanup_error:
                print(f"Failed to cleanup file after database error: {cleanup_error}")
            
            db.session.rollback()
            return jsonify({'error': f'Failed to save document record: {str(db_error)}'}), 500
        
        # Format response
        doc_dict = new_document.to_dict()
        doc_dict['StaffName'] = staff.StaffName
        doc_dict['StaffRole'] = staff.StaffRole
        
        if document_type_id:
            doc_type = StaffDocumentType.query.get(document_type_id)
            if doc_type:
                doc_dict['DocumentTypeName'] = doc_type.DocumentTypeName
        
        return jsonify({
            'message': 'Staff document uploaded successfully',
            'staff_document': doc_dict
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error uploading staff document: {e}")
        return jsonify({'error': str(e)}), 500

@staff_documents_bp.route('/staff_documents/<int:document_id>', methods=['PUT'])
def update_staff_document(document_id):
    """Update staff document metadata"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Find the document
        document = StaffDocuments.query.get(document_id)
        if not document:
            return jsonify({'error': 'Staff document not found'}), 404
            
        # Update fields that can be modified
        if 'DocumentTypeId' in data:
            document.DocumentTypeId = data['DocumentTypeId']
            
        if 'metadata' in data and isinstance(data['metadata'], dict):
            # Merge existing metadata with new metadata
            current_metadata = document.document_metadata or {}
            current_metadata.update(data['metadata'])
            document.document_metadata = current_metadata
        
        db.session.commit()
        
        # Get updated document with staff and document type info
        result = db.session.query(
            StaffDocuments, 
            Staff.StaffName, 
            Staff.StaffRole,
            StaffDocumentType.DocumentTypeName
        ).join(
            Staff, StaffDocuments.StaffId == Staff.StaffId
        ).outerjoin(
            StaffDocumentType, StaffDocuments.DocumentTypeId == StaffDocumentType.DocumentTypeId
        ).filter(
            StaffDocuments.DocumentId == document_id
        ).first()
        
        doc, staff_name, staff_role, doc_type_name = result
        doc_dict = doc.to_dict()
        doc_dict['StaffName'] = staff_name
        doc_dict['StaffRole'] = staff_role
        doc_dict['DocumentTypeName'] = doc_type_name
        
        return jsonify({
            'message': 'Staff document updated successfully',
            'staff_document': doc_dict
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error updating staff document: {e}")
        return jsonify({'error': str(e)}), 500

@staff_documents_bp.route('/staff_documents/<int:document_id>', methods=['DELETE'])
def delete_staff_document(document_id):
    """Delete a staff document"""
    try:
        # Find the document
        document = StaffDocuments.query.get(document_id)
        if not document:
            return jsonify({'error': 'Staff document not found'}), 404
            
        # Get file paths before deleting the record
        file_path = None
        thumbnail_path = None
        
        if document.document_links:
            if 'file_path' in document.document_links:
                file_path = os.path.join(get_full_staff_documents_path(), document.document_links['file_path'])
            
            if 'thumbnail_path' in document.document_links:
                thumbnail_path = os.path.join(get_full_staff_documents_path(), document.document_links['thumbnail_path'])
        
        # Delete the database record
        db.session.delete(document)
        db.session.commit()
        
        # Delete the original file if it exists
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                current_app.logger.info(f"Deleted original file: {file_path}")
            except OSError as e:
                current_app.logger.warning(f"Could not delete original file {file_path}: {e}")
        
        # Delete the thumbnail file if it exists
        if thumbnail_path and os.path.exists(thumbnail_path):
            try:
                os.remove(thumbnail_path)
                current_app.logger.info(f"Deleted thumbnail file: {thumbnail_path}")
            except OSError as e:
                current_app.logger.warning(f"Could not delete thumbnail file {thumbnail_path}: {e}")
                
        return jsonify({'message': 'Staff document deleted successfully'})
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting staff document: {e}")
        return jsonify({'error': str(e)}), 500

@staff_documents_bp.route('/staff/<staff_id>/documents', methods=['GET'])
def get_staff_documents(staff_id):
    """Get all documents for a specific staff member"""
    try:
        # Verify staff exists
        staff = Staff.query.get(staff_id)
        if not staff:
            return jsonify({'error': 'Staff not found'}), 404
            
        # Query the documents with document type info
        results = db.session.query(
            StaffDocuments, 
            StaffDocumentType.DocumentTypeName
        ).outerjoin(
            StaffDocumentType, StaffDocuments.DocumentTypeId == StaffDocumentType.DocumentTypeId
        ).filter(
            StaffDocuments.StaffId == staff_id
        ).all()
        
        # Format response
        documents = []
        for doc, doc_type_name in results:
            doc_dict = doc.to_dict()
            doc_dict['StaffName'] = staff.StaffName
            doc_dict['StaffRole'] = staff.StaffRole
            doc_dict['DocumentTypeName'] = doc_type_name
            documents.append(doc_dict)
            
        return jsonify({
            'staff_id': staff_id,
            'staff_name': staff.StaffName,
            'staff_role': staff.StaffRole,
            'staff_documents': documents
        })
    except Exception as e:
        print(f"Error getting staff documents: {e}")
        return jsonify({'error': str(e)}), 500

# Legacy endpoints for backward compatibility
@staff_documents_bp.route('/', methods=['GET'])
def list_documents_legacy():
    """Legacy endpoint - redirects to new endpoint"""
    return list_staff_documents()

@staff_documents_bp.route('/<int:document_id>', methods=['GET'])
def get_document_legacy(document_id):
    """Legacy endpoint - redirects to new endpoint"""
    return get_staff_document(document_id)

@staff_documents_bp.route('/', methods=['POST'])
def upload_document_legacy():
    """Legacy endpoint - redirects to new endpoint"""
    return upload_staff_document()

@staff_documents_bp.route('/<int:document_id>', methods=['PUT'])
def update_document_legacy(document_id):
    """Legacy endpoint - redirects to new endpoint"""
    return update_staff_document(document_id)

@staff_documents_bp.route('/<int:document_id>', methods=['DELETE'])
def delete_document_legacy(document_id):
    """Legacy endpoint - redirects to new endpoint"""
    return delete_staff_document(document_id)

@staff_documents_bp.route('/types', methods=['GET'])
def list_document_types():
    """Get all staff document types"""
    try:
        types = StaffDocumentType.query.all()
        return jsonify({'staff_document_types': [t.to_dict() for t in types]})
    except Exception as e:
        print(f"Error listing document types: {e}")
        return jsonify({'error': str(e)}), 500

@staff_documents_bp.route('/staff', methods=['GET'])
def list_staff():
    """Get all staff members"""
    try:
        staff = Staff.query.all()
        return jsonify({'staff': [s.to_dict() for s in staff]})
    except Exception as e:
        print(f"Error listing staff: {e}")
        return jsonify({'error': str(e)}), 500
