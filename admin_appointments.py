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

from database import DatabaseOperations
from admin_session import AdminSession

session = AdminSession()
session.start_session()

if not session.is_logged_in():
    print("Location: admin_login.py")
    print()
    sys.exit()

admin_info = session.get_admin_info()

# Handle filters
form = cgi.FieldStorage()
filter_date = form.getvalue('date', '')
filter_doctor = form.getvalue('doctor_id', '')
filter_status = form.getvalue('status', '')

# Base query with joins
query = """
    SELECT a.*, 
           p.full_name as patient_name, p.reg_number, p.phone as patient_phone,
           d.full_name as doctor_name, d.specialty
    FROM appointments a
    JOIN patients p ON a.patient_id = p.patient_id
    JOIN doctors d ON a.doctor_id = d.doctor_id
    WHERE 1=1
"""
params = []

if filter_date:
    query += " AND DATE(a.appointment_date) = %s"
    params.append(filter_date)
if filter_doctor:
    query += " AND a.doctor_id = %s"
    params.append(filter_doctor)
if filter_status:
    query += " AND a.status = %s"
    params.append(filter_status)

query += " ORDER BY a.appointment_date DESC, a.appointment_time DESC"

appointments = DatabaseOperations.execute_query(query, tuple(params) if params else None, fetch_all=True) or []

# Get doctors for filter dropdown
doctors = DatabaseOperations.execute_query("SELECT doctor_id, full_name FROM doctors ORDER BY full_name", fetch_all=True) or []

print("Content-Type: text/html; charset=utf-8")
print()

today = datetime.now().strftime('%Y-%m-%d')
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manage Appointments - Clinic Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary: #2A5C82;
            --secondary: #4A90E2;
            --success: #50C878;
            --danger: #FF6B6B;
            --warning: #FFD93D;
            --dark: #2C3E50;
        }}
        body {{ font-family: 'Inter', sans-serif; background: #f4f6f9; }}
        .sidebar {{ position: fixed; width: 260px; height: 100vh; background: linear-gradient(135deg, var(--dark) 0%, var(--primary) 100%); color: white; padding: 20px; }}
        .main-content {{ margin-left: 260px; padding: 20px 30px; }}
        .top-bar {{ background: white; border-radius: 15px; padding: 15px 25px; margin-bottom: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .filter-card {{ background: white; border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .table-card {{ background: white; border-radius: 15px; padding: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .status-badge {{
            padding: 5px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600;
        }}
        .status-Scheduled {{ background: #cce5ff; color: #004085; }}
        .status-Completed {{ background: #d4edda; color: #155724; }}
        .status-Cancelled {{ background: #f8d7da; color: #721c24; }}
        .status-No-Show {{ background: #fff3cd; color: #856404; }}
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
            <li><a href="admin_doctors.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-user-md me-2"></i>Doctors</a></li>
            <li><a href="admin_patients.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-users me-2"></i>Patients</a></li>
            <li><a href="admin_appointments.py" class="text-white text-decoration-none d-block p-2 active"><i class="fas fa-calendar-check me-2"></i>Appointments</a></li>
            <li><a href="admin_specialties.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-stethoscope me-2"></i>Specialties</a></li>
            <li><a href="admin_reports.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-chart-bar me-2"></i>Reports</a></li>
            <li><a href="admin_settings.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-cog me-2"></i>Settings</a></li>
            <li><hr class="bg-white opacity-25"></li>
            <li><a href="admin_logout.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-sign-out-alt me-2"></i>Logout</a></li>
        </ul>
    </div>
    
    <div class="main-content">
        <div class="top-bar">
            <h4 class="mb-0"><i class="fas fa-calendar-check me-2 text-primary"></i>Manage Appointments</h4>
        </div>
        
        <div class="filter-card">
            <form method="get" class="row g-3">
                <div class="col-md-3">
                    <label class="form-label">Date</label>
                    <input type="date" name="date" class="form-control" value="{filter_date}">
                </div>
                <div class="col-md-3">
                    <label class="form-label">Doctor</label>
                    <select name="doctor_id" class="form-select">
                        <option value="">All Doctors</option>
""")
for d in doctors:
    selected = 'selected' if str(d['doctor_id']) == filter_doctor else ''
    print(f'<option value="{d["doctor_id"]}" {selected}>{d["full_name"]}</option>')
print(f"""
                    </select>
                </div>
                <div class="col-md-3">
                    <label class="form-label">Status</label>
                    <select name="status" class="form-select">
                        <option value="">All Status</option>
                        <option value="Scheduled" {'selected' if filter_status=='Scheduled' else ''}>Scheduled</option>
                        <option value="Completed" {'selected' if filter_status=='Completed' else ''}>Completed</option>
                        <option value="Cancelled" {'selected' if filter_status=='Cancelled' else ''}>Cancelled</option>
                        <option value="No-Show" {'selected' if filter_status=='No-Show' else ''}>No-Show</option>
                    </select>
                </div>
                <div class="col-md-3 d-flex align-items-end">
                    <button type="submit" class="btn btn-primary-custom w-100"><i class="fas fa-filter me-2"></i>Apply Filters</button>
                </div>
            </form>
        </div>
        
        <div class="table-card">
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Date</th>
                            <th>Time</th>
                            <th>Patient</th>
                            <th>Doctor</th>
                            <th>Specialty</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
""")

if appointments:
    for apt in appointments:
        status_class = f"status-{apt['status'].replace(' ', '-')}"
        print(f"""
                        <tr>
                            <td>{apt['appointment_id']}</td>
                            <td>{apt['appointment_date']}</td>
                            <td>{apt['appointment_time']}</td>
                            <td>
                                <strong>{apt['patient_name']}</strong><br>
                                <small>{apt['reg_number']}</small>
                            </td>
                            <td>{apt['doctor_name']}</td>
                            <td>{apt['specialty']}</td>
                            <td><span class="status-badge {status_class}">{apt['status']}</span></td>
                            <td>
                                <a href="admin_view_appointment.py?id={apt['appointment_id']}" class="btn btn-sm btn-outline-info" title="View"><i class="fas fa-eye"></i></a>
                                <a href="admin_edit_appointment.py?id={apt['appointment_id']}" class="btn btn-sm btn-outline-primary" title="Edit"><i class="fas fa-edit"></i></a>
                            </td>
                        </tr>
        """)
else:
    print("""
                        <tr>
                            <td colspan="8" class="text-center py-4">
                                <i class="fas fa-calendar-times fa-3x text-muted mb-3"></i>
                                <p class="text-muted">No appointments found</p>
                            </td>
                        </tr>
    """)

print("""
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")