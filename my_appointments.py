#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Patient Appointments Module
Displays patient's appointment history and allows cancellation
"""

import cgi
import cgitb
import os
import sys

cgitb.enable()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from session import SessionManager
from database import DatabaseOperations

print("Content-Type: text/html; charset=utf-8")
print()

# Start session
session = SessionManager()
session.start_session()

# Check if user is logged in
if not session.is_logged_in() or session.get('user_type') != 'patient':
    print('<meta http-equiv="refresh" content="0;url=patient_login.py">')
    sys.exit()

# Get user info
user_info = session.get_user_info()
patient_id = user_info['user_id']

# Handle cancellation
form = cgi.FieldStorage()
cancel_id = form.getvalue('cancel', '')
if cancel_id:
    try:
        DatabaseOperations.cancel_appointment(cancel_id, patient_id)
        print('<meta http-equiv="refresh" content="0;url=my_appointments.py?cancelled=1">')
        sys.exit()
    except:
        pass

# Get appointments
try:
    appointments = DatabaseOperations.get_patient_appointments(patient_id)
    
    # Separate upcoming and past appointments
    from datetime import datetime
    today = datetime.now().date()
    
    upcoming = []
    past = []
    
    for apt in appointments:
        apt_date = datetime.strptime(str(apt['appointment_date']), '%Y-%m-%d').date()
        if apt_date >= today and apt['status'] in ['Scheduled', 'Rescheduled']:
            upcoming.append(apt)
        else:
            past.append(apt)
except Exception as e:
    appointments = []
    upcoming = []
    past = []
    error = str(e)

# HTML Template
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Appointments - Clinic Management System</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome 6 -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        :root {{
            --primary-color: #2A5C82;
            --secondary-color: #4A90E2;
            --gradient-primary: linear-gradient(135deg, #2A5C82 0%, #4A90E2 100%);
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background: #f8f9fa;
        }}
        
        .navbar {{
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .appointments-container {{
            max-width: 1200px;
            margin: 100px auto 50px;
            padding: 0 20px;
        }}
        
        .page-header {{
            background: var(--gradient-primary);
            color: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(42, 92, 130, 0.3);
        }}
        
        .appointment-card {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border-left: 4px solid var(--primary-color);
        }}
        
        .appointment-card:hover {{
            transform: translateX(5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
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
        
        .btn-cancel {{
            background: #dc3545;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 15px;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }}
        
        .btn-cancel:hover {{
            background: #c82333;
            transform: translateY(-2px);
            box-shadow: 0 5px 10px rgba(220, 53, 69, 0.3);
        }}
        
        .btn-reschedule {{
            background: #ffc107;
            color: #212529;
            border: none;
            border-radius: 8px;
            padding: 8px 15px;
            font-size: 0.9rem;
            margin-right: 10px;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            background: white;
            border-radius: 20px;
        }}
        
        .empty-state i {{
            font-size: 4rem;
            color: #dee2e6;
            margin-bottom: 20px;
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
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-light fixed-top">
        <div class="container">
            <a class="navbar-brand" href="index.py">
                <i class="fas fa-clinic-medical me-2 text-primary"></i>
                ClinicCare
            </a>
            <div class="ms-auto d-flex align-items-center">
                <span class="me-3">
                    <i class="fas fa-user me-2 text-primary"></i>
                    {user_info['full_name']}
                </span>
                <a href="logout.py" class="btn btn-outline-danger btn-sm">
                    <i class="fas fa-sign-out-alt me-1"></i>Logout
                </a>
            </div>
        </div>
    </nav>
    
    <div class="appointments-container">
        <div class="page-header">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h2><i class="fas fa-calendar-check me-3"></i>My Appointments</h2>
                    <p class="mb-0">View and manage all your appointments</p>
                </div>
                <div class="col-md-4 text-md-end">
                    <a href="book_appointment.py" class="btn btn-light">
                        <i class="fas fa-plus me-2"></i>Book New Appointment
                    </a>
                </div>
            </div>
        </div>
        
        <!-- Filter Tabs -->
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
        
        <!-- Tab Content -->
        <div class="tab-content" id="appointmentTabsContent">
            <!-- Upcoming Appointments -->
            <div class="tab-pane fade show active" id="upcoming" role="tabpanel">
""")

