#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Doctor Dashboard Module
Displays doctor's appointments and schedule
"""

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

# ----- Header collection -----
headers = []

session = SessionManager()
session.start_session()

cookie_header = session.get_cookie_header()
if cookie_header:
    headers.append(cookie_header)

# Check if doctor is logged in
if not session.is_logged_in() or session.get('user_type') != 'doctor':
    headers.append("Location: doctor_login.py")
    for h in headers:
        print(h)
    print()
    sys.exit()

doctor_info = session.get_user_info()
doctor_id = doctor_info['user_id']

# Get date parameter
form = cgi.FieldStorage()
selected_date = form.getvalue('date', datetime.now().strftime('%Y-%m-%d'))

# Validate selected_date
try:
    datetime.strptime(selected_date, '%Y-%m-%d')
except ValueError:
    selected_date = datetime.now().strftime('%Y-%m-%d')

# Fetch data
today_appointments = []   # appointments on selected date
upcoming = []             # future appointments (after today)
past = []                 # past appointments (before today)
doctor = None
error = None

try:
    # Today's appointments (selected date)
    today_appointments = DatabaseOperations.execute_query(
        """SELECT a.*, p.full_name as patient_name, p.phone,
                  TIME_FORMAT(a.appointment_time, '%h:%i %p') as time_formatted
           FROM appointments a
           JOIN patients p ON a.patient_id = p.patient_id
           WHERE a.doctor_id = %s AND a.appointment_date = %s
           ORDER BY a.appointment_time""",
        (doctor_id, selected_date),
        fetch_all=True
    ) or []

    # Upcoming appointments (future)
    upcoming = DatabaseOperations.execute_query(
        """SELECT a.*, p.full_name as patient_name, p.phone,
                  DATE_FORMAT(a.appointment_date, '%a %m/%d') as date_formatted,
                  TIME_FORMAT(a.appointment_time, '%h:%i %p') as time_formatted
           FROM appointments a
           JOIN patients p ON a.patient_id = p.patient_id
           WHERE a.doctor_id = %s AND a.appointment_date > CURDATE()
           ORDER BY a.appointment_date, a.appointment_time""",
        (doctor_id,),
        fetch_all=True
    ) or []

    # Past appointments (last 10)
    past = DatabaseOperations.execute_query(
        """SELECT a.*, p.full_name as patient_name, p.phone,
                  DATE_FORMAT(a.appointment_date, '%Y-%m-%d') as date_formatted,
                  TIME_FORMAT(a.appointment_time, '%h:%i %p') as time_formatted
           FROM appointments a
           JOIN patients p ON a.patient_id = p.patient_id
           WHERE a.doctor_id = %s AND a.appointment_date < CURDATE()
           ORDER BY a.appointment_date DESC, a.appointment_time DESC
           LIMIT 10""",
        (doctor_id,),
        fetch_all=True
    ) or []

    doctor = DatabaseOperations.get_doctor_by_id(doctor_id)
except Exception as e:
    error = str(e)

# Compute statistics
today_count = len(today_appointments)
upcoming_count = len(upcoming)
completed_today = sum(1 for a in today_appointments if a['status'] == 'Completed')
cancelled_today = sum(1 for a in today_appointments if a['status'] == 'Cancelled')
scheduled_today = sum(1 for a in today_appointments if a['status'] == 'Scheduled')
unique_patients = len(set(a['patient_id'] for a in upcoming if 'patient_id' in a))

# Add content type header
headers.append("Content-Type: text/html; charset=utf-8")
for hdr in headers:
    print(hdr)
print()

def h(s):
    """Escape HTML special characters."""
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

# HTML template
print(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Doctor Dashboard - Clinic Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --primary: #2A5C82;
            --secondary: #4A90E2;
            --accent: #50C878;
            --danger: #FF6B6B;
            --dark: #2C3E50;
            --gradient-primary: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        }}
        body {{ font-family: 'Inter', sans-serif; background: #f8f9fa; }}
        .navbar {{ background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .dashboard-container {{ max-width: 1400px; margin: 100px auto 50px; padding: 0 20px; }}
        .welcome-card {{
            background: var(--gradient-primary); color: white;
            border-radius: 20px; padding: 30px; margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(42,92,130,0.3);
        }}
        .stat-card {{
            background: white; border-radius: 15px; padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1); transition: 0.3s;
        }}
        .stat-card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0,0,0,0.15); }}
        .appointment-card {{
            background: white; border-radius: 15px; padding: 20px; margin-bottom: 15px;
            border-left: 4px solid var(--primary); transition: 0.3s;
        }}
        .appointment-card:hover {{ transform: translateX(5px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .status-badge {{
            padding: 5px 10px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;
        }}
        .status-scheduled {{ background: #fff3cd; color: #856404; }}
        .status-completed {{ background: #d4edda; color: #155724; }}
        .status-cancelled {{ background: #f8d7da; color: #721c24; }}
        .btn-primary-custom {{
            background: var(--gradient-primary); color: white; border: none;
            border-radius: 10px; padding: 10px 20px; font-weight: 600; transition: 0.3s;
        }}
        .btn-primary-custom:hover {{ transform: translateY(-2px); box-shadow: 0 10px 20px rgba(42,92,130,0.3); }}
        .time-slot {{ font-size: 1.2rem; font-weight: 600; color: var(--primary); }}
        .calendar-nav {{
            display: flex; align-items: center; justify-content: center;
            gap: 20px; margin-bottom: 20px;
        }}
        .compact-item {{
            padding: 8px 0; border-bottom: 1px solid #eee;
        }}
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-light fixed-top">
        <div class="container">
            <a class="navbar-brand" href="index.py">
                <i class="fas fa-clinic-medical me-2 text-primary"></i>ClinicCare
            </a>
            <div class="ms-auto d-flex align-items-center">
                <span class="me-3">
                    <i class="fas fa-user-md me-2 text-primary"></i>
                    Dr. {h(doctor_info['full_name'])}
                </span>
                <a href="doctor_profile.py" class="btn btn-outline-primary btn-sm me-2" title="Profile"><i class="fas fa-user"></i></a>
                <a href="logout.py" class="btn btn-outline-danger btn-sm">
                    <i class="fas fa-sign-out-alt me-1"></i>Logout
                </a>
            </div>
        </div>
    </nav>
    
    <div class="dashboard-container">
        <!-- Welcome Card -->
        <div class="welcome-card">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h2>Welcome back, Dr. {h(doctor_info['full_name'])}!</h2>
                    <p class="mb-0">
                        <i class="fas fa-calendar me-2"></i>
                        {datetime.now().strftime('%A, %B %d, %Y')}
                    </p>
                </div>
                <div class="col-md-4 text-md-end">
                    <span class="badge bg-light text-dark p-3">
                        <i class="fas fa-clock me-2"></i>
                        {h(doctor['available_from'] if doctor and doctor.get('available_from') else '09:00')} – {h(doctor['available_to'] if doctor and doctor.get('available_to') else '17:00')}
                    </span>
                </div>
            </div>
        </div>
        
        <!-- Stats Cards -->
        <div class="row g-4 mb-5">
            <div class="col-md-3">
                <div class="stat-card">
                    <div class="d-flex align-items-center">
                        <div class="flex-shrink-0"><i class="fas fa-calendar-check fa-3x text-primary"></i></div>
                        <div class="flex-grow-1 ms-3">
                            <h3 class="mb-0">{today_count}</h3>
                            <p class="text-muted mb-0">Today's Appointments</p>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <div class="d-flex align-items-center">
                        <div class="flex-shrink-0"><i class="fas fa-clock fa-3x text-warning"></i></div>
                        <div class="flex-grow-1 ms-3">
                            <h3 class="mb-0">{upcoming_count}</h3>
                            <p class="text-muted mb-0">Upcoming</p>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <div class="d-flex align-items-center">
                        <div class="flex-shrink-0"><i class="fas fa-check-circle fa-3x text-success"></i></div>
                        <div class="flex-grow-1 ms-3">
                            <h3 class="mb-0">{completed_today}</h3>
                            <p class="text-muted mb-0">Completed Today</p>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <div class="d-flex align-items-center">
                        <div class="flex-shrink-0"><i class="fas fa-users fa-3x text-info"></i></div>
                        <div class="flex-grow-1 ms-3">
                            <h3 class="mb-0">{unique_patients}</h3>
                            <p class="text-muted mb-0">Unique Patients</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Calendar Navigation -->
        <div class="calendar-nav">
            <a href="?date={ (datetime.strptime(selected_date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d') }" class="btn btn-outline-primary">
                <i class="fas fa-chevron-left"></i>
            </a>
            <h4 class="mb-0">{ datetime.strptime(selected_date, '%Y-%m-%d').strftime('%B %d, %Y') }</h4>
            <a href="?date={ (datetime.strptime(selected_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d') }" class="btn btn-outline-primary">
                <i class="fas fa-chevron-right"></i>
            </a>
        </div>
        
        <div class="row">
            <!-- Today's Appointments List -->
            <div class="col-md-7">
                <div class="card border-0 shadow-sm">
                    <div class="card-header bg-white py-3">
                        <h5 class="mb-0"><i class="fas fa-list me-2 text-primary"></i>Today's Schedule</h5>
                    </div>
                    <div class="card-body">
""")
if today_appointments:
    for apt in today_appointments:
        status_class = "status-" + apt['status'].lower()
        print(f"""
                        <div class="appointment-card">
                            <div class="row align-items-center">
                                <div class="col-md-2">
                                    <div class="time-slot">{h(apt['time_formatted'])}</div>
                                </div>
                                <div class="col-md-4">
                                    <h6 class="mb-1">{h(apt['patient_name'])}</h6>
                                    <small class="text-muted"><i class="fas fa-phone me-1"></i>{h(apt.get('phone', ''))}</small>
                                </div>
                                <div class="col-md-3">
                                    <span class="status-badge {status_class}">{apt['status']}</span>
                                </div>
                                <div class="col-md-3 text-end">
                                    <a href="appointment_details.py?id={apt['appointment_id']}" class="btn btn-sm btn-outline-primary"><i class="fas fa-eye"></i></a>
                                    <a href="complete_appointment.py?id={apt['appointment_id']}" class="btn btn-sm btn-outline-success" onclick="return confirm('Mark this appointment as completed?')"><i class="fas fa-check"></i></a>
                                </div>
                            </div>
                        </div>
        """)
