#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# Python 3.13 compatibility - CLEAN IMPORT SECTION
import sys
import os
import hashlib
import bcrypt
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Handle CGI modules for Python 3.13
try:
    import cgi
    import cgitb
except ImportError:
    import cgi
    # Simple cgitb replacement
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

# Import your custom modules
from session import SessionManager
from database import DatabaseOperations
from validation import Validator

# COLLECT ALL HEADERS FIRST - THEN PRINT THEM TOGETHER
headers = []

# Start session
session = SessionManager()
session.start_session()

# Collect session cookie headers
if hasattr(session, '_get_cookie_headers'):
    cookie_headers = session._get_cookie_headers()
    if cookie_headers:
        headers.extend(cookie_headers)

# Add content-type header
headers.append("Content-Type: text/html; charset=utf-8")

# If already logged in, redirect to dashboard
if session.is_logged_in():
    headers.append("Location: dashboard.py")
    # Print all headers at once
    for header in headers:
        print(header)
    print()  # Blank line after headers
    sys.exit()

# Get form data
form = cgi.FieldStorage()
action = form.getvalue('action', '')

# Initialize variables
errors = []
success = False
form_data = {}

if action == 'register':
    # Get form values
    form_data = {
        'reg_number': form.getvalue('reg_number', ''),
        'full_name': form.getvalue('full_name', ''),
        'email': form.getvalue('email', ''),
        'phone': form.getvalue('phone', ''),
        'password': form.getvalue('password', ''),
        'confirm_password': form.getvalue('confirm_password', ''),
        'date_of_birth': form.getvalue('date_of_birth', ''),
        'address': form.getvalue('address', ''),
        'emergency_contact': form.getvalue('emergency_contact', ''),
        'blood_group': form.getvalue('blood_group', '')
    }
    
    # Validate form data
    errors = Validator.validate_patient_registration(form_data)
    
    # Check if registration number already exists
    if not errors:
        existing = DatabaseOperations.get_patient_by_reg_number(form_data['reg_number'])
        if existing:
            errors.append("Registration number already exists")
    
    # Check if email already exists
    if not errors:
        existing = DatabaseOperations.get_patient_by_email(form_data['email'])
        if existing:
            errors.append("Email already registered")
    
    # If no errors, create patient account
    if not errors:
        try:
            # Hash password with bcrypt
            password_hash = bcrypt.hashpw(
                form_data['password'].encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            
            # Prepare patient data
            patient_data = {
                'reg_number': form_data['reg_number'],
                'full_name': form_data['full_name'],
                'email': form_data['email'],
                'phone': form_data['phone'],
                'password_hash': password_hash,
                'date_of_birth': form_data['date_of_birth'],
                'address': form_data['address'],
                'emergency_contact': form_data['emergency_contact'],
                'blood_group': form_data['blood_group']
            }
            
            # Create patient
            patient_id = DatabaseOperations.create_patient(patient_data)
            
            if patient_id:
                success = True
                # Auto-login after registration
                session.login(
                    patient_id, 
                    'patient', 
                    form_data['full_name'], 
                    form_data['email']
                )
                # Add meta refresh for redirect
                headers.append("Refresh: 2; url=index.py")
        except Exception as e:
            errors.append(f"Registration failed: {str(e)}")

# NOW PRINT ALL HEADERS AT ONCE
for header in headers:
    print(header)
print()  # Blank line after headers

# Get today's date for max attribute
today = datetime.now().date()

# HTML Template (continued)
print(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Patient Registration - Clinic Management System</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome 6 -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
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
        
        .register-container {{
            max-width: 900px;
            width: 100%;
            margin: 0 auto;
        }}
        
        .register-card {{
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
        
        .register-header {{
            background: var(--gradient-primary);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .register-header h2 {{
            font-weight: 700;
            margin-bottom: 10px;
        }}
        
        .register-header p {{
            opacity: 0.9;
            margin: 0;
        }}
        
        .register-body {{
            padding: 40px;
        }}
        
        .form-label {{
            font-weight: 500;
            color: var(--dark-color);
            margin-bottom: 5px;
        }}
        
        .form-control, .form-select {{
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 12px 15px;
            font-size: 0.95rem;
            transition: all 0.3s ease;
        }}
        
        .form-control:focus, .form-select:focus {{
            border-color: var(--primary-color);
            box-shadow: 0 0 0 0.2rem rgba(42, 92, 130, 0.25);
        }}
        
        .btn-register {{
            background: var(--gradient-primary);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 15px;
            font-weight: 600;
            font-size: 1.1rem;
            width: 100%;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .btn-register:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(42, 92, 130, 0.3);
        }}
        
        .alert {{
            border-radius: 10px;
            border: none;
            padding: 15px 20px;
            margin-bottom: 25px;
        }}
        
        .alert-success {{
            background: #d4edda;
            color: #155724;
            border-left: 4px solid #28a745;
        }}
        
        .alert-danger {{
            background: #f8d7da;
            color: #721c24;
            border-left: 4px solid var(--danger-color);
        }}
        
        .password-strength {{
            height: 5px;
            background: #e0e0e0;
            border-radius: 5px;
            margin-top: 10px;
            overflow: hidden;
        }}
        
        .password-strength-bar {{
            height: 100%;
            width: 0;
            transition: all 0.3s ease;
        }}
        
        .strength-weak {{ background: #dc3545; width: 33.33%; }}
        .strength-medium {{ background: #ffc107; width: 66.66%; }}
        .strength-strong {{ background: #28a745; width: 100%; }}
        
        .login-link {{
            text-align: center;
            margin-top: 20px;
            color: #666;
        }}
        
        .login-link a {{
            color: var(--primary-color);
            text-decoration: none;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="register-container">
        <div class="register-card">
            <div class="register-header">
                <h2><i class="fas fa-user-plus me-2"></i>Patient Registration</h2>
                <p>Create your account to access our healthcare services</p>
            </div>
            
            <div class="register-body">
""")

if success:
    print("""
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    Registration successful! Redirecting to dashboard...
                </div>
    """)

if errors:
    print('<div class="alert alert-danger"><i class="fas fa-exclamation-circle me-2"></i>')
    for error in errors:
        print(f'<div>{error}</div>')
    print('</div>')

# Escape form data for HTML
reg_number = form_data.get('reg_number', '').replace('"', '&quot;')
full_name = form_data.get('full_name', '').replace('"', '&quot;')
email = form_data.get('email', '').replace('"', '&quot;')
phone = form_data.get('phone', '').replace('"', '&quot;')
address = form_data.get('address', '').replace('"', '&quot;')
emergency_contact = form_data.get('emergency_contact', '').replace('"', '&quot;')

print(f"""
                <form method="post" action="patient_register.py" id="registerForm">
                    <input type="hidden" name="action" value="register">
                    
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">
                                <i class="fas fa-id-card me-2 text-primary"></i>Registration Number *
                            </label>
                            <input type="text" 
                                   class="form-control" 
                                   name="reg_number" 
                                   value="{reg_number}"
                                   placeholder="e.g., PAT001"
                                   pattern="PAT[0-9]{{3}}"
                                   title="Format: PAT followed by 3 digits (e.g., PAT001)"
                                   required>
                            <small class="text-muted">Format: PAT followed by 3 digits</small>
                        </div>
                        
                        <div class="col-md-6 mb-3">
                            <label class="form-label">
                                <i class="fas fa-user me-2 text-primary"></i>Full Name *
                            </label>
                            <input type="text" 
                                   class="form-control" 
                                   name="full_name" 
                                   value="{full_name}"
                                   placeholder="Enter your full name"
                                   required>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">
                                <i class="fas fa-envelope me-2 text-primary"></i>Email Address *
                            </label>
                            <input type="email" 
                                   class="form-control" 
                                   name="email" 
                                   value="{email}"
                                   placeholder="you@example.com"
                                   required>
                        </div>
                        
                        <div class="col-md-6 mb-3">
                            <label class="form-label">
                                <i class="fas fa-phone me-2 text-primary"></i>Phone Number *
                            </label>
                            <input type="tel" 
                                   class="form-control" 
                                   name="phone" 
                                   value="{phone}"
                                   placeholder="+254XXXXXXXXX"
                                   pattern="\+254[0-9]{{9}}"
                                   title="Format: +254 followed by 9 digits"
                                   required>
                            <small class="text-muted">Format: +254XXXXXXXXX</small>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">
                                <i class="fas fa-lock me-2 text-primary"></i>Password *
                            </label>
                            <input type="password" 
                                   class="form-control" 
                                   name="password" 
                                   id="password"
                                   placeholder="Create a strong password"
                                   minlength="8"
                                   required>
                            <div class="password-strength mt-2">
                                <div class="password-strength-bar" id="strengthBar"></div>
                            </div>
                            <small class="text-muted">Minimum 8 characters with uppercase, lowercase & number</small>
                        </div>
                        
                        <div class="col-md-6 mb-3">
                            <label class="form-label">
                                <i class="fas fa-lock me-2 text-primary"></i>Confirm Password *
                            </label>
                            <input type="password" 
                                   class="form-control" 
                                   name="confirm_password" 
                                   id="confirm_password"
                                   placeholder="Re-enter your password"
                                   required>
                            <div class="invalid-feedback" id="passwordMatch"></div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">
                                <i class="fas fa-calendar me-2 text-primary"></i>Date of Birth *
                            </label>
                            <input type="date" 
                                   class="form-control" 
                                   name="date_of_birth" 
                                   value="{form_data.get('date_of_birth', '')}"
                                   max="{today}"
                                   required>
                        </div>
                        
                        <div class="col-md-6 mb-3">
                            <label class="form-label">
                                <i class="fas fa-tint me-2 text-primary"></i>Blood Group
                            </label>
                            <select class="form-select" name="blood_group">
                                <option value="">Select Blood Group</option>
                                <option value="A+" {"selected" if form_data.get('blood_group') == 'A+' else ""}>A+</option>
                                <option value="A-" {"selected" if form_data.get('blood_group') == 'A-' else ""}>A-</option>
                                <option value="B+" {"selected" if form_data.get('blood_group') == 'B+' else ""}>B+</option>
                                <option value="B-" {"selected" if form_data.get('blood_group') == 'B-' else ""}>B-</option>
                                <option value="O+" {"selected" if form_data.get('blood_group') == 'O+' else ""}>O+</option>
                                <option value="O-" {"selected" if form_data.get('blood_group') == 'O-' else ""}>O-</option>
                                <option value="AB+" {"selected" if form_data.get('blood_group') == 'AB+' else ""}>AB+</option>
                                <option value="AB-" {"selected" if form_data.get('blood_group') == 'AB-' else ""}>AB-</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">
                            <i class="fas fa-map-marker-alt me-2 text-primary"></i>Address
                        </label>
                        <textarea class="form-control" 
                                  name="address" 
                                  rows="2"
                                  placeholder="Your residential address">{address}</textarea>
                    </div>
                    
                    <div class="mb-4">
                        <label class="form-label">
                            <i class="fas fa-phone-alt me-2 text-primary"></i>Emergency Contact
                        </label>
                        <input type="tel" 
                               class="form-control" 
                               name="emergency_contact" 
                               value="{emergency_contact}"
                               placeholder="Emergency contact number"
                               pattern="\+254[0-9]{{9}}">
                        <small class="text-muted">Optional: Format +254XXXXXXXXX</small>
                    </div>
                    
                    <div class="mb-3">
                        <div class="form-check">
                            <input type="checkbox" class="form-check-input" id="terms" required>
                            <label class="form-check-label" for="terms">
                                I agree to the <a href="#" class="text-primary">Terms of Service</a> and 
                                <a href="#" class="text-primary">Privacy Policy</a> *
                            </label>
                        </div>
                    </div>
                    
                    <button type="submit" class="btn btn-register" id="submitBtn">
                        <span class="spinner-border spinner-border-sm d-none" id="spinner" role="status"></span>
                        <span id="btnText"><i class="fas fa-user-plus me-2"></i>Create Account</span>
                    </button>
                    
                    <div class="login-link">
                        Already have an account? <a href="patient_login.py">Login here</a>
                    </div>
                </form>
            </div>
        </div>
    </div>
    
    <script>
        // Password strength checker
        const password = document.getElementById('password');
        const confirmPassword = document.getElementById('confirm_password');
        const strengthBar = document.getElementById('strengthBar');
        const passwordMatch = document.getElementById('passwordMatch');
        const form = document.getElementById('registerForm');
        const submitBtn = document.getElementById('submitBtn');
        const spinner = document.getElementById('spinner');
        const btnText = document.getElementById('btnText');
        
        password.addEventListener('input', checkPasswordStrength);
        confirmPassword.addEventListener('input', checkPasswordMatch);
        
        function checkPasswordStrength() {{
            const val = password.value;
            let strength = 0;
            
            if (val.length >= 8) strength++;
            if (val.match(/[a-z]+/)) strength++;
            if (val.match(/[A-Z]+/)) strength++;
            if (val.match(/[0-9]+/)) strength++;
            if (val.match(/[$@#&!]+/)) strength++;
            
            strengthBar.className = 'password-strength-bar';
            if (strength <= 2) {{
                strengthBar.classList.add('strength-weak');
            }} else if (strength <= 4) {{
                strengthBar.classList.add('strength-medium');
            }} else {{
                strengthBar.classList.add('strength-strong');
            }}
        }}
        
        function checkPasswordMatch() {{
            if (confirmPassword.value && password.value !== confirmPassword.value) {{
                confirmPassword.classList.add('is-invalid');
                passwordMatch.textContent = 'Passwords do not match';
            }} else {{
                confirmPassword.classList.remove('is-invalid');
                passwordMatch.textContent = '';
            }}
        }}
        
        form.addEventListener('submit', function(e) {{
            if (password.value !== confirmPassword.value) {{
                e.preventDefault();
                alert('Passwords do not match!');
                return;
            }}
            
            // Show loading state
            submitBtn.disabled = true;
            spinner.classList.remove('d-none');
            btnText.innerHTML = 'Creating Account...';
        }});
    </script>
</body>
</html>
""")