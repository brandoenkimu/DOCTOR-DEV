#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


import sys
# Force UTF-8 for stdout to avoid encoding errors

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
from validation import Validator

# Check admin session
session = AdminSession()
session.start_session()

if not session.is_logged_in():
    print("Location: admin_login.py")
    print()
    sys.exit()

admin_info = session.get_admin_info()

# Get form data
form = cgi.FieldStorage()
action = form.getvalue('action', '')

# Get specialties for dropdown
specialties = DatabaseOperations.execute_query(
    "SELECT * FROM specialties ORDER BY specialty_name", 
    fetch_all=True
) or []

errors = []
success = False
form_data = {}
generated_password = None

if action == 'add_doctor':
    # Get form values
    form_data = {
        'license_number': form.getvalue('license_number', ''),
        'full_name': form.getvalue('full_name', ''),
        'email': form.getvalue('email', ''),
        'phone': form.getvalue('phone', ''),
        'specialty': form.getvalue('specialty', ''),
        'qualification': form.getvalue('qualification', ''),
        'experience_years': form.getvalue('experience_years', '0'),
        'consultation_fee': form.getvalue('consultation_fee', '0'),
        'available_from': form.getvalue('available_from', '09:00'),
        'available_to': form.getvalue('available_to', '17:00'),
        'password': form.getvalue('password', '').strip(),
    }
    
    # Validation
    if not form_data['license_number']:
        errors.append("License number is required")
    if not form_data['full_name']:
        errors.append("Full name is required")
    if not form_data['email']:
        errors.append("Email is required")
    if not form_data['phone']:
        errors.append("Phone number is required")
    if not form_data['specialty']:
        errors.append("Specialty is required")
    
    # Check if license number exists
    if not errors:
        check = DatabaseOperations.execute_query(
            "SELECT * FROM doctors WHERE license_number = %s",
            (form_data['license_number'],),
            fetch_one=True
        )
        if check:
            errors.append("License number already exists")
    
    # Check if email exists
    if not errors:
        check = DatabaseOperations.execute_query(
            "SELECT * FROM doctors WHERE email = %s",
            (form_data['email'],),
            fetch_one=True
        )
        if check:
            errors.append("Email already registered")
    
    # If no errors, create doctor
    if not errors:
        try:
            # Determine password
            if form_data['password']:
                plain_password = form_data['password']
            else:
                # Generate from phone number
                digits = ''.join(filter(str.isdigit, form_data['phone']))
                if len(digits) >= 6:
                    plain_password = digits[-6:]
                else:
                    plain_password = digits + '123'
                plain_password = 'Doc' + plain_password
            generated_password = plain_password

            # Hash password
            password_hash = bcrypt.hashpw(
                plain_password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')
            
            # Validate admin_id before using it as created_by
            created_by = None
            if admin_info and 'admin_id' in admin_info:
                admin_check = DatabaseOperations.execute_query(
                    "SELECT admin_id FROM admins WHERE admin_id = %s",
                    (admin_info['admin_id'],),
                    fetch_one=True
                )
                if admin_check:
                    created_by = admin_info['admin_id']
                else:
                    import sys
                    sys.stderr.write(f"Warning: Admin ID {admin_info['admin_id']} not found. Setting created_by to NULL.\n")
            
            # Insert doctor
            query = """
                INSERT INTO doctors 
                (license_number, full_name, email, phone, password_hash, 
                 specialty, qualification, experience_years, consultation_fee,
                 available_from, available_to, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                form_data['license_number'],
                form_data['full_name'],
                form_data['email'],
                form_data['phone'],
                password_hash,
                form_data['specialty'],
                form_data['qualification'],
                int(form_data['experience_years']) if form_data['experience_years'] else 0,
                float(form_data['consultation_fee']) if form_data['consultation_fee'] else 0.00,
                form_data['available_from'],
                form_data['available_to'],
                created_by
            )
            
            doctor_id = DatabaseOperations.execute_query(query, params)
            
            if doctor_id:
                success = True
                form_data = {}
        except Exception as e:
            errors.append(f"Failed to add doctor: {str(e)} (created_by={created_by})")

print("Content-Type: text/html; charset=utf-8")
print()

print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Add Doctor - Clinic Management System</title>
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
        
        .sidebar {{
            position: fixed;
            top: 0;
            left: 0;
            height: 100vh;
            width: 260px;
            background: linear-gradient(135deg, var(--dark) 0%, var(--primary) 100%);
            color: white;
            padding: 20px;
        }}
        
        .sidebar-logo {{
            text-align: center;
            padding: 20px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 20px;
        }}
        
        .sidebar-menu {{
            list-style: none;
            padding: 0;
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
        
        .form-container {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        
        .form-header {{
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        
        .form-label {{
            font-weight: 600;
            color: var(--dark);
            margin-bottom: 8px;
        }}
        
        .form-control, .form-select {{
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 10px 15px;
            transition: all 0.3s ease;
        }}
        
        .form-control:focus, .form-select:focus {{
            border-color: var(--primary);
            box-shadow: 0 0 0 0.2rem rgba(42, 92, 130, 0.25);
        }}
        
        .btn-save {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            border: none;
            border-radius: 10px;
            padding: 12px 30px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        .btn-save:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(42, 92, 130, 0.3);
            color: white;
        }}
        
        .btn-cancel {{
            background: #f8f9fa;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 12px 30px;
            font-weight: 600;
            color: #666;
            margin-right: 10px;
        }}
        
        .btn-cancel:hover {{
            background: #e0e0e0;
        }}
        
        .alert {{
            border-radius: 10px;
            border: none;
            padding: 15px 20px;
            margin-bottom: 25px;
        }}
        
        .required::after {{
            content: "*";
            color: var(--danger);
            margin-left: 4px;
        }}
        
        .info-text {{
            font-size: 0.85rem;
            color: #6c757d;
            margin-top: 5px;
        }}
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
            <li><a href="admin_dashboard.py"><i class="fas fa-tachometer-alt"></i> Dashboard</a></li>
            <li><a href="admin_doctors.py" class="active"><i class="fas fa-user-md"></i> Manage Doctors</a></li>
            <li><a href="admin_patients.py"><i class="fas fa-users"></i> Manage Patients</a></li>
            <li><a href="admin_appointments.py"><i class="fas fa-calendar-check"></i> Appointments</a></li>
            <li><a href="admin_logout.py"><i class="fas fa-sign-out-alt"></i> Logout</a></li>
        </ul>
    </div>
    
    <!-- Main Content -->
    <div class="main-content">
        <div class="top-bar">
            <h4 class="mb-0"><i class="fas fa-user-md me-2 text-primary"></i>Add New Doctor</h4>
            <div class="user-info">
                <span>Welcome, <strong>{admin_info['full_name']}</strong></span>
            </div>
        </div>
        
        <div class="form-container">
            <div class="form-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0"><i class="fas fa-user-plus me-2 text-primary"></i>Doctor Registration Form</h5>
                <span class="text-muted">All fields marked with * are required</span>
            </div>
            
""")