else:
    print("""
                        <div class="text-center py-5">
                            <i class="fas fa-calendar-times fa-4x text-muted mb-3"></i>
                            <h5>No appointments scheduled for today</h5>
                            <p class="text-muted">Enjoy your day!</p>
                        </div>
""")
print("""
                    </div>
                </div>
            </div>
            
            <!-- Right Column -->
            <div class="col-md-5">
                <!-- Quick Actions -->
                <div class="card border-0 shadow-sm mb-4">
                    <div class="card-header bg-white py-3">
                        <h5 class="mb-0"><i class="fas fa-bolt me-2 text-primary"></i>Quick Actions</h5>
                    </div>
                    <div class="card-body">
                        <div class="d-grid gap-2">
                            <a href="full_schedule.py" class="btn btn-primary-custom"><i class="fas fa-calendar me-2"></i>View Full Schedule</a>
                            <a href="update_availability.py" class="btn btn-outline-primary"><i class="fas fa-clock me-2"></i>Update Availability</a>
                            <a href="export_report.py" class="btn btn-outline-primary"><i class="fas fa-download me-2"></i>Export Report</a>
                            <a href="doctor_profile.py" class="btn btn-outline-primary"><i class="fas fa-user-md me-2"></i>My Profile</a>
                        </div>
                    </div>
                </div>
                
                <!-- Upcoming Appointments -->
                <div class="card border-0 shadow-sm mb-4">
                    <div class="card-header bg-white py-3">
                        <h5 class="mb-0"><i class="fas fa-calendar-alt me-2 text-primary"></i>Upcoming Appointments</h5>
                    </div>
                    <div class="card-body">
""")
if upcoming:
    for apt in upcoming[:5]:
        print(f"""
                        <div class="compact-item d-flex justify-content-between align-items-center">
                            <div>
                                <strong>{h(apt['date_formatted'])} {h(apt['time_formatted'])}</strong><br>
                                <small>{h(apt['patient_name'])}</small>
                            </div>
                            <span class="badge bg-warning">{apt['status']}</span>
                        </div>
        """)
