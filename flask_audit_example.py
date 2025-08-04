"""
Example Flask routes demonstrating audit system integration
Shows how to implement change tracking in your HIS application
"""

from flask import Flask, request, session, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from authorization_audit.audit_system import AuditManager, with_audit_context
from datetime import datetime, timedelta
import json

app = Flask(__name__)
db = SQLAlchemy(app)

# Initialize audit manager
audit = AuditManager(db.session)

# =============================================================================
# PATIENT MANAGEMENT WITH AUDIT TRACKING
# =============================================================================

@app.route('/api/patient/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """Update patient information with full audit tracking"""
    
    # Set audit context
    audit.set_context(
        user_id=session['user_id'], 
        session_id=session.get('session_id'),
        ip_address=request.remote_addr
    )
    
    # Set reason for changes
    reason = request.json.get('change_reason', 'Patient information update')
    audit.set_change_reason(reason)
    
    try:
        # Get patient and update
        patient = db.session.execute(
            "SELECT * FROM Patient WHERE PatientId = %s", 
            (patient_id,)
        ).fetchone()
        
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Update patient data (triggers will automatically log changes)
        update_data = request.json
        update_fields = []
        update_values = []
        
        for field in ['PatientName', 'PatientGender', 'PatientAge', 
                     'PatientAddress', 'Allergy', 'History', 'PatientNote']:
            if field in update_data:
                update_fields.append(f"{field} = %s")
                update_values.append(update_data[field])
        
        if update_fields:
            update_values.append(patient_id)
            query = f"UPDATE Patient SET {', '.join(update_fields)} WHERE PatientId = %s"
            db.session.execute(query, update_values)
            db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Patient updated successfully',
            'audit_logged': True
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/patient/<int:patient_id>/audit')
def get_patient_audit(patient_id):
    """Get complete audit history for a patient"""
    
    try:
        history = audit.get_patient_history(patient_id)
        return jsonify({
            'patient_id': patient_id,
            'audit_history': history,
            'total_changes': len(history)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============================================================================
# VISIT MANAGEMENT WITH AUDIT TRACKING
# =============================================================================

@app.route('/api/visit', methods=['POST'])
def create_visit():
    """Create new visit with audit tracking"""
    
    audit.set_context(
        user_id=session['user_id'],
        session_id=session.get('session_id'),
        ip_address=request.remote_addr
    )
    
    audit.set_change_reason("New visit created")
    
    try:
        visit_data = request.json
        
        # Insert new visit (trigger will log creation)
        query = """
        INSERT INTO Visit (PatientId, DepartmentId, VisitPurpose, VisitTime, StaffId)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        result = db.session.execute(query, (
            visit_data['patient_id'],
            visit_data['department_id'],
            visit_data['visit_purpose'],
            visit_data.get('visit_time', datetime.now()),
            session['user_id']
        ))
        
        visit_id = result.lastrowid
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'visit_id': visit_id,
            'message': 'Visit created successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/visit/<int:visit_id>/drug', methods=['POST'])
def add_drug_prescription(visit_id):
    """Add drug prescription with audit tracking"""
    
    audit.set_context(
        user_id=session['user_id'],
        session_id=session.get('session_id'),
        ip_address=request.remote_addr
    )
    
    audit.set_change_reason("Drug prescription added")
    
    try:
        drug_data = request.json
        
        # Insert drug prescription (trigger will log)
        query = """
        INSERT INTO VisitDrug (VisitId, DrugId, DrugRoute, DrugQuantity, 
                              DrugTimes, DrugAtTime, Note, IsCustom)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        db.session.execute(query, (
            visit_id,
            drug_data['drug_id'],
            drug_data['route'],
            drug_data['quantity'],
            drug_data['times'],
            drug_data.get('at_time'),
            drug_data.get('note', ''),
            drug_data.get('is_custom', 0)
        ))
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Drug prescription added successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/visit/<int:visit_id>/drug/<drug_id>', methods=['PUT'])
def update_drug_prescription(visit_id, drug_id):
    """Update drug prescription with audit tracking"""
    
    audit.set_context(
        user_id=session['user_id'],
        session_id=session.get('session_id'),
        ip_address=request.remote_addr
    )
    
    reason = request.json.get('change_reason', 'Drug prescription modified')
    audit.set_change_reason(reason)
    
    try:
        update_data = request.json
        update_fields = []
        update_values = []
        
        for field in ['DrugRoute', 'DrugQuantity', 'DrugTimes', 'Note']:
            if field.lower() in update_data:
                update_fields.append(f"{field} = %s")
                update_values.append(update_data[field.lower()])
        
        if update_fields:
            update_values.extend([visit_id, drug_id])
            query = f"""
            UPDATE VisitDrug 
            SET {', '.join(update_fields)} 
            WHERE VisitId = %s AND DrugId = %s
            """
            db.session.execute(query, update_values)
            db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Drug prescription updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# =============================================================================
# AUDIT REPORTING ENDPOINTS
# =============================================================================

@app.route('/api/audit/recent')
def get_recent_changes():
    """Get recent changes across all tables"""
    
    days = request.args.get('days', 7, type=int)
    table_name = request.args.get('table')
    
    try:
        changes = audit.get_recent_changes(days=days, table_name=table_name)
        return jsonify({
            'period_days': days,
            'table_filter': table_name,
            'changes': changes
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/audit/user/<int:user_id>')
def get_user_activity(user_id):
    """Get activity summary for a specific user"""
    
    days = request.args.get('days', 30, type=int)
    
    try:
        activity = audit.get_user_activity(user_id=user_id, days=days)
        return jsonify({
            'user_id': user_id,
            'period_days': days,
            'activity': activity
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/audit/report')
def generate_audit_report():
    """Generate comprehensive audit report"""
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    table_name = request.args.get('table')
    
    if not start_date or not end_date:
        return jsonify({'error': 'start_date and end_date required'}), 400
    
    try:
        report = audit.export_audit_report(
            start_date=start_date,
            end_date=end_date,
            table_name=table_name
        )
        return jsonify(report)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/visit/<int:visit_id>/audit/drug')
def get_visit_drug_audit(visit_id):
    """Get drug prescription audit history for a visit"""
    
    try:
        history = audit.get_drug_prescription_history(visit_id)
        return jsonify({
            'visit_id': visit_id,
            'drug_audit_history': history
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============================================================================
# AUDIT DASHBOARD ENDPOINTS
# =============================================================================

@app.route('/audit/dashboard')
def audit_dashboard():
    """Render audit dashboard page"""
    return render_template('audit_dashboard.html')

@app.route('/api/audit/stats')
def get_audit_stats():
    """Get audit statistics for dashboard"""
    
    try:
        # Get recent activity stats
        recent_query = """
        SELECT 
            DATE(ChangeDate) as date,
            COUNT(*) as total_changes,
            COUNT(DISTINCT ChangedBy) as active_users,
            COUNT(DISTINCT TableName) as tables_modified
        FROM AuditLog 
        WHERE ChangeDate >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        GROUP BY DATE(ChangeDate)
        ORDER BY date DESC
        """
        
        recent_stats = db.session.execute(recent_query).fetchall()
        
        # Get table activity stats
        table_query = """
        SELECT 
            TableName,
            COUNT(*) as change_count,
            COUNT(DISTINCT ChangedBy) as unique_users,
            MAX(ChangeDate) as last_change
        FROM AuditLog 
        WHERE ChangeDate >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY TableName
        ORDER BY change_count DESC
        """
        
        table_stats = db.session.execute(table_query).fetchall()
        
        # Get top active users
        user_query = """
        SELECT 
            s.StaffName,
            s.StaffRole,
            d.DepartmentName,
            COUNT(al.AuditId) as change_count
        FROM AuditLog al
        JOIN Staff s ON al.ChangedBy = s.StaffId
        LEFT JOIN Department d ON s.DepartmentId = d.DepartmentId
        WHERE al.ChangeDate >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        GROUP BY s.StaffId, s.StaffName, s.StaffRole, d.DepartmentName
        ORDER BY change_count DESC
        LIMIT 10
        """
        
        user_stats = db.session.execute(user_query).fetchall()
        
        return jsonify({
            'recent_activity': [dict(row) for row in recent_stats],
            'table_activity': [dict(row) for row in table_stats],
            'top_users': [dict(row) for row in user_stats]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============================================================================
# MIDDLEWARE FOR AUTOMATIC AUDIT CONTEXT
# =============================================================================

@app.before_request
def set_audit_context():
    """Automatically set audit context for all requests"""
    if 'user_id' in session:
        audit.set_context(
            user_id=session['user_id'],
            session_id=session.get('session_id'),
            ip_address=request.remote_addr
        )

if __name__ == '__main__':
    app.run(debug=True)
