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

# Start admin session
session = AdminSession()
session.start_session()

if not session.is_logged_in():
    print("Location: admin_login.py")
    print()
    sys.exit()

admin_info = session.get_admin_info()

# Get doctor ID from query string
form = cgi.FieldStorage()
doctor_id = form.getvalue('id', '')
if not doctor_id:
    print("Location: admin_doctors.py")
    print()
    sys.exit()

# Fetch doctor details
doctor = DatabaseOperations.execute_query(
    """SELECT d.*,
              (SELECT COUNT(*) FROM appointments WHERE doctor_id = d.doctor_id) as total_appointments,
              (SELECT COUNT(*) FROM appointments WHERE doctor_id = d.doctor_id AND status = 'Completed') as completed_appointments
       FROM doctors d
       WHERE d.doctor_id = %s""",
    (doctor_id,),
    fetch_one=True
)

if not doctor:
    print("Location: admin_doctors.py")
    print()
    sys.exit()

# Fetch doctor's weekly schedule
schedule = DatabaseOperations.execute_query(
    """SELECT * FROM schedules
       WHERE doctor_id = %s
       ORDER BY FIELD(day_of_week, 'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'),
                start_time""",
    (doctor_id,),
    fetch_all=True
) or []

# Fetch recent appointments (last 5)
recent_appointments = DatabaseOperations.execute_query(
    """SELECT a.*, p.full_name as patient_name, p.phone as patient_phone
       FROM appointments a
       JOIN patients p ON a.patient_id = p.patient_id
       WHERE a.doctor_id = %s
       ORDER BY a.appointment_date DESC, a.appointment_time DESC
       LIMIT 5""",
    (doctor_id,),
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
    <title>View Doctor - Clinic Management System</title>
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
        .schedule-card {{ background: #f8f9fa; border-radius: 15px; padding: 20px; margin-top: 20px; }}
        .badge-status {{ padding: 5px 10px; border-radius: 20px; }}
        .badge-active {{ background: #d4edda; color: #155724; }}
        .badge-inactive {{ background: #f8d7da; color: #721c24; }}
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
            <li><a href="admin_doctors.py" class="active"><i class="fas fa-user-md"></i> Doctors</a></li>
            <li><a href="admin_logout.py"><i class="fas fa-sign-out-alt"></i> Logout</a></li>
        </ul>
    </div>

    <div class="main-content">
        <div class="top-bar d-flex justify-content-between align-items-center">
            <h4 class="mb-0"><i class="fas fa-user-md me-2 text-primary"></i>Doctor Profile</h4>
            <div>
                <a href="admin_doctors.py" class="btn btn-outline-secondary btn-sm me-2"><i class="fas fa-arrow-left"></i> Back</a>
                <a href="admin_edit_doctor.py?id={h(doctor_id)}" class="btn btn-edit btn-sm"><i class="fas fa-edit"></i> Edit</a>
            </div>
        </div>

        <!-- Profile Header -->
        <div class="profile-card">
            <div class="row">
                <div class="col-md-8">
                    <h3 class="mb-3">{h(doctor['full_name'])}</h3>
                    <p class="mb-1"><i class="fas fa-id-card me-2 text-primary"></i> License: {h(doctor['license_number'])}</p>
                    <p class="mb-1"><i class="fas fa-stethoscope me-2 text-primary"></i> Specialty: {h(doctor['specialty'])}</p>
                    <p class="mb-1"><i class="fas fa-envelope me-2 text-primary"></i> {h(doctor['email'])}</p>
                    <p class="mb-1"><i class="fas fa-phone me-2 text-primary"></i> {h(doctor['phone'])}</p>
                    <p class="mb-1"><i class="fas fa-calendar-alt me-2 text-primary"></i> Member since: {h(doctor['created_at'])}</p>
                    <p class="mb-1"><i class="fas fa-clock me-2 text-primary"></i> Working hours: {h(doctor['available_from'])} – {h(doctor['available_to'])}</p>
                    <p class="mb-1">
                        <i class="fas fa-toggle-{'on' if doctor['is_active'] else 'off'} me-2 text-primary"></i>
                        Status: <span class="badge-status {'badge-active' if doctor['is_active'] else 'badge-inactive'}">{'Active' if doctor['is_active'] else 'Inactive'}</span>
                    </p>
                </div>
                <div class="col-md-4 text-md-end">
                    <div class="p-3 bg-light rounded">
                        <h5>Statistics</h5>
                        <p class="mb-1">Total Appointments: <strong>{h(doctor['total_appointments'] or 0)}</strong></p>
                        <p class="mb-1">Completed: <strong>{h(doctor['completed_appointments'] or 0)}</strong></p>
                    </div>
                </div>
            </div>

            <hr>
            <h5 class="mb-3">Qualifications</h5>
            <p>{h(doctor['qualification'] or 'Not provided')}</p>
            <p>Experience: {h(doctor['experience_years'] or 0)} years</p>
            <p>Consultation Fee: KES {h(doctor['consultation_fee'] or 0)}</p>

            <!-- Schedule Section -->
            <div class="schedule-card">
                <h5 class="mb-3"><i class="fas fa-calendar-week me-2 text-primary"></i>Weekly Schedule</h5>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr><th>Day</th><th>Start</th><th>End</th><th>Max Patients</th></tr>
                        </thead>
                        <tbody>
""")

if schedule:
    days_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    for day in days_order:
        day_slots = [s for s in schedule if s['day_of_week'] == day]
        if day_slots:
            for s in day_slots:
                print(f"""
                            <tr>
                                <td>{day}</td>
                                <td>{s['start_time']}</td>
                                <td>{s['end_time']}</td>
                                <td>{s.get('max_patients',10)}</td>
                            </tr>""")
        else:
            print(f"""
                            <tr>
                                <td>{day}</td>
                                <td colspan="3" class="text-muted">Not available</td>
                            </tr>""")
else:
    print('<tr><td colspan="4" class="text-center text-muted">No schedule defined</td></tr>')

print("""
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Recent Appointments -->
            <div class="mt-4">
                <h5 class="mb-3"><i class="fas fa-calendar-check me-2 text-primary"></i>Recent Appointments</h5>
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr><th>Date</th><th>Time</th><th>Patient</th><th>Phone</th><th>Status</th></tr>
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
                                <td>{h(apt['patient_name'])}</td>
                                <td>{h(apt.get('patient_phone',''))}</td>
                                <td><span class="badge {status_class}">{apt['status']}</span></td>
                            </tr>""")
else:
    print('<tr><td colspan="5" class="text-center text-muted">No recent appointments</td></tr>')

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