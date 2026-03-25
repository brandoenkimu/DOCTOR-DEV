#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Reschedule Appointment Module
Allows patients to change the date/time of an existing appointment
"""

import cgi
import cgitb
import os
import sys
import json
from datetime import datetime, timedelta

cgitb.enable()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from session import SessionManager
from database import DatabaseOperations
from validation import Validator

# --- Header collection ---
headers = []

# Start session
session = SessionManager()
session.start_session()

# Get cookie header
cookie_header = session.get_cookie_header()
if cookie_header:
    headers.append(cookie_header)

# Check if user is logged in
if not session.is_logged_in() or session.get('user_type') != 'patient':
    headers.append("Location: patient_login.py")
    for h in headers:
        print(h)
    print()
    sys.exit()

user_info = session.get_user_info()
patient_id = user_info['user_id']

# Get appointment ID from query string
form = cgi.FieldStorage()
appointment_id = form.getvalue('id', '')

if not appointment_id:
    headers.append("Location: my_appointments.py")
    for h in headers:
        print(h)
    print()
    sys.exit()

# Fetch the appointment and verify ownership
appointment = DatabaseOperations.execute_query(
    """SELECT a.*, d.full_name as doctor_name, d.specialty,
              d.doctor_id, d.consultation_fee
       FROM appointments a
       JOIN doctors d ON a.doctor_id = d.doctor_id
       WHERE a.appointment_id = %s AND a.patient_id = %s""",
    (appointment_id, patient_id),
    fetch_one=True
)

if not appointment:
    headers.append("Location: my_appointments.py")
    for h in headers:
        print(h)
    print()
    sys.exit()

# Get form data for rescheduling
action = form.getvalue('action', '')
new_date = form.getvalue('appointment_date', '')
new_slot = form.getvalue('slot_id', '')
new_symptoms = form.getvalue('symptoms', appointment['symptoms'] or '')

# Initialize variables
errors = []
success = False
available_slots = []
doctors = []

# Get list of doctors (optional, if we allow changing doctor)
try:
    doctors = DatabaseOperations.get_doctors_by_specialty()
except Exception as e:
    errors.append(f"Error loading doctors: {str(e)}")

# If new date selected, get available slots for the same doctor
if new_date and appointment:
    try:
        available_slots = DatabaseOperations.generate_time_slots(
            appointment['doctor_id'], new_date
        )
    except Exception as e:
        errors.append(f"Error loading slots: {str(e)}")

# Process reschedule
if action == 'reschedule':
    # Validate
    if not new_date:
        errors.append("Please select a new date")
    if not new_slot:
        errors.append("Please select a new time slot")
    
    if not errors:
        try:
            # Call a method to reschedule (will be added to DatabaseOperations)
            # This method should free the old slot and book the new one
            new_appointment_id = DatabaseOperations.reschedule_appointment(
                appointment_id,
                patient_id,
                appointment['doctor_id'],
                new_slot,
                new_symptoms
            )
            if new_appointment_id:
                success = True
        except Exception as e:
            errors.append(f"Reschedule failed: {str(e)}")

# Prepare headers for HTML output
headers.append("Content-Type: text/html; charset=utf-8")
for h in headers:
    print(h)
print()

# HTML starts here
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reschedule Appointment - Clinic Management System</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome 6 -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Flatpickr for date picking -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">
    
    <style>
        :root {{
            --primary: #2A5C82;
            --secondary: #4A90E2;
            --accent: #50C878;
            --danger: #FF6B6B;
            --gradient-primary: linear-gradient(135deg, #2A5C82 0%, #4A90E2 100%);
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background: #f4f6f9;
        }}
        
        .navbar {{
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .reschedule-container {{
            max-width: 1000px;
            margin: 100px auto 50px;
            padding: 0 20px;
        }}
        
        .card-custom {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .card-header-custom {{
            background: var(--gradient-primary);
            color: white;
            padding: 30px;
        }}
        
        .card-body-custom {{
            padding: 30px;
        }}
        
        .current-appointment {{
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            border-left: 4px solid var(--primary);
        }}
        
        .slot-card {{
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 15px;
        }}
        
        .slot-card:hover {{
            border-color: var(--accent);
            background: #f0fff4;
        }}
        
        .slot-card.selected {{
            border-color: var(--accent);
            background: #e8f5e9;
        }}
        
        .slot-card.booked {{
            opacity: 0.5;
            cursor: not-allowed;
            background: #f5f5f5;
        }}
        
        .btn-primary-custom {{
            background: var(--gradient-primary);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 12px 30px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        .btn-primary-custom:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(42,92,130,0.3);
            color: white;
        }}
        
        .btn-outline-custom {{
            border: 2px solid var(--primary);
            color: var(--primary);
            border-radius: 10px;
            padding: 12px 30px;
            font-weight: 600;
        }}
        
        .btn-outline-custom:hover {{
            background: var(--primary);
            color: white;
        }}
        
        .alert {{
            border-radius: 10px;
        }}
        
        .info-label {{
            font-weight: 600;
            color: #2C3E50;
        }}
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-light fixed-top">
        <div class="container">
            <a class="navbar-brand" href="index.py">
                <i class="fas fa-clinic-medical me-2 text-primary"></i>ClinicCare
            </a>
            <div class="ms-auto d-flex align-items-center">
                <span class="me-3">
                    <i class="fas fa-user me-2 text-primary"></i>{user_info['full_name']}
                </span>
                <a href="my_appointments.py" class="btn btn-outline-primary btn-sm me-2">
                    <i class="fas fa-arrow-left"></i> Back
                </a>
                <a href="logout.py" class="btn btn-outline-danger btn-sm">
                    <i class="fas fa-sign-out-alt"></i> Logout
                </a>
            </div>
        </div>
    </nav>
    
    <div class="reschedule-container">
        <div class="card-custom">
            <div class="card-header-custom">
                <h3><i class="fas fa-calendar-alt me-2"></i>Reschedule Appointment</h3>
                <p class="mb-0">Change the date and time of your appointment</p>
            </div>
            <div class="card-body-custom">
""")

