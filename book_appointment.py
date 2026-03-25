#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Appointment Booking Module
Allows patients to book appointments with doctors
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
if not session.is_logged_in():
    headers.append("Location: patient_login.py")
    for h in headers:
        print(h)
    print()
    sys.exit()

# Get current user
user_info = session.get_user_info()
patient_id = user_info['user_id']

# Get form data
form = cgi.FieldStorage()
action = form.getvalue('action', '')
selected_doctor = form.getvalue('doctor_id', '')
selected_date = form.getvalue('appointment_date', '')
selected_slot = form.getvalue('slot_id', '')
symptoms = form.getvalue('symptoms', '')

# Initialize variables
errors = []
success = False
doctors = []
available_slots = []
appointment_id = None

# Get list of doctors for selection
try:
    specialty_filter = form.getvalue('specialty', '')
    doctors = DatabaseOperations.get_doctors_by_specialty(specialty_filter)
except Exception as e:
    errors.append(f"Error loading doctors: {str(e)}")

# Get specialties for filter
try:
    specialties = DatabaseOperations.get_all_specialties()
except:
    specialties = []

# If doctor and date selected, get available slots
if selected_doctor and selected_date:
    try:
        available_slots = DatabaseOperations.generate_time_slots(selected_doctor, selected_date)
    except Exception as e:
        errors.append(f"Error loading slots: {str(e)}")

# Process booking
if action == 'book':
    # Validate booking data
    booking_data = {
        'doctor_id': selected_doctor,
        'appointment_date': selected_date,
        'slot_id': selected_slot,
        'symptoms': symptoms
    }
    
    errors = Validator.validate_appointment_booking(booking_data)
    
    if not errors:
        try:
            # Book the appointment
            appointment_id = DatabaseOperations.book_appointment(
                patient_id,
                selected_doctor,
                selected_slot,
                symptoms
            )
            
            if appointment_id:
                success = True
                # Clear form data after successful booking
                selected_doctor = ''
                selected_date = ''
                selected_slot = ''
                symptoms = ''
        except Exception as e:
            errors.append(f"Booking failed: {str(e)}")

# Determine content type (if we are outputting HTML)
headers.append("Content-Type: text/html; charset=utf-8")

# Print all headers
for h in headers:
    print(h)
print()  # blank line after headers

