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

from database import DatabaseOperations
from admin_session import AdminSession

session = AdminSession()
session.start_session()

if not session.is_logged_in():
    print("Location: admin_login.py")
    print()
    sys.exit()

admin_info = session.get_admin_info()

# Get patient ID from query string
form = cgi.FieldStorage()
patient_id = form.getvalue('id', '')
if not patient_id:
    print("Location: admin_patients.py")
    print()
    sys.exit()

# Fetch patient details
patient = DatabaseOperations.execute_query(
    """SELECT p.*,
              (SELECT COUNT(*) FROM appointments WHERE patient_id = p.patient_id) as total_appointments,
              (SELECT COUNT(*) FROM appointments WHERE patient_id = p.patient_id AND appointment_date >= CURDATE()) as upcoming_appointments,
              (SELECT COUNT(*) FROM appointments WHERE patient_id = p.patient_id AND status = 'Completed') as completed_appointments
       FROM patients p
       WHERE p.patient_id = %s""",
    (patient_id,),
    fetch_one=True
)

if not patient:
    print("Location: admin_patients.py")
    print()
    sys.exit()

# Fetch recent appointments (last 5)
recent_appointments = DatabaseOperations.execute_query(
    """SELECT a.*, d.full_name as doctor_name, d.specialty
       FROM appointments a
       JOIN doctors d ON a.doctor_id = d.doctor_id
       WHERE a.patient_id = %s
       ORDER BY a.appointment_date DESC, a.appointment_time DESC
       LIMIT 5""",
    (patient_id,),
    fetch_all=True
) or []

# Output headers
print("Content-Type: text/html; charset=utf-8")
print()

def h(s):
    """Escape HTML special characters."""
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

# HTML begins
print(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>View Patient - Clinic Management System</title>
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
        .sidebar {{ position: fixed; width: 260px; height: 100vh; background: linear-gradient(135deg, var(--dark), var(--primary)); color: white; padding: 20px; }}
        .sidebar-logo {{ text-align: center; padding: 20px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        .sidebar-menu a {{ color: rgba(255,255,255,0.8); text-decoration: none; padding: 12px 15px; display: block; }}
        .sidebar-menu a:hover, .sidebar-menu a.active {{ background: rgba(255,255,255,0.1); color: white; }}
        .main-content {{ margin-left: 260px; padding: 20px 30px; }}
        .top-bar {{ background: white; border-radius: 15px; padding: 15px 25px; margin-bottom: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .profile-card {{ background: white; border-radius: 20px; padding: 30px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); margin-bottom: 30px; }}
        .info-label {{ font-weight: 600; color: var(--dark); width: 150px; }}
        .stat-badge {{ background: #f8f9fa; border-radius: 10px; padding: 15px; text-align: center; }}
        .stat-number {{ font-size: 1.8rem; font-weight: 700; color: var(--primary); }}
        .btn-edit {{ background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; border: none; }}
    </style>
</head>
<body>
    <!-- Sidebar -->
    <div class="sidebar">
        <div class="sidebar-logo">
            <i class="fas fa-clinic-medical fa-3x"></i>
            <h3>ClinicCare</h3>
        </div>
        <ul class="sidebar-menu">
            <li><a href="admin_dashboard.py"><i class="fas fa-tachometer-alt"></i> Dashboard</a></li>
            <li><a href="admin_patients.py" class="active"><i class="fas fa-users"></i> Patients</a></li>
            <li><a href="admin_logout.py"><i class="fas fa-sign-out-alt"></i> Logout</a></li>
        </ul>
    </div>

    <div class="main-content">
        <div class="top-bar d-flex justify-content-between align-items-center">
            <h4 class="mb-0"><i class="fas fa-user me-2 text-primary"></i>Patient Profile</h4>
            <div>
                <a href="admin_patients.py" class="btn btn-outline-secondary btn-sm me-2"><i class="fas fa-arrow-left"></i> Back</a>
                <a href="admin_edit_patient.py?id={h(patient_id)}" class="btn btn-edit btn-sm"><i class="fas fa-edit"></i> Edit</a>
            </div>
        </div>

        <!-- Profile Header -->
        <div class="profile-card">
            <div class="row">
                <div class="col-md-8">
                    <h3 class="mb-3">{h(patient['full_name'])}</h3>
                    <p class="mb-1"><i class="fas fa-id-card me-2 text-primary"></i> Reg. Number: {h(patient['reg_number'])}</p>
                    <p class="mb-1"><i class="fas fa-envelope me-2 text-primary"></i> {h(patient['email'])}</p>
                    <p class="mb-1"><i class="fas fa-phone me-2 text-primary"></i> {h(patient['phone'])}</p>
                    <p class="mb-1"><i class="fas fa-calendar-alt me-2 text-primary"></i> Date of Birth: {h(patient['date_of_birth'])}</p>
                    <p class="mb-1"><i class="fas fa-tint me-2 text-primary"></i> Blood Group: {h(patient['blood_group'] or 'Not specified')}</p>
                    <p class="mb-1"><i class="fas fa-map-marker-alt me-2 text-primary"></i> Address: {h(patient['address'] or 'Not provided')}</p>
                    <p class="mb-1"><i class="fas fa-phone-alt me-2 text-primary"></i> Emergency Contact: {h(patient['emergency_contact'] or 'Not provided')}</p>
                    <p class="mb-1"><i class="fas fa-calendar-check me-2 text-primary"></i> Registered: {h(patient['created_at'])}</p>
                </div>
                <div class="col-md-4">
                    <div class="stat-badge mb-3">
                        <div class="stat-number">{h(patient['total_appointments'] or 0)}</div>
                        <div class="text-muted">Total Appointments</div>
                    </div>
                    <div class="stat-badge mb-3">
                        <div class="stat-number">{h(patient['upcoming_appointments'] or 0)}</div>
                        <div class="text-muted">Upcoming</div>
                    </div>
                    <div class="stat-badge">
                        <div class="stat-number">{h(patient['completed_appointments'] or 0)}</div>
                        <div class="text-muted">Completed</div>
                    </div>
                </div>
            </div>

            <!-- Recent Appointments -->
            <div class="mt-5">
                <h5 class="mb-3"><i class="fas fa-calendar-check me-2 text-primary"></i>Recent Appointments</h5>
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Time</th>
                                <th>Doctor</th>
                                <th>Specialty</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
""")

if recent_appointments:
    for apt in recent_appointments:
        status_class = {
            'Scheduled': 'bg-warning',
            'Completed': 'bg-success',
            'Cancelled': 'bg-danger',
            'No-Show': 'bg-secondary'
        }.get(apt['status'], 'bg-info')
        print(f"""
                            <tr>
                                <td>{apt['appointment_date']}</td>
                                <td>{apt['appointment_time']}</td>
                                <td>Dr. {h(apt['doctor_name'])}</td>
                                <td>{h(apt['specialty'])}</td>
                                <td><span class="badge {status_class}">{apt['status']}</span></td>
                                <td>
                                    <a href="admin_view_appointment.py?id={apt['appointment_id']}" class="btn btn-sm btn-outline-primary"><i class="fas fa-eye"></i></a>
                                </td>
                            </tr>
        """)
else:
    print("""
                            <tr>
                                <td colspan="6" class="text-center py-4 text-muted">No appointments found.</td>
                            </tr>
""")

print("""
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
""")