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
    import  cgi
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

from session import SessionManager
from database import DatabaseOperations

# Start patient session
session = SessionManager()
session.start_session()

if not session.is_logged_in() or session.get('user_type') != 'patient':
    print("Location: patient_login.py")
    print()
    sys.exit()

patient_info = session.get_user_info()
patient_id = patient_info['user_id']

# Get patient details from database
patient = DatabaseOperations.execute_query(
    "SELECT * FROM patients WHERE patient_id = %s",
    (patient_id,),
    fetch_one=True
)

if not patient:
    # Something wrong, logout
    session.logout()
    print("Location: patient_login.py")
    print()
    sys.exit()

# Get appointment stats
appointment_stats = DatabaseOperations.execute_query(
    """SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN status = 'Scheduled' THEN 1 ELSE 0 END) as upcoming,
        SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed
       FROM appointments WHERE patient_id = %s""",
    (patient_id,),
    fetch_one=True
)

print("Content-Type: text/html; charset=utf-8")
print()

today = datetime.now().strftime("%Y-%m-%d")
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Profile - Clinic Management System</title>
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
        
        body {{
            font-family: 'Inter', sans-serif;
            background: #f4f6f9;
        }}
        
        .navbar {{
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .profile-container {{
            max-width: 1000px;
            margin: 100px auto 50px;
            padding: 0 20px;
        }}
        
        .profile-header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(42,92,130,0.3);
        }}
        
        .profile-avatar {{
            width: 100px;
            height: 100px;
            background: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--primary);
            font-size: 3rem;
            font-weight: bold;
            margin-bottom: 20px;
            border: 4px solid rgba(255,255,255,0.3);
        }}
        
        .info-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        
        .info-label {{
            font-weight: 600;
            color: var(--dark);
            margin-bottom: 5px;
        }}
        
        .info-value {{
            color: #666;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }}
        
        .stat-card {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-number {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary);
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9rem;
        }}
        
        .btn-edit {{
            background: white;
            color: var(--primary);
            border: 2px solid white;
            border-radius: 10px;
            padding: 10px 25px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.3s ease;
        }}
        
        .btn-edit:hover {{
            background: transparent;
            color: white;
        }}
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-light fixed-top">
        <div class="container">
            <a class="navbar-brand" href="index.py">
                <i class="fas fa-clinic-medical me-2 text-primary"></i>
                ClinicCare
            </a>
            <div class="ms-auto d-flex align-items-center">
                <span class="me-3">
                    <i class="fas fa-user me-2 text-primary"></i>
                    {patient_info['full_name']}
                </span>
                <a href="patient_dashboard.py" class="btn btn-outline-primary btn-sm me-2">
                    <i class="fas fa-tachometer-alt"></i> Dashboard
                </a>
                <a href="logout.py" class="btn btn-outline-danger btn-sm">
                    <i class="fas fa-sign-out-alt"></i> Logout
                </a>
            </div>
        </div>
    </nav>
    
    <div class="profile-container">
        <div class="profile-header">
            <div class="row align-items-center">
                <div class="col-md-2 text-center">
                    <div class="profile-avatar mx-auto">
                        {patient['full_name'][0]}
                    </div>
                </div>
                <div class="col-md-8">
                    <h2 class="mb-2">{patient['full_name']}</h2>
                    <p class="mb-1">
                        <i class="fas fa-id-card me-2"></i>
                        Registration: {patient['reg_number']}
                    </p>
                    <p class="mb-1">
                        <i class="fas fa-envelope me-2"></i>
                        {patient['email']}
                    </p>
                    <p class="mb-0">
                        <i class="fas fa-phone me-2"></i>
                        {patient['phone']}
                    </p>
                </div>
                <div class="col-md-2 text-end">
                    <a href="patient_edit_profile.py" class="btn-edit">
                        <i class="fas fa-edit me-2"></i>Edit
                    </a>
                </div>
            </div>
        </div>
        
        <!-- Statistics -->
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="stat-card">
                    <div class="stat-number">{appointment_stats['total'] or 0}</div>
                    <div class="stat-label">Total Appointments</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="stat-card">
                    <div class="stat-number">{appointment_stats['upcoming'] or 0}</div>
                    <div class="stat-label">Upcoming</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="stat-card">
                    <div class="stat-number">{appointment_stats['completed'] or 0}</div>
                    <div class="stat-label">Completed</div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <!-- Personal Information -->
            <div class="col-md-6">
                <div class="info-card">
                    <h5 class="mb-4"><i class="fas fa-user me-2 text-primary"></i>Personal Information</h5>
                    <div class="row">
                        <div class="col-md-5 info-label">Date of Birth:</div>
                        <div class="col-md-7 info-value">{patient['date_of_birth']}</div>
                    </div>
                    <div class="row">
                        <div class="col-md-5 info-label">Blood Group:</div>
                        <div class="col-md-7 info-value">{patient['blood_group'] or 'Not specified'}</div>
                    </div>
                    <div class="row">
                        <div class="col-md-5 info-label">Address:</div>
                        <div class="col-md-7 info-value">{patient['address'] or 'Not provided'}</div>
                    </div>
                </div>
            </div>
            
            <!-- Contact Information -->
            <div class="col-md-6">
                <div class="info-card">
                    <h5 class="mb-4"><i class="fas fa-address-book me-2 text-primary"></i>Contact Information</h5>
                    <div class="row">
                        <div class="col-md-5 info-label">Email:</div>
                        <div class="col-md-7 info-value">{patient['email']}</div>
                    </div>
                    <div class="row">
                        <div class="col-md-5 info-label">Phone:</div>
                        <div class="col-md-7 info-value">{patient['phone']}</div>
                    </div>
                    <div class="row">
                        <div class="col-md-5 info-label">Emergency Contact:</div>
                        <div class="col-md-7 info-value">{patient['emergency_contact'] or 'Not provided'}</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Quick Actions -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="info-card">
                    <h5 class="mb-3"><i class="fas fa-tasks me-2 text-primary"></i>Quick Actions</h5>
                    <div class="d-flex gap-2">
                        <a href="book_appointment.py" class="btn btn-primary">
                            <i class="fas fa-calendar-plus me-2"></i>Book Appointment
                        </a>
                        <a href="my_appointments.py" class="btn btn-outline-primary">
                            <i class="fas fa-list me-2"></i>My Appointments
                        </a>
                        <a href="patient_change_password.py" class="btn btn-outline-secondary">
                            <i class="fas fa-key me-2"></i>Change Password
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")