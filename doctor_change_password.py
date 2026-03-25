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

headers = []
session = SessionManager()
session.start_session()

cookie_header = session.get_cookie_header()
if cookie_header:
    headers.append(cookie_header)

if not session.is_logged_in() or session.get('user_type') != 'doctor':
    headers.append("Location: doctor_login.py")
    for h in headers:
        print(h)
    print()
    sys.exit()

doctor_info = session.get_user_info()
doctor_id = doctor_info['user_id']

form = cgi.FieldStorage()
action = form.getvalue('action', '')
errors = []
success = False

if action == 'change':
    current = form.getvalue('current', '')
    new = form.getvalue('new', '')
    confirm = form.getvalue('confirm', '')

    # Fetch current hash
    doctor = DatabaseOperations.execute_query(
        "SELECT password_hash FROM doctors WHERE doctor_id = %s",
        (doctor_id,),
        fetch_one=True
    )
    if not doctor:
        errors.append("User not found")
    else:
        if not bcrypt.checkpw(current.encode('utf-8'), doctor['password_hash'].encode('utf-8')):
            errors.append("Current password is incorrect")
        elif new != confirm:
            errors.append("New passwords do not match")
        elif len(new) < 8:
            errors.append("Password must be at least 8 characters")
        else:
            new_hash = bcrypt.hashpw(new.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            DatabaseOperations.execute_query(
                "UPDATE doctors SET password_hash = %s WHERE doctor_id = %s",
                (new_hash, doctor_id)
            )
            success = True

headers.append("Content-Type: text/html; charset=utf-8")
for hdr in headers:
    print(hdr)
print()

def h(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

print(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Change Password - Clinic Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
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
                <a href="doctor_profile.py" class="btn btn-outline-primary btn-sm me-2"><i class="fas fa-arrow-left"></i> Back</a>
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
    print('<div class="alert alert-success">Password changed successfully! <a href="doctor_profile.py">Return to Profile</a></div>')
else:
    if errors:
        print('<div class="alert alert-danger"><ul class="mb-0">')
        for e in errors:
            print(f'<li>{h(e)}</li>')
        print('</ul></div>')

    print("""
                <form method="post" action="doctor_change_password.py">
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
                        <a href="doctor_profile.py" class="btn btn-secondary me-2">Cancel</a>
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