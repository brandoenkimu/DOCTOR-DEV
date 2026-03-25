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

# Check admin session
session = AdminSession()
session.start_session()

if not session.is_logged_in():
    print("Location: admin_login.py")
    print()
    sys.exit()

admin_info = session.get_admin_info()

# Handle search and filters
form = cgi.FieldStorage()
search = form.getvalue('search', '')

# Build query
query = "SELECT * FROM patients"
params = []
if search:
    query += " WHERE reg_number LIKE %s OR full_name LIKE %s OR email LIKE %s OR phone LIKE %s"
    search_term = f"%{search}%"
    params = [search_term, search_term, search_term, search_term]
query += " ORDER BY created_at DESC"

patients = DatabaseOperations.execute_query(query, tuple(params) if params else None, fetch_all=True) or []

print("Content-Type: text/html; charset=utf-8")
print()

print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manage Patients - Clinic Management System</title>
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
        .btn-primary-custom {{ background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; border: none; }}
        .search-box {{ max-width: 300px; }}
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
            <li><a href="admin_patients.py" class="text-white text-decoration-none d-block p-2 active"><i class="fas fa-users me-2"></i>Patients</a></li>
            <li><a href="admin_appointments.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-calendar-check me-2"></i>Appointments</a></li>
            <li><a href="admin_specialties.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-stethoscope me-2"></i>Specialties</a></li>
            <li><a href="admin_reports.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-chart-bar me-2"></i>Reports</a></li>
            <li><a href="admin_settings.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-cog me-2"></i>Settings</a></li>
            <li><hr class="bg-white opacity-25"></li>
            <li><a href="admin_logout.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-sign-out-alt me-2"></i>Logout</a></li>
        </ul>
    </div>
    
    <div class="main-content">
        <div class="top-bar d-flex justify-content-between align-items-center">
            <h4 class="mb-0"><i class="fas fa-users me-2 text-primary"></i>Manage Patients</h4>
            <form method="get" class="d-flex">
                <input type="text" name="search" class="form-control search-box me-2" placeholder="Search patients..." value="{search}">
                <button type="submit" class="btn btn-primary-custom"><i class="fas fa-search"></i></button>
            </form>
        </div>
        
        <div class="table-card">
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Reg No.</th>
                            <th>Full Name</th>
                            <th>Email</th>
                            <th>Phone</th>
                            <th>Blood Group</th>
                            <th>Registered</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
""")

if patients:
    for p in patients:
        print(f"""
                        <tr>
                            <td>{p['patient_id']}</td>
                            <td><strong>{p['reg_number']}</strong></td>
                            <td>{p['full_name']}</td>
                            <td>{p['email']}</td>
                            <td>{p['phone']}</td>
                            <td><span class="badge bg-info">{p['blood_group'] or 'N/A'}</span></td>
                            <td>{p['created_at']}</td>
                            <td>
                                <a href="admin_view_patient.py?id={p['patient_id']}" class="btn btn-sm btn-outline-info" title="View"><i class="fas fa-eye"></i></a>
                                <a href="admin_edit_patient.py?id={p['patient_id']}" class="btn btn-sm btn-outline-primary" title="Edit"><i class="fas fa-edit"></i></a>
                            </td>
                        </tr>
        """)
else:
    print("""
                        <tr>
                            <td colspan="8" class="text-center py-4">
                                <i class="fas fa-users fa-3x text-muted mb-3"></i>
                                <p class="text-muted">No patients found</p>
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