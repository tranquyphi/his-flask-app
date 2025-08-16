"""
Patient Documents API Blueprint
CRUD operations for managing patient documents
"""
from flask import Blueprint, request, jsonify, current_app, send_file
from models import db, PatientDocuments, DocumentType, DOCUMENTS_PATH, Patient
import os
import json
import uuid
import datetime
import mimetypes
from werkzeug.utils import secure_filename
import io

patient_documents_bp = Blueprint('patient_documents', __name__)

def get_full_document_path():
    """Get the absolute path to the documents directory"""
    # Use the application root path + the documents path
    return os.path.join(current_app.root_path, DOCUMENTS_PATH.lstrip('/'))

def ensure_documents_dir():
    """Ensure the documents directory exists"""
    docs_path = get_full_document_path()
    if not os.path.exists(docs_path):
        os.makedirs(docs_path, exist_ok=True)
    return docs_path

def generate_unique_filename(original_filename):
    """Generate a unique filename to avoid conflicts"""
    # Get file extension
    _, ext = os.path.splitext(original_filename)
    # Generate a unique filename with timestamp and UUID
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}{ext}"

@patient_documents_bp.route('/patient_documents', methods=['GET'])
def list_patient_documents():
    """List all patient documents with optional filter by patient ID"""
    try:
        # Get query parameters
        patient_id = request.args.get('patient_id')
        document_type_id = request.args.get('document_type_id')
        
        # Start with base query
        query = db.session.query(
            PatientDocuments, 
            Patient.PatientName, 
            Patient.PatientAge,
            DocumentType.DocumentTypeName
        ).join(
            Patient, PatientDocuments.PatientId == Patient.PatientId
        ).outerjoin(
            DocumentType, PatientDocuments.DocumentTypeId == DocumentType.DocumentTypeId
        )
        
        # Apply filters if provided
        if patient_id:
            query = query.filter(PatientDocuments.PatientId == patient_id)
        if document_type_id:
            query = query.filter(PatientDocuments.DocumentTypeId == document_type_id)
        
        # Execute query
        results = query.all()
        
        # Format response
        documents = []
        for doc, patient_name, patient_age, doc_type_name in results:
            doc_dict = doc.to_dict()
            doc_dict['PatientName'] = patient_name
            doc_dict['PatientAge'] = patient_age
            doc_dict['DocumentTypeName'] = doc_type_name
            documents.append(doc_dict)
            
        return jsonify({'patient_documents': documents})
    except Exception as e:
        print(f"Error listing patient documents: {e}")
        return jsonify({'error': str(e)}), 500

@patient_documents_bp.route('/patient_documents/<int:document_id>', methods=['GET'])
def get_patient_document(document_id):
    """Get a specific patient document by ID"""
    try:
        # Query the document with patient and document type info
        result = db.session.query(
            PatientDocuments, 
            Patient.PatientName, 
            Patient.PatientAge,
            DocumentType.DocumentTypeName
        ).join(
            Patient, PatientDocuments.PatientId == Patient.PatientId
        ).outerjoin(
            DocumentType, PatientDocuments.DocumentTypeId == DocumentType.DocumentTypeId
        ).filter(
            PatientDocuments.DocumentId == document_id
        ).first()
        
        if not result:
            return jsonify({'error': 'Patient document not found'}), 404
            
        doc, patient_name, patient_age, doc_type_name = result
        doc_dict = doc.to_dict()
        doc_dict['PatientName'] = patient_name
        doc_dict['PatientAge'] = patient_age
        doc_dict['DocumentTypeName'] = doc_type_name
        
        # Check if file should be returned
        download = request.args.get('download', 'false').lower() == 'true'
        
        if download:
            # Get document path from document_links
            if doc.document_links and 'file_path' in doc.document_links:
                file_path = os.path.join(get_full_document_path(), doc.document_links['file_path'])
                
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
                
        return jsonify({'patient_document': doc_dict})
    except Exception as e:
        print(f"Error getting patient document: {e}")
        return jsonify({'error': str(e)}), 500