if success and generated_password:
    print(f"""
            <div class="alert alert-success">
                <i class="fas fa-check-circle me-2"></i>
                Doctor added successfully!<br>
                <strong>Default password:</strong> <code>{generated_password}</code><br>
                <small class="text-muted">The doctor should change this password after first login.</small><br>
                <a href="admin_doctors.py" class="alert-link">View all doctors</a>
            </div>
    """)
elif success:
    print("""
            <div class="alert alert-success">
                <i class="fas fa-check-circle me-2"></i>
                Doctor added successfully! 
                <a href="admin_doctors.py" class="alert-link">View all doctors</a>
            </div>
    """)

if errors:
    print('<div class="alert alert-danger"><i class="fas fa-exclamation-circle me-2"></i>')
    for error in errors:
        print(f'<div>{error}</div>')
    print('</div>')

print(f"""
            <form method="post" action="admin_add_doctor.py">
                <input type="hidden" name="action" value="add_doctor">
                
                <div class="row">
                    <div class="col-md-6 mb-4">
                        <label class="form-label required">License Number</label>
                        <input type="text" 
                               class="form-control" 
                               name="license_number" 
                               value="{form_data.get('license_number', '')}"
                               placeholder="e.g., LIC001"
                               required>
                        <div class="info-text">Medical license number (unique identifier)</div>
                    </div>
                    
                    <div class="col-md-6 mb-4">
                        <label class="form-label required">Full Name</label>
                        <input type="text" 
                               class="form-control" 
                               name="full_name" 
                               value="{form_data.get('full_name', '')}"
                               placeholder="Dr. John Doe"
                               required>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-4">
                        <label class="form-label required">Email Address</label>
                        <input type="email" 
                               class="form-control" 
                               name="email" 
                               value="{form_data.get('email', '')}"
                               placeholder="doctor@clinic.com"
                               required>
                    </div>
                    
                    <div class="col-md-6 mb-4">
                        <label class="form-label required">Phone Number</label>
                        <input type="tel" 
                               class="form-control" 
                               name="phone" 
                               value="{form_data.get('phone', '')}"
                               placeholder="+254XXXXXXXXX"
                               pattern="\+254[0-9]{{9}}"
                               required>
                        <div class="info-text">Format: +254XXXXXXXXX</div>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-4">
                        <label class="form-label required">Specialty</label>
                        <select class="form-select" name="specialty" required>
                            <option value="">Select Specialty</option>
""")

