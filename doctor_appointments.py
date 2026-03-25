#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Doctor Appointments Page
Displays the doctor's schedule and allows status management.
"""

import sys
import cgi
import cgitb
import os
from datetime import datetime

cgitb.enable()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from session import SessionManager
from database import DatabaseOperations

# --- HEADER COLLECTION ---
headers = []

# Start session
session = SessionManager()
session.start_session()

# Check if logged in as doctor
if not session.is_logged_in() or session.get('user_type') != 'doctor':
    headers.append("Location: doctor_login.py")
    for h in headers: print(h)
    print()
    sys.exit()

# Get doctor info
user_info = session.get_user_info()
doctor_id = user_info['user_id']

# Handle status update (complete or cancel)
form = cgi.FieldStorage()
action = form.getvalue('action')
appointment_id = form.getvalue('appointment_id')
new_status = None

if action == 'complete':
    new_status = 'Completed'
elif action == 'cancel':
    new_status = 'Cancelled'

if appointment_id and new_status:
    try:
        # You'll need a method like `update_appointment_status` in DatabaseOperations
        DatabaseOperations.update_appointment_status(appointment_id, new_status)
        # Redirect to avoid resubmission on refresh
        headers.append("Location: doctor_appointments.py?updated=1")
        for h in headers: print(h)
        print()
        sys.exit()
    except Exception as e:
        error_message = str(e)

# Fetch appointments for this doctor
try:
    appointments = DatabaseOperations.get_doctor_all_appointments(doctor_id)
except Exception as e:
    appointments = []
    error_message = f"Error loading appointments: {e}"

# Separate upcoming and past appointments
today = datetime.now().date()
upcoming = []
past = []

for apt in appointments:
    # Convert appointment_date to date object if string
    apt_date = apt['appointment_date']
    if isinstance(apt_date, str):
        apt_date = datetime.strptime(apt_date, '%Y-%m-%d').date()
    if apt_date >= today and apt['status'] in ['Scheduled', 'Rescheduled']:
        upcoming.append(apt)
    else:
        past.append(apt)

# Add content-type header
headers.append("Content-Type: text/html; charset=utf-8")
cookie_header = session.get_cookie_header()
if cookie_header:
    headers.append(cookie_header)

# Print all headers
for header in headers:
    print(header)
print()  # Blank line

# HTML Template
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Appointments - Doctor | ClinicCare</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome 6 -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- AOS Animation -->
    <link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">
    
    <style>
        :root {{
            --primary-color: #2A5C82;
            --secondary-color: #4A90E2;
            --accent-color: #50C878;
            --danger-color: #FF6B6B;
            --dark-color: #2C3E50;
            --light-color: #F8F9FA;
            --gradient-primary: linear-gradient(135deg, #2A5C82 0%, #4A90E2 100%);
            --shadow-sm: 0 2px 4px rgba(0,0,0,0.1);
            --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
            --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
            --shadow-hover: 0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            color: var(--dark-color);
            overflow-x: hidden;
        }}
        
        /* Navbar Styles */
        .navbar {{
            background: rgba(255, 255, 255, 0.95) !important;
            backdrop-filter: blur(10px);
            box-shadow: var(--shadow-sm);
            padding: 1rem 0;
        }}
        
        .navbar-brand {{
            font-weight: 700;
            font-size: 1.5rem;
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .nav-link {{
            font-weight: 500;
            color: var(--dark-color) !important;
            margin: 0 0.5rem;
            transition: all 0.3s ease;
            position: relative;
        }}
        
        .nav-link::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 2px;
            background: var(--gradient-primary);
            transition: width 0.3s ease;
        }}
        
        .nav-link:hover::after {{
            width: 80%;
        }}
        
        .nav-link:hover {{
            color: var(--primary-color) !important;
        }}
        
        /* Hero Section */
        .hero-section {{
            background: var(--gradient-primary);
            color: white;
            padding: 120px 0 80px;
            position: relative;
            overflow: hidden;
        }}
        
        .hero-title {{
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 1.5rem;
        }}
        
        /* Appointment Cards */
        .appointment-card {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: var(--shadow-md);
            transition: all 0.3s ease;
            border-left: 4px solid var(--primary-color);
        }}
        
        .appointment-card:hover {{
            transform: translateX(5px);
            box-shadow: var(--shadow-lg);
        }}
        
        .appointment-card.past {{
            opacity: 0.8;
            border-left-color: #6c757d;
        }}
        
        .status-badge {{
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        
        .status-scheduled {{ background: #cce5ff; color: #004085; }}
        .status-completed {{ background: #d4edda; color: #155724; }}
        .status-cancelled {{ background: #f8d7da; color: #721c24; }}
        .status-rescheduled {{ background: #fff3cd; color: #856404; }}
        
        .btn-action {{
            border-radius: 8px;
            padding: 5px 12px;
            font-size: 0.85rem;
            transition: all 0.3s ease;
        }}
        
        .btn-complete {{
            background: #28a745;
            color: white;
        }}
        
        .btn-complete:hover {{
            background: #218838;
            transform: translateY(-1px);
        }}
        
        .btn-cancel {{
            background: #dc3545;
            color: white;
        }}
        
        .btn-cancel:hover {{
            background: #c82333;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            background: white;
            border-radius: 20px;
        }}
        
        .filter-tabs {{
            margin-bottom: 30px;
        }}
        
        .filter-tabs .nav-link {{
            color: var(--primary-color);
            border-radius: 10px;
            padding: 10px 20px;
            font-weight: 500;
        }}
        
        .filter-tabs .nav-link.active {{
            background: var(--gradient-primary);
            color: white;
        }}
        
        /* Footer */
        .footer {{
            background: var(--dark-color);
            color: white;
            padding: 60px 0 30px;
            margin-top: 80px;
        }}
        
        .footer a {{
            color: rgba(255,255,255,0.8);
            text-decoration: none;
            transition: all 0.3s ease;
        }}
        
        .footer a:hover {{
            color: white;
            padding-left: 5px;
        }}
        
        .social-links a {{
            display: inline-block;
            width: 40px;
            height: 40px;
            background: rgba(255,255,255,0.1);
            border-radius: 50%;
            text-align: center;
            line-height: 40px;
            margin-right: 10px;
            transition: all 0.3s ease;
        }}
        
        .social-links a:hover {{
            background: var(--primary-color);
            transform: translateY(-3px);
        }}
    </style>
</head>
<body>
    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg navbar-light fixed-top">
        <div class="container">
            <a class="navbar-brand" href="index.py">
                <i class="fas fa-clinic-medical me-2"></i>
                ClinicCare
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="index.py#home">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="index.py#features">Features</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="index.py#specialties">Specialties</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="about.py">About</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="contact.py">Contact</a>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-user-circle me-1"></i>
                            {user_info['full_name']}
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li><a class="dropdown-item" href="doctor_dashboard.py">
                                <i class="fas fa-tachometer-alt me-2"></i>Dashboard
                            </a></li>
                            <li><a class="dropdown-item active" href="doctor_appointments.py">
                                <i class="fas fa-calendar-check me-2"></i>My Appointments
                            </a></li>
                            <li><a class="dropdown-item" href="doctor_profile.py">
                                <i class="fas fa-user-circle me-2"></i>My Profile
                            </a></li>
                            <li><a class="dropdown-item" href="doctor_change_password.py">
                                <i class="fas fa-key me-2"></i>Change Password
                            </a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-danger" href="logout.py">
                                <i class="fas fa-sign-out-alt me-2"></i>Logout
                            </a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero-section">
        <div class="container">
            <div class="row">
                <div class="col-lg-8 mx-auto text-center">
                    <h1 class="hero-title">My Appointments</h1>
                    <p class="lead">Manage your scheduled visits with patients</p>
                </div>
            </div>
        </div>
    </section>

    <div class="container" style="margin-top: 40px;">
        <!-- Success/Error Messages -->
        <div id="message-area">
            {f'<div class="alert alert-success alert-dismissible fade show" role="alert">Appointment updated successfully!<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>' if 'updated=1' in sys.argv else ''}
            {f'<div class="alert alert-danger">{error_message}</div>' if 'error_message' in locals() else ''}
        </div>
        
        <!-- Tabs -->
        <ul class="nav nav-pills filter-tabs" id="appointmentTabs" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link active" id="upcoming-tab" data-bs-toggle="tab" data-bs-target="#upcoming" type="button" role="tab">
                    Upcoming ({len(upcoming)})
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="past-tab" data-bs-toggle="tab" data-bs-target="#past" type="button" role="tab">
                    Past ({len(past)})
                </button>
            </li>
        </ul>
        
        <div class="tab-content" id="appointmentTabsContent">
            <!-- Upcoming Appointments -->
            <div class="tab-pane fade show active" id="upcoming" role="tabpanel">
""")

