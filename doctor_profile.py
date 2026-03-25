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

# Fetch doctor details
doctor = DatabaseOperations.execute_query(
    "SELECT * FROM doctors WHERE doctor_id = %s",
    (doctor_id,),
    fetch_one=True
)

if not doctor:
    # Something went wrong – log out
    session.logout()
    headers.append("Location: doctor_login.py")
    for h in headers:
        print(h)
    print()
    sys.exit()

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
    <title>Doctor Profile - Clinic Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary: #2A5C82;
            --secondary: #4A90E2;
            --dark: #2C3E50;
        }}
        body {{ font-family: 'Inter', sans-serif; background: #f4f6f9; }}
        .navbar {{ background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .profile-container {{ max-width: 900px; margin: 100px auto 50px; padding: 0 20px; }}
        .card {{ border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
        .profile-header {{ background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; border-radius: 20px 20px 0 0; padding: 30px; }}
        .profile-avatar {{
            width: 80px; height: 80px; background: white; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            color: var(--primary); font-size: 2.5rem; font-weight: bold;
            margin-bottom: 15px;
        }}
        .info-label {{ font-weight: 600; color: var(--dark); width: 150px; }}
        .btn-edit {{ background: white; color: var(--primary); border: 2px solid white; }}
        .btn-edit:hover {{ background: transparent; color: white; }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light fixed-top">
        <div class="container">
            <a class="navbar-brand" href="index.py"><i class="fas fa-clinic-medical me-2 text-primary"></i>ClinicCare</a>
            <div class="ms-auto">
                <a href="doctor_dashboard.py" class="btn btn-outline-primary btn-sm me-2"><i class="fas fa-arrow-left"></i> Dashboard</a>
                <a href="logout.py" class="btn btn-outline-danger btn-sm">Logout</a>
            </div>
        </div>
    </nav>

    <div class="profile-container">
        <div class="card">
            <div class="profile-header">
                <div class="d-flex align-items-center">
                    <div class="profile-avatar me-4">{h(doctor['full_name'][0])}</div>
                    <div>
                        <h2 class="mb-1">Dr. {h(doctor['full_name'])}</h2>
                        <p class="mb-0"><i class="fas fa-id-card me-2"></i>{h(doctor['license_number'])}</p>
                    </div>
                    <div class="ms-auto">
                        <a href="doctor_edit_profile.py" class="btn btn-edit"><i class="fas fa-edit me-2"></i>Edit</a>
                    </div>
                </div>
            </div>
            <div class="card-body p-4">
                <div class="row">
                    <div class="col-md-6">
                        <h5 class="mb-3"><i class="fas fa-address-card me-2 text-primary"></i>Personal Information</h5>
                        <table class="table table-borderless">
                            <tr><td class="info-label">Full Name:</td><td>{h(doctor['full_name'])}</td></tr>
                            <tr><td class="info-label">Email:</td><td>{h(doctor['email'])}</td></tr>
                            <tr><td class="info-label">Phone:</td><td>{h(doctor['phone'])}</td></tr>
                            <tr><td class="info-label">License:</td><td>{h(doctor['license_number'])}</td></tr>
                        </table>
                    </div>
                    <div class="col-md-6">
                        <h5 class="mb-3"><i class="fas fa-briefcase me-2 text-primary"></i>Professional Details</h5>
                        <table class="table table-borderless">
                            <tr><td class="info-label">Specialty:</td><td>{h(doctor['specialty'])}</td></tr>
                            <tr><td class="info-label">Qualification:</td><td>{h(doctor['qualification'] or 'Not provided')}</td></tr>
                            <tr><td class="info-label">Experience:</td><td>{h(doctor['experience_years'] or 0)} years</td></tr>
                            <tr><td class="info-label">Consultation Fee:</td><td>KES {h(doctor['consultation_fee'] or 0)}</td></tr>
                        </table>
                    </div>
                </div>
                <hr>
                <div class="row">
                    <div class="col-md-6">
                        <h5 class="mb-3"><i class="fas fa-clock me-2 text-primary"></i>Working Hours</h5>
                        <p><strong>From:</strong> {h(doctor['available_from'])}  <strong>To:</strong> {h(doctor['available_to'])}</p>
                    </div>
                    <div class="col-md-6">
                        <h5 class="mb-3"><i class="fas fa-calendar-alt me-2 text-primary"></i>Account Info</h5>
                        <p><strong>Member since:</strong> {h(doctor['created_at'])}</p>
                        <p><strong>Status:</strong> <span class="badge bg-{'success' if doctor['is_active'] else 'danger'}">{'Active' if doctor['is_active'] else 'Inactive'}</span></p>
                    </div>
                </div>
                <div class="text-end mt-4">
                    <a href="doctor_change_password.py" class="btn btn-outline-primary"><i class="fas fa-key"></i> Change Password</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
""")