# HTML Template
print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Book Appointment - Clinic Management System</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome 6 -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Flatpickr for date picking -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">
    
    <style>
        :root {{
            --primary-color: #2A5C82;
            --secondary-color: #4A90E2;
            --accent-color: #50C878;
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
        
        .booking-container {{
            max-width: 1200px;
            margin: 100px auto 50px;
            padding: 0 20px;
        }}
        
        .booking-card {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .booking-header {{
            background: var(--gradient-primary);
            color: white;
            padding: 30px;
        }}
        
        .booking-body {{
            padding: 30px;
        }}
        
        .doctor-card {{
            border: 2px solid #e0e0e0;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .doctor-card:hover {{
            border-color: var(--primary-color);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .doctor-card.selected {{
            border-color: var(--primary-color);
            background: #f0f7ff;
        }}
        
        .slot-card {{
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .slot-card:hover {{
            border-color: var(--accent-color);
            background: #f0fff4;
        }}
        
        .slot-card.selected {{
            border-color: var(--accent-color);
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
            box-shadow: 0 10px 20px rgba(42, 92, 130, 0.3);
            color: white;
        }}
        
        .alert {{
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        
        .progress-bar {{
            height: 4px;
            background: var(--gradient-primary);
            transition: width 0.3s ease;
        }}
        
        .step-indicator {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 40px;
            position: relative;
        }}
        
        .step {{
            flex: 1;
            text-align: center;
            position: relative;
        }}
        
        .step-number {{
            width: 40px;
            height: 40px;
            background: #e0e0e0;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 10px;
            font-weight: bold;
            color: #666;
            transition: all 0.3s ease;
        }}
        
        .step.active .step-number {{
            background: var(--primary-color);
            color: white;
        }}
        
        .step.completed .step-number {{
            background: var(--accent-color);
            color: white;
        }}
        
        .step-label {{
            font-size: 0.9rem;
            color: #666;
        }}
        
        .step.active .step-label {{
            color: var(--primary-color);
            font-weight: 600;
        }}
        
        /* Custom notification style */
        .notification-info {{
            border-left: 4px solid var(--primary-color);
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
            <div class="ms-auto">
                <span class="me-3">
                    <i class="fas fa-user me-2"></i>{user_info['full_name']}
                </span>
                <a href="logout.py" class="btn btn-outline-danger btn-sm">
                    <i class="fas fa-sign-out-alt me-1"></i>Logout
                </a>
            </div>
        </div>
    </nav>
    
    <div class="booking-container">
        <div class="booking-card">
            <div class="booking-header">
                <h3><i class="fas fa-calendar-plus me-2"></i>Book an Appointment</h3>
                <p class="mb-0">Follow the steps below to schedule your visit</p>
            </div>
            
            <div class="booking-body">
                <!-- Step Indicator -->
                <div class="step-indicator">
                    <div class="step {'active' if not selected_doctor else 'completed'}">
                        <div class="step-number">1</div>
                        <div class="step-label">Select Doctor</div>
                    </div>
                    <div class="step {'active' if selected_doctor and not selected_slot else 'completed' if selected_doctor else ''}">
                        <div class="step-number">2</div>
                        <div class="step-label">Choose Date & Time</div>
                    </div>
                    <div class="step {'active' if selected_slot and not success else 'completed' if success else ''}">
                        <div class="step-number">3</div>
                        <div class="step-label">Confirm Details</div>
                    </div>
                </div>
""")

if success:
    print(f"""
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    Appointment booked successfully! Your appointment ID is #{appointment_id}
                </div>
                <div class="text-center mt-4">
                    <a href="my_appointments.py" class="btn btn-primary-custom">
                        <i class="fas fa-calendar-check me-2"></i>View My Appointments
                    </a>
                    <a href="book_appointment.py" class="btn btn-outline-primary ms-2">
                        <i class="fas fa-plus me-2"></i>Book Another
                    </a>
                </div>
    """)
else:
    if errors:
        print('<div class="alert alert-danger"><i class="fas fa-exclamation-circle me-2"></i>')
        for error in errors:
            print(f'<div>{error}</div>')
        print('</div>')
    
    print(f"""
                <form method="post" action="book_appointment.py" id="bookingForm">
                    <input type="hidden" name="action" value="book">
                    <input type="hidden" name="doctor_id" id="selectedDoctor" value="{selected_doctor}">
                    <input type="hidden" name="slot_id" id="selectedSlot" value="{selected_slot}">
                    
                    <!-- Step 1: Select Doctor -->
                    <div class="step-content" id="step1" style="display: {'block' if not selected_doctor else 'none'}">
                        <h5 class="mb-4">Select a Doctor</h5>
                        
                        <!-- Specialty Filter -->
                        <div class="mb-4">
                            <label class="form-label fw-bold">Filter by Specialty</label>
                            <select class="form-select" id="specialtyFilter" style="max-width: 300px;">
                                <option value="">All Specialties</option>
    """)
    
    for specialty in specialties:
        selected = 'selected' if specialty_filter == specialty['specialty_name'] else ''
        print(f'<option value="{specialty["specialty_name"]}" {selected}>{specialty["specialty_name"]}</option>')
    
    print("""
                            </select>
                        </div>
                        
                        <div class="row" id="doctorsList">
    """)
    
    for doctor in doctors:
        print(f"""
                            <div class="col-md-6">
                                <div class="doctor-card" onclick="selectDoctor({doctor['doctor_id']})">
                                    <div class="d-flex align-items-center">
                                        <div class="me-3">
                                            <i class="fas fa-user-md fa-3x text-primary"></i>
                                        </div>
                                        <div>
                                            <h5 class="mb-1">{doctor['full_name']}</h5>
                                            <p class="mb-1">
                                                <span class="badge bg-primary">{doctor['specialty']}</span>
                                            </p>
                                            <small class="text-muted">
                                                <i class="fas fa-clock me-1"></i>
                                                {doctor['experience_years']} years experience
                                            </small>
                                        </div>
                                    </div>
                                </div>
                            </div>
        """)
    
    print(f"""
                        </div>
                        
                        <div class="text-end mt-4">
                            <button type="button" class="btn btn-primary-custom" onclick="proceedToStep2()" id="step1Next" disabled>
                                Next <i class="fas fa-arrow-right ms-2"></i>
                            </button>
                        </div>
                    </div>
                    
                    <!-- Step 2: Select Date and Time -->
                    <div class="step-content" id="step2" style="display: {'block' if selected_doctor and not selected_slot else 'none'}">
                        <h5 class="mb-4">Select Appointment Date & Time</h5>
                        
                        <!-- Notification: appears until both date and time are selected -->
                        <div id="selectionNotification" class="alert alert-info alert-dismissible fade show notification-info" role="alert">
                            <i class="fas fa-info-circle me-2"></i>
                            <strong>Please select a date and a time slot.</strong> 
                            Once you choose both, this message will disappear.
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6 mb-4">
                                <label class="form-label fw-bold">Select Date</label>
                                <input type="text" 
                                       class="form-control" 
                                       id="appointmentDate" 
                                       name="appointment_date"
                                       value="{selected_date}"
                                       placeholder="Choose a date">
                            </div>
                            
                            <div class="col-md-6 mb-4">
                                <label class="form-label fw-bold">Available Time Slots</label>
                                <div id="timeSlots" class="row g-3">
    """)
    
    if available_slots:
        for slot in available_slots:
            selected_class = 'selected' if str(slot['slot_id']) == selected_slot else ''
            # Format times as strings to avoid datetime issues
            start_str = slot['start_time'].strftime('%H:%M') if hasattr(slot['start_time'], 'strftime') else slot['start_time']
            end_str = slot['end_time'].strftime('%H:%M') if hasattr(slot['end_time'], 'strftime') else slot['end_time']
            print(f"""
                                    <div class="col-4">
                                        <div class="slot-card {selected_class}" 
                                             onclick="selectSlot({slot['slot_id']})">
                                            <strong>{start_str}</strong>
                                            <br>
                                            <small class="text-muted">{end_str}</small>
                                        </div>
                                    </div>
            """)
    else:
        print('<p class="text-muted">Please select a date to see available slots</p>')
    
    print("""
                                </div>
                            </div>
                        </div>
                        
                        <div class="d-flex justify-content-between mt-4">
                            <button type="button" class="btn btn-outline-secondary" onclick="goToStep1()">
                                <i class="fas fa-arrow-left me-2"></i>Back
                            </button>
                            <button type="button" class="btn btn-primary-custom" onclick="proceedToStep3()" id="step2Next" disabled>
                                Next <i class="fas fa-arrow-right ms-2"></i>
                            </button>
                        </div>
                    </div>
                    
                    <!-- Step 3: Confirm Details -->
                    <div class="step-content" id="step3" style="display: {'block' if selected_slot else 'none'}">
                        <h5 class="mb-4">Confirm Appointment Details</h5>
                        
                        <div class="row">
                            <div class="col-md-8">
                                <div class="card border-0 bg-light mb-4">
                                    <div class="card-body">
                                        <h6 class="mb-3">Appointment Summary</h6>
                                        <table class="table table-borderless">
                                            <tr>
                                                <td><strong>Doctor:</strong></td>
                                                <td id="confirmDoctor"></td>
                                            </tr>
                                            <tr>
                                                <td><strong>Date:</strong></td>
                                                <td id="confirmDate"></td>
                                            </tr>
                                            <tr>
                                                <td><strong>Time:</strong></td>
                                                <td id="confirmTime"></td>
                                            </tr>
                                        </table>
                                    </div>
                                </div>
                                
                                <div class="mb-4">
                                    <label class="form-label fw-bold">Describe Your Symptoms</label>
                                    <textarea class="form-control" 
                                              name="symptoms" 
                                              rows="4"
                                              placeholder="Please describe your symptoms or reason for visit">{symptoms}</textarea>
                                </div>
                            </div>
                        </div>
                        
                        <div class="d-flex justify-content-between mt-4">
                            <button type="button" class="btn btn-outline-secondary" onclick="goToStep2()">
                                <i class="fas fa-arrow-left me-2"></i>Back
                            </button>
                            <button type="submit" class="btn btn-primary-custom">
                                <i class="fas fa-check me-2"></i>Confirm Booking
                            </button>
                        </div>
                    </div>
                </form>
    """)
    
    # Hidden data for JavaScript
    doctors_json = json.dumps(doctors, default=str).replace("'", "&apos;")
    print(f"""
                <div style="display: none;" 
                     id="doctorsData" 
                     data-doctors='{doctors_json}'>
                </div>
    """)

print("""
            </div>
        </div>
    </div>
    
    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>
    
    <script>
        // Initialize date picker
        flatpickr("#appointmentDate", {
            minDate: "today",
            maxDate: new Date().fp_incr(30),
            disable: [
                function(date) {
                    // Disable weekends
                    return date.getDay() === 0 || date.getDay() === 6;
                }
            ],
            onChange: function(selectedDates, dateStr, instance) {
                if (dateStr) {
                    loadTimeSlots(dateStr);
                }
                // After date change, reset slot selection and check notification
                selectedSlot = '';
                document.getElementById('selectedSlot').value = '';
                document.getElementById('step2Next').disabled = true;
                updateNotificationVisibility();
            }
        });
        
        let selectedDoctor = document.getElementById('selectedDoctor').value;
        let selectedSlot = document.getElementById('selectedSlot').value;
        
        // Function to show/hide the notification based on selections
        function updateNotificationVisibility() {
            const dateInput = document.getElementById('appointmentDate');
            const dateSelected = dateInput && dateInput.value ? true : false;
            const timeSelected = selectedSlot ? true : false;
            const notification = document.getElementById('selectionNotification');
            if (notification) {
                if (dateSelected && timeSelected) {
                    // Both selected: hide the notification
                    notification.style.display = 'none';
                } else {
                    // Show notification if not hidden manually
                    notification.style.display = 'block';
                }
            }
        }
        
        function selectDoctor(doctorId) {
            selectedDoctor = doctorId;
            document.getElementById('selectedDoctor').value = doctorId;
            document.getElementById('step1Next').disabled = false;
            
            // Update UI
            document.querySelectorAll('.doctor-card').forEach(card => {
                card.classList.remove('selected');
            });
            event.currentTarget.classList.add('selected');
        }
        
        function selectSlot(slotId) {
            selectedSlot = slotId;
            document.getElementById('selectedSlot').value = slotId;
            document.getElementById('step2Next').disabled = false;
            
            // Update UI
            document.querySelectorAll('.slot-card').forEach(card => {
                card.classList.remove('selected');
            });
            event.currentTarget.classList.add('selected');
            
            // Update notification visibility
            updateNotificationVisibility();
        }
        
        function proceedToStep2() {
            if (selectedDoctor) {
                document.getElementById('step1').style.display = 'none';
                document.getElementById('step2').style.display = 'block';
                
                // Update step indicators
                updateSteps(2);
                
                // Check if date and time are already selected (e.g., after going back)
                updateNotificationVisibility();
            }
        }
        
        function proceedToStep3() {
            if (selectedSlot) {
                // Load confirmation details
                loadConfirmationDetails();
                
                document.getElementById('step2').style.display = 'none';
                document.getElementById('step3').style.display = 'block';
                
                // Update step indicators
                updateSteps(3);
            }
        }
        
        function goToStep1() {
            document.getElementById('step2').style.display = 'none';
            document.getElementById('step1').style.display = 'block';
            updateSteps(1);
        }
        
        function goToStep2() {
            document.getElementById('step3').style.display = 'none';
            document.getElementById('step2').style.display = 'block';
            updateSteps(2);
            
            // Ensure notification visibility reflects current selections
            updateNotificationVisibility();
        }
        
        function updateSteps(step) {
            const steps = document.querySelectorAll('.step');
            steps.forEach((s, index) => {
                s.classList.remove('active', 'completed');
                if (index + 1 < step) {
                    s.classList.add('completed');
                } else if (index + 1 === step) {
                    s.classList.add('active');
                }
            });
        }
        
        function loadTimeSlots(date) {
            const doctorId = document.getElementById('selectedDoctor').value;
            
            fetch(`get_slots.py?doctor_id=${doctorId}&date=${date}`)
                .then(response => response.json())
                .then(data => {
                    const slotsContainer = document.getElementById('timeSlots');
                    if (data.slots && data.slots.length > 0) {
                        slotsContainer.innerHTML = data.slots.map(slot => {
                            const bookedClass = slot.is_booked ? 'booked' : '';
                            const clickHandler = !slot.is_booked ? `selectSlot(${slot.slot_id})` : '';
                            return `
                                <div class="col-4">
                                    <div class="slot-card ${bookedClass}" 
                                         onclick="${clickHandler}">
                                        <strong>${slot.start_time}</strong><br>
                                        <small>${slot.end_time}</small>
                                    </div>
                                </div>
                            `;
                        }).join('');
                    } else {
                        slotsContainer.innerHTML = '<p class="text-muted">No available slots for this date</p>';
                    }
                })
                .catch(error => {
                    console.error('Error loading slots:', error);
                    document.getElementById('timeSlots').innerHTML = '<p class="text-muted">Error loading slots. Please try again.</p>';
                });
        }
        
        function loadConfirmationDetails() {
            // Get doctor details from data attribute
            const doctorsData = JSON.parse(document.getElementById('doctorsData').dataset.doctors);
            const doctor = doctorsData.find(d => d.doctor_id == selectedDoctor);
            
            if (doctor) {
                document.getElementById('confirmDoctor').textContent = doctor.full_name;
            }
            
            const date = document.querySelector('input[name="appointment_date"]').value;
            document.getElementById('confirmDate').textContent = new Date(date).toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
            
            // Get selected slot time
            const selectedSlotCard = document.querySelector('.slot-card.selected');
            if (selectedSlotCard) {
                document.getElementById('confirmTime').textContent = selectedSlotCard.querySelector('strong').textContent;
            }
        }
        
        // Specialty filter
        const specialtyFilter = document.getElementById('specialtyFilter');
        if (specialtyFilter) {
            specialtyFilter.addEventListener('change', function() {
                const specialty = this.value;
                window.location.href = `book_appointment.py?specialty=${specialty}`;
            });
        }
        
        // Enable/disable next buttons based on selections
        if (selectedDoctor) {
            document.getElementById('step1Next').disabled = false;
        }
        if (selectedSlot) {
            document.getElementById('step2Next').disabled = false;
        }
        
        // Initial check for notification when page loads with pre-selected date/time
        document.addEventListener('DOMContentLoaded', function() {
            updateNotificationVisibility();
        });
    </script>
</body>
</html>
""")