@patient_documents_bp.route('/patient_documents', methods=['POST'])
def upload_patient_document():
    """Upload a new patient document"""
    try:
        # Check if we have a file in the request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        
        # Validate file
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        # Get form data
        patient_id = request.form.get('patient_id')
        document_type_id = request.form.get('document_type_id')
        
        # Validate patient ID
        if not patient_id:
            return jsonify({'error': 'Patient ID is required'}), 400
            
        # Verify patient exists
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
            
        # Ensure document directory exists
        docs_path = ensure_documents_dir()
        
        # Generate a unique filename
        secure_name = secure_filename(file.filename)
        unique_filename = generate_unique_filename(secure_name)
        
        # Save the file
        file_path = os.path.join(docs_path, unique_filename)
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Determine file type
        file_type = file.content_type or mimetypes.guess_type(file.filename)[0] or 'application/octet-stream'
        
        # Create document links JSON
        document_links = {
            'file_path': unique_filename,
            'url': f"{DOCUMENTS_PATH}/{unique_filename}"
        }
        
        # Create metadata JSON
        metadata_value = {
            'upload_timestamp': datetime.datetime.now().isoformat(),
            'uploader': request.form.get('uploader', 'system'),
            'description': request.form.get('description', '')
        }
        
        # Create document record
        new_document = PatientDocuments(
            PatientId=patient_id,
            DocumentTypeId=document_type_id if document_type_id else None,
            document_links=document_links,
            document_metadata=metadata_value,
            original_filename=file.filename,
            file_type=file_type,
            file_size=file_size
        )
        
        db.session.add(new_document)
        db.session.commit()
        
        # Format response
        doc_dict = new_document.to_dict()
        doc_dict['PatientName'] = patient.PatientName
        doc_dict['PatientAge'] = patient.PatientAge
        
        if document_type_id:
            doc_type = DocumentType.query.get(document_type_id)
            if doc_type:
                doc_dict['DocumentTypeName'] = doc_type.DocumentTypeName
        
        return jsonify({
            'message': 'Patient document uploaded successfully',
            'patient_document': doc_dict
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error uploading patient document: {e}")
        return jsonify({'error': str(e)}), 500

@patient_documents_bp.route('/patient_documents/<int:document_id>', methods=['PUT'])
def update_patient_document(document_id):
    """Update patient document metadata"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Find the document
        document = PatientDocuments.query.get(document_id)
        if not document:
            return jsonify({'error': 'Patient document not found'}), 404
            
        # Update fields that can be modified
        if 'DocumentTypeId' in data:
            document.DocumentTypeId = data['DocumentTypeId']
            
        if 'metadata' in data and isinstance(data['metadata'], dict):
            # Merge existing metadata with new metadata
            current_metadata = document.document_metadata or {}
            current_metadata.update(data['metadata'])
            document.document_metadata = current_metadata
        
        db.session.commit()
        
        # Get updated document with patient and document type info
        result = db.session.query(
            PatientDocuments, 
            Patient.PatientName, 
            Patient.PatientAge,
            DocumentType.DocumentTypeName
        ).join(
            Patient, PatientDocuments.PatientId == Patient.PatientId
        ).outerjoin(
            DocumentType, PatientDocuments.DocumentTypeId == DocumentType.DocumentTypeId
        ).filter(
            PatientDocuments.DocumentId == document_id
        ).first()
        
        doc, patient_name, patient_age, doc_type_name = result
        doc_dict = doc.to_dict()
        doc_dict['PatientName'] = patient_name
        doc_dict['PatientAge'] = patient_age
        doc_dict['DocumentTypeName'] = doc_type_name
        
        return jsonify({
            'message': 'Patient document updated successfully',
            'patient_document': doc_dict
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error updating patient document: {e}")
        return jsonify({'error': str(e)}), 500

@patient_documents_bp.route('/patient_documents/<int:document_id>', methods=['DELETE'])
def delete_patient_document(document_id):
    """Delete a patient document"""
    try:
        # Find the document
        document = PatientDocuments.query.get(document_id)
        if not document:
            return jsonify({'error': 'Patient document not found'}), 404
            
        # Get file path before deleting the record
        file_path = None
        if document.document_links and 'file_path' in document.document_links:
            file_path = os.path.join(get_full_document_path(), document.document_links['file_path'])
        
        # Delete the database record
        db.session.delete(document)
        db.session.commit()
        
        # Delete the file if it exists
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"Warning: Could not delete file {file_path}: {e}")
                # We don't return error here since the database record was deleted successfully
                
        return jsonify({'message': 'Patient document deleted successfully'})
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting patient document: {e}")
        return jsonify({'error': str(e)}), 500

@patient_documents_bp.route('/patients/<patient_id>/documents', methods=['GET'])
def get_patient_documents(patient_id):
    """Get all documents for a specific patient"""
    try:
        # Verify patient exists
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
            
        # Query the documents with document type info
        results = db.session.query(
            PatientDocuments, 
            DocumentType.DocumentTypeName
        ).outerjoin(
            DocumentType, PatientDocuments.DocumentTypeId == DocumentType.DocumentTypeId
        ).filter(
            PatientDocuments.PatientId == patient_id
        ).all()
        
        # Format response
        documents = []
        for doc, doc_type_name in results:
            doc_dict = doc.to_dict()
            doc_dict['PatientName'] = patient.PatientName
            doc_dict['PatientAge'] = patient.PatientAge
            doc_dict['DocumentTypeName'] = doc_type_name
            documents.append(doc_dict)
            
        return jsonify({
            'patient_id': patient_id,
            'patient_name': patient.PatientName,
            'patient_documents': documents
        })
    except Exception as e:
        print(f"Error getting patient documents: {e}")
        return jsonify({'error': str(e)}), 500
