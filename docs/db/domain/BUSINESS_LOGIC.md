# Visit business logic
## Visit staff
A patient can be visited by staff (table Visit)
A visit is assigned to one or many staff. (table VisitStaff)

## Staff Assignment Rules
Based on purpose's visit (Visit.VisitPurpose):

### Consultation Visits ("Hội chẩn")
- Can be assigned to many staff from any department
- Staff must be available (Staff.StaffAvailable = 1)

### Non-Consultation Visits
- Can only be assigned to staff who:
  - Are available (Staff.StaffAvailable = 1) implemented through UI (selection by dropdown list with restrict choices)
  - Belong to the patient's current department (PatientDepartment.Current = 1) implemented through UI (selection by dropdown list with restrict choices)

## Department Assignment Rules
- A patient's current department is determined by PatientDepartment.Current = 1
- Staff must be actively assigned to a department (StaffDepartment.Current = 1)
- When a patient changes departments, the previous assignment becomes inactive (Current = 0)


