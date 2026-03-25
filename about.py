#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
About Us page for Clinic Management System
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
    <title>About Us - ClinicCare</title>
    
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
        
        /* Content Cards */
        .about-card {
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: var(--shadow-md);
            transition: all 0.3s ease;
            height: 100%;
        }
        
        .about-card:hover {
            transform: translateY(-5px);
            box-shadow: var(--shadow-hover);
        }
        
        .team-member {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .team-member img {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            object-fit: cover;
            margin-bottom: 1rem;
            border: 4px solid var(--primary-color);
            transition: transform 0.3s ease;
        }
        
        .team-member img:hover {
            transform: scale(1.05);
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
                        <a class="nav-link active" href="about.py">About</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="contact.py">Contact</a>
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
                    <h1 class="hero-title">About ClinicCare</h1>
                    <p class="hero-subtitle">
                        Your trusted partner in modern healthcare management
                    </p>
                </div>
            </div>
        </div>
    </section>

    <!-- Our Story -->
    <section class="py-5">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-lg-6 mb-4 mb-lg-0" data-aos="fade-right">
                    <h2 class="display-6 fw-bold mb-4">Our Story</h2>
                    <p class="lead mb-3">
                        Founded in 2026, ClinicCare emerged from a vision to revolutionize healthcare accessibility in Kenya.
                    </p>
                    <p>
                        We recognized that patients needed a seamless way to connect with doctors, manage appointments, and track their health records.
                        Starting as a small project at Kirinyaga University, we have grown into a trusted platform serving thousands of patients across the region.
                    </p>
                    <p>
                        Today, ClinicCare is proud to partner with leading healthcare professionals to provide quality, convenient, and patient-centered care.
                        Our mission is to make healthcare management simple, efficient, and accessible to everyone.
                    </p>
                </div>
                <div class="col-lg-6" data-aos="fade-left">
                    <img src="https://picsum.photos/id/20/600/400" alt="Our Story" class="img-fluid rounded-4 shadow-lg">
                </div>
            </div>
        </div>
    </section>

    <!-- Mission, Vision, Values -->
    <section class="py-5 bg-light">
        <div class="container">
            <div class="row g-4">
                <div class="col-md-4" data-aos="fade-up" data-aos-delay="100">
                    <div class="about-card text-center">
                        <div class="feature-icon mx-auto mb-3">
                            <i class="fas fa-bullseye fa-3x text-primary"></i>
                        </div>
                        <h3 class="h4 mb-3">Our Mission</h3>
                        <p class="text-muted">
                            To provide a seamless, patient-centered healthcare management system that empowers individuals to take control of their health.
                        </p>
                    </div>
                </div>
                <div class="col-md-4" data-aos="fade-up" data-aos-delay="200">
                    <div class="about-card text-center">
                        <div class="feature-icon mx-auto mb-3">
                            <i class="fas fa-eye fa-3x text-primary"></i>
                        </div>
                        <h3 class="h4 mb-3">Our Vision</h3>
                        <p class="text-muted">
                            To be the leading digital health platform in Africa, bridging the gap between patients and quality healthcare.
                        </p>
                    </div>
                </div>
                <div class="col-md-4" data-aos="fade-up" data-aos-delay="300">
                    <div class="about-card text-center">
                        <div class="feature-icon mx-auto mb-3">
                            <i class="fas fa-heart fa-3x text-primary"></i>
                        </div>
                        <h3 class="h4 mb-3">Our Values</h3>
                        <p class="text-muted">
                            Compassion, Integrity, Innovation, Excellence, and Patient-Centered Care.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Our Team -->
    <section class="py-5">
        <div class="container">
            <div class="text-center mb-5" data-aos="fade-up">
                <h2 class="display-5 fw-bold mb-3">Meet Our Team</h2>
                <p class="lead text-muted">Dedicated professionals committed to your health</p>
            </div>
            <div class="row">
                <div class="col-md-4" data-aos="fade-up" data-aos-delay="100">
                    <div class="team-member">
                        <img src="https://ui-avatars.com/api/?name=Dr.+Jane+Wanjiku&size=150&background=2A5C82&color=fff" alt="Dr. Jane Wanjiku">
                        <h5 class="mt-3">Dr. Jane Wanjiku</h5>
                        <p class="text-muted">Medical Director</p>
                        <small class="text-muted">15+ years experience in general medicine</small>
                    </div>
                </div>
                <div class="col-md-4" data-aos="fade-up" data-aos-delay="200">
                    <div class="team-member">
                        <img src="https://ui-avatars.com/api/?name=Dr.+John+Kimani&size=150&background=2A5C82&color=fff" alt="Dr. John Kimani">
                        <h5 class="mt-3">Dr. John Kimani</h5>
                        <p class="text-muted">Senior Consultant</p>
                        <small class="text-muted">Cardiology specialist</small>
                    </div>
                </div>
                <div class="col-md-4" data-aos="fade-up" data-aos-delay="300">
                    <div class="team-member">
                        <img src="https://ui-avatars.com/api/?name=Sarah+Omondi&size=150&background=2A5C82&color=fff" alt="Sarah Omondi">
                        <h5 class="mt-3">Sarah Omondi</h5>
                        <p class="text-muted">Patient Care Coordinator</p>
                        <small class="text-muted">Ensuring smooth patient experience</small>
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