if upcoming:
    for apt in upcoming:
        status_class = f"status-{apt['status'].lower()}"
        # Format date and time
        apt_date = apt['appointment_date']
        if isinstance(apt_date, str):
            apt_date = datetime.strptime(apt_date, '%Y-%m-%d')
        date_formatted = apt_date.strftime('%A, %B %d, %Y')
        time_formatted = apt['appointment_time'].strftime('%I:%M %p') if hasattr(apt['appointment_time'], 'strftime') else apt['appointment_time']
        
        # Only show actions if appointment is still scheduled/rescheduled
        show_actions = apt['status'] in ['Scheduled', 'Rescheduled']
        
        print(f"""
                <div class="appointment-card">
                    <div class="row align-items-center">
                        <div class="col-md-3">
                            <div class="d-flex align-items-center">
                                <i class="fas fa-user-circle fa-2x text-primary me-3"></i>
                                <div>
                                    <h6 class="mb-1">{apt['patient_name']}</h6>
                                    <small class="text-muted">Patient</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <i class="fas fa-calendar me-2 text-primary"></i>
                            {date_formatted}
                        </div>
                        <div class="col-md-2">
                            <i class="fas fa-clock me-2 text-primary"></i>
                            {time_formatted}
                        </div>
                        <div class="col-md-2">
                            <span class="status-badge {status_class}">{apt['status']}</span>
                        </div>
                        <div class="col-md-3 text-end">
        """)
        
        if show_actions:
            # Mark as Complete button
            print(f"""
                            <a href="doctor_appointments.py?action=complete&appointment_id={apt['appointment_id']}" 
                               class="btn btn-action btn-complete me-2"
                               onclick="return confirm('Mark this appointment as completed?')">
                                <i class="fas fa-check me-1"></i>Complete
                            </a>
                            <a href="doctor_appointments.py?action=cancel&appointment_id={apt['appointment_id']}" 
                               class="btn btn-action btn-cancel"
                               onclick="return confirm('Cancel this appointment? This cannot be undone.')">
                                <i class="fas fa-times me-1"></i>Cancel
                            </a>
            """)
        else:
            print('<span class="text-muted">No actions available</span>')
        
        print("""
                        </div>
                    </div>
                </div>
        """)
