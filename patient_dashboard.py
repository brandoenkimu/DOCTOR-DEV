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

# --- Header collection ---
headers = []

session = SessionManager()
session.start_session()

# Get cookie header
cookie_header = session.get_cookie_header()
if cookie_header:
    headers.append(cookie_header)

if not session.is_logged_in() or session.get('user_type') != 'patient':
    headers.append("Location: patient_login.py")
    for h in headers:
        print(h)
    print()
    sys.exit()

patient_info = session.get_user_info()
patient_id = patient_info['user_id']

# Get upcoming appointments
upcoming = DatabaseOperations.execute_query(
    """SELECT a.*, d.full_name as doctor_name, d.specialty
       FROM appointments a
       JOIN doctors d ON a.doctor_id = d.doctor_id
       WHERE a.patient_id = %s AND a.appointment_date >= CURDATE() AND a.status = 'Scheduled'
       ORDER BY a.appointment_date, a.appointment_time
       LIMIT 5""",
    (patient_id,),
    fetch_all=True
) or []

# Get recent activity
recent = DatabaseOperations.execute_query(
    """SELECT a.*, d.full_name as doctor_name
       FROM appointments a
       JOIN doctors d ON a.doctor_id = d.doctor_id
       WHERE a.patient_id = %s
       ORDER BY a.appointment_date DESC
       LIMIT 5""",
    (patient_id,),
    fetch_all=True
) or []

# Helper function to generate appointment list HTML
def generate_appointment_list(appointments, empty_message):
    if not appointments:
        return f'<p class="text-muted">{empty_message}</p>'
    html = '<ul class="list-group">'
    for a in appointments:
        html += f'<li class="list-group-item d-flex justify-content-between align-items-center">{a["appointment_date"]} {a["appointment_time"]} - Dr. {a["doctor_name"]} <span class="badge bg-primary">{a["status"]}</span></li>'
    html += '</ul>'
    return html

# Add content type header
headers.append("Content-Type: text/html; charset=utf-8")

# Print all headers
for h in headers:
    print(h)
print()

# HTML starts here
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Patient Dashboard - Clinic Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary: #2A5C82;
            --secondary: #4A90E2;
        }}
        body {{ font-family: 'Inter', sans-serif; background: #f4f6f9; }}
        .navbar {{ background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .dashboard {{ max-width: 1200px; margin: 100px auto 50px; padding: 0 20px; }}
        .welcome-card {{ background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; border-radius: 20px; padding: 30px; margin-bottom: 30px; }}
        .card {{ border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .quick-action {{ background: white; border-radius: 10px; padding: 20px; text-align: center; transition: 0.3s; }}
        .quick-action:hover {{ transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light fixed-top">
        <div class="container">
            <a class="navbar-brand" href="index.py"><i class="fas fa-clinic-medical me-2 text-primary"></i>ClinicCare</a>
            <div class="ms-auto d-flex align-items-center">
                <span class="me-3"><i class="fas fa-user me-2"></i>{patient_info['full_name']}</span>
                <a href="patient_profile.py" class="btn btn-outline-primary btn-sm me-2">Profile</a>
                <a href="logout.py" class="btn btn-outline-danger btn-sm">Logout</a>
            </div>
        </div>
    </nav>
    
    <div class="dashboard">
        <div class="welcome-card">
            <h2>Welcome back, {patient_info['full_name']}!</h2>
            <p>Manage your appointments and health records</p>
        </div>
        
        <div class="row">
            <div class="col-md-3">
                <a href="book_appointment.py" class="text-decoration-none">
                    <div class="quick-action">
                        <i class="fas fa-calendar-plus fa-3x text-primary mb-3"></i>
                        <h5>Book Appointment</h5>
                    </div>
                </a>
            </div>
            <div class="col-md-3">
                <a href="my_appointments.py" class="text-decoration-none">
                    <div class="quick-action">
                        <i class="fas fa-list fa-3x text-primary mb-3"></i>
                        <h5>My Appointments</h5>
                    </div>
                </a>
            </div>
            <div class="col-md-3">
                <a href="patient_profile.py" class="text-decoration-none">
                    <div class="quick-action">
                        <i class="fas fa-user-circle fa-3x text-primary mb-3"></i>
                        <h5>My Profile</h5>
                    </div>
                </a>
            </div>
            <div class="col-md-3">
                <a href="patient_change_password.py" class="text-decoration-none">
                    <div class="quick-action">
                        <i class="fas fa-key fa-3x text-primary mb-3"></i>
                        <h5>Change Password</h5>
                    </div>
                </a>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header bg-white">
                        <h5 class="mb-0"><i class="fas fa-clock me-2 text-primary"></i>Upcoming Appointments</h5>
                    </div>
                    <div class="card-body">
                        {generate_appointment_list(upcoming, 'No upcoming appointments.')}
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header bg-white">
                        <h5 class="mb-0"><i class="fas fa-history me-2 text-primary"></i>Recent Activity</h5>
                    </div>
                    <div class="card-body">
                        {generate_appointment_list(recent, 'No recent activity.')}
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
""")