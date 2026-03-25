#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-

import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
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

# Handle status toggle
form = cgi.FieldStorage()
action = form.getvalue('action', '')
doctor_id = form.getvalue('id', '')

if action == 'toggle' and doctor_id:
    # Get current status
    current = DatabaseOperations.execute_query(
        "SELECT is_active FROM doctors WHERE doctor_id = %s",
        (doctor_id,),
        fetch_one=True
    )
    if current:
        new_status = 0 if current['is_active'] else 1
        DatabaseOperations.execute_query(
            "UPDATE doctors SET is_active = %s WHERE doctor_id = %s",
            (new_status, doctor_id)
        )

# Get all doctors
doctors = DatabaseOperations.execute_query("""
    SELECT d.*, 
           (SELECT COUNT(*) FROM appointments WHERE doctor_id = d.doctor_id) as appointment_count
    FROM doctors d
    ORDER BY d.created_at DESC
""", fetch_all=True) or []

print("Content-Type: text/html; charset=utf-8")
print()

print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manage Doctors - Clinic Management System</title>
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
        .sidebar {{ position: fixed; width: 260px; height: 100vh; background: linear-gradient(135deg, var(--dark) 0%, var(--primary) 100%); color: white; padding: 20px; }}
        .main-content {{ margin-left: 260px; padding: 20px 30px; }}
        .top-bar {{ background: white; border-radius: 15px; padding: 15px 25px; margin-bottom: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .table-card {{ background: white; border-radius: 15px; padding: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .badge-status {{ padding: 5px 10px; border-radius: 20px; font-size: 0.8rem; }}
        .badge-active {{ background: #d4edda; color: #155724; }}
        .badge-inactive {{ background: #f8d7da; color: #721c24; }}
        .btn-action {{ padding: 5px 10px; margin: 0 2px; }}
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
            <li><a href="admin_doctors.py" class="text-white text-decoration-none d-block p-2 active"><i class="fas fa-user-md me-2"></i>Doctors</a></li>
            <li><a href="admin_add_doctor.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-plus-circle me-2"></i>Add Doctor</a></li>
            <li><a href="admin_logout.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-sign-out-alt me-2"></i>Logout</a></li>
        </ul>
    </div>
    
    <div class="main-content">
        <div class="top-bar d-flex justify-content-between align-items-center">
            <h4 class="mb-0"><i class="fas fa-user-md me-2 text-primary"></i>Manage Doctors</h4>
            <a href="admin_add_doctor.py" class="btn btn-primary">
                <i class="fas fa-plus me-2"></i>Add New Doctor
            </a>
        </div>
        
        <div class="table-card">
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>License #</th>
                            <th>Doctor Name</th>
                            <th>Specialty</th>
                            <th>Email</th>
                            <th>Phone</th>
                            <th>Appointments</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
""")

for doctor in doctors:
    status_class = "badge-active" if doctor.get('is_active', 1) else "badge-inactive"
    status_text = "Active" if doctor.get('is_active', 1) else "Inactive"
    print(f"""
                        <tr>
                            <td>{doctor['doctor_id']}</td>
                            <td><strong>{doctor['license_number']}</strong></td>
                            <td>{doctor['full_name']}</td>
                            <td>{doctor['specialty']}</td>
                            <td>{doctor['email']}</td>
                            <td>{doctor['phone']}</td>
                            <td><span class="badge bg-info">{doctor.get('appointment_count', 0)}</span></td>
                            <td><span class="badge-status {status_class}">{status_text}</span></td>
                            <td>
                                <a href="admin_edit_doctor.py?id={doctor['doctor_id']}" class="btn btn-sm btn-outline-primary btn-action" title="Edit">
                                    <i class="fas fa-edit"></i>
                                </a>
                                <a href="admin_view_doctor.py?id={doctor['doctor_id']}" class="btn btn-sm btn-outline-info btn-action" title="View">
                                    <i class="fas fa-eye"></i>
                                </a>
                                <a href="?action=toggle&id={doctor['doctor_id']}" class="btn btn-sm btn-outline-warning btn-action" title="Toggle Status">
                                    <i class="fas fa-toggle-{'on' if doctor.get('is_active', 1) else 'off'}"></i>
                                </a>
                            </td>
                        </tr>
    """)

print("""
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
""")