else:
    print("""
                <div class="empty-state">
                    <i class="fas fa-calendar-times fa-3x text-muted mb-3"></i>
                    <h4>No Upcoming Appointments</h4>
                    <p class="text-muted">You have no scheduled appointments at the moment.</p>
                </div>
""")

print("""
            </div>
            
            <!-- Past Appointments -->
            <div class="tab-pane fade" id="past" role="tabpanel">
""")

if past:
    for apt in past:
        status_class = f"status-{apt['status'].lower()}"
        apt_date = apt['appointment_date']
        if isinstance(apt_date, str):
            apt_date = datetime.strptime(apt_date, '%Y-%m-%d')
        date_formatted = apt_date.strftime('%A, %B %d, %Y')
        time_formatted = apt['appointment_time'].strftime('%I:%M %p') if hasattr(apt['appointment_time'], 'strftime') else apt['appointment_time']
        
        print(f"""
                <div class="appointment-card past">
                    <div class="row align-items-center">
                        <div class="col-md-3">
                            <div class="d-flex align-items-center">
                                <i class="fas fa-user-circle fa-2x text-muted me-3"></i>
                                <div>
                                    <h6 class="mb-1">{apt['patient_name']}</h6>
                                    <small class="text-muted">Patient</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <i class="fas fa-calendar me-2 text-muted"></i>
                            {date_formatted}
                        </div>
                        <div class="col-md-2">
                            <i class="fas fa-clock me-2 text-muted"></i>
                            {time_formatted}
                        </div>
                        <div class="col-md-2">
                            <span class="status-badge {status_class}">{apt['status']}</span>
                        </div>
                        <div class="col-md-3 text-end">
                            <a href="appointment_details.py?id={apt['appointment_id']}" class="btn btn-outline-primary btn-sm">
                                <i class="fas fa-eye me-1"></i>View Details
                            </a>
                        </div>
                    </div>
                </div>
        """)
