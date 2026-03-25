#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


import sys
import os
import bcrypt
from datetime import datetime

# Force UTF-8 for output
sys.stdout.reconfigure(encoding='utf-8')

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
                # Avoid Unicode in output
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

# If already logged in, redirect to dashboard
if session.is_logged_in():
    print("Location: admin_dashboard.py")
    print()
    sys.exit()

# Get form data
form = cgi.FieldStorage()
action = form.getvalue('action', '')

errors = []
debug_info = []

if action == 'login':
    username = form.getvalue('username', '').strip()
    password = form.getvalue('password', '')
    
    if not username or not password:
        errors.append("Username and password are required")
    else:
        try:
            # Get admin from database
            query = "SELECT * FROM admins WHERE username = %s OR email = %s"
            admin = DatabaseOperations.execute_query(query, (username, username), fetch_one=True)
            
            if admin:
                debug_info.append(f"Admin found: {admin['username']}")
                
                # Verify password
                try:
                    if bcrypt.checkpw(password.encode('utf-8'), admin['password_hash'].encode('utf-8')):
                        debug_info.append("Password verification SUCCESS")
                        
                        # Login successful
                        session.login(
                            admin['admin_id'],
                            admin['full_name'],
                            admin['username'],
                            admin['role']
                        )
                        
                        # Update last login
                        try:
                            update_query = "UPDATE admins SET last_login = NOW() WHERE admin_id = %s"
                            DatabaseOperations.execute_query(update_query, (admin['admin_id'],))
                        except:
                            pass
                        
                        # Redirect
                        print("Location: admin_dashboard.py")
                        print()
                        sys.exit()
                    else:
                        errors.append("Invalid password")
                        debug_info.append("Password verification FAILED")
                except Exception as e:
                    errors.append(f"Password check error: {str(e)}")
                    debug_info.append(f"Password exception: {str(e)}")
            else:
                errors.append("Invalid username")
                debug_info.append(f"Admin not found: {username}")
        except Exception as e:
            errors.append(f"Database error: {str(e)}")
            debug_info.append(f"DB exception: {str(e)}")

# HTML Template (no Unicode characters)
print("Content-Type: text/html; charset=utf-8")
print()

today = datetime.now().year
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login - Clinic Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary: #2A5C82;
            --secondary: #4A90E2;
            --danger: #FF6B6B;
        }}
        body {{
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .login-container {{ max-width: 400px; width: 100%; }}
        .login-card {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        .login-header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .login-body {{ padding: 40px 30px; }}
        .form-control {{
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 12px 15px;
        }}
        .form-control:focus {{
            border-color: var(--primary);
            box-shadow: 0 0 0 0.2rem rgba(42, 92, 130, 0.25);
        }}
        .btn-login {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 14px;
            font-weight: 600;
            width: 100%;
        }}
        .btn-login:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(42, 92, 130, 0.3);
        }}
        .alert {{
            border-radius: 10px;
            padding: 15px 20px;
            margin-bottom: 25px;
        }}
        .alert-danger {{ background: #f8d7da; color: #721c24; border-left: 4px solid var(--danger); }}
        .alert-info {{ background: #d1ecf1; color: #0c5460; border-left: 4px solid var(--secondary); }}
        .debug-info {{ font-size: 0.8rem; margin-top: 10px; }}
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-card">
            <div class="login-header">
                <i class="fas fa-shield-alt fa-3x mb-3"></i>
                <h2><i class="fas fa-user-shield me-2"></i>Admin Login</h2>
                <p>Secure access for clinic administrators</p>
            </div>
            <div class="login-body">
""")

if errors:
    print('<div class="alert alert-danger"><i class="fas fa-exclamation-circle me-2"></i>')
    for error in errors:
        print(f'<div>{error}</div>')
    print('</div>')

if debug_info and action == 'login':
    print('<div class="alert alert-info"><i class="fas fa-info-circle me-2"></i>')
    print('<strong>Debug Info:</strong>')
    for info in debug_info:
        # Ensure info is ASCII-safe
        safe_info = info.encode('ascii', 'replace').decode('ascii')
        print(f'<div class="debug-info">{safe_info}</div>')
    print('</div>')

print(f"""
                <form method="post" action="admin_login.py">
                    <input type="hidden" name="action" value="login">
                    <div class="mb-4">
                        <label class="form-label fw-bold">
                            <i class="fas fa-user me-2 text-primary"></i>Username or Email
                        </label>
                        <input type="text" class="form-control" name="username" 
                               value="{username if 'username' in locals() else ''}" required>
                    </div>
                    <div class="mb-4">
                        <label class="form-label fw-bold">
                            <i class="fas fa-lock me-2 text-primary"></i>Password
                        </label>
                        <input type="password" class="form-control" name="password" required>
                    </div>
                    <button type="submit" class="btn btn-login mb-3">
                        <i class="fas fa-sign-in-alt me-2"></i>Login
                    </button>
                    <div class="back-link text-center">
                        <a href="index.py" class="text-decoration-none small">
                            <i class="fas fa-arrow-left me-1"></i>Back to Main Site
                        </a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
""")