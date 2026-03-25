#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import cgi
    import cgitb
except ImportError:
    import cgi
    class SimpleCGITB:
        @staticmethod
        def enable():
            import traceback
            def excepthook(type, value, tb):
                import html
                trace = ''.join(traceback.format_exception(type, value, tb))
                print("Status: 500 Internal Server Error")
                print("Content-Type: text/html\n")
                print(f"<html><body><pre>{html.escape(trace)}</pre></body></html>")
            sys.excepthook = excepthook
    cgitb = SimpleCGITB()

cgitb.enable()

from session import SessionManager
from database import DatabaseOperations

session = SessionManager()
session.start_session()

if not session.is_logged_in() or session.get('user_type') != 'patient':
    print("Location: patient_login.py")
    print()
    sys.exit()

patient_info = session.get_user_info()
patient_id = patient_info['user_id']

# Get current patient data
patient = DatabaseOperations.execute_query(
    "SELECT * FROM patients WHERE patient_id = %s",
    (patient_id,),
    fetch_one=True
)

if not patient:
    session.logout()
    print("Location: patient_login.py")
    print()
    sys.exit()

form = cgi.FieldStorage()
action = form.getvalue('action', '')

errors = []
success = False

if action == 'update':
    # Get form data
    full_name = form.getvalue('full_name', '').strip()
    email = form.getvalue('email', '').strip()
    phone = form.getvalue('phone', '').strip()
    address = form.getvalue('address', '').strip()
    emergency_contact = form.getvalue('emergency_contact', '').strip()
    blood_group = form.getvalue('blood_group', '')

    # Validation
    if not full_name:
        errors.append("Full name is required")
    if not email:
        errors.append("Email is required")
    if not phone:
        errors.append("Phone is required")

    # Check email uniqueness (excluding current patient)
    if not errors:
        check = DatabaseOperations.execute_query(
            "SELECT * FROM patients WHERE email = %s AND patient_id != %s",
            (email, patient_id),
            fetch_one=True
        )
        if check:
            errors.append("Email already used by another account")

    if not errors:
        try:
            DatabaseOperations.execute_query(
                """UPDATE patients SET 
                   full_name = %s, email = %s, phone = %s,
                   address = %s, emergency_contact = %s, blood_group = %s
                   WHERE patient_id = %s""",
                (full_name, email, phone, address, emergency_contact, blood_group, patient_id)
            )
            success = True
            # Update session name
            session.set('full_name', full_name)
            patient['full_name'] = full_name
            patient['email'] = email
            patient['phone'] = phone
            patient['address'] = address
            patient['emergency_contact'] = emergency_contact
            patient['blood_group'] = blood_group
        except Exception as e:
            errors.append(f"Update failed: {e}")

print("Content-Type: text/html; charset=utf-8")
print()

today = datetime.now().date()
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Profile - Clinic Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary: #2A5C82;
            --secondary: #4A90E2;
            --danger: #FF6B6B;
            --dark: #2C3E50;
        }}
        body {{ font-family: 'Inter', sans-serif; background: #f4f6f9; }}
        .navbar {{ background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .edit-container {{ max-width: 800px; margin: 100px auto 50px; padding: 0 20px; }}
        .card {{ border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
        .card-header {{ background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%); color: white; border-radius: 20px 20px 0 0 !important; }}
        .btn-save {{ background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; border: none; }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light fixed-top">
        <div class="container">
            <a class="navbar-brand" href="index.py"><i class="fas fa-clinic-medical me-2 text-primary"></i>ClinicCare</a>
            <div class="ms-auto">
                <a href="patient_profile.py" class="btn btn-outline-primary btn-sm me-2"><i class="fas fa-arrow-left"></i> Back to Profile</a>
                <a href="logout.py" class="btn btn-outline-danger btn-sm">Logout</a>
            </div>
        </div>
    </nav>
    
    <div class="edit-container">
        <div class="card">
            <div class="card-header">
                <h4 class="mb-0"><i class="fas fa-edit me-2"></i>Edit Profile</h4>
            </div>
            <div class="card-body">
""")

if success:
    print('<div class="alert alert-success">Profile updated successfully! <a href="patient_profile.py">View Profile</a></div>')

if errors:
    print('<div class="alert alert-danger"><ul class="mb-0">')
    for e in errors:
        print(f'<li>{e}</li>')
    print('</ul></div>')

print(f"""
                <form method="post" action="patient_edit_profile.py">
                    <input type="hidden" name="action" value="update">
                    
                    <div class="mb-3">
                        <label class="form-label">Full Name</label>
                        <input type="text" class="form-control" name="full_name" value="{patient['full_name']}" required>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">Email</label>
                        <input type="email" class="form-control" name="email" value="{patient['email']}" required>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">Phone</label>
                        <input type="tel" class="form-control" name="phone" value="{patient['phone']}" required>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">Address</label>
                        <textarea class="form-control" name="address" rows="2">{patient['address'] or ''}</textarea>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">Emergency Contact</label>
                        <input type="tel" class="form-control" name="emergency_contact" value="{patient['emergency_contact'] or ''}">
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">Blood Group</label>
                        <select class="form-select" name="blood_group">
                            <option value="">Select</option>
                            <option value="A+" {"selected" if patient['blood_group']=='A+' else ""}>A+</option>
                            <option value="A-" {"selected" if patient['blood_group']=='A-' else ""}>A-</option>
                            <option value="B+" {"selected" if patient['blood_group']=='B+' else ""}>B+</option>
                            <option value="B-" {"selected" if patient['blood_group']=='B-' else ""}>B-</option>
                            <option value="O+" {"selected" if patient['blood_group']=='O+' else ""}>O+</option>
                            <option value="O-" {"selected" if patient['blood_group']=='O-' else ""}>O-</option>
                            <option value="AB+" {"selected" if patient['blood_group']=='AB+' else ""}>AB+</option>
                            <option value="AB-" {"selected" if patient['blood_group']=='AB-' else ""}>AB-</option>
                        </select>
                    </div>
                    
                    <hr>
                    <div class="text-end">
                        <a href="patient_profile.py" class="btn btn-secondary me-2">Cancel</a>
                        <button type="submit" class="btn btn-save">Save Changes</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
""")