for specialty in specialties:
    selected = 'selected' if form_data.get('specialty') == specialty['specialty_name'] else ''
    print(f'<option value="{specialty["specialty_name"]}" {selected}>{specialty["specialty_name"]}</option>')

print(f"""
                        </select>
                    </div>
                    
                    <div class="col-md-6 mb-4">
                        <label class="form-label">Qualification</label>
                        <input type="text" 
                               class="form-control" 
                               name="qualification" 
                               value="{form_data.get('qualification', '')}"
                               placeholder="e.g., MD, FACC">
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-4 mb-4">
                        <label class="form-label">Experience (Years)</label>
                        <input type="number" 
                               class="form-control" 
                               name="experience_years" 
                               value="{form_data.get('experience_years', '0')}"
                               min="0"
                               max="70">
                    </div>
                    
                    <div class="col-md-4 mb-4">
                        <label class="form-label">Consultation Fee (KES)</label>
                        <input type="number" 
                               class="form-control" 
                               name="consultation_fee" 
                               value="{form_data.get('consultation_fee', '0')}"
                               min="0"
                               step="100">
                    </div>
                    
                    <div class="col-md-4 mb-4">
                        <label class="form-label">Default Password</label>
                        <input type="text" 
                               class="form-control" 
                               name="password" 
                               value="{form_data.get('password', '')}">
                        <div class="info-text">Leave empty to auto‑generate from phone number</div>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-4">
                        <label class="form-label">Available From</label>
                        <input type="time" 
                               class="form-control" 
                               name="available_from" 
                               value="{form_data.get('available_from', '09:00')}">
                    </div>
                    
                    <div class="col-md-6 mb-4">
                        <label class="form-label">Available To</label>
                        <input type="time" 
                               class="form-control" 
                               name="available_to" 
                               value="{form_data.get('available_to', '17:00')}">
                    </div>
                </div>
                
                <hr class="my-4">
                
                <div class="d-flex justify-content-end">
                    <a href="admin_doctors.py" class="btn btn-cancel">
                        <i class="fas fa-times me-2"></i>Cancel
                    </a>
                    <button type="submit" class="btn btn-save">
                        <i class="fas fa-save me-2"></i>Add Doctor
                    </button>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
""")