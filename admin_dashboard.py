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

# Check admin session
session = AdminSession()
session.start_session()

if not session.is_logged_in():
    print("Location: admin_login.py")
    print()
    sys.exit()

admin_info = session.get_admin_info()

# Get statistics
total_doctors = DatabaseOperations.execute_query("SELECT COUNT(*) as count FROM doctors", fetch_one=True)
total_patients = DatabaseOperations.execute_query("SELECT COUNT(*) as count FROM patients", fetch_one=True)
total_appointments = DatabaseOperations.execute_query("SELECT COUNT(*) as count FROM appointments", fetch_one=True)
today_appointments = DatabaseOperations.execute_query(
    "SELECT COUNT(*) as count FROM appointments WHERE DATE(appointment_date) = CURDATE()", 
    fetch_one=True
)

# Get recent doctors
recent_doctors = DatabaseOperations.execute_query(
    "SELECT * FROM doctors ORDER BY created_at DESC LIMIT 5", 
    fetch_all=True
) or []

print("Content-Type: text/html; charset=utf-8")
print()

today = datetime.now().strftime("%Y-%m-%d")
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - Clinic Management System</title>
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
        
        body {{
            font-family: 'Inter', sans-serif;
            background: #f4f6f9;
        }}
        
        .sidebar {{
            position: fixed;
            top: 0;
            left: 0;
            height: 100vh;
            width: 260px;
            background: linear-gradient(135deg, var(--dark) 0%, var(--primary) 100%);
            color: white;
            padding: 20px;
            overflow-y: auto;
        }}
        
        .sidebar-logo {{
            text-align: center;
            padding: 20px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 20px;
        }}
        
        .sidebar-logo h3 {{
            font-weight: 700;
            font-size: 1.5rem;
            margin: 10px 0 0;
        }}
        
        .sidebar-menu {{
            list-style: none;
            padding: 0;
        }}
        
        .sidebar-menu li {{
            margin-bottom: 5px;
        }}
        
        .sidebar-menu a {{
            color: rgba(255,255,255,0.8);
            text-decoration: none;
            padding: 12px 15px;
            display: block;
            border-radius: 10px;
            transition: all 0.3s ease;
        }}
        
        .sidebar-menu a:hover,
        .sidebar-menu a.active {{
            background: rgba(255,255,255,0.1);
            color: white;
            transform: translateX(5px);
        }}
        
        .sidebar-menu i {{
            width: 25px;
            margin-right: 10px;
        }}
        
        .main-content {{
            margin-left: 260px;
            padding: 20px 30px;
        }}
        
        .top-bar {{
            background: white;
            border-radius: 15px;
            padding: 15px 25px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .user-info {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .user-avatar {{
            width: 45px;
            height: 45px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.2rem;
            font-weight: bold;
        }}
        
        .stat-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            transition: all 0.3s ease;
            border-left: 4px solid transparent;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }}
        
        .stat-card.doctors {{ border-left-color: var(--primary); }}
        .stat-card.patients {{ border-left-color: var(--success); }}
        .stat-card.appointments {{ border-left-color: var(--warning); }}
        .stat-card.today {{ border-left-color: var(--secondary); }}
        
        .stat-icon {{
            width: 50px;
            height: 50px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            margin-bottom: 15px;
        }}
        
        .stat-icon.doctors {{ background: rgba(42, 92, 130, 0.1); color: var(--primary); }}
        .stat-icon.patients {{ background: rgba(80, 200, 120, 0.1); color: var(--success); }}
        .stat-icon.appointments {{ background: rgba(255, 217, 61, 0.1); color: var(--warning); }}
        .stat-icon.today {{ background: rgba(74, 144, 226, 0.1); color: var(--secondary); }}
        
        .stat-number {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9rem;
        }}
        
        .table-card {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-top: 20px;
        }}
        
        .btn-primary-custom {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 20px;
            transition: all 0.3s ease;
        }}
        
        .btn-primary-custom:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(42, 92, 130, 0.3);
            color: white;
        }}
        
        .badge-status {{
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }}
        
        .badge-active {{ background: #d4edda; color: #155724; }}
        .badge-inactive {{ background: #f8d7da; color: #721c24; }}
    </style>
</head>
<body>
    <!-- Sidebar -->
    <div class="sidebar">
        <div class="sidebar-logo">
            <i class="fas fa-clinic-medical fa-3x"></i>
            <h3>ClinicCare</h3>
            <p class="small opacity-75">Admin Panel</p>
        </div>
        
        <ul class="sidebar-menu">
            <li><a href="admin_dashboard.py" class="active">
                <i class="fas fa-tachometer-alt"></i> Dashboard
            </a></li>
            <li><a href="admin_doctors.py">
                <i class="fas fa-user-md"></i> Manage Doctors
            </a></li>
            <li><a href="admin_patients.py">
                <i class="fas fa-users"></i> Manage Patients
            </a></li>
            <li><a href="admin_appointments.py">
                <i class="fas fa-calendar-check"></i> Appointments
            </a></li>
            <li><a href="admin_specialties.py">
                <i class="fas fa-stethoscope"></i> Specialties
            </a></li>
            <li><a href="admin_reports.py">
                <i class="fas fa-chart-bar"></i> Reports
            </a></li>
            <li><a href="admin_settings.py">
                <i class="fas fa-cog"></i> Settings
            </a></li>
            <li><hr class="bg-white opacity-25"></li>
            <li><a href="admin_logout.py">
                <i class="fas fa-sign-out-alt"></i> Logout
            </a></li>
        </ul>
    </div>
    
    <!-- Main Content -->
    <div class="main-content">
        <!-- Top Bar -->
        <div class="top-bar">
            <h4 class="mb-0"><i class="fas fa-tachometer-alt me-2 text-primary"></i>Dashboard</h4>
            <div class="user-info">
                <div>
                    <small class="text-muted d-block">Welcome back,</small>
                    <strong>{admin_info['full_name']}</strong>
                </div>
                <div class="user-avatar">
                    {admin_info['full_name'][0]}
                </div>
            </div>
        </div>
        
        <!-- Statistics Cards -->
        <div class="row">
            <div class="col-md-3">
                <div class="stat-card doctors">
                    <div class="stat-icon doctors">
                        <i class="fas fa-user-md"></i>
                    </div>
                    <div class="stat-number">{total_doctors['count'] if total_doctors else 0}</div>
                    <div class="stat-label">Total Doctors</div>
                    <small class="text-muted">Registered specialists</small>
                </div>
            </div>
            
            <div class="col-md-3">
                <div class="stat-card patients">
                    <div class="stat-icon patients">
                        <i class="fas fa-users"></i>
                    </div>
                    <div class="stat-number">{total_patients['count'] if total_patients else 0}</div>
                    <div class="stat-label">Total Patients</div>
                    <small class="text-muted">Active patients</small>
                </div>
            </div>
            
            <div class="col-md-3">
                <div class="stat-card appointments">
                    <div class="stat-icon appointments">
                        <i class="fas fa-calendar-alt"></i>
                    </div>
                    <div class="stat-number">{total_appointments['count'] if total_appointments else 0}</div>
                    <div class="stat-label">Total Appointments</div>
                    <small class="text-muted">All time</small>
                </div>
            </div>
            
            <div class="col-md-3">
                <div class="stat-card today">
                    <div class="stat-icon today">
                        <i class="fas fa-clock"></i>
                    </div>
                    <div class="stat-number">{today_appointments['count'] if today_appointments else 0}</div>
                    <div class="stat-label">Today's Appointments</div>
                    <small class="text-muted">{today}</small>
                </div>
            </div>
        </div>
        
        <!-- Quick Actions -->
        <div class="row mt-4">
            <div class="col-md-12">
                <div class="d-flex gap-2 mb-4">
                    <a href="admin_add_doctor.py" class="btn btn-primary-custom">
                        <i class="fas fa-plus-circle me-2"></i>Add New Doctor
                    </a>
                    <a href="admin_add_patient.py" class="btn btn-outline-primary">
                        <i class="fas fa-user-plus me-2"></i>Add Patient
                    </a>
                    <a href="admin_schedule.py" class="btn btn-outline-primary">
                        <i class="fas fa-calendar-plus me-2"></i>Manage Schedule
                    </a>
                </div>
            </div>
        </div>
        
        <!-- Recent Doctors -->
        <div class="table-card">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h5 class="mb-0"><i class="fas fa-user-md me-2 text-primary"></i>Recently Added Doctors</h5>
                <a href="admin_doctors.py" class="text-decoration-none">View All <i class="fas fa-arrow-right ms-1"></i></a>
            </div>
            
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>License #</th>
                            <th>Doctor Name</th>
                            <th>Specialty</th>
                            <th>Email</th>
                            <th>Phone</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
""")

for doctor in recent_doctors:
    status_class = "badge-active" if doctor.get('is_active', 1) else "badge-inactive"
    status_text = "Active" if doctor.get('is_active', 1) else "Inactive"
    print(f"""
                        <tr>
                            <td><strong>{doctor['license_number']}</strong></td>
                            <td>{doctor['full_name']}</td>
                            <td>{doctor['specialty']}</td>
                            <td>{doctor['email']}</td>
                            <td>{doctor['phone']}</td>
                            <td><span class="badge-status {status_class}">{status_text}</span></td>
                            <td>
                                <a href="admin_edit_doctor.py?id={doctor['doctor_id']}" class="btn btn-sm btn-outline-primary">
                                    <i class="fas fa-edit"></i>
                                </a>
                                <a href="admin_view_doctor.py?id={doctor['doctor_id']}" class="btn btn-sm btn-outline-info">
                                    <i class="fas fa-eye"></i>
                                </a>
                            </td>
                        </tr>
    """)

if not recent_doctors:
    print("""
                        <tr>
                            <td colspan="7" class="text-center py-4">
                                <i class="fas fa-user-md fa-3x text-muted mb-3"></i>
                                <p class="text-muted">No doctors added yet</p>
                                <a href="admin_add_doctor.py" class="btn btn-primary-custom btn-sm">
                                    <i class="fas fa-plus me-2"></i>Add Your First Doctor
                                </a>
                            </td>
                        </tr>
    """)

print(f"""
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- System Info -->
        <div class="row mt-4">
            <div class="col-md-6">
                <div class="table-card">
                    <h5 class="mb-3"><i class="fas fa-info-circle me-2 text-primary"></i>System Information</h5>
                    <table class="table table-borderless">
                        <tr>
                            <td><strong>Server Time:</strong></td>
                            <td>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
                        </tr>
                        <tr>
                            <td><strong>Python Version:</strong></td>
                            <td>3.13.5</td>
                        </tr>
                        <tr>
                            <td><strong>Database:</strong></td>
                            <td>MySQL</td>
                        </tr>
                        <tr>
                            <td><strong>Admin Role:</strong></td>
                            <td><span class="badge bg-primary">{admin_info['role']}</span></td>
                        </tr>
                    </table>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="table-card">
                    <h5 class="mb-3"><i class="fas fa-bell me-2 text-primary"></i>Quick Tips</h5>
                    <ul class="list-unstyled">
                        <li class="mb-2"><i class="fas fa-check-circle text-success me-2"></i>Add new doctors from the "Manage Doctors" section</li>
                        <li class="mb-2"><i class="fas fa-check-circle text-success me-2"></i>Set doctor schedules and consultation fees</li>
                        <li class="mb-2"><i class="fas fa-check-circle text-success me-2"></i>Monitor today's appointments</li>
                        <li class="mb-2"><i class="fas fa-check-circle text-success me-2"></i>Generate reports from the Reports section</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")