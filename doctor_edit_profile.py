#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


import sys
import os
import bcrypt
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
            def excepthook(typ, val, tb):
                import html
                trace = ''.join(traceback.format_exception(typ, val, tb))
                trace = trace.encode('ascii', 'replace').decode('ascii')
                print("Status: 500 Internal Server Error")
                print("Content-Type: text/html\n")
                print(f"<html><body><pre>{html.escape(trace)}</pre></body></html>")
            sys.excepthook = excepthook
    cgitb = SimpleCGITB()

cgitb.enable()

from session import SessionManager
from database import DatabaseOperations

headers = []
session = SessionManager()
session.start_session()

cookie_header = session.get_cookie_header()
if cookie_header:
    headers.append(cookie_header)

if not session.is_logged_in() or session.get('user_type') != 'doctor':
    headers.append("Location: doctor_login.py")
    for h in headers:
        print(h)
    print()
    sys.exit()

doctor_info = session.get_user_info()
doctor_id = doctor_info['user_id']

# Fetch current data
doctor = DatabaseOperations.execute_query(
    "SELECT * FROM doctors WHERE doctor_id = %s",
    (doctor_id,),
    fetch_one=True
)
if not doctor:
    headers.append("Location: doctor_login.py")
    for h in headers:
        print(h)
    print()
    sys.exit()

# Get specialties for dropdown
specialties = DatabaseOperations.execute_query(
    "SELECT * FROM specialties ORDER BY specialty_name",
    fetch_all=True
) or []

form = cgi.FieldStorage()
action = form.getvalue('action', '')
errors = []
success = False

if action == 'update':
    # Get form values
    full_name = form.getvalue('full_name', '').strip()
    email = form.getvalue('email', '').strip()
    phone = form.getvalue('phone', '').strip()
    specialty = form.getvalue('specialty', '').strip()
    qualification = form.getvalue('qualification', '').strip()
    experience_years = form.getvalue('experience_years', '0').strip()
    consultation_fee = form.getvalue('consultation_fee', '0').strip()
    available_from = form.getvalue('available_from', doctor['available_from'])
    available_to = form.getvalue('available_to', doctor['available_to'])

    # Validation
    if not full_name:
        errors.append("Full name is required")
    if not email:
        errors.append("Email is required")
    if not phone:
        errors.append("Phone number is required")
    if not specialty:
        errors.append("Specialty is required")

    # Email uniqueness check (excluding current doctor)
    if not errors:
        check = DatabaseOperations.execute_query(
            "SELECT doctor_id FROM doctors WHERE email = %s AND doctor_id != %s",
            (email, doctor_id),
            fetch_one=True
        )
        if check:
            errors.append("Email already used by another doctor")

    if not errors:
        try:
            DatabaseOperations.execute_query(
                """UPDATE doctors SET
                    full_name = %s, email = %s, phone = %s,
                    specialty = %s, qualification = %s,
                    experience_years = %s, consultation_fee = %s,
                    available_from = %s, available_to = %s,
                    updated_at = NOW()
                   WHERE doctor_id = %s""",
                (
                    full_name, email, phone, specialty, qualification,
                    int(experience_years) if experience_years else 0,
                    float(consultation_fee) if consultation_fee else 0.00,
                    available_from, available_to,
                    doctor_id
                )
            )
            success = True
            # Update session name
            session.set('full_name', full_name)
            doctor['full_name'] = full_name
            doctor['email'] = email
            doctor['phone'] = phone
            doctor['specialty'] = specialty
            doctor['qualification'] = qualification
            doctor['experience_years'] = experience_years
            doctor['consultation_fee'] = consultation_fee
            doctor['available_from'] = available_from
            doctor['available_to'] = available_to
        except Exception as e:
            errors.append(f"Update failed: {e}")

headers.append("Content-Type: text/html; charset=utf-8")
for hdr in headers:
    print(hdr)
print()

def h(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

print(f"""<!DOCTYPE html>
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
        }}
        body {{ font-family: 'Inter', sans-serif; background: #f4f6f9; }}
        .navbar {{ background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .edit-container {{ max-width: 800px; margin: 100px auto 50px; }}
        .card {{ border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light fixed-top">
        <div class="container">
            <a class="navbar-brand" href="index.py"><i class="fas fa-clinic-medical me-2 text-primary"></i>ClinicCare</a>
            <div class="ms-auto">
                <a href="doctor_profile.py" class="btn btn-outline-primary btn-sm me-2"><i class="fas fa-arrow-left"></i> Cancel</a>
                <a href="logout.py" class="btn btn-outline-danger btn-sm">Logout</a>
            </div>
        </div>
    </nav>

    <div class="edit-container">
        <div class="card">
            <div class="card-header bg-white">
                <h4 class="mb-0"><i class="fas fa-edit me-2 text-primary"></i>Edit Profile</h4>
            </div>
            <div class="card-body">
""")

if success:
    print('<div class="alert alert-success">Profile updated successfully! <a href="doctor_profile.py">View Profile</a></div>')

if errors:
    print('<div class="alert alert-danger"><ul class="mb-0">')
    for e in errors:
        print(f'<li>{h(e)}</li>')
    print('</ul></div>')

print(f"""
                <form method="post" action="doctor_edit_profile.py">
                    <input type="hidden" name="action" value="update">

                    <div class="mb-3">
                        <label class="form-label">License Number</label>
                        <input type="text" class="form-control" value="{h(doctor['license_number'])}" readonly>
                    </div>

                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Full Name *</label>
                            <input type="text" class="form-control" name="full_name" value="{h(doctor['full_name'])}" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Email *</label>
                            <input type="email" class="form-control" name="email" value="{h(doctor['email'])}" required>
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Phone *</label>
                            <input type="tel" class="form-control" name="phone" value="{h(doctor['phone'])}" pattern="\\+254[0-9]{{9}}" required>
                            <small class="text-muted">Format: +254XXXXXXXXX</small>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Specialty *</label>
                            <select class="form-select" name="specialty" required>
                                <option value="">Select</option>
""")
for spec in specialties:
    selected = 'selected' if doctor['specialty'] == spec['specialty_name'] else ''
    print(f'<option value="{h(spec["specialty_name"])}" {selected}>{h(spec["specialty_name"])}</option>')
print(f"""
                            </select>
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Qualification</label>
                            <input type="text" class="form-control" name="qualification" value="{h(doctor['qualification'] or '')}">
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Experience (years)</label>
                            <input type="number" class="form-control" name="experience_years" value="{h(doctor['experience_years'] or 0)}" min="0">
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Consultation Fee (KES)</label>
                            <input type="number" class="form-control" name="consultation_fee" value="{h(doctor['consultation_fee'] or 0)}" min="0" step="100">
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Available From</label>
                            <input type="time" class="form-control" name="available_from" value="{h(doctor['available_from'])}">
                        </div>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Available To</label>
                        <input type="time" class="form-control" name="available_to" value="{h(doctor['available_to'])}">
                    </div>

                    <hr>
                    <div class="text-end">
                        <a href="doctor_profile.py" class="btn btn-secondary me-2">Cancel</a>
                        <button type="submit" class="btn btn-primary">Save Changes</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
""")