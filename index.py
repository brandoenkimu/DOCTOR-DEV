#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Main entry point for Clinic Management System
Displays homepage with login/registration options and clinic information
"""
import sys
import cgi
import cgitb
import os
from datetime import datetime

# Enable CGI traceback for debugging
cgitb.enable()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from session import SessionManager
from database import DatabaseOperations
from validation import Validator

# --- HEADER COLLECTION ---
headers = []

# Start session
session = SessionManager()
session.start_session()

# Get current user info
user_info = session.get_user_info()
user_type = session.get('user_type')  # 'patient', 'doctor', or 'admin'

# Determine dashboard and other links based on user type
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
        # fallback (shouldn't happen)
        dashboard_link = '#'
        appointments_link = '#'
        profile_link = '#'
        change_password_link = '#'
else:
    # Placeholders for when not logged in (not used)
    dashboard_link = appointments_link = profile_link = change_password_link = '#'

# Get statistics for dashboard
try:
    total_doctors = len(DatabaseOperations.get_doctors_by_specialty() or [])
    specialties = DatabaseOperations.get_all_specialties() or []
    total_specialties = len(specialties)
except:
    total_doctors = 0
    total_specialties = 0
    specialties = []

# Add content-type header
headers.append("Content-Type: text/html; charset=utf-8")

# Add cookie header if present
cookie_header = session.get_cookie_header()
if cookie_header:
    headers.append(cookie_header)

# Print all headers
for header in headers:
    print(header)
print()  # Blank line separating headers and body


# HTML Template with Bootstrap 5 and modern UI/UX
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clinic Management System - Kirinyaga University</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome 6 -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- AOS Animation -->
    <link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">
    
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
            --gradient-success: linear-gradient(135deg, #50C878 0%, #2ECC71 100%);
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
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: #f1f1f1;
            border-radius: 10px;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: var(--primary-color);
            border-radius: 10px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: var(--secondary-color);
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
        
        .hero-section::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: rotate 30s linear infinite;
        }}
        
        @keyframes rotate {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}
        
        .hero-title {{
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 1.5rem;
            animation: fadeInUp 1s ease;
        }}
        
        .hero-subtitle {{
            font-size: 1.25rem;
            margin-bottom: 2rem;
            opacity: 0.9;
            animation: fadeInUp 1s ease 0.2s both;
        }}
        
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        /* Feature Cards */
        .feature-card {{
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: var(--shadow-md);
            transition: all 0.3s ease;
            height: 100%;
            border: none;
            overflow: hidden;
            position: relative;
        }}
        
        .feature-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--gradient-primary);
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }}
        
        .feature-card:hover::before {{
            transform: scaleX(1);
        }}
        
        .feature-card:hover {{
            transform: translateY(-10px);
            box-shadow: var(--shadow-hover);
        }}
        
        .feature-icon {{
            width: 70px;
            height: 70px;
            background: var(--gradient-primary);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1.5rem;
            color: white;
            font-size: 1.75rem;
            transition: all 0.3s ease;
        }}
        
        .feature-card:hover .feature-icon {{
            transform: rotateY(180deg);
        }}
        
        .feature-title {{
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--dark-color);
        }}
        
        .feature-text {{
            color: #666;
            line-height: 1.6;
            margin-bottom: 1.5rem;
        }}
        
        /* Stats Cards */
        .stat-card {{
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: var(--shadow-md);
            text-align: center;
            transition: all 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: scale(1.05);
            box-shadow: var(--shadow-lg);
        }}
        
        .stat-number {{
            font-size: 2.5rem;
            font-weight: 700;
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }}
        
        .stat-label {{
            color: #666;
            font-weight: 500;
        }}
        
        /* Buttons */
        .btn-custom {{
            padding: 12px 30px;
            border-radius: 50px;
            font-weight: 600;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            z-index: 1;
        }}
        
        .btn-custom::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s ease;
            z-index: -1;
        }}
        
        .btn-custom:hover::before {{
            left: 100%;
        }}
        
        .btn-primary-custom {{
            background: var(--gradient-primary);
            border: none;
            color: white;
            box-shadow: 0 4px 15px rgba(42, 92, 130, 0.3);
        }}
        
        .btn-primary-custom:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(42, 92, 130, 0.4);
            color: white;
        }}
        
        .btn-outline-custom {{
            background: transparent;
            border: 2px solid white;
            color: white;
        }}
        
        .btn-outline-custom:hover {{
            background: white;
            color: var(--primary-color);
            transform: translateY(-2px);
        }}
        
        /* Specialty Cards */
        .specialty-card {{
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: var(--shadow-sm);
            transition: all 0.3s ease;
            text-align: center;
            cursor: pointer;
            border: none;
            text-decoration: none;
            display: block;
            color: inherit;
        }}
        
        .specialty-card:hover {{
            transform: translateY(-5px);
            box-shadow: var(--shadow-md);
            background: var(--gradient-primary);
            color: white;
        }}
        
        .specialty-card:hover .specialty-icon {{
            color: white;
        }}
        
        .specialty-icon {{
            font-size: 2.5rem;
            color: var(--primary-color);
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }}
        
        .specialty-name {{
            font-weight: 600;
            margin-bottom: 0.5rem;
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
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .hero-title {{
                font-size: 2.5rem;
            }}
            
            .hero-section {{
                padding: 100px 0 60px;
                text-align: center;
            }}
            
            .feature-card {{
                margin-bottom: 20px;
            }}
        }}
        
        /* Loading Animation */
        .loading-spinner {{
            width: 50px;
            height: 50px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        /* Toast Notifications */
        .toast-container {{
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
        }}
        
        .toast-custom {{
            background: white;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 10px;
            box-shadow: var(--shadow-lg);
            animation: slideIn 0.3s ease;
        }}
        
        @keyframes slideIn {{
            from {{
                transform: translateX(100%);
                opacity: 0;
            }}
            to {{
                transform: translateX(0);
                opacity: 1;
            }}
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
                        <a class="nav-link" href="#home">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#features">Features</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#specialties">Specialties</a>
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

print(f"""
                </ul>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section id="home" class="hero-section">
        <div class="container position-relative">
            <div class="row align-items-center">
                <div class="col-lg-6" data-aos="fade-right">
                    <h1 class="hero-title">
                        Your Health, <br>Our Priority
                    </h1>
                    <p class="hero-subtitle">
                        Experience seamless healthcare with our advanced online clinic management system. 
                        Book appointments, consult with specialists, and manage your health records - all in one place.
                    </p>
                    <div class="d-flex gap-3">
                        <a href="book_appointment.py" class="btn btn-custom btn-primary-custom">
                            <i class="fas fa-calendar-plus me-2"></i>Book Appointment
                        </a>
                        <a href="#features" class="btn btn-custom btn-outline-custom">
                            <i class="fas fa-play-circle me-2"></i>Watch Demo
                        </a>
                    </div>
                </div>
                <div class="col-lg-6" data-aos="fade-left">
                    <img src="/assets/images/healthcare-hero-illustrated-stockcake.webp" alt="Healthcare Illustration" class="img-fluid">
                </div>
            </div>
        </div>
    </section>

    <!-- Stats Section -->
    <section class="py-5">
        <div class="container">
            <div class="row g-4">
                <div class="col-md-4" data-aos="fade-up" data-aos-delay="100">
                    <div class="stat-card">
                        <div class="stat-number">{total_doctors}+</div>
                        <div class="stat-label">Expert Doctors</div>
                    </div>
                </div>
                <div class="col-md-4" data-aos="fade-up" data-aos-delay="200">
                    <div class="stat-card">
                        <div class="stat-number">{total_specialties}+</div>
                        <div class="stat-label">Medical Specialties</div>
                    </div>
                </div>
                <div class="col-md-4" data-aos="fade-up" data-aos-delay="300">
                    <div class="stat-card">
                        <div class="stat-number">24/7</div>
                        <div class="stat-label">Patient Support</div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="py-5">
        <div class="container">
            <div class="text-center mb-5" data-aos="fade-up">
                <h2 class="display-5 fw-bold mb-3">Why Choose Our Clinic?</h2>
                <p class="lead text-muted">Experience healthcare reimagined with our innovative features</p>
            </div>
            <div class="row g-4">
                <div class="col-md-6 col-lg-3" data-aos="fade-up" data-aos-delay="100">
                    <div class="feature-card">
                        <div class="feature-icon">
                            <i class="fas fa-calendar-check"></i>
                        </div>
                        <h3 class="feature-title">Easy Booking</h3>
                        <p class="feature-text">Book appointments with your preferred doctors in just a few clicks, 24/7.</p>
                        <a href="feature_easy_booking.py" class="text-decoration-none">Learn more <i class="fas fa-arrow-right ms-2"></i></a>
                    </div>
                </div>
                <div class="col-md-6 col-lg-3" data-aos="fade-up" data-aos-delay="200">
                    <div class="feature-card">
                        <div class="feature-icon">
                            <i class="fas fa-user-md"></i>
                        </div>
                        <h3 class="feature-title">Expert Doctors</h3>
                        <p class="feature-text">Access to qualified specialists across various medical fields.</p>
                        <a href="feature_expert_doctors.py" class="text-decoration-none">Learn more <i class="fas fa-arrow-right ms-2"></i></a>
                    </div>
                </div>
                <div class="col-md-6 col-lg-3" data-aos="fade-up" data-aos-delay="300">
                    <div class="feature-card">
                        <div class="feature-icon">
                            <i class="fas fa-clock"></i>
                        </div>
                        <h3 class="feature-title">24/7 Access</h3>
                        <p class="feature-text">Manage your appointments and health records anytime, anywhere.</p>
                        <a href="feature_24_7_access.py" class="text-decoration-none">Learn more <i class="fas fa-arrow-right ms-2"></i></a>
                    </div>
                </div>
                <div class="col-md-6 col-lg-3" data-aos="fade-up" data-aos-delay="400">
                    <div class="feature-card">
                        <div class="feature-icon">
                            <i class="fas fa-shield-alt"></i>
                        </div>
                        <h3 class="feature-title">Secure & Private</h3>
                        <p class="feature-text">Your health data is encrypted and protected with enterprise-grade security.</p>
                        <a href="feature_secure_private.py" class="text-decoration-none">Learn more <i class="fas fa-arrow-right ms-2"></i></a>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Specialties Section -->
    <section id="specialties" class="py-5 bg-light">
        <div class="container">
            <div class="text-center mb-5" data-aos="fade-up">
                <h2 class="display-5 fw-bold mb-3">Our Medical Specialties</h2>
                <p class="lead text-muted">Comprehensive care across all major medical fields</p>
            </div>
            <div class="row g-4">
