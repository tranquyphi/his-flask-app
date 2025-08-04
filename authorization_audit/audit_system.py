"""
Audit System Module for Hospital Information System
Provides easy-to-use audit tracking functionality for Flask application
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
import json

class AuditManager:
    """
    Manages audit logging for database changes
    """
    
    def __init__(self, db_connection):
        """
        Initialize audit manager with database connection
        
        Args:
            db_connection: SQLAlchemy database connection or session
        """
        self.db = db_connection
        self.current_user_id = None
        self.current_session_id = None
        self.current_ip = None
    
    def set_context(self, user_id: int, session_id: str = None, ip_address: str = None):
        """
        Set audit context for current operation
        
        Args:
            user_id: ID of the staff member making changes
            session_id: Application session ID
            ip_address: IP address of the user
        """
        self.current_user_id = user_id
        self.current_session_id = session_id
        self.current_ip = ip_address
        
        # Set MySQL session variables for triggers
        try:
            self.db.execute(f"SET @current_user_id = {user_id}")
            if session_id:
                self.db.execute(f"SET @session_id = '{session_id}'")
            self.db.commit()
        except Exception as e:
            print(f"Warning: Could not set audit context: {e}")
    
    def log_change(self, table_name: str, record_id: str, operation: str, 
                   field_name: str = None, old_value: Any = None, 
                   new_value: Any = None, reason: str = None):
        """
        Manually log a change to the audit table
        
        Args:
            table_name: Name of the table being changed
            record_id: ID of the record being changed
            operation: 'INSERT', 'UPDATE', or 'DELETE'
            field_name: Name of the specific field changed
            old_value: Previous value
            new_value: New value
            reason: Reason for the change
        """
        if not self.current_user_id:
            raise ValueError("Audit context not set. Call set_context() first.")
        
        query = """
        INSERT INTO AuditLog (
            TableName, RecordId, Operation, FieldName, 
            OldValue, NewValue, ChangedBy, ChangeReason, 
            SessionId, IPAddress
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        self.db.execute(query, (
            table_name, str(record_id), operation, field_name,
            str(old_value) if old_value is not None else None,
            str(new_value) if new_value is not None else None,
            self.current_user_id, reason,
            self.current_session_id, self.current_ip
        ))
        self.db.commit()
    
    def set_change_reason(self, reason: str):
        """
        Set reason for upcoming database changes
        
        Args:
            reason: Explanation for the changes
        """
        try:
            self.db.execute(f"SET @change_reason = '{reason}'")
            self.db.commit()
        except Exception as e:
            print(f"Warning: Could not set change reason: {e}")
    
    def get_patient_history(self, patient_id: int) -> List[Dict]:
        """
        Get complete audit history for a patient
        
        Args:
            patient_id: Patient ID to get history for
            
        Returns:
            List of audit records
        """
        query = """
        SELECT 
            ChangeDate, StaffName as ChangedBy, Operation, ChangeReason,
            CASE 
                WHEN OldPatientName != NewPatientName THEN 
                    CONCAT('Name: ', COALESCE(OldPatientName, 'NULL'), ' → ', COALESCE(NewPatientName, 'NULL'))
                WHEN OldPatientAge != NewPatientAge THEN 
                    CONCAT('Age: ', COALESCE(OldPatientAge, 'NULL'), ' → ', COALESCE(NewPatientAge, 'NULL'))
                WHEN OldPatientAddress != NewPatientAddress THEN 
                    CONCAT('Address changed')
                WHEN OldAllergy != NewAllergy THEN 
                    CONCAT('Allergy info updated')
                WHEN OldHistory != NewHistory THEN 
                    CONCAT('Medical history updated')
                ELSE 'Other changes'
            END as ChangeDescription
        FROM PatientAudit pa
        JOIN Staff s ON pa.ChangedBy = s.StaffId
        WHERE pa.PatientId = %s
        ORDER BY pa.ChangeDate DESC
        """
        
        result = self.db.execute(query, (patient_id,))
        return [dict(row) for row in result.fetchall()]
    
    def get_visit_history(self, visit_id: int) -> List[Dict]:
        """
        Get complete audit history for a visit
        
        Args:
            visit_id: Visit ID to get history for
            
        Returns:
            List of audit records
        """
        query = """
        SELECT 
            va.ChangeDate, s.StaffName as ChangedBy, va.Operation, va.ChangeReason,
            CASE 
                WHEN va.OldVisitTime != va.NewVisitTime THEN 
                    CONCAT('Visit Time: ', va.OldVisitTime, ' → ', va.NewVisitTime)
                WHEN va.OldDepartmentId != va.NewDepartmentId THEN 
                    CONCAT('Department: ', od.DepartmentName, ' → ', nd.DepartmentName)
                WHEN va.OldStaffId != va.NewStaffId THEN 
                    CONCAT('Attending Staff changed')
                ELSE 'Other changes'
            END as ChangeDescription
        FROM VisitAudit va
        JOIN Staff s ON va.ChangedBy = s.StaffId
        LEFT JOIN Department od ON va.OldDepartmentId = od.DepartmentId
        LEFT JOIN Department nd ON va.NewDepartmentId = nd.DepartmentId
        WHERE va.VisitId = %s
        ORDER BY va.ChangeDate DESC
        """
        
        result = self.db.execute(query, (visit_id,))
        return [dict(row) for row in result.fetchall()]
    
    def get_drug_prescription_history(self, visit_id: int) -> List[Dict]:
        """
        Get drug prescription change history for a visit
        
        Args:
            visit_id: Visit ID to get drug history for
            
        Returns:
            List of drug prescription audit records
        """
        query = """
        SELECT 
            da.ChangeDate, s.StaffName as ChangedBy, d.DrugName,
            da.Operation, da.ChangeReason,
            CASE 
                WHEN da.OldDrugQuantity != da.NewDrugQuantity THEN 
                    CONCAT('Quantity: ', da.OldDrugQuantity, ' → ', da.NewDrugQuantity)
                WHEN da.OldDrugRoute != da.NewDrugRoute THEN 
                    CONCAT('Route: ', da.OldDrugRoute, ' → ', da.NewDrugRoute)
                WHEN da.OldDrugTimes != da.NewDrugTimes THEN 
                    CONCAT('Times: ', da.OldDrugTimes, ' → ', da.NewDrugTimes)
                ELSE 'Other prescription changes'
            END as ChangeDescription
        FROM VisitDrugAudit da
        JOIN Staff s ON da.ChangedBy = s.StaffId
        JOIN Drug d ON da.DrugId = d.DrugId
        WHERE da.VisitId = %s
        ORDER BY da.ChangeDate DESC
        """
        
        result = self.db.execute(query, (visit_id,))
        return [dict(row) for row in result.fetchall()]
    
    def get_recent_changes(self, days: int = 7, table_name: str = None) -> List[Dict]:
        """
        Get recent changes across all tables or specific table
        
        Args:
            days: Number of days to look back
            table_name: Optional specific table to filter by
            
        Returns:
            List of recent changes
        """
        base_query = """
        SELECT 
            al.ChangeDate, al.TableName, al.RecordId, al.Operation,
            s.StaffName as ChangedBy, s.StaffRole,
            d.DepartmentName as ChangedByDepartment,
            al.ChangeReason
        FROM AuditLog al
        JOIN Staff s ON al.ChangedBy = s.StaffId
        LEFT JOIN Department d ON s.DepartmentId = d.DepartmentId
        WHERE al.ChangeDate >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        """
        
        params = [days]
        
        if table_name:
            base_query += " AND al.TableName = %s"
            params.append(table_name)
        
        base_query += " ORDER BY al.ChangeDate DESC LIMIT 100"
        
        result = self.db.execute(base_query, params)
        return [dict(row) for row in result.fetchall()]
    
    def get_user_activity(self, user_id: int, days: int = 30) -> List[Dict]:
        """
        Get activity summary for a specific user
        
        Args:
            user_id: Staff ID to get activity for
            days: Number of days to look back
            
        Returns:
            List of user activities
        """
        query = """
        SELECT 
            DATE(ChangeDate) as ActivityDate,
            TableName,
            Operation,
            COUNT(*) as ChangeCount
        FROM AuditLog
        WHERE ChangedBy = %s 
          AND ChangeDate >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        GROUP BY DATE(ChangeDate), TableName, Operation
        ORDER BY ActivityDate DESC, ChangeCount DESC
        """
        
        result = self.db.execute(query, (user_id, days))
        return [dict(row) for row in result.fetchall()]
    
    def export_audit_report(self, start_date: str, end_date: str, 
                           table_name: str = None) -> Dict:
        """
        Export comprehensive audit report for a date range
        
        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            table_name: Optional table to filter by
            
        Returns:
            Dictionary containing audit report data
        """
        base_query = """
        SELECT 
            al.ChangeDate, al.TableName, al.RecordId, al.Operation,
            s.StaffName as ChangedBy, s.StaffRole,
            d.DepartmentName as ChangedByDepartment,
            al.ChangeReason, al.IPAddress
        FROM AuditLog al
        JOIN Staff s ON al.ChangedBy = s.StaffId
        LEFT JOIN Department d ON s.DepartmentId = d.DepartmentId
        WHERE DATE(al.ChangeDate) BETWEEN %s AND %s
        """
        
        params = [start_date, end_date]
        
        if table_name:
            base_query += " AND al.TableName = %s"
            params.append(table_name)
        
        base_query += " ORDER BY al.ChangeDate DESC"
        
        result = self.db.execute(base_query, params)
        changes = [dict(row) for row in result.fetchall()]
        
        # Generate summary statistics
        summary_query = """
        SELECT 
            TableName,
            Operation,
            COUNT(*) as Count,
            COUNT(DISTINCT ChangedBy) as UniqueUsers
        FROM AuditLog
        WHERE DATE(ChangeDate) BETWEEN %s AND %s
        """
        
        if table_name:
            summary_query += " AND TableName = %s"
        
        summary_query += " GROUP BY TableName, Operation ORDER BY Count DESC"
        
        summary_result = self.db.execute(summary_query, params)
        summary = [dict(row) for row in summary_result.fetchall()]
        
        return {
            'period': {'start': start_date, 'end': end_date},
            'table_filter': table_name,
            'total_changes': len(changes),
            'changes': changes,
            'summary': summary,
            'generated_at': datetime.now().isoformat()
        }


# Flask decorator for automatic audit context
def with_audit_context(f):
    """
    Decorator to automatically set audit context from Flask session
    """
    from functools import wraps
    from flask import session, request
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'audit_manager' in kwargs and 'user_id' in session:
            audit_manager = kwargs['audit_manager']
            audit_manager.set_context(
                user_id=session['user_id'],
                session_id=session.get('session_id'),
                ip_address=request.remote_addr
            )
        return f(*args, **kwargs)
    return decorated_function


# Usage example in Flask routes
"""
Example usage in Flask application:

from audit_system import AuditManager, with_audit_context

# Initialize audit manager
audit = AuditManager(db.session)

@app.route('/patient/<int:patient_id>/update', methods=['POST'])
@with_audit_context
def update_patient(patient_id):
    # Set audit context
    audit.set_context(
        user_id=session['user_id'], 
        session_id=session['session_id'],
        ip_address=request.remote_addr
    )
    
    # Set reason for changes
    audit.set_change_reason("Patient information update via web interface")
    
    # Make database changes (triggers will automatically log)
    patient = Patient.query.get(patient_id)
    patient.PatientName = request.form['name']
    patient.PatientAge = request.form['age']
    db.session.commit()
    
    return jsonify({'status': 'success'})

@app.route('/patient/<int:patient_id>/audit')
def patient_audit_history(patient_id):
    history = audit.get_patient_history(patient_id)
    return jsonify(history)
"""
