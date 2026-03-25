#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


import sys
import os
from datetime import datetime, timedelta

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

# Get date range from form (default: last 30 days)
form = cgi.FieldStorage()
date_from = form.getvalue('from', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
date_to = form.getvalue('to', datetime.now().strftime('%Y-%m-%d'))

# Statistics
# 1. Appointments per day in range
appointments_per_day = DatabaseOperations.execute_query("""
    SELECT DATE(appointment_date) as date, COUNT(*) as count
    FROM appointments
    WHERE appointment_date BETWEEN %s AND %s
    GROUP BY DATE(appointment_date)
    ORDER BY date
""", (date_from, date_to), fetch_all=True) or []

# 2. Appointments by status
appointments_by_status = DatabaseOperations.execute_query("""
    SELECT status, COUNT(*) as count
    FROM appointments
    WHERE appointment_date BETWEEN %s AND %s
    GROUP BY status
""", (date_from, date_to), fetch_all=True) or []

# 3. Top doctors by appointments
top_doctors = DatabaseOperations.execute_query("""
    SELECT d.full_name, d.specialty, COUNT(a.appointment_id) as appointment_count
    FROM doctors d
    LEFT JOIN appointments a ON d.doctor_id = a.doctor_id
        AND a.appointment_date BETWEEN %s AND %s
    GROUP BY d.doctor_id
    ORDER BY appointment_count DESC
    LIMIT 5
""", (date_from, date_to), fetch_all=True) or []

# 4. New patients registered in range
new_patients = DatabaseOperations.execute_query("""
    SELECT COUNT(*) as count
    FROM patients
    WHERE DATE(created_at) BETWEEN %s AND %s
""", (date_from, date_to), fetch_one=True)

# 5. Total appointments in range
total_appointments = DatabaseOperations.execute_query("""
    SELECT COUNT(*) as count
    FROM appointments
    WHERE appointment_date BETWEEN %s AND %s
""", (date_from, date_to), fetch_one=True)

print("Content-Type: text/html; charset=utf-8")
print()

print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reports - Clinic Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --primary: #2A5C82;
            --secondary: #4A90E2;
            --dark: #2C3E50;
        }}
        body {{ font-family: 'Inter', sans-serif; background: #f4f6f9; }}
        .sidebar {{ position: fixed; width: 260px; height: 100vh; background: linear-gradient(135deg, var(--dark) 0%, var(--primary) 100%); color: white; padding: 20px; }}
        .main-content {{ margin-left: 260px; padding: 20px 30px; }}
        .top-bar {{ background: white; border-radius: 15px; padding: 15px 25px; margin-bottom: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .card-custom {{ background: white; border-radius: 15px; padding: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .stat-number {{ font-size: 2rem; font-weight: 700; color: var(--primary); }}
    </style>
</head>
<body>
    <div class="sidebar">
        <!-- same sidebar -->
        <div class="sidebar-logo text-center mb-4">
            <i class="fas fa-clinic-medical fa-3x"></i>
            <h3>ClinicCare</h3>
        </div>
        <ul class="list-unstyled">
            <li><a href="admin_dashboard.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-tachometer-alt me-2"></i>Dashboard</a></li>
            <li><a href="admin_doctors.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-user-md me-2"></i>Doctors</a></li>
            <li><a href="admin_patients.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-users me-2"></i>Patients</a></li>
            <li><a href="admin_appointments.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-calendar-check me-2"></i>Appointments</a></li>
            <li><a href="admin_specialties.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-stethoscope me-2"></i>Specialties</a></li>
            <li><a href="admin_reports.py" class="text-white text-decoration-none d-block p-2 active"><i class="fas fa-chart-bar me-2"></i>Reports</a></li>
            <li><a href="admin_settings.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-cog me-2"></i>Settings</a></li>
            <li><hr class="bg-white opacity-25"></li>
            <li><a href="admin_logout.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-sign-out-alt me-2"></i>Logout</a></li>
        </ul>
    </div>
    
    <div class="main-content">
        <div class="top-bar">
            <h4 class="mb-0"><i class="fas fa-chart-bar me-2 text-primary"></i>Reports</h4>
        </div>
        
        <div class="card-custom">
            <form method="get" class="row g-3">
                <div class="col-md-4">
                    <label class="form-label">From Date</label>
                    <input type="date" name="from" class="form-control" value="{date_from}">
                </div>
                <div class="col-md-4">
                    <label class="form-label">To Date</label>
                    <input type="date" name="to" class="form-control" value="{date_to}">
                </div>
                <div class="col-md-4 d-flex align-items-end">
                    <button type="submit" class="btn btn-primary-custom"><i class="fas fa-sync-alt me-2"></i>Update</button>
                </div>
            </form>
        </div>
        
        <div class="row">
            <div class="col-md-3">
                <div class="card-custom text-center">
                    <div class="stat-number">{total_appointments['count'] if total_appointments else 0}</div>
                    <div class="text-muted">Appointments</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card-custom text-center">
                    <div class="stat-number">{new_patients['count'] if new_patients else 0}</div>
                    <div class="text-muted">New Patients</div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card-custom">
                    <h5 class="mb-3">Appointments by Status</h5>
                    <canvas id="statusChart"></canvas>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card-custom">
                    <h5 class="mb-3">Appointments per Day</h5>
                    <canvas id="dailyChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="card-custom">
            <h5 class="mb-3">Top Doctors</h5>
            <table class="table">
                <thead>
                    <tr>
                        <th>Doctor</th>
                        <th>Specialty</th>
                        <th>Appointments</th>
                    </tr>
                </thead>
                <tbody>
""")
for doc in top_doctors:
    print(f"<tr><td>{doc['full_name']}</td><td>{doc['specialty']}</td><td>{doc['appointment_count']}</td></tr>")
print("""
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        // Status chart
        const statusCtx = document.getElementById('statusChart').getContext('2d');
        new Chart(statusCtx, {
            type: 'pie',
            data: {
                labels: [""")
status_labels = []
status_counts = []
for s in appointments_by_status:
    status_labels.append(f"'{s['status']}'")
    status_counts.append(s['count'])
print(','.join(status_labels))
print("],\n datasets: [{ data: [", end='')
print(','.join(str(c) for c in status_counts))
print("], backgroundColor: ['#4A90E2', '#50C878', '#FF6B6B', '#FFD93D'] }] } });")

print("""
        // Daily chart
        const dailyCtx = document.getElementById('dailyChart').getContext('2d');
        new Chart(dailyCtx, {
            type: 'line',
            data: {
                labels: [""")
daily_labels = []
daily_counts = []
for d in appointments_per_day:
    daily_labels.append(f"'{d['date']}'")
    daily_counts.append(d['count'])
print(','.join(daily_labels))
print("],\n datasets: [{ data: [", end='')
print(','.join(str(c) for c in daily_counts))
print("], borderColor: '#2A5C82', fill: false }] } });")
print("""
    </script>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")