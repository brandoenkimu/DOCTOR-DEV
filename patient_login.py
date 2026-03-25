#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Patient Login Module
Handles patient authentication with session management
"""

import cgi
import cgitb
import os
import sys
import bcrypt

cgitb.enable()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from session import SessionManager
from database import DatabaseOperations
from validation import Validator

# --- HEADER COLLECTION ---
headers = []

# Start session
session = SessionManager()
session.start_session()

# Get cookie header (if any)
cookie_header = session.get_cookie_header()
if cookie_header:
    headers.append(cookie_header)

# If already logged in, redirect to dashboard
if session.is_logged_in():
    headers.append("Location: dashboard.py")
    for h in headers:
        print(h)
    print()  # blank line after headers
    sys.exit()

# Get form data
form = cgi.FieldStorage()
action = form.getvalue('action', '')

# Initialize variables
errors = []
success = False

if action == 'login':
    reg_number = form.getvalue('reg_number', '')
    password = form.getvalue('password', '')
    remember = form.getvalue('remember', '')
    
    # Validate input
    if not reg_number:
        errors.append("Registration number is required")
    if not password:
        errors.append("Password is required")
    
    # Authenticate user
    if not errors:
        patient = DatabaseOperations.get_patient_by_reg_number(reg_number)
        
        if patient and bcrypt.checkpw(
            password.encode('utf-8'), 
            patient['password_hash'].encode('utf-8')
        ):
            # Login successful
            session.login(
                patient['patient_id'],
                'patient',
                patient['full_name'],
                patient['email']
            )
            
            # Set remember me cookie if requested
            if remember:
                # In production, set a secure remember me token
                pass
            
            # Get updated cookie header after login (regenerated session)
            new_cookie = session.get_cookie_header()
            if new_cookie:
                headers.append(new_cookie)
            
            # Redirect to index
            headers.append("Location: index.py")
            for h in headers:
                print(h)
            print()
            sys.exit()
        else:
            errors.append("Invalid registration number or password")

# If we reach here, we need to output the login form (with possible errors)
headers.append("Content-Type: text/html; charset=utf-8")

# Print all headers
for h in headers:
    print(h)
print()  # blank line after headers

# HTML Template (starts here)
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Patient Login - Clinic Management System</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome 6 -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Custom CSS -->
    <style>
        :root {{
            --primary-color: #2A5C82;
            --secondary-color: #4A90E2;
            --accent-color: #50C878;
            --danger-color: #FF6B6B;
            --dark-color: #2C3E50;
            --light-color: #F8F9FA;
            --gradient-primary: linear-gradient(135deg, #2A5C82 0%, #4A90E2 100%);
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
        
        .login-container {{
            max-width: 450px;
            width: 100%;
            margin: 0 auto;
        }}
        
        .login-card {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            overflow: hidden;
            animation: slideIn 0.5s ease;
        }}
        
        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .login-header {{
            background: var(--gradient-primary);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        
        .login-header h2 {{
            font-weight: 700;
            margin-bottom: 10px;
        }}
        
        .login-header p {{
            opacity: 0.9;
            margin: 0;
        }}
        
        .login-body {{
            padding: 40px 30px;
        }}
        
        .form-label {{
            font-weight: 500;
            color: var(--dark-color);
            margin-bottom: 5px;
        }}
        
        .form-control {{
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 12px 15px;
            font-size: 0.95rem;
            transition: all 0.3s ease;
        }}
        
        .form-control:focus {{
            border-color: var(--primary-color);
            box-shadow: 0 0 0 0.2rem rgba(42, 92, 130, 0.25);
        }}
        
        .form-control.is-invalid {{
            border-color: var(--danger-color);
        }}
        
        .btn-login {{
            background: var(--gradient-primary);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 14px;
            font-weight: 600;
            font-size: 1.1rem;
            width: 100%;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 20px;
        }}
        
        .btn-login:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(42, 92, 130, 0.3);
            color: white;
        }}
        
        .btn-login:active {{
            transform: translateY(0);
        }}
        
        .alert {{
            border-radius: 10px;
            border: none;
            padding: 15px 20px;
            margin-bottom: 25px;
            animation: fadeIn 0.3s ease;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        .alert-danger {{
            background: #f8d7da;
            color: #721c24;
            border-left: 4px solid var(--danger-color);
        }}
        
        .register-link {{
            text-align: center;
            margin-top: 25px;
            color: #666;
        }}
        
        .register-link a {{
            color: var(--primary-color);
            text-decoration: none;
            font-weight: 600;
        }}
        
        .register-link a:hover {{
            text-decoration: underline;
        }}
        
        .forgot-password {{
            text-align: right;
            margin-top: 10px;
        }}
        
        .forgot-password a {{
            color: #666;
            text-decoration: none;
            font-size: 0.9rem;
        }}
        
        .forgot-password a:hover {{
            color: var(--primary-color);
        }}
        
        .form-check-input:checked {{
            background-color: var(--primary-color);
            border-color: var(--primary-color);
        }}
        
        .spinner-border {{
            width: 1.5rem;
            height: 1.5rem;
            margin-right: 10px;
        }}
        
        /* Doctor Login Link */
        .doctor-link {{
            text-align: center;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #e0e0e0;
        }}
        
        .doctor-link a {{
            color: var(--primary-color);
            text-decoration: none;
            font-weight: 500;
        }}
        
        .doctor-link a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-card">
            <div class="login-header">
                <h2><i class="fas fa-user me-2"></i>Patient Login</h2>
                <p>Access your healthcare portal</p>
            </div>
            
            <div class="login-body">
""")

