"""
SQLAlchemy ORM Approaches for Database Views - Demonstration
============================================================

This file demonstrates different ways to work with database views in SQLAlchemy ORM:

1. ✅ ORM Model for Views (Recommended - What we implemented)
2. 🔄 Using db.text() with ORM session
3. 🔄 Using Query with from_statement()
4. 🔄 Using Hybrid approach with relationships

"""

from models import (
    create_app, db, PatientWithDepartment, StaffWithDepartment, 
    Patient, Staff, Department
)
from sqlalchemy import text

def demonstrate_orm_view_approaches():
    """Demonstrate different approaches to query views with SQLAlchemy ORM"""
    
    app = create_app('development')
    
    with app.app_context():
        print("=== SQLAlchemy ORM Approaches for Database Views ===\n")
        
        # Method 1: ORM Model for Views (RECOMMENDED - What we implemented)
        print("1. ✅ ORM Model for Views (Current Implementation)")
        print("   Pros: Type safety, relationship support, clean syntax")
        print("   Code:")
        print("   patients = PatientWithDepartment.query.all()")
        print("   patient = PatientWithDepartment.query.filter_by(PatientId='P001').first()")
        print("   patients_with_cardiology = PatientWithDepartment.query.filter_by(DepartmentName='Cardiology').all()")
        print()
        
        # Method 2: Using db.text() with ORM session
        print("2. 🔄 Using db.text() with ORM session")
        print("   Pros: Flexible SQL, still uses ORM session")
        print("   Cons: No type safety, manual result processing")
        print("   Code:")
        print("   result = db.session.execute(text('SELECT * FROM patients_with_department WHERE DepartmentName = :dept'), {'dept': 'Cardiology'})")
        print("   patients = [dict(row) for row in result]")
        print()
        
        # Method 3: Using Query with from_statement()
        print("3. 🔄 Using Query with from_statement()")
        print("   Pros: Combines ORM models with custom SQL")
        print("   Cons: More complex, limited flexibility")
        print("   Code:")
        print("   stmt = text('SELECT * FROM patients_with_department WHERE DepartmentName = :dept')")
        print("   patients = db.session.query(PatientWithDepartment).from_statement(stmt).params(dept='Cardiology').all()")
        print()
        
        # Method 4: Hybrid approach with relationships
        print("4. 🔄 Hybrid approach with relationships")
        print("   Pros: Uses existing relationships, no view needed")
        print("   Cons: More complex queries, potential N+1 problems")
        print("   Code:")
        print("   patients = db.session.query(Patient).join(PatientDepartment).filter(PatientDepartment.Current == True).join(Department).all()")
        print()
        
        print("=== Why we chose Method 1 (ORM Model for Views) ===")
        print("✅ Type safety and IDE support")
        print("✅ Clean, readable code")
        print("✅ Automatic serialization with to_dict() method")
        print("✅ Consistent with SQLAlchemy patterns")
        print("✅ Easy filtering and querying")
        print("✅ Built-in error handling and fallbacks")
        print()
        
        # Demonstrate actual usage
        try:
            print("=== Live Demo (if views exist) ===")
            patients = PatientWithDepartment.query.limit(3).all()
            if patients:
                print(f"Found {len(patients)} patients with departments:")
                for patient in patients:
                    print(f"  - {patient.PatientName} in {patient.DepartmentName or 'No Department'}")
            else:
                print("No patients found (views may not be created yet)")
        except Exception as e:
            print(f"Views not created yet: {e}")
            print("This is expected - views will be created when database is set up")

def show_advanced_orm_patterns():
    """Show advanced patterns for working with view models"""
    
    app = create_app('development')
    
    with app.app_context():
        print("\n=== Advanced ORM Patterns for Views ===\n")
        
        print("1. Filtering and Searching:")
        print("   # Find patients in specific department")
        print("   cardiology_patients = PatientWithDepartment.query.filter_by(DepartmentName='Cardiology').all()")
        print("")
        print("   # Search by patient name")
        print("   johns = PatientWithDepartment.query.filter(PatientWithDepartment.PatientName.like('%John%')).all()")
        print("")
        print("   # Complex filtering")
        print("   emergency_patients = PatientWithDepartment.query.filter(")
        print("       PatientWithDepartment.DepartmentType == 'Cấp cứu',")
        print("       PatientWithDepartment.PatientAge.cast(db.Integer) > 65")
        print("   ).all()")
        print()
        
        print("2. Aggregation and Grouping:")
        print("   # Count patients by department")
        print("   from sqlalchemy import func")
        print("   dept_counts = db.session.query(")
        print("       PatientWithDepartment.DepartmentName,")
        print("       func.count(PatientWithDepartment.PatientId).label('patient_count')")
        print("   ).group_by(PatientWithDepartment.DepartmentName).all()")
        print()
        
        print("3. Pagination:")
        print("   # Paginated results")
        print("   page = PatientWithDepartment.query.paginate(")
        print("       page=1, per_page=10, error_out=False")
        print("   )")
        print("   patients = page.items")
        print()
        
        print("4. Ordering:")
        print("   # Order by department, then by name")
        print("   patients = PatientWithDepartment.query.order_by(")
        print("       PatientWithDepartment.DepartmentName,")
        print("       PatientWithDepartment.PatientName")
        print("   ).all()")
        print()

def create_additional_view_models():
    """Template for creating additional view models"""
    
    print("\n=== Template for Additional View Models ===\n")
    
    template = '''
class ExampleViewModel(db.Model):
    """ORM Model for example_view database view"""
    __tablename__ = 'example_view'
    __table_args__ = {'info': dict(is_view=True)}  # Mark as view
    
    # Define all columns that exist in the view
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    # ... other columns
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            # ... other fields
        }
    
    def __repr__(self):
        return f'<ExampleViewModel {self.id}: {self.name}>'

# Usage:
def get_all_examples():
    """Get all records from view using ORM"""
    try:
        examples = ExampleViewModel.query.all()
        return [example.to_dict() for example in examples]
    except Exception as e:
        print(f"Error querying view: {e}")
        # Fallback to base tables if needed
        return []
'''
    
    print("Template code:")
    print(template)

if __name__ == "__main__":
    demonstrate_orm_view_approaches()
    show_advanced_orm_patterns()
    create_additional_view_models()
