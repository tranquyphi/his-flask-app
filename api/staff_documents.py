"""
API endpoints for StaffDocuments
"""
from flask import Blueprint, request, jsonify, current_app
from models.StaffDocuments import StaffDocuments, Staff, StaffDocumentType
from models_main import db

bp = Blueprint('staff_documents_api', __name__, url_prefix='/api/staff_documents')

@bp.route('/', methods=['GET'])
def list_documents():
    docs = StaffDocuments.query.all()
    return jsonify([doc.to_dict() for doc in docs])

@bp.route('/<int:document_id>', methods=['GET'])
def get_document(document_id):
    doc = StaffDocuments.query.get_or_404(document_id)
    return jsonify(doc.to_dict())

import os
from werkzeug.utils import secure_filename

@bp.route('/', methods=['POST'])
def upload_document():
    # Accept multipart/form-data
    staff_id = request.form.get('StaffId')
    document_type_id = request.form.get('DocumentTypeId')
    document_metadata = request.form.get('document_metadata')
    original_filename = request.form.get('original_filename')
    file_size = request.form.get('FileSize')
    file = request.files.get('file')
    if not file or not staff_id or not document_type_id:
        return jsonify({'error': 'Missing required fields or file'}), 400
    allowed_ext = {'png','jpg','jpeg','gif','pdf','doc','docx','xls','xlsx','ppt','pptx','txt','rtf','csv','zip'}
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in allowed_ext:
        return jsonify({'error': 'File type not allowed'}), 400
    filename = secure_filename(file.filename)
    save_dir = os.path.join(current_app.root_path, 'static', 'staff_documents')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)
    file.save(save_path)
    # Build document_links as a JSON with file path
    document_links = {'path': f'/static/staff_documents/{filename}'}
    doc = StaffDocuments(
        StaffId=staff_id,
        DocumentTypeId=document_type_id,
        document_links=document_links,
        document_metadata=document_metadata,
        FileSize=file_size,
        original_filename=original_filename
    )
    db.session.add(doc)
    db.session.commit()
    return jsonify(doc.to_dict()), 201

@bp.route('/<int:document_id>', methods=['PUT'])
def update_document(document_id):
    doc = StaffDocuments.query.get_or_404(document_id)
    data = request.json
    doc.DocumentTypeId = data.get('DocumentTypeId', doc.DocumentTypeId)
    doc.document_links = data.get('document_links', doc.document_links)
    doc.document_metadata = data.get('document_metadata', doc.document_metadata)
    doc.FileSize = data.get('FileSize', doc.FileSize)
    doc.original_filename = data.get('original_filename', doc.original_filename)
    db.session.commit()
    return jsonify(doc.to_dict())

@bp.route('/<int:document_id>', methods=['DELETE'])
def delete_document(document_id):
    doc = StaffDocuments.query.get_or_404(document_id)
    db.session.delete(doc)
    db.session.commit()
    return jsonify({'result': 'deleted'})

@bp.route('/types', methods=['GET'])
def list_document_types():
    types = StaffDocumentType.query.all()
    return jsonify([t.to_dict() for t in types])

@bp.route('/staff', methods=['GET'])
def list_staff():
    staff = Staff.query.all()
    return jsonify([s.to_dict() for s in staff])