if errors:
    print('<div class="alert alert-danger"><i class="fas fa-exclamation-circle me-2"></i>')
    for error in errors:
        print(f'<div>{error}</div>')
    print('</div>')

print(f"""
                <form method="post" action="patient_login.py" id="loginForm">
                    <input type="hidden" name="action" value="login">
                    
                    <div class="mb-4">
                        <label class="form-label">
                            <i class="fas fa-id-card me-2 text-primary"></i>Registration Number
                        </label>
                        <input type="text" 
                               class="form-control" 
                               name="reg_number" 
                               placeholder="Enter your registration number (e.g., PAT001)"
                               value="{form.getvalue('reg_number', '')}"
                               required>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">
                            <i class="fas fa-lock me-2 text-primary"></i>Password
                        </label>
                        <input type="password" 
                               class="form-control" 
                               name="password" 
                               placeholder="Enter your password"
                               required>
                    </div>
                    
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <div class="form-check">
                            <input type="checkbox" class="form-check-input" id="remember" name="remember">
                            <label class="form-check-label" for="remember">Remember me</label>
                        </div>
                        <div class="forgot-password">
                            <a href="forgot_password.py"><i class="fas fa-question-circle me-1"></i>Forgot Password?</a>
                        </div>
                    </div>
                    
                    <button type="submit" class="btn btn-login" id="submitBtn">
                        <span class="spinner-border spinner-border-sm d-none" id="spinner" role="status"></span>
                        <span id="btnText"><i class="fas fa-sign-in-alt me-2"></i>Login</span>
                    </button>
                    
                    <div class="register-link">
                        Don't have an account? <a href="patient_register.py">Register here</a>
                    </div>
                    
                    <div class="doctor-link">
                        <i class="fas fa-user-md me-2"></i>
                        <a href="doctor_login.py">Login as Doctor</a>
                    </div>
                </form>
            </div>
        </div>
    </div>
    
    <script>
        const form = document.getElementById('loginForm');
        const submitBtn = document.getElementById('submitBtn');
        const spinner = document.getElementById('spinner');
        const btnText = document.getElementById('btnText');
        
        form.addEventListener('submit', function(e) {{
            // Show loading state
            submitBtn.disabled = true;
            spinner.classList.remove('d-none');
            btnText.innerHTML = 'Logging in...';
        }});
        
        // Add input validation
        const regNumber = document.querySelector('input[name="reg_number"]');
        regNumber.addEventListener('input', function() {{
            this.classList.remove('is-invalid');
        }});
        
        // Auto-format registration number
        regNumber.addEventListener('blur', function() {{
            let value = this.value.toUpperCase();
            if (value && !value.startsWith('PAT')) {{
                value = 'PAT' + value.replace(/[^0-9]/g, '');
            }}
            this.value = value;
        }});
    </script>
</body>
</html>
""")