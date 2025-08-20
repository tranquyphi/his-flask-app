"""
Document Type API Blueprint
CRUD operations for Document Type management
"""
from flask import Blueprint, request, jsonify
from models import db
from models import DocumentType

document_types_bp = Blueprint('document_types', __name__)

@document_types_bp.route('/document_types', methods=['GET'])
def list_document_types():
    """List all document types"""
    try:
        document_types = DocumentType.query.all()
        return jsonify({'document_types': [doc_type.to_dict() for doc_type in document_types]})
    except Exception as e:
        print(f"Error listing document types: {e}")
        return jsonify({'error': str(e)}), 500

@document_types_bp.route('/document_types/<int:type_id>', methods=['GET'])
def get_document_type(type_id):
    """Get a specific document type by ID"""
    try:
        document_type = DocumentType.query.get(type_id)
        if not document_type:
            return jsonify({'error': 'Document type not found'}), 404
        return jsonify({'document_type': document_type.to_dict()})
    except Exception as e:
        print(f"Error getting document type: {e}")
        return jsonify({'error': str(e)}), 500

@document_types_bp.route('/document_types', methods=['POST'])
def create_document_type():
    """Create a new document type"""
    try:
        data = request.json
        if not data or 'DocumentTypeName' not in data:
            return jsonify({'error': 'DocumentTypeName is required'}), 400
            
        new_doc_type = DocumentType(DocumentTypeName=data['DocumentTypeName'])
        
        db.session.add(new_doc_type)
        db.session.commit()
        
        return jsonify({
            'message': 'Document type created successfully',
            'document_type': new_doc_type.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating document type: {e}")
        return jsonify({'error': str(e)}), 500

@document_types_bp.route('/document_types/<int:type_id>', methods=['PUT'])
def update_document_type(type_id):
    """Update an existing document type"""
    try:
        data = request.json
        if not data or 'DocumentTypeName' not in data:
            return jsonify({'error': 'DocumentTypeName is required'}), 400
            
        document_type = DocumentType.query.get(type_id)
        if not document_type:
            return jsonify({'error': 'Document type not found'}), 404
            
        document_type.DocumentTypeName = data['DocumentTypeName']
        db.session.commit()
        
        return jsonify({
            'message': 'Document type updated successfully',
            'document_type': document_type.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error updating document type: {e}")
        return jsonify({'error': str(e)}), 500

@document_types_bp.route('/document_types/<int:type_id>', methods=['DELETE'])
def delete_document_type(type_id):
    """Delete a document type"""
    try:
        document_type = DocumentType.query.get(type_id)
        if not document_type:
            return jsonify({'error': 'Document type not found'}), 404
            
        db.session.delete(document_type)
        db.session.commit()
        
        return jsonify({'message': 'Document type deleted successfully'})
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting document type: {e}")
        return jsonify({'error': str(e)}), 500