""")

# Display specialties dynamically
for i, specialty in enumerate(specialties[:8]):
    delay = 100 + (i * 50)
    specialty_name = specialty['specialty_name']
    # Encode for URL
    specialty_url_encoded = specialty_name.replace(' ', '+')
    print(f"""
                <div class="col-md-3 col-6" data-aos="fade-up" data-aos-delay="{delay}">
                    <a href="book_appointment.py?specialty={specialty_url_encoded}" class="specialty-card text-decoration-none">
                        <div class="specialty-icon">
                            <i class="{specialty.get('icon_class', 'fas fa-stethoscope')}"></i>
                        </div>
                        <div class="specialty-name">{specialty_name}</div>
                        <small class="text-muted">{specialty.get('description', '')[:50]}...</small>
                    </a>
                </div>
    """)

print("""
            </div>
        </div>
    </section>

    <!-- How It Works Section -->
    <section class="py-5">
        <div class="container">
            <div class="text-center mb-5" data-aos="fade-up">
                <h2 class="display-5 fw-bold mb-3">How It Works</h2>
                <p class="lead text-muted">Simple steps to better healthcare</p>
            </div>
            <div class="row">
                <div class="col-md-3 text-center" data-aos="fade-up" data-aos-delay="100">
                    <div class="position-relative">
                        <div class="display-1 fw-bold text-primary opacity-25">1</div>
                        <div class="position-absolute top-50 start-50 translate-middle">
                            <i class="fas fa-user-plus fa-3x text-primary"></i>
                        </div>
                    </div>
                    <h4 class="mt-3">Register</h4>
                    <p class="text-muted">Create your account with basic information</p>
                </div>
                <div class="col-md-3 text-center" data-aos="fade-up" data-aos-delay="200">
                    <div class="position-relative">
                        <div class="display-1 fw-bold text-primary opacity-25">2</div>
                        <div class="position-absolute top-50 start-50 translate-middle">
                            <i class="fas fa-search fa-3x text-primary"></i>
                        </div>
                    </div>
                    <h4 class="mt-3">Find Doctor</h4>
                    <p class="text-muted">Search by specialty or availability</p>
                </div>
                <div class="col-md-3 text-center" data-aos="fade-up" data-aos-delay="300">
                    <div class="position-relative">
                        <div class="display-1 fw-bold text-primary opacity-25">3</div>
                        <div class="position-absolute top-50 start-50 translate-middle">
                            <i class="fas fa-calendar-alt fa-3x text-primary"></i>
                        </div>
                    </div>
                    <h4 class="mt-3">Book Slot</h4>
                    <p class="text-muted">Choose available time that suits you</p>
                </div>
                <div class="col-md-3 text-center" data-aos="fade-up" data-aos-delay="400">
                    <div class="position-relative">
                        <div class="display-1 fw-bold text-primary opacity-25">4</div>
                        <div class="position-absolute top-50 start-50 translate-middle">
                            <i class="fas fa-check-circle fa-3x text-primary"></i>
                        </div>
                    </div>
                    <h4 class="mt-3">Get Confirmation</h4>
                    <p class="text-muted">Receive instant booking confirmation</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Testimonials Section -->
    <section class="py-5 bg-light">
        <div class="container">
            <div class="text-center mb-5" data-aos="fade-up">
                <h2 class="display-5 fw-bold mb-3">What Our Patients Say</h2>
                <p class="lead text-muted">Real experiences from real people</p>
            </div>
            <div class="row">
                <div class="col-md-4 mb-4" data-aos="fade-up" data-aos-delay="100">
                    <div class="card h-100 border-0 shadow-sm">
                        <div class="card-body p-4">
                            <div class="mb-3">
                                <i class="fas fa-star text-warning"></i>
                                <i class="fas fa-star text-warning"></i>
                                <i class="fas fa-star text-warning"></i>
                                <i class="fas fa-star text-warning"></i>
                                <i class="fas fa-star text-warning"></i>
                            </div>
                            <p class="card-text mb-4">"Excellent service! The online booking system is so convenient. I booked an appointment with a cardiologist in minutes."</p>
                            <div class="d-flex align-items-center">
                                <img src="https://ui-avatars.com/api/?name=John+ Mwangi&size=50&background=2A5C82&color=fff" class="rounded-circle me-3" width="50">
                                <div>
                                    <h6 class="mb-0">John Mwangi</h6>
                                    <small class="text-muted">Patient</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-4 mb-4" data-aos="fade-up" data-aos-delay="200">
                    <div class="card h-100 border-0 shadow-sm">
                        <div class="card-body p-4">
                            <div class="mb-3">
                                <i class="fas fa-star text-warning"></i>
                                <i class="fas fa-star text-warning"></i>
                                <i class="fas fa-star text-warning"></i>
                                <i class="fas fa-star text-warning"></i>
                                <i class="fas fa-star text-warning"></i>
                            </div>
                            <p class="card-text mb-4">"The doctors are very professional and caring. The system makes it easy to keep track of all my appointments."</p>
                            <div class="d-flex align-items-center">
                                <img src="https://ui-avatars.com/api/?name=Mary+Akinyi&size=50&background=2A5C82&color=fff" class="rounded-circle me-3" width="50">
                                <div>
                                    <h6 class="mb-0">Mary Akinyi</h6>
                                    <small class="text-muted">Patient</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-4 mb-4" data-aos="fade-up" data-aos-delay="300">
                    <div class="card h-100 border-0 shadow-sm">
                        <div class="card-body p-4">
                            <div class="mb-3">
                                <i class="fas fa-star text-warning"></i>
                                <i class="fas fa-star text-warning"></i>
                                <i class="fas fa-star text-warning"></i>
                                <i class="fas fa-star text-warning"></i>
                                <i class="fas fa-star-half-alt text-warning"></i>
                            </div>
                            <p class="card-text mb-4">"Great platform! The reminder notifications help me never miss an appointment. Highly recommended!"</p>
                            <div class="d-flex align-items-center">
                                <img src="https://ui-avatars.com/api/?name=Peter+Kimani&size=50&background=2A5C82&color=fff" class="rounded-circle me-3" width="50">
                                <div>
                                    <h6 class="mb-0">Peter Kimani</h6>
                                    <small class="text-muted">Patient</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
