#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


import sys
import os
import bcrypt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Python 3.13+ compatibility for removed cgi/cgitb
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
                # Replace non-ASCII to avoid encoding errors
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

# Add session cookie header if any
cookie_header = session.get_cookie_header()
if cookie_header:
    headers.append(cookie_header)

# If already logged in as doctor, redirect to dashboard
if session.is_logged_in() and session.get('user_type') == 'doctor':
    headers.append("Location: doctor_dashboard.py")
    for h in headers:
        print(h)
    print()
    sys.exit()

# ----- Process login -----
form = cgi.FieldStorage()
action = form.getvalue('action', '')
errors = []

if action == 'login':
    license_number = form.getvalue('license_number', '').strip()
    password = form.getvalue('password', '')

    if not license_number or not password:
        errors.append("License number and password are required")
    else:
        # Fetch doctor by license number (exact match)
        doctor = DatabaseOperations.execute_query(
            "SELECT * FROM doctors WHERE license_number = %s",
            (license_number,),
            fetch_one=True
        )
        # Debug output (visible in Apache error log)
        sys.stderr.write(f"Login attempt for license: {license_number}\n")
        if doctor:
            sys.stderr.write(f"Doctor found: {doctor['full_name']}, hash: {doctor['password_hash'][:20]}...\n")
            try:
                # Verify password using bcrypt
                if bcrypt.checkpw(password.encode('utf-8'), doctor['password_hash'].encode('utf-8')):
                    # Login successful
                    session.login(
                        doctor['doctor_id'],
                        'doctor',
                        doctor['full_name'],
                        doctor['email']
                    )
                    # Get updated cookie after login (session ID regenerated)
                    new_cookie = session.get_cookie_header()
                    if new_cookie:
                        headers.append(new_cookie)
                    headers.append("Location: doctor_dashboard.py")
                    for h in headers:
                        print(h)
                    print()
                    sys.exit()
                else:
                    errors.append("Invalid license number or password")
                    sys.stderr.write("Password verification failed\n")
            except Exception as e:
                errors.append("Password verification error")
                sys.stderr.write(f"bcrypt exception: {e}\n")
        else:
            errors.append("Invalid license number or password")
            sys.stderr.write("Doctor not found\n")

# ----- Output login form (with errors) -----
headers.append("Content-Type: text/html; charset=utf-8")
for h in headers:
    print(h)
print()

def h(s):
    """Escape HTML special characters."""
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

print("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Doctor Login - Clinic Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #2A5C82;
            --secondary: #4A90E2;
            --danger: #FF6B6B;
            --dark: #2C3E50;
            --gradient-primary: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        }
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .login-container {
            max-width: 450px;
            width: 100%;
        }
        .login-card {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .login-header {
            background: var(--gradient-primary);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        .login-header h2 {
            font-weight: 700;
            margin-bottom: 10px;
        }
        .login-header p {
            opacity: 0.9;
            margin: 0;
        }
        .login-body {
            padding: 40px 30px;
        }
        .form-label {
            font-weight: 500;
            color: var(--dark);
            margin-bottom: 5px;
        }
        .form-control {
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 12px 15px;
            transition: 0.3s;
        }
        .form-control:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 0.2rem rgba(42,92,130,0.25);
        }
        .btn-login {
            background: var(--gradient-primary);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 14px;
            font-weight: 600;
            width: 100%;
            transition: 0.3s;
        }
        .btn-login:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(42,92,130,0.3);
        }
        .alert {
            border-radius: 10px;
            border: none;
            padding: 15px 20px;
            margin-bottom: 25px;
        }
        .alert-danger {
            background: #f8d7da;
            color: #721c24;
            border-left: 4px solid var(--danger);
        }
        .back-link {
            text-align: center;
            margin-top: 20px;
        }
        .back-link a {
            color: #666;
            text-decoration: none;
            font-size: 0.9rem;
        }
        .back-link a:hover {
            color: var(--primary);
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-card">
            <div class="login-header">
                <i class="fas fa-user-md fa-3x mb-3"></i>
                <h2><i class="fas fa-user-md me-2"></i>Doctor Login</h2>
                <p>Access your clinical dashboard</p>
            </div>
            <div class="login-body">
""")

if errors:
    print('<div class="alert alert-danger"><i class="fas fa-exclamation-circle me-2"></i>')
    for e in errors:
        print(f'<div>{h(e)}</div>')
    print('</div>')

print("""
                <form method="post" action="doctor_login.py">
                    <input type="hidden" name="action" value="login">
                    <div class="mb-4">
                        <label class="form-label fw-bold">
                            <i class="fas fa-id-card me-2 text-primary"></i>License Number
                        </label>
                        <input type="text" class="form-control" name="license_number" required>
                    </div>
                    <div class="mb-4">
                        <label class="form-label fw-bold">
                            <i class="fas fa-lock me-2 text-primary"></i>Password
                        </label>
                        <input type="password" class="form-control" name="password" required>
                    </div>
                    <button type="submit" class="btn btn-login mb-3">
                        <i class="fas fa-sign-in-alt me-2"></i>Login to Dashboard
                    </button>
                    <div class="back-link">
                        <a href="index.py"><i class="fas fa-arrow-left me-1"></i>Back to Main Site</a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
""")