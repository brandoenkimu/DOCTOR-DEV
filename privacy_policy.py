#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Privacy Policy Page
"""

import sys
import cgi
import cgitb
import os

cgitb.enable()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from session import SessionManager

# --- HEADER COLLECTION ---
headers = []

# Start session
session = SessionManager()
session.start_session()

# Get current user info
user_info = session.get_user_info()
user_type = session.get('user_type')

# Determine dashboard and other links based on user type (for the dropdown)
if user_info:
    if user_type == 'patient':
        dashboard_link = 'patient_dashboard.py'
        appointments_link = 'my_appointments.py'
        profile_link = 'patient_profile.py'
        change_password_link = 'patient_change_password.py'
    elif user_type == 'doctor':
        dashboard_link = 'doctor_dashboard.py'
        appointments_link = 'doctor_appointments.py'
        profile_link = 'doctor_profile.py'
        change_password_link = 'doctor_change_password.py'
    elif user_type == 'admin':
        dashboard_link = 'admin_dashboard.py'
        appointments_link = 'admin_appointments.py'
        profile_link = 'admin_profile.py'
        change_password_link = 'admin_change_password.py'
    else:
        dashboard_link = appointments_link = profile_link = change_password_link = '#'
else:
    # Not logged in – these won't be used
    dashboard_link = appointments_link = profile_link = change_password_link = '#'

# Add content-type header
headers.append("Content-Type: text/html; charset=utf-8")

# Add cookie header if present
cookie_header = session.get_cookie_header()
if cookie_header:
    headers.append(cookie_header)

# Print all headers
for header in headers:
    print(header)
print()  # Blank line

# HTML Template
print("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy Policy - ClinicCare</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome 6 -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- AOS Animation -->
    <link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">
    
    <style>
        :root {
            --primary-color: #2A5C82;
            --secondary-color: #4A90E2;
            --accent-color: #50C878;
            --danger-color: #FF6B6B;
            --dark-color: #2C3E50;
            --light-color: #F8F9FA;
            --gradient-primary: linear-gradient(135deg, #2A5C82 0%, #4A90E2 100%);
            --gradient-success: linear-gradient(135deg, #50C878 0%, #2ECC71 100%);
            --shadow-sm: 0 2px 4px rgba(0,0,0,0.1);
            --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
            --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
            --shadow-hover: 0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            color: var(--dark-color);
            overflow-x: hidden;
        }
        
        /* Navbar Styles */
        .navbar {
            background: rgba(255, 255, 255, 0.95) !important;
            backdrop-filter: blur(10px);
            box-shadow: var(--shadow-sm);
            padding: 1rem 0;
        }
        
        .navbar-brand {
            font-weight: 700;
            font-size: 1.5rem;
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .nav-link {
            font-weight: 500;
            color: var(--dark-color) !important;
            margin: 0 0.5rem;
            transition: all 0.3s ease;
            position: relative;
        }
        
        .nav-link::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 2px;
            background: var(--gradient-primary);
            transition: width 0.3s ease;
        }
        
        .nav-link:hover::after {
            width: 80%;
        }
        
        .nav-link:hover {
            color: var(--primary-color) !important;
        }
        
        /* Hero Section */
        .hero-section {
            background: var(--gradient-primary);
            color: white;
            padding: 120px 0 80px;
            position: relative;
            overflow: hidden;
        }
        
        .hero-title {
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 1.5rem;
        }
        
        /* Content Section */
        .content-section {
            padding: 80px 0;
        }
        
        .content-card {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: var(--shadow-md);
            margin-bottom: 2rem;
        }
        
        /* Footer */
        .footer {
            background: var(--dark-color);
            color: white;
            padding: 60px 0 30px;
            margin-top: 80px;
        }
        
        .footer a {
            color: rgba(255,255,255,0.8);
            text-decoration: none;
            transition: all 0.3s ease;
        }
        
        .footer a:hover {
            color: white;
            padding-left: 5px;
        }
        
        .social-links a {
            display: inline-block;
            width: 40px;
            height: 40px;
            background: rgba(255,255,255,0.1);
            border-radius: 50%;
            text-align: center;
            line-height: 40px;
            margin-right: 10px;
            transition: all 0.3s ease;
        }
        
        .social-links a:hover {
            background: var(--primary-color);
            transform: translateY(-3px);
        }
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
""")

