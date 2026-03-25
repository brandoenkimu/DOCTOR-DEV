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

from database import DatabaseOperations
from admin_session import AdminSession

session = AdminSession()
session.start_session()

if not session.is_logged_in():
    print("Location: admin_login.py")
    print()
    sys.exit()

admin_info = session.get_admin_info()

# Get doctor ID from query string
form = cgi.FieldStorage()
doctor_id = form.getvalue('id', '')
if not doctor_id:
    print("Location: admin_doctors.py")
    print()
    sys.exit()

# Fetch doctor data
doctor = DatabaseOperations.execute_query(
    "SELECT * FROM doctors WHERE doctor_id = %s",
    (doctor_id,),
    fetch_one=True
)
if not doctor:
    print("Location: admin_doctors.py")
    print()
    sys.exit()

# Get specialties for dropdown
specialties = DatabaseOperations.execute_query(
    "SELECT * FROM specialties ORDER BY specialty_name",
    fetch_all=True
) or []

# Process form submission
action = form.getvalue('action', '')
errors = []
success = False

if action == 'update':
    # Get submitted values
    full_name = form.getvalue('full_name', '').strip()
    email = form.getvalue('email', '').strip()
    phone = form.getvalue('phone', '').strip()
    specialty = form.getvalue('specialty', '').strip()
    qualification = form.getvalue('qualification', '').strip()
    experience_years = form.getvalue('experience_years', '0').strip()
    consultation_fee = form.getvalue('consultation_fee', '0').strip()
    available_from = form.getvalue('available_from', '09:00')
    available_to = form.getvalue('available_to', '17:00')
    is_active = form.getvalue('is_active', '1')
    # Password reset fields
    reset_password = form.getvalue('reset_password', '')
    new_password = form.getvalue('new_password', '').strip()

    # Validation
    if not full_name:
        errors.append("Full name is required")
    if not email:
        errors.append("Email is required")
    if not phone:
        errors.append("Phone number is required")
    if not specialty:
        errors.append("Specialty is required")

    # Check email uniqueness (excluding current doctor)
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
            # Build update query
            query = """
                UPDATE doctors SET
                    full_name = %s,
                    email = %s,
                    phone = %s,
                    specialty = %s,
                    qualification = %s,
                    experience_years = %s,
                    consultation_fee = %s,
                    available_from = %s,
                    available_to = %s,
                    is_active = %s,
                    updated_at = NOW()
            """
            params = [
                full_name,
                email,
                phone,
                specialty,
                qualification,
                int(experience_years) if experience_years else 0,
                float(consultation_fee) if consultation_fee else 0.00,
                available_from,
                available_to,
                1 if is_active == '1' else 0
            ]

            # Handle password reset
            if reset_password == 'on' and new_password:
                hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                query += ", password_hash = %s"
                params.append(hashed)

            query += " WHERE doctor_id = %s"
            params.append(doctor_id)

            DatabaseOperations.execute_query(query, tuple(params))
            success = True
            # Refresh doctor data
            doctor = DatabaseOperations.execute_query(
                "SELECT * FROM doctors WHERE doctor_id = %s",
                (doctor_id,),
                fetch_one=True
            )
        except Exception as e:
            errors.append(f"Update failed: {str(e)}")

# Output headers
print("Content-Type: text/html; charset=utf-8")
print()