else:
    print("""
                <div class="empty-state">
                    <i class="fas fa-history fa-3x text-muted mb-3"></i>
                    <h4>No Past Appointments</h4>
                    <p class="text-muted">Your appointment history will appear here.</p>
                </div>
""")

print("""
            </div>
        </div>
    </div>
    
    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <div class="row g-4">
                <div class="col-lg-4">
                    <h5 class="mb-4">ClinicCare</h5>
                    <p class="mb-4">Providing quality healthcare through innovative technology solutions.</p>
                    <div class="social-links">
                        <a href="https://facebook.com/61568374984253?text=Hello%20Bentely%20Brand"><i class="fab fa-facebook-f"></i></a>
                        <a href="https://x.com/messages/compose?recipient_screen_name=n_bentely&text=Hello%20Bentely%20Brand"><i class="fab fa-twitter"></i></a>
                        <a href="#"><i class="fab fa-linkedin-in"></i></a>
                        <a href="https://www.instagram.com/brandonlavie/"><i class="fab fa-instagram"></i></a>
                    </div>
                </div>
                <div class="col-lg-2 col-md-4">
                    <h5 class="mb-4">Quick Links</h5>
                    <ul class="list-unstyled">
                        <li class="mb-2"><a href="index.py#home">Home</a></li>
                        <li class="mb-2"><a href="index.py#features">Features</a></li>
                        <li class="mb-2"><a href="index.py#specialties">Specialties</a></li>
                        <li class="mb-2"><a href="about.py">About Us</a></li>
                    </ul>
                </div>
                <div class="col-lg-3 col-md-4">
                    <h5 class="mb-4">Contact Info</h5>
                    <ul class="list-unstyled">
                        <li class="mb-3">
                            <i class="fas fa-map-marker-alt me-2"></i>
                            Kirinyaga University, Kenya
                        </li>
                        <li class="mb-3">
                            <i class="fas fa-phone me-2"></i>
                            +254 116 747 630
                        </li>
                        <li class="mb-3">
                            <i class="fas fa-envelope me-2"></i>
                            info@cliniccare.com
                        </li>
                    </ul>
                </div>
                <div class="col-lg-3 col-md-4">
                    <h5 class="mb-4">Newsletter</h5>
                    <p class="mb-3">Subscribe for health tips and updates</p>
                    <div class="input-group">
                        <input type="email" class="form-control bg-transparent text-white border-white" placeholder="Your email">
                        <button class="btn btn-primary-custom" type="button">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
            <hr class="my-4 bg-white opacity-25">
            <div class="text-center">
                <p class="mb-0">&copy; 2026 ClinicCare. All rights reserved. | SSE 2304 Server-Side Programming CAT II</p>
            </div>
        </div>
    </footer>
    
    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
    <script>
        AOS.init({ duration: 800, once: true });
    </script>
</body>
</html>
""")