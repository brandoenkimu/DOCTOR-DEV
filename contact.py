#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Contact Us page for Clinic Management System
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

# Parse form data (if contact form submitted)
form = cgi.FieldStorage()
contact_action = form.getvalue('action')
contact_success = False
contact_error = None

if contact_action == 'send_message':
    name = form.getvalue('name', '').strip()
    email = form.getvalue('email', '').strip()
    message = form.getvalue('message', '').strip()
    if name and email and message:
        # For simplicity, we just simulate success.
        # In a real system, you could send email or store in DB.
        contact_success = True
    else:
        contact_error = "Please fill in all fields."

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

# HTML Template
print("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact Us - ClinicCare</title>
    
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
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--primary-color);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--secondary-color);
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
        
        .nav-link.active::after {
            width: 80%;
        }
        
        /* Hero Section */
        .hero-section {
            background: var(--gradient-primary);
            color: white;
            padding: 120px 0 80px;
            position: relative;
            overflow: hidden;
        }
        
        .hero-section::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: rotate 30s linear infinite;
        }
        
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        .hero-title {
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 1.5rem;
            animation: fadeInUp 1s ease;
        }
        
        .hero-subtitle {
            font-size: 1.25rem;
            margin-bottom: 2rem;
            opacity: 0.9;
            animation: fadeInUp 1s ease 0.2s both;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Contact Cards */
        .contact-card {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: var(--shadow-md);
            transition: all 0.3s ease;
            height: 100%;
            text-align: center;
        }
        
        .contact-card:hover {
            transform: translateY(-5px);
            box-shadow: var(--shadow-hover);
        }
        
        .contact-icon {
            width: 70px;
            height: 70px;
            background: var(--gradient-primary);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1.5rem;
            color: white;
            font-size: 1.75rem;
        }
        
        /* Contact Form */
        .contact-form {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: var(--shadow-md);
        }
        
        .form-control, .form-select {
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            padding: 0.75rem;
        }
        
        .form-control:focus, .form-select:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 0.2rem rgba(42, 92, 130, 0.25);
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
        
        /* Responsive */
        @media (max-width: 768px) {
            .hero-title {
                font-size: 2.5rem;
            }
            
            .hero-section {
                padding: 100px 0 60px;
                text-align: center;
            }
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
                        <a class="nav-link active" href="contact.py">Contact</a>
                    </li>
""")

if user_info:
    print(f"""
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-user-circle me-1"></i>
                            {user_info['full_name']}
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li><a class="dropdown-item" href="patient_dashboard.py">
                                <i class="fas fa-tachometer-alt me-2"></i>Dashboard
                            </a></li>
                            <li><a class="dropdown-item" href="my_appointments.py">
                                <i class="fas fa-calendar-check me-2"></i>My Appointments
                            </a></li>
                            <li><a class="dropdown-item" href="patient_profile.py">
                                <i class="fas fa-user-circle me-2"></i>My Profile
                            </a></li>
                            <li><a class="dropdown-item" href="patient_change_password.py">
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
        <div class="container position-relative">
            <div class="row">
                <div class="col-lg-8 mx-auto text-center" data-aos="fade-up">
                    <h1 class="hero-title">Contact Us</h1>
                    <p class="hero-subtitle">
                        We're here to help. Reach out to us anytime.
                    </p>
                </div>
            </div>
        </div>
    </section>

    <!-- Contact Cards -->
    <section class="py-5">
        <div class="container">
            <div class="row g-4">
                <div class="col-md-4" data-aos="fade-up" data-aos-delay="100">
                    <div class="contact-card">
                        <div class="contact-icon mx-auto">
                            <i class="fas fa-map-marker-alt"></i>
                        </div>
                        <h5>Visit Us</h5>
                        <p class="text-muted">
                            Kirinyaga University<br>
                            P.O. Box 143-10300, Kerugoya<br>
                            Kenya
                        </p>
                    </div>
                </div>
                <div class="col-md-4" data-aos="fade-up" data-aos-delay="200">
                    <div class="contact-card">
                        <div class="contact-icon mx-auto">
                            <i class="fas fa-phone-alt"></i>
                        </div>
                        <h5>Call Us</h5>
                        <p class="text-muted">
                            +254 116 747 630<br>
                            +254 722 123 456<br>
                            Mon-Fri: 8am - 6pm
                        </p>
                    </div>
                </div>
                <div class="col-md-4" data-aos="fade-up" data-aos-delay="300">
                    <div class="contact-card">
                        <div class="contact-icon mx-auto">
                            <i class="fas fa-envelope"></i>
                        </div>
                        <h5>Email Us</h5>
                        <p class="text-muted">
                            info@cliniccare.com<br>
                            support@cliniccare.com<br>
                            We reply within 24h
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Contact Form -->
    <section class="py-5 bg-light">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-lg-8" data-aos="fade-up">
                    <div class="contact-form">
                        <h3 class="text-center mb-4">Send Us a Message</h3>
""")

if contact_success:
    print("""
                        <div class="alert alert-success">
                            <i class="fas fa-check-circle me-2"></i>
                            Thank you for your message! We'll get back to you soon.
                        </div>
    """)
elif contact_error:
    print(f"""
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-circle me-2"></i>
                            {contact_error}
                        </div>
    """)

print("""
                        <form method="post" action="contact.py">
                            <input type="hidden" name="action" value="send_message">
                            <div class="mb-3">
                                <label for="name" class="form-label">Full Name</label>
                                <input type="text" class="form-control" id="name" name="name" required>
                            </div>
                            <div class="mb-3">
                                <label for="email" class="form-label">Email Address</label>
                                <input type="email" class="form-control" id="email" name="email" required>
                            </div>
                            <div class="mb-3">
                                <label for="message" class="form-label">Message</label>
                                <textarea class="form-control" id="message" name="message" rows="5" required></textarea>
                            </div>
                            <div class="text-center">
                                <button type="submit" class="btn btn-primary-custom btn-lg px-5">
                                    <i class="fas fa-paper-plane me-2"></i>Send Message
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Map Section (optional) -->
    <section class="py-5">
        <div class="container">
            <div class="text-center mb-4" data-aos="fade-up">
                <h3>Find Us Here</h3>
            </div>
            <div class="ratio ratio-16x9" data-aos="fade-up">
                <iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3988.761781380277!2d37.31264031474466!3d-0.538032099638248!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x1827c1f5b3c2f7e9%3A0x4e6b2f0e8b5c3a7!2sKirinyaga%20University!5e0!3m2!1sen!2ske!4v1642150000000!5m2!1sen!2ske" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy"></iframe>
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

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
    <script>
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
    </script>
</body>
</html>
""")