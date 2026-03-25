#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Full Schedule Module – displays all appointments for the doctor
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
filter_date = form.getvalue('date', '')

# Get all appointments for this doctor
query = """
    SELECT a.*, p.full_name as patient_name, p.phone, p.reg_number
    FROM appointments a
    JOIN patients p ON a.patient_id = p.patient_id
    WHERE a.doctor_id = %s
"""
params = [doctor_id]
if filter_date:
    query += " AND a.appointment_date = %s"
    params.append(filter_date)
query += " ORDER BY a.appointment_date DESC, a.appointment_time DESC"

appointments = DatabaseOperations.execute_query(query, tuple(params), fetch_all=True) or []

headers.append("Content-Type: text/html; charset=utf-8")
for h in headers: print(h)
print()

def h(s): return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;').replace("'",'&#39;')

print(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Full Schedule - Clinic Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{ --primary: #2A5C82; --secondary: #4A90E2; }}
        body {{ font-family: 'Inter', sans-serif; background: #f4f6f9; }}
        .navbar {{ background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .container {{ margin-top: 100px; }}
        .card {{ border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .badge-scheduled {{ background: #fff3cd; color: #856404; }}
        .badge-completed {{ background: #d4edda; color: #155724; }}
        .badge-cancelled {{ background: #f8d7da; color: #721c24; }}
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
            <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                <h4 class="mb-0"><i class="fas fa-calendar-alt me-2"></i>Full Schedule</h4>
                <form method="get" class="d-flex">
                    <input type="date" name="date" class="form-control form-control-sm me-2" value="{h(filter_date)}">
                    <button type="submit" class="btn btn-light btn-sm"><i class="fas fa-filter"></i> Filter</button>
                </form>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Time</th>
                                <th>Patient</th>
                                <th>Reg No</th>
                                <th>Phone</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
""")
if appointments:
    for apt in appointments:
        status_class = "badge-" + apt['status'].lower().replace(' ', '-')
        print(f"""
                            <tr>
                                <td>{apt['appointment_date']}</td>
                                <td>{apt['appointment_time']}</td>
                                <td>{h(apt['patient_name'])}</td>
                                <td>{h(apt['reg_number'])}</td>
                                <td>{h(apt['phone'])}</td>
                                <td><span class="badge {status_class}">{apt['status']}</span></td>
                                <td>
                                    <a href="appointment_details.py?id={apt['appointment_id']}" class="btn btn-sm btn-outline-info"><i class="fas fa-eye"></i></a>
                                </td>
                            </tr>
        """)
else:
    print('<tr><td colspan="7" class="text-center">No appointments found.</td></tr>')
print("""
                        </tbody>
                    </table>
                </div>
                <div class="text-end mt-3">
                    <a href="export_report.py" class="btn btn-success"><i class="fas fa-download me-2"></i>Export CSV</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
""")