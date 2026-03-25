#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Admin Edit Appointment – allows admin to modify appointment details.
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

session = AdminSession()
session.start_session()

if not session.is_logged_in():
    print("Location: admin_login.py")
    print()
    sys.exit()

admin_info = session.get_admin_info()

form = cgi.FieldStorage()
appointment_id = form.getvalue('id', '')
action = form.getvalue('action', '')

if not appointment_id:
    print("Location: admin_appointments.py")
    print()
    sys.exit()

# Fetch current appointment data
appointment = DatabaseOperations.execute_query("""
    SELECT a.*, p.patient_id, d.doctor_id
    FROM appointments a
    JOIN patients p ON a.patient_id = p.patient_id
    JOIN doctors d ON a.doctor_id = d.doctor_id
    WHERE a.appointment_id = %s
""", (appointment_id,), fetch_one=True)

if not appointment:
    print("Location: admin_appointments.py")
    print()
    sys.exit()

message = ''
error = ''

if action == 'update':
    # Get form values
    new_date = form.getvalue('appointment_date', appointment['appointment_date'])
    new_time = form.getvalue('appointment_time', appointment['appointment_time'])
    new_status = form.getvalue('status', appointment['status'])
    new_symptoms = form.getvalue('symptoms', appointment['symptoms'] or '')

    # Basic validation
    try:
        datetime.strptime(new_date, '%Y-%m-%d')
        datetime.strptime(new_time, '%H:%M:%S')
        # Update database
        DatabaseOperations.execute_query(
            """UPDATE appointments SET appointment_date = %s, appointment_time = %s,
               status = %s, symptoms = %s WHERE appointment_id = %s""",
            (new_date, new_time, new_status, new_symptoms, appointment_id)
        )
        message = "Appointment updated successfully."
        # Refresh appointment data
        appointment['appointment_date'] = new_date
        appointment['appointment_time'] = new_time
        appointment['status'] = new_status
        appointment['symptoms'] = new_symptoms
    except ValueError:
        error = "Invalid date or time format."

# Output page
print("Content-Type: text/html; charset=utf-8")
print()

def h(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

print(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Appointment - Clinic Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {{ font-family: 'Inter', sans-serif; background: #f4f6f9; }}
        .sidebar {{ position: fixed; width: 260px; height: 100vh; background: linear-gradient(135deg, #2C3E50, #2A5C82); color: white; padding: 20px; }}
        .main-content {{ margin-left: 260px; padding: 20px 30px; }}
        .top-bar {{ background: white; border-radius: 15px; padding: 15px 25px; margin-bottom: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .card-custom {{ background: white; border-radius: 20px; padding: 25px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }}
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
            <h4 class="mb-0"><i class="fas fa-edit me-2 text-primary"></i>Edit Appointment #{h(appointment_id)}</h4>
        </div>
        
        <div class="card-custom">
""")

if message:
    print(f'<div class="alert alert-success">{h(message)}</div>')
if error:
    print(f'<div class="alert alert-danger">{h(error)}</div>')

print(f"""
            <form method="post" action="admin_edit_appointment.py">
                <input type="hidden" name="action" value="update">
                <input type="hidden" name="id" value="{h(appointment_id)}">
                <div class="mb-3">
                    <label class="form-label">Appointment Date</label>
                    <input type="date" class="form-control" name="appointment_date" value="{h(appointment['appointment_date'])}" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Appointment Time</label>
                    <input type="time" class="form-control" name="appointment_time" value="{h(appointment['appointment_time'])}" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Status</label>
                    <select class="form-select" name="status">
                        <option value="Scheduled" {'selected' if appointment['status']=='Scheduled' else ''}>Scheduled</option>
                        <option value="Completed" {'selected' if appointment['status']=='Completed' else ''}>Completed</option>
                        <option value="Cancelled" {'selected' if appointment['status']=='Cancelled' else ''}>Cancelled</option>
                        <option value="No-Show" {'selected' if appointment['status']=='No-Show' else ''}>No-Show</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">Symptoms / Notes</label>
                    <textarea class="form-control" name="symptoms" rows="3">{h(appointment['symptoms'] or '')}</textarea>
                </div>
                <button type="submit" class="btn btn-primary">Update Appointment</button>
                <a href="admin_view_appointment.py?id={h(appointment_id)}" class="btn btn-secondary">Cancel</a>
            </form>
        </div>
    </div>
</body>
</html>
""")