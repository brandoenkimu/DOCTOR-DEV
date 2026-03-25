#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Appointment Details Module
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

from session import SessionManager
from database import DatabaseOperations

headers = []
session = SessionManager()
session.start_session()
cookie = session.get_cookie_header()
if cookie: headers.append(cookie)

if not session.is_logged_in() or session.get('user_type') != 'doctor':
    headers.append("Location: doctor_login.py")
    for h in headers: print(h); print()
    sys.exit()

doctor_info = session.get_user_info()
doctor_id = doctor_info['user_id']

form = cgi.FieldStorage()
apt_id = form.getvalue('id', '')
if not apt_id:
    headers.append("Location: doctor_dashboard.py")
    for h in headers: print(h); print()
    sys.exit()

# Fetch appointment details (ensure it belongs to this doctor)
apt = DatabaseOperations.execute_query(
    """SELECT a.*, p.full_name as patient_name, p.reg_number, p.phone, p.email, p.date_of_birth,
              p.address, p.emergency_contact, p.blood_group
       FROM appointments a
       JOIN patients p ON a.patient_id = p.patient_id
       WHERE a.appointment_id = %s AND a.doctor_id = %s""",
    (apt_id, doctor_id),
    fetch_one=True
)
if not apt:
    headers.append("Location: doctor_dashboard.py")
    for h in headers: print(h); print()
    sys.exit()

# Handle update of diagnosis/prescription
message = ''
if 'update' in form:
    diagnosis = form.getvalue('diagnosis', '')
    prescription = form.getvalue('prescription', '')
    notes = form.getvalue('notes', '')
    try:
        DatabaseOperations.execute_query(
            "UPDATE appointments SET diagnosis=%s, prescription=%s, notes=%s WHERE appointment_id=%s",
            (diagnosis, prescription, notes, apt_id)
        )
        message = '<div class="alert alert-success">Record updated.</div>'
        apt['diagnosis'] = diagnosis
        apt['prescription'] = prescription
        apt['notes'] = notes
    except Exception as e:
        message = f'<div class="alert alert-danger">Error: {e}</div>'

headers.append("Content-Type: text/html; charset=utf-8")
for h in headers: print(h)
print()

def h(s): return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;').replace("'",'&#39;')

print(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Appointment Details - Clinic Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{ --primary: #2A5C82; --secondary: #4A90E2; }}
        body {{ font-family: 'Inter', sans-serif; background: #f4f6f9; }}
        .navbar {{ background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .container {{ margin-top: 100px; }}
        .card {{ border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .info-label {{ font-weight: 600; color: var(--dark); }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light fixed-top">
        <div class="container">
            <a class="navbar-brand" href="index.py"><i class="fas fa-clinic-medical me-2 text-primary"></i>ClinicCare</a>
            <div class="ms-auto">
                <span class="me-3"><i class="fas fa-user-md me-2"></i>Dr. {h(doctor_info['full_name'])}</span>
                <a href="doctor_dashboard.py" class="btn btn-outline-primary btn-sm me-2">Dashboard</a>
                <a href="logout.py" class="btn btn-outline-danger btn-sm">Logout</a>
            </div>
        </div>
    </nav>
    
    <div class="container">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h4 class="mb-0"><i class="fas fa-calendar-check me-2"></i>Appointment #{apt['appointment_id']}</h4>
            </div>
            <div class="card-body">
                {message}
                <div class="row">
                    <div class="col-md-6">
                        <h5>Patient Information</h5>
                        <p><strong>Name:</strong> {h(apt['patient_name'])}</p>
                        <p><strong>Reg No:</strong> {h(apt['reg_number'])}</p>
                        <p><strong>Phone:</strong> {h(apt['phone'])}</p>
                        <p><strong>Email:</strong> {h(apt['email'])}</p>
                        <p><strong>DOB:</strong> {apt['date_of_birth']}</p>
                        <p><strong>Blood Group:</strong> {h(apt['blood_group'] or 'N/A')}</p>
                        <p><strong>Address:</strong> {h(apt['address'] or 'N/A')}</p>
                        <p><strong>Emergency Contact:</strong> {h(apt['emergency_contact'] or 'N/A')}</p>
                    </div>
                    <div class="col-md-6">
                        <h5>Appointment Details</h5>
                        <p><strong>Date:</strong> {apt['appointment_date']}</p>
                        <p><strong>Time:</strong> {apt['appointment_time']} - {apt['end_time']}</p>
                        <p><strong>Status:</strong> {apt['status']}</p>
                        <p><strong>Symptoms:</strong> {h(apt['symptoms'] or 'None')}</p>
                    </div>
                </div>
                <hr>
                <form method="post">
                    <input type="hidden" name="id" value="{apt_id}">
                    <h5>Clinical Notes</h5>
                    <div class="mb-3">
                        <label class="form-label">Diagnosis</label>
                        <textarea class="form-control" name="diagnosis" rows="2">{h(apt['diagnosis'] or '')}</textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Prescription</label>
                        <textarea class="form-control" name="prescription" rows="3">{h(apt['prescription'] or '')}</textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Additional Notes</label>
                        <textarea class="form-control" name="notes" rows="2">{h(apt['notes'] or '')}</textarea>
                    </div>
                    <button type="submit" name="update" value="1" class="btn btn-primary"><i class="fas fa-save me-2"></i>Save Notes</button>
                    <a href="full_schedule.py" class="btn btn-secondary">Back</a>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
""")