if user_info:
    # User is logged in – show dropdown with dynamic links
    print(f"""
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-user-circle me-1"></i>
                            {user_info['full_name']}
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li><a class="dropdown-item" href="{dashboard_link}">
                                <i class="fas fa-tachometer-alt me-2"></i>Dashboard
                            </a></li>
                            <li><a class="dropdown-item" href="{appointments_link}">
                                <i class="fas fa-calendar-check me-2"></i>My Appointments
                            </a></li>
                            <li><a class="dropdown-item" href="{profile_link}">
                                <i class="fas fa-user-circle me-2"></i>My Profile
                            </a></li>
                            <li><a class="dropdown-item" href="{change_password_link}">
                                <i class="fas fa-key me-2"></i>Change Password
                            </a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-danger" href="logout.py">
                                <i class="fas fa-sign-out-alt me-2"></i>Logout
                            </a></li>
                        </ul>
                    </li>
    """)
else:
    # User not logged in
    print("""
                    <li class="nav-item">
                        <a class="nav-link" href="patient_login.py">
                            <i class="fas fa-sign-in-alt me-1"></i>Login
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="patient_register.py">
                            <i class="fas fa-user-plus me-1"></i>Register
                        </a>
                    </li>
    """)

print("""
                </ul>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero-section">
        <div class="container">
            <div class="row">
                <div class="col-lg-8 mx-auto text-center">
                    <h1 class="hero-title">Privacy Policy</h1>
                    <p class="lead">Your privacy is important to us. Learn how we protect your information.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Content -->
    <section class="content-section">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-lg-10">
                    <div class="content-card">
                        <h2 class="mb-4">ClinicCare Privacy Policy</h2>
                        <p class="text-muted">Last updated: March 2026</p>
                        
                        <h4 class="mt-4">1. Introduction</h4>
                        <p>ClinicCare ("we," "our," or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our website and services. Please read this policy carefully. By using our services, you consent to the practices described herein.</p>
                        
                        <h4 class="mt-4">2. Information We Collect</h4>
                        <p>We may collect personal information that you voluntarily provide to us when you register for an account, book an appointment, or communicate with us. This includes:</p>
                        <ul>
                            <li>Full name, registration number (for patients), license number (for doctors)</li>
                            <li>Email address, phone number, date of birth, address</li>
                            <li>Medical history, symptoms, diagnoses, prescriptions, and other health-related information</li>
                            <li>Payment information (if applicable)</li>
                            <li>Technical data such as IP address, browser type, and usage statistics</li>
                        </ul>
                        
                        <h4 class="mt-4">3. How We Use Your Information</h4>
                        <p>We use your information to:</p>
                        <ul>
                            <li>Provide, operate, and maintain our services</li>
                            <li>Process appointments and manage your medical records</li>
                            <li>Communicate with you regarding appointments, reminders, and updates</li>
                            <li>Improve our services and user experience</li>
                            <li>Comply with legal obligations and protect our rights</li>
                        </ul>
                        
                        <h4 class="mt-4">4. Data Security</h4>
                        <p>We implement industry-standard security measures, including encryption, access controls, and regular audits, to protect your data. However, no method of transmission over the internet is 100% secure. We cannot guarantee absolute security.</p>
                        
                        <h4 class="mt-4">5. Sharing Your Information</h4>
                        <p>We do not sell, trade, or rent your personal information to third parties. We may share information with:</p>
                        <ul>
                            <li>Healthcare providers involved in your care</li>
                            <li>Service providers who assist in operating our platform (e.g., hosting, analytics)</li>
                            <li>Legal authorities when required by law</li>
                        </ul>
                        
                        <h4 class="mt-4">6. Your Rights</h4>
                        <p>You have the right to:</p>
                        <ul>
                            <li>Access, correct, or delete your personal information</li>
                            <li>Withdraw consent at any time</li>
                            <li>Request a copy of your data</li>
                            <li>Lodge a complaint with a supervisory authority</li>
                        </ul>
                        <p>To exercise these rights, please contact us at <a href="mailto:privacy@cliniccare.com">privacy@cliniccare.com</a>.</p>
                        
                        <h4 class="mt-4">7. Cookies</h4>
                        <p>We use cookies to enhance your experience. You can control cookie preferences through your browser settings.</p>
                        
                        <h4 class="mt-4">8. Changes to This Policy</h4>
                        <p>We may update this policy from time to time. Changes will be posted on this page with an updated effective date.</p>
                        
                        <h4 class="mt-4">9. Contact Us</h4>
                        <p>If you have any questions about this Privacy Policy, please contact us:</p>
                        <ul>
                            <li>Email: privacy@cliniccare.com</li>
                            <li>Phone: +254 116 747 630</li>
                            <li>Address: Kirinyaga University, Kenya</li>
                        </ul>
                        
                        <div class="text-center mt-5">
                            <a href="index.py" class="btn btn-primary-custom">Return to Home</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

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

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
    <script>
        AOS.init({ duration: 800, once: true });
    </script>
</body>
</html>
""")