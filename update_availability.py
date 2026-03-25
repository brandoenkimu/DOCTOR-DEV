#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Update Availability Module – lets doctor change working hours
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
if cookie:
    headers.append(cookie)

if not session.is_logged_in() or session.get('user_type') != 'doctor':
    headers.append("Location: doctor_login.py")
    for h in headers: print(h); print()
    sys.exit()

doctor_info = session.get_user_info()
doctor_id = doctor_info['user_id']

form = cgi.FieldStorage()
action = form.getvalue('action', '')
message = ''
error = ''

# Fetch current availability
doctor = DatabaseOperations.get_doctor_by_id(doctor_id)
current_from = doctor['available_from'] if doctor and doctor.get('available_from') else '09:00'
current_to = doctor['available_to'] if doctor and doctor.get('available_to') else '17:00'

if action == 'update':
    new_from = form.getvalue('available_from', '').strip()
    new_to = form.getvalue('available_to', '').strip()
    if not new_from or not new_to:
        error = "Both start and end times are required."
    else:
        try:
            # simple validation – could add more
            DatabaseOperations.execute_query(
                "UPDATE doctors SET available_from = %s, available_to = %s WHERE doctor_id = %s",
                (new_from, new_to, doctor_id)
            )
            message = "Availability updated successfully."
            current_from, current_to = new_from, new_to
        except Exception as e:
            error = f"Database error: {e}"

headers.append("Content-Type: text/html; charset=utf-8")
for h in headers:
    print(h)
print()

def h(s): return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;').replace("'",'&#39;')

print(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Update Availability - Clinic Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary: #2A5C82; --secondary: #4A90E2;
        }}
        body {{ font-family: 'Inter', sans-serif; background: #f4f6f9; }}
        .navbar {{ background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .container {{ max-width: 600px; margin-top: 100px; }}
        .card {{ border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
        .btn-primary {{ background: linear-gradient(135deg, var(--primary), var(--secondary)); border: none; }}
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
                <h4 class="mb-0"><i class="fas fa-clock me-2"></i>Update Working Hours</h4>
            </div>
            <div class="card-body">
""")
if message:
    print(f'<div class="alert alert-success">{h(message)}</div>')
if error:
    print(f'<div class="alert alert-danger">{h(error)}</div>')
print(f"""
                <form method="post">
                    <input type="hidden" name="action" value="update">
                    <div class="mb-3">
                        <label class="form-label">Available From</label>
                        <input type="time" class="form-control" name="available_from" value="{h(current_from)}" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Available To</label>
                        <input type="time" class="form-control" name="available_to" value="{h(current_to)}" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100"><i class="fas fa-save me-2"></i>Update</button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
""")