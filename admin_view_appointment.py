#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Admin View Appointment – shows full details of any appointment (admin only).
"""

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

from admin_session import AdminSession
from database import DatabaseOperations

# No header collection for cookie – only output after we decide what to send
session = AdminSession()
session.start_session()

if not session.is_logged_in():
    print("Location: admin_login.py")
    print()
    sys.exit()

admin_info = session.get_admin_info()

form = cgi.FieldStorage()
appointment_id = form.getvalue('id', '')

if not appointment_id:
    print("Location: admin_appointments.py")
    print()
    sys.exit()

# Fetch appointment with all related info
appointment = DatabaseOperations.execute_query("""
    SELECT a.*,
           p.full_name AS patient_name, p.phone AS patient_phone, p.email AS patient_email,
           p.date_of_birth, p.blood_group, p.address, p.emergency_contact,
           d.full_name AS doctor_name, d.specialty, d.license_number
    FROM appointments a
    JOIN patients p ON a.patient_id = p.patient_id
    JOIN doctors d ON a.doctor_id = d.doctor_id
    WHERE a.appointment_id = %s
""", (appointment_id,), fetch_one=True)

if not appointment:
    print("Location: admin_appointments.py")
    print()
    sys.exit()

# Now output the page
print("Content-Type: text/html; charset=utf-8")
print()

def h(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

print(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin View Appointment - Clinic Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {{ font-family: 'Inter', sans-serif; background: #f4f6f9; }}
        .sidebar {{ position: fixed; width: 260px; height: 100vh; background: linear-gradient(135deg, #2C3E50, #2A5C82); color: white; padding: 20px; }}
        .main-content {{ margin-left: 260px; padding: 20px 30px; }}
        .top-bar {{ background: white; border-radius: 15px; padding: 15px 25px; margin-bottom: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .card-custom {{ background: white; border-radius: 20px; padding: 25px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }}
        .info-label {{ font-weight: 600; color: #2C3E50; width: 150px; }}
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-logo text-center mb-4">
            <i class="fas fa-clinic-medical fa-3x"></i>
            <h3>ClinicCare</h3>
        </div>
        <ul class="list-unstyled">
            <li><a href="admin_dashboard.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-tachometer-alt me-2"></i>Dashboard</a></li>
            <li><a href="admin_appointments.py" class="text-white text-decoration-none d-block p-2 active"><i class="fas fa-calendar-check me-2"></i>Appointments</a></li>
            <li><a href="admin_logout.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-sign-out-alt me-2"></i>Logout</a></li>
        </ul>
    </div>
    
    <div class="main-content">
        <div class="top-bar">
            <h4 class="mb-0"><i class="fas fa-calendar-check me-2 text-primary"></i>Appointment #{h(appointment_id)}</h4>
        </div>
        
        <div class="card-custom">
            <div class="row">
                <div class="col-md-6">
                    <h5 class="mb-3">Appointment Details</h5>
                    <table class="table table-borderless">
                        <tr><td class="info-label">Date:</td><td>{h(appointment['appointment_date'])}</td></tr>
                        <tr><td class="info-label">Time:</td><td>{h(appointment['appointment_time'])}</td></tr>
                        <tr><td class="info-label">Status:</td><td><span class="badge bg-{'warning' if appointment['status']=='Scheduled' else 'success' if appointment['status']=='Completed' else 'danger'}">{h(appointment['status'])}</span></td></tr>
                        <tr><td class="info-label">Symptoms:</td><td>{h(appointment['symptoms'] or 'None')}</td></tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h5 class="mb-3">Doctor Information</h5>
                    <table class="table table-borderless">
                        <tr><td class="info-label">Name:</td><td>Dr. {h(appointment['doctor_name'])}</td></tr>
                        <tr><td class="info-label">Specialty:</td><td>{h(appointment['specialty'])}</td></tr>
                        <tr><td class="info-label">License:</td><td>{h(appointment['license_number'])}</td></tr>
                    </table>
                </div>
            </div>
            <hr>
            <h5 class="mb-3">Patient Information</h5>
            <div class="row">
                <div class="col-md-6">
                    <table class="table table-borderless">
                        <tr><td class="info-label">Name:</td><td>{h(appointment['patient_name'])}</td></tr>
                        <tr><td class="info-label">Phone:</td><td>{h(appointment['patient_phone'])}</td></tr>
                        <tr><td class="info-label">Email:</td><td>{h(appointment['patient_email'])}</td></tr>
                        <tr><td class="info-label">DOB:</td><td>{h(appointment['date_of_birth'])}</td></tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <table class="table table-borderless">
                        <tr><td class="info-label">Blood Group:</td><td>{h(appointment['blood_group'] or 'N/A')}</td></tr>
                        <tr><td class="info-label">Emergency Contact:</td><td>{h(appointment['emergency_contact'] or 'N/A')}</td></tr>
                        <tr><td class="info-label">Address:</td><td>{h(appointment['address'] or 'N/A')}</td></tr>
                    </table>
                </div>
            </div>
            <div class="text-end mt-4">
                <a href="admin_edit_appointment.py?id={appointment_id}" class="btn btn-primary"><i class="fas fa-edit"></i> Edit</a>
                <a href="admin_appointments.py" class="btn btn-secondary">Back</a>
            </div>
        </div>
    </div>
</body>
</html>
""")