def h(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

# HTML starts
print(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Doctor - Clinic Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary: #2A5C82;
            --secondary: #4A90E2;
            --success: #50C878;
            --danger: #FF6B6B;
            --dark: #2C3E50;
        }}
        body {{ font-family: 'Inter', sans-serif; background: #f4f6f9; }}
        .sidebar {{ position: fixed; width: 260px; height: 100vh; background: linear-gradient(135deg, var(--dark), var(--primary)); color: white; padding: 20px; }}
        .sidebar-logo {{ text-align: center; padding: 20px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        .sidebar-menu a {{ color: rgba(255,255,255,0.8); text-decoration: none; padding: 12px 15px; display: block; }}
        .sidebar-menu a:hover, .sidebar-menu a.active {{ background: rgba(255,255,255,0.1); color: white; }}
        .main-content {{ margin-left: 260px; padding: 20px 30px; }}
        .top-bar {{ background: white; border-radius: 15px; padding: 15px 25px; margin-bottom: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .form-container {{ background: white; border-radius: 20px; padding: 30px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }}
        .form-header {{ border-bottom: 2px solid #f0f0f0; padding-bottom: 20px; margin-bottom: 30px; }}
        .btn-save {{ background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; border: none; }}
        .btn-cancel {{ background: #f8f9fa; border: 2px solid #e0e0e0; color: #666; margin-right: 10px; }}
        .alert {{ border-radius: 10px; }}
        .password-section {{ background: #f8f9fa; border-radius: 15px; padding: 20px; margin-top: 20px; }}
    </style>
</head>
<body>
    <!-- Sidebar -->
    <div class="sidebar">
        <div class="sidebar-logo">
            <i class="fas fa-clinic-medical fa-3x"></i>
            <h3>ClinicCare</h3>
        </div>
        <ul class="sidebar-menu">
            <li><a href="admin_dashboard.py"><i class="fas fa-tachometer-alt"></i> Dashboard</a></li>
            <li><a href="admin_doctors.py" class="active"><i class="fas fa-user-md"></i> Doctors</a></li>
            <li><a href="admin_logout.py"><i class="fas fa-sign-out-alt"></i> Logout</a></li>
        </ul>
    </div>

    <div class="main-content">
        <div class="top-bar d-flex justify-content-between align-items-center">
            <h4 class="mb-0"><i class="fas fa-edit me-2 text-primary"></i>Edit Doctor</h4>
            <span>Welcome, {h(admin_info['full_name'])}</span>
        </div>

        <div class="form-container">
            <div class="form-header">
                <h5 class="mb-0"><i class="fas fa-user-md me-2 text-primary"></i>Doctor Information</h5>
            </div>

""")

if success:
    print('<div class="alert alert-success">Doctor updated successfully! <a href="admin_doctors.py" class="alert-link">Back to list</a></div>')

if errors:
    print('<div class="alert alert-danger"><ul class="mb-0">')
    for e in errors:
        print(f'<li>{h(e)}</li>')
    print('</ul></div>')

print(f"""
            <form method="post" action="admin_edit_doctor.py">
                <input type="hidden" name="action" value="update">
                <input type="hidden" name="id" value="{h(doctor_id)}">

                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">License Number</label>
                        <input type="text" class="form-control" value="{h(doctor['license_number'])}" readonly>
                        <small class="text-muted">License number cannot be changed.</small>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Full Name *</label>
                        <input type="text" class="form-control" name="full_name" value="{h(doctor['full_name'])}" required>
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Email *</label>
                        <input type="email" class="form-control" name="email" value="{h(doctor['email'])}" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Phone *</label>
                        <input type="tel" class="form-control" name="phone" value="{h(doctor['phone'])}" pattern="\\+254[0-9]{{9}}" required>
                        <small class="text-muted">Format: +254XXXXXXXXX</small>
                    </div>
                </div>

                <div class="row">
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
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Qualification</label>
                        <input type="text" class="form-control" name="qualification" value="{h(doctor['qualification'] or '')}">
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-3 mb-3">
                        <label class="form-label">Experience (years)</label>
                        <input type="number" class="form-control" name="experience_years" value="{h(doctor['experience_years'] or 0)}" min="0">
                    </div>
                    <div class="col-md-3 mb-3">
                        <label class="form-label">Consultation Fee (KES)</label>
                        <input type="number" class="form-control" name="consultation_fee" value="{h(doctor['consultation_fee'] or 0)}" min="0" step="100">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Status</label>
                        <div class="form-check form-switch">
                            <input class="form-check-input" type="checkbox" name="is_active" value="1" {'checked' if doctor['is_active'] else ''}>
                            <label class="form-check-label">Active</label>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Available From</label>
                        <input type="time" class="form-control" name="available_from" value="{h(doctor['available_from'])}">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Available To</label>
                        <input type="time" class="form-control" name="available_to" value="{h(doctor['available_to'])}">
                    </div>
                </div>

                <!-- Password reset section -->
                <div class="password-section">
                    <h6><i class="fas fa-key me-2"></i>Reset Password</h6>
                    <div class="form-check mb-3">
                        <input class="form-check-input" type="checkbox" name="reset_password" id="resetCheck">
                        <label class="form-check-label" for="resetCheck">Reset password</label>
                    </div>
                    <div id="passwordFields" style="display: none;">
                        <label class="form-label">New Password</label>
                        <input type="text" class="form-control" name="new_password" placeholder="Enter new password">
                        <small class="text-muted">Leave blank to keep current password.</small>
                    </div>
                </div>

                <hr>
                <div class="text-end">
                    <a href="admin_doctors.py" class="btn btn-cancel">Cancel</a>
                    <button type="submit" class="btn btn-save">Update Doctor</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        // Toggle password fields
        document.getElementById('resetCheck').addEventListener('change', function() {{
            document.getElementById('passwordFields').style.display = this.checked ? 'block' : 'none';
        }});
    </script>
</body>
</html>
""")