else:
    print('<p class="text-muted">No upcoming appointments.</p>')
print("""
                    </div>
                </div>
                
                <!-- Recent Past Appointments -->
                <div class="card border-0 shadow-sm">
                    <div class="card-header bg-white py-3">
                        <h5 class="mb-0"><i class="fas fa-history me-2 text-primary"></i>Recent Past Appointments</h5>
                    </div>
                    <div class="card-body">
""")
if past:
    for apt in past[:5]:
        print(f"""
                        <div class="compact-item d-flex justify-content-between align-items-center">
                            <div>
                                <strong>{h(apt['date_formatted'])} {h(apt['time_formatted'])}</strong><br>
                                <small>{h(apt['patient_name'])}</small>
                            </div>
                            <span class="badge bg-secondary">{apt['status']}</span>
                        </div>
        """)
else:
    print('<p class="text-muted">No past appointments.</p>')
print("""
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Chart for today's appointments (optional, keep if you want)
        const ctx = document.getElementById('statsChart');
        if (ctx) {
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Scheduled', 'Completed', 'Cancelled'],
                    datasets: [{
                        data: [""" + str(scheduled_today) + """, """ + str(completed_today) + """, """ + str(cancelled_today) + """],
                        backgroundColor: ['#ffc107', '#28a745', '#dc3545']
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }
            });
        }
    </script>
</body>
</html>
""")