""")

# Call to Action – personalized for logged‑in users
if user_info:
    # Prepare personalized welcome message based on user type
    if user_type == 'patient':
        welcome_msg = f"Welcome back, {user_info['full_name']}! Ready to book your next appointment?"
    elif user_type == 'doctor':
        welcome_msg = f"Welcome back, Dr. {user_info['full_name']}! Manage your schedule and patients."
    elif user_type == 'admin':
        welcome_msg = f"Welcome back, {user_info['full_name']}! Manage the clinic operations."
    else:
        welcome_msg = "Welcome back! Manage your account."

    print(f"""
    <!-- Call to Action -->
    <section class="py-5">
        <div class="container">
            <div class="card border-0 bg-gradient-primary text-white p-5" style="background: var(--gradient-primary);">
                <div class="row align-items-center">
                    <div class="col-lg-8 text-center text-lg-start mb-4 mb-lg-0">
                        <h3 class="h2 mb-2">{welcome_msg}</h3>
                        <p class="mb-0 opacity-75">Access your personalized dashboard to manage appointments, profile, and more.</p>
                    </div>
                    <div class="col-lg-4 text-center text-lg-end">
                        <a href="{dashboard_link}" class="btn btn-light btn-lg px-5">
                            <i class="fas fa-tachometer-alt me-2"></i>Go to Dashboard
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </section>
    """)
else:
    print("""
    <!-- Call to Action -->
    <section class="py-5">
        <div class="container">
            <div class="card border-0 bg-gradient-primary text-white p-5" style="background: var(--gradient-primary);">
                <div class="row align-items-center">
                    <div class="col-lg-8 text-center text-lg-start mb-4 mb-lg-0">
                        <h3 class="h2 mb-2">Ready to Experience Better Healthcare?</h3>
                        <p class="mb-0 opacity-75">Join thousands of satisfied patients who trust us with their health</p>
                    </div>
                    <div class="col-lg-4 text-center text-lg-end">
                        <a href="patient_register.py" class="btn btn-light btn-lg px-5">
                            <i class="fas fa-calendar-plus me-2"></i>Get Started
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </section>
    """)

print("""
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
                        <li class="mb-2"><a href="#home">Home</a></li>
                        <li class="mb-2"><a href="#features">Features</a></li>
                        <li class="mb-2"><a href="#specialties">Specialties</a></li>
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

    <!-- Toast Container -->
    <div class="toast-container" id="toastContainer"></div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
    <script>
        // Initialize AOS
        AOS.init({
            duration: 800,
            once: true
        });
        
        // Smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
        
        // Navbar background on scroll
        window.addEventListener('scroll', function() {
            const navbar = document.querySelector('.navbar');
            if (window.scrollY > 50) {
                navbar.style.background = 'rgba(255, 255, 255, 0.98)';
                navbar.style.boxShadow = 'var(--shadow-md)';
            } else {
                navbar.style.background = 'rgba(255, 255, 255, 0.95)';
                navbar.style.boxShadow = 'var(--shadow-sm)';
            }
        });
        
        // Show toast message
        function showToast(message, type = 'success') {{
            const toastContainer = document.getElementById('toastContainer');
            const toast = document.createElement('div');
            toast.className = 'toast-custom';
            toast.innerHTML = `
                <div class="d-flex align-items-center">
                    <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} text-${type} me-2"></i>
                    <div>${message}</div>
                </div>
            `;
            toastContainer.appendChild(toast);
            setTimeout(() => {{
                toast.remove();
            }}, 3000);
        }}
    </script>
</body>
</html>
""")