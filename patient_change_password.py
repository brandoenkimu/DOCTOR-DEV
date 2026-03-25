#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


import sys
import os
import bcrypt

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

from session import SessionManager
from database import DatabaseOperations

session = SessionManager()
session.start_session()

if not session.is_logged_in() or session.get('user_type') != 'patient':
    print("Location: patient_login.py")
    print()
    sys.exit()

patient_info = session.get_user_info()
patient_id = patient_info['user_id']

form = cgi.FieldStorage()
action = form.getvalue('action', '')

errors = []
success = False

if action == 'change':
    current = form.getvalue('current', '')
    new = form.getvalue('new', '')
    confirm = form.getvalue('confirm', '')

    # Get current hash
    patient = DatabaseOperations.execute_query(
        "SELECT password_hash FROM patients WHERE patient_id = %s",
        (patient_id,),
        fetch_one=True
    )

    if not patient:
        errors.append("User not found")
    else:
        if not bcrypt.checkpw(current.encode('utf-8'), patient['password_hash'].encode('utf-8')):
            errors.append("Current password is incorrect")
        elif new != confirm:
            errors.append("New passwords do not match")
        elif len(new) < 8:
            errors.append("Password must be at least 8 characters")
        else:
            new_hash = bcrypt.hashpw(new.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            DatabaseOperations.execute_query(
                "UPDATE patients SET password_hash = %s WHERE patient_id = %s",
                (new_hash, patient_id)
            )
            success = True

print("Content-Type: text/html; charset=utf-8")
print()

print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Change Password - Clinic Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary: #2A5C82;
            --secondary: #4A90E2;
            --danger: #FF6B6B;
            --dark: #2C3E50;
        }}
        body {{ font-family: 'Inter', sans-serif; background: #f4f6f9; }}
        .navbar {{ background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .container {{ max-width: 500px; margin-top: 100px; }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light fixed-top">
        <div class="container">
            <a class="navbar-brand" href="index.py"><i class="fas fa-clinic-medical me-2 text-primary"></i>ClinicCare</a>
            <div class="ms-auto">
                <a href="patient_profile.py" class="btn btn-outline-primary btn-sm me-2"><i class="fas fa-arrow-left"></i> Back</a>
                <a href="logout.py" class="btn btn-outline-danger btn-sm">Logout</a>
            </div>
        </div>
    </nav>
    
    <div class="container">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h4 class="mb-0"><i class="fas fa-key me-2"></i>Change Password</h4>
            </div>
            <div class="card-body">
""")

if success:
    print('<div class="alert alert-success">Password changed successfully! <a href="patient_profile.py">Return to Profile</a></div>')
else:
    if errors:
        print('<div class="alert alert-danger"><ul class="mb-0">')
        for e in errors:
            print(f'<li>{e}</li>')
        print('</ul></div>')

    print("""
                <form method="post" action="patient_change_password.py">
                    <input type="hidden" name="action" value="change">
                    <div class="mb-3">
                        <label class="form-label">Current Password</label>
                        <input type="password" class="form-control" name="current" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">New Password</label>
                        <input type="password" class="form-control" name="new" required minlength="8">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Confirm New Password</label>
                        <input type="password" class="form-control" name="confirm" required>
                    </div>
                    <div class="text-end">
                        <a href="patient_profile.py" class="btn btn-secondary me-2">Cancel</a>
                        <button type="submit" class="btn btn-primary">Change Password</button>
                    </div>
                </form>
    """)

print("""
            </div>
        </div>
    </div>
</body>
</html>
""")