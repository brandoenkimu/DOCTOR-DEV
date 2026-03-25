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

session = AdminSession()
session.start_session()

if not session.is_logged_in():
    print("Location: admin_login.py")
    print()
    sys.exit()

admin_info = session.get_admin_info()

form = cgi.FieldStorage()
action = form.getvalue('action', '')
message = ''

if action == 'change_password':
    current = form.getvalue('current', '')
    new = form.getvalue('new', '')
    confirm = form.getvalue('confirm', '')
    
    # Verify current password
    admin = DatabaseOperations.execute_query("SELECT * FROM admins WHERE admin_id = %s", (admin_info['admin_id'],), fetch_one=True)
    if admin and bcrypt.checkpw(current.encode('utf-8'), admin['password_hash'].encode('utf-8')):
        if new == confirm and len(new) >= 8:
            new_hash = bcrypt.hashpw(new.encode('utf-8'), bcrypt.gensalt()).decode()
            DatabaseOperations.execute_query("UPDATE admins SET password_hash = %s WHERE admin_id = %s", (new_hash, admin_info['admin_id']))
            message = '<div class="alert alert-success">Password changed successfully.</div>'
        else:
            message = '<div class="alert alert-danger">New password must match and be at least 8 characters.</div>'
    else:
        message = '<div class="alert alert-danger">Current password is incorrect.</div>'

elif action == 'update_settings':
    # You can store settings in a new table `settings` or in config file.
    # For simplicity, we'll just show a message.
    message = '<div class="alert alert-info">Settings saved (simulated).</div>'

print("Content-Type: text/html; charset=utf-8")
print()

print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Settings - Clinic Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
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
        .card-custom {{ background: white; border-radius: 15px; padding: 25px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); margin-bottom: 20px; }}
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
            <li><a href="admin_reports.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-chart-bar me-2"></i>Reports</a></li>
            <li><a href="admin_settings.py" class="text-white text-decoration-none d-block p-2 active"><i class="fas fa-cog me-2"></i>Settings</a></li>
            <li><hr class="bg-white opacity-25"></li>
            <li><a href="admin_logout.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-sign-out-alt me-2"></i>Logout</a></li>
        </ul>
    </div>
    
    <div class="main-content">
        <div class="top-bar">
            <h4 class="mb-0"><i class="fas fa-cog me-2 text-primary"></i>System Settings</h4>
        </div>
        
        {message}
        
        <div class="row">
            <div class="col-md-6">
                <div class="card-custom">
                    <h5 class="mb-4"><i class="fas fa-key me-2 text-primary"></i>Change Password</h5>
                    <form method="post">
                        <input type="hidden" name="action" value="change_password">
                        <div class="mb-3">
                            <label class="form-label">Current Password</label>
                            <input type="password" name="current" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">New Password</label>
                            <input type="password" name="new" class="form-control" required minlength="8">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Confirm New Password</label>
                            <input type="password" name="confirm" class="form-control" required>
                        </div>
                        <button type="submit" class="btn btn-primary-custom"><i class="fas fa-save me-2"></i>Update Password</button>
                    </form>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card-custom">
                    <h5 class="mb-4"><i class="fas fa-clock me-2 text-primary"></i>Clinic Hours</h5>
                    <form method="post">
                        <input type="hidden" name="action" value="update_settings">
                        <div class="mb-3">
                            <label class="form-label">Opening Time</label>
                            <input type="time" name="open" class="form-control" value="08:00">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Closing Time</label>
                            <input type="time" name="close" class="form-control" value="20:00">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Lunch Break Start</label>
                            <input type="time" name="break_start" class="form-control" value="13:00">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Lunch Break End</label>
                            <input type="time" name="break_end" class="form-control" value="14:00">
                        </div>
                        <button type="submit" class="btn btn-primary-custom"><i class="fas fa-save me-2"></i>Save Settings</button>
                    </form>
                </div>
            </div>
        </div>
        
        <div class="card-custom">
            <h5 class="mb-4"><i class="fas fa-info-circle me-2 text-primary"></i>System Information</h5>
            <table class="table table-borderless">
                <tr>
                    <td>Python Version:</td>
                    <td>3.13.5</td>
                </tr>
                <tr>
                    <td>Database:</td>
                    <td>MySQL</td>
                </tr>
                <tr>
                    <td>Server Time:</td>
                    <td>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
                </tr>
                <tr>
                    <td>Admin:</td>
                    <td>{admin_info['full_name']} ({admin_info['username']})</td>
                </tr>
            </table>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")