if upcoming:
    for apt in upcoming:
        status_class = f"status-{apt['status'].lower()}"
        can_cancel = apt['status'] == 'Scheduled'
        
        print(f"""
                <div class="appointment-card">
                    <div class="row align-items-center">
                        <div class="col-md-3">
                            <div class="d-flex align-items-center">
                                <i class="fas fa-user-md fa-2x text-primary me-3"></i>
                                <div>
                                    <h6 class="mb-1">Dr. {apt['doctor_name']}</h6>
                                    <small class="text-muted">{apt['specialty']}</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <i class="fas fa-calendar me-2 text-primary"></i>
                            {apt['date_formatted']}
                        </div>
                        <div class="col-md-2">
                            <i class="fas fa-clock me-2 text-primary"></i>
                            {apt['time_formatted']}
                        </div>
                        <div class="col-md-2">
                            <span class="status-badge {status_class}">{apt['status']}</span>
                        </div>
                        <div class="col-md-3 text-end">
        """)
        
        if can_cancel:
            print(f"""
                            <button class="btn btn-reschedule" onclick="reschedule({apt['appointment_id']})">
                                <i class="fas fa-calendar-alt me-1"></i>Reschedule
                            </button>
                            <button class="btn btn-cancel" onclick="cancelAppointment({apt['appointment_id']})">
                                <i class="fas fa-times me-1"></i>Cancel
                            </button>
            """)
        
        print("""
                        </div>
                    </div>
                </div>
        """)
else:
    print("""
                <div class="empty-state">
                    <i class="fas fa-calendar-times"></i>
                    <h4>No Upcoming Appointments</h4>
                    <p class="text-muted mb-4">You haven't scheduled any appointments yet</p>
                    <a href="book_appointment.py" class="btn btn-primary-custom">
                        <i class="fas fa-calendar-plus me-2"></i>Book Your First Appointment
                    </a>
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
        print(f"""
                <div class="appointment-card past">
                    <div class="row align-items-center">
                        <div class="col-md-3">
                            <div class="d-flex align-items-center">
                                <i class="fas fa-user-md fa-2x text-muted me-3"></i>
                                <div>
                                    <h6 class="mb-1">Dr. {apt['doctor_name']}</h6>
                                    <small class="text-muted">{apt['specialty']}</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <i class="fas fa-calendar me-2 text-muted"></i>
                            {apt['date_formatted']}
                        </div>
                        <div class="col-md-2">
                            <i class="fas fa-clock me-2 text-muted"></i>
                            {apt['time_formatted']}
                        </div>
                        <div class="col-md-2">
                            <span class="status-badge {status_class}">{apt['status']}</span>
                        </div>
                        <div class="col-md-3 text-end">
                            <button class="btn btn-outline-primary btn-sm" onclick="viewDetails({apt['appointment_id']})">
                                <i class="fas fa-eye me-1"></i>View Details
                            </button>
                        </div>
                    </div>
                </div>
        """)
else:
    print("""
                <div class="empty-state">
                    <i class="fas fa-history"></i>
                    <h4>No Past Appointments</h4>
                    <p class="text-muted">Your appointment history will appear here</p>
                </div>
""")

print("""
            </div>
        </div>
    </div>
    
    <!-- Cancel Confirmation Modal -->
    <div class="modal fade" id="cancelModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Cancel Appointment</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p>Are you sure you want to cancel this appointment?</p>
                    <p class="text-muted small">This action cannot be undone.</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <a href="#" id="confirmCancel" class="btn btn-danger">Yes, Cancel Appointment</a>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <script>
        function cancelAppointment(appointmentId) {
            const modal = new bootstrap.Modal(document.getElementById('cancelModal'));
            document.getElementById('confirmCancel').href = `?cancel=${appointmentId}`;
            modal.show();
        }
        
        function reschedule(appointmentId) {
            window.location.href = `reschedule_appointment.py?id=${appointmentId}`;
        }
        
        function viewDetails(appointmentId) {
            window.location.href = `appointment_details.py?id=${appointmentId}`;
        }
        
        // Show cancellation message if present
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('cancelled') === '1') {
            alert('Appointment cancelled successfully');
        }
    </script>
</body>
</html>
""")