if success:
    print(f"""
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    Appointment rescheduled successfully!
                </div>
                <div class="text-center mt-4">
                    <a href="my_appointments.py" class="btn btn-primary-custom">
                        <i class="fas fa-calendar-check me-2"></i>View My Appointments
                    </a>
                </div>
    """)
else:
    if errors:
        print('<div class="alert alert-danger"><i class="fas fa-exclamation-circle me-2"></i>')
        for e in errors:
            print(f'<div>{e}</div>')
        print('</div>')
    
    # Current appointment details
    print(f"""
                <div class="current-appointment">
                    <h5 class="mb-3"><i class="fas fa-info-circle me-2 text-primary"></i>Current Appointment</h5>
                    <div class="row">
                        <div class="col-md-3">
                            <div class="info-label">Doctor</div>
                            <div>Dr. {appointment['doctor_name']}</div>
                            <small class="text-muted">{appointment['specialty']}</small>
                        </div>
                        <div class="col-md-3">
                            <div class="info-label">Date</div>
                            <div>{appointment['appointment_date']}</div>
                        </div>
                        <div class="col-md-3">
                            <div class="info-label">Time</div>
                            <div>{appointment['appointment_time']}</div>
                        </div>
                        <div class="col-md-3">
                            <div class="info-label">Status</div>
                            <div><span class="badge bg-warning">{appointment['status']}</span></div>
                        </div>
                    </div>
                </div>
                
                <form method="post" action="reschedule_appointment.py?id={appointment_id}" id="rescheduleForm">
                    <input type="hidden" name="action" value="reschedule">
                    <input type="hidden" name="slot_id" id="selectedSlot" value="{new_slot}">
                    
                    <h5 class="mb-4"><i class="fas fa-calendar-plus me-2 text-primary"></i>Select New Date & Time</h5>
                    
                    <div class="row">
                        <div class="col-md-6 mb-4">
                            <label class="form-label fw-bold">New Appointment Date</label>
                            <input type="text" 
                                   class="form-control" 
                                   id="appointmentDate" 
                                   name="appointment_date"
                                   value="{new_date}"
                                   placeholder="Choose a date"
                                   required>
                        </div>
                        <div class="col-md-6 mb-4">
                            <label class="form-label fw-bold">Available Time Slots</label>
                            <div id="timeSlots" class="row g-3">
    """)
    
    if available_slots:
        for slot in available_slots:
            selected_class = 'selected' if str(slot['slot_id']) == new_slot else ''
            start_str = slot['start_time'].strftime('%H:%M') if hasattr(slot['start_time'], 'strftime') else slot['start_time']
            end_str = slot['end_time'].strftime('%H:%M') if hasattr(slot['end_time'], 'strftime') else slot['end_time']
            print(f"""
                                <div class="col-4">
                                    <div class="slot-card {selected_class}" 
                                         onclick="selectSlot({slot['slot_id']})">
                                        <strong>{start_str}</strong><br>
                                        <small class="text-muted">{end_str}</small>
                                    </div>
                                </div>
            """)
    else:
        print('<p class="text-muted">Select a date to see available slots</p>')
    
    print("""
                            </div>
                        </div>
                    </div>
                    
                    <div class="mb-4">
                        <label class="form-label fw-bold">Symptoms / Reason (optional)</label>
                        <textarea class="form-control" 
                                  name="symptoms" 
                                  rows="3"
                                  placeholder="Describe any symptoms or reason for visit">{new_symptoms}</textarea>
                    </div>
                    
                    <div class="d-flex justify-content-between mt-4">
                        <a href="my_appointments.py" class="btn btn-outline-custom">
                            <i class="fas fa-times me-2"></i>Cancel
                        </a>
                        <button type="submit" class="btn btn-primary-custom" id="submitBtn">
                            <i class="fas fa-check me-2"></i>Confirm Reschedule
                        </button>
                    </div>
                </form>
    """)
    
    # Hidden data for JavaScript
    print(f"""
                <div style="display: none;" id="doctorId">{appointment['doctor_id']}</div>
            </div>
        </div>
    </div>
    
    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>
    
    <script>
        flatpickr("#appointmentDate", {{
            minDate: "today",
            maxDate: new Date().fp_incr(30),
            disable: [
                function(date) {{
                    return date.getDay() === 0 || date.getDay() === 6;
                }}
            ],
            onChange: function(selectedDates, dateStr, instance) {{
                if (dateStr) {{
                    loadTimeSlots(dateStr);
                }}
            }}
        }});
        
        let selectedSlot = document.getElementById('selectedSlot').value;
        
        function selectSlot(slotId) {{
            selectedSlot = slotId;
            document.getElementById('selectedSlot').value = slotId;
            document.querySelectorAll('.slot-card').forEach(card => {{
                card.classList.remove('selected');
            }});
            event.currentTarget.classList.add('selected');
        }}
        
        function loadTimeSlots(date) {{
            const doctorId = document.getElementById('doctorId').textContent;
            
            fetch(`get_slots.py?doctor_id=${{doctorId}}&date=${{date}}`)
                .then(response => response.json())
                .then(data => {{
                    const slotsContainer = document.getElementById('timeSlots');
                    if (data.slots && data.slots.length > 0) {{
                        slotsContainer.innerHTML = data.slots.map(slot => {{
                            const bookedClass = slot.is_booked ? 'booked' : '';
                            const clickHandler = !slot.is_booked ? `selectSlot(${{slot.slot_id}})` : '';
                            return `
                                <div class="col-4">
                                    <div class="slot-card ${{bookedClass}}" 
                                         onclick="${{clickHandler}}">
                                        <strong>${{slot.start_time}}</strong><br>
                                        <small>${{slot.end_time}}</small>
                                    </div>
                                </div>
                            `;
                        }}).join('');
                    }} else {{
                        slotsContainer.innerHTML = '<p class="text-muted">No available slots for this date</p>';
                    }}
                }});
        }}
    </script>
</body>
</html>
""")