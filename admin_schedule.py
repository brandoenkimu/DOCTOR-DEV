#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


import sys
import os
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

# Check admin session
session = AdminSession()
session.start_session()

if not session.is_logged_in():
    print("Location: admin_login.py")
    print()
    sys.exit()

admin_info = session.get_admin_info()

# Handle actions (add, edit, delete schedule)
form = cgi.FieldStorage()
action = form.getvalue('action', '')
message = ''

if action == 'add_schedule':
    doctor_id = form.getvalue('doctor_id', '')
    day = form.getvalue('day_of_week', '')
    start = form.getvalue('start_time', '')
    end = form.getvalue('end_time', '')
    max_patients = form.getvalue('max_patients', '10')
    
    if doctor_id and day and start and end:
        try:
            DatabaseOperations.execute_query(
                """INSERT INTO schedules (doctor_id, day_of_week, start_time, end_time, max_patients)
                   VALUES (%s, %s, %s, %s, %s)""",
                (doctor_id, day, start, end, int(max_patients))
            )
            message = '<div class="alert alert-success">Schedule added successfully.</div>'
        except Exception as e:
            message = f'<div class="alert alert-danger">Error adding schedule: {e}</div>'
    else:
        message = '<div class="alert alert-warning">All fields required.</div>'

elif action == 'delete_schedule':
    schedule_id = form.getvalue('schedule_id', '')
    if schedule_id:
        try:
            DatabaseOperations.execute_query(
                "DELETE FROM schedules WHERE schedule_id = %s",
                (schedule_id,)
            )
            message = '<div class="alert alert-success">Schedule deleted.</div>'
        except Exception as e:
            message = f'<div class="alert alert-danger">Error deleting schedule: {e}</div>'

# Get all doctors with their schedules
doctors = DatabaseOperations.execute_query(
    "SELECT doctor_id, full_name, specialty FROM doctors ORDER BY full_name",
    fetch_all=True
) or []

# For each doctor, fetch schedules
doctor_schedules = {}
for doctor in doctors:
    schedules = DatabaseOperations.execute_query(
        """SELECT * FROM schedules WHERE doctor_id = %s 
           ORDER BY FIELD(day_of_week, 'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'),
                    start_time""",
        (doctor['doctor_id'],),
        fetch_all=True
    ) or []
    doctor_schedules[doctor['doctor_id']] = schedules

print("Content-Type: text/html; charset=utf-8")
print()

print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manage Schedules - Clinic Management System</title>
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
        
        body {{ font-family: 'Inter', sans-serif; background: #f4f6f9; }}
        .sidebar {{ position: fixed; width: 260px; height: 100vh; background: linear-gradient(135deg, var(--dark) 0%, var(--primary) 100%); color: white; padding: 20px; }}
        .main-content {{ margin-left: 260px; padding: 20px 30px; }}
        .top-bar {{ background: white; border-radius: 15px; padding: 15px 25px; margin-bottom: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .doctor-card {{ background: white; border-radius: 15px; padding: 20px; margin-bottom: 25px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .schedule-table {{ margin-top: 15px; }}
        .btn-sm-custom {{ padding: 3px 8px; font-size: 0.8rem; }}
        .day-badge {{ background: var(--primary); color: white; padding: 5px 10px; border-radius: 20px; font-size: 0.8rem; }}
        .add-schedule-btn {{ float: right; }}
    </style>
</head>
<body>
    <!-- Sidebar -->
    <div class="sidebar">
        <div class="sidebar-logo text-center mb-4">
            <i class="fas fa-clinic-medical fa-3x"></i>
            <h3>ClinicCare</h3>
        </div>
        <ul class="list-unstyled">
            <li><a href="admin_dashboard.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-tachometer-alt me-2"></i>Dashboard</a></li>
            <li><a href="admin_doctors.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-user-md me-2"></i>Doctors</a></li>
            <li><a href="admin_patients.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-users me-2"></i>Patients</a></li>
            <li><a href="admin_appointments.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-calendar-check me-2"></i>Appointments</a></li>
            <li><a href="admin_schedule.py" class="text-white text-decoration-none d-block p-2 active"><i class="fas fa-clock me-2"></i>Schedules</a></li>
            <li><a href="admin_logout.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-sign-out-alt me-2"></i>Logout</a></li>
        </ul>
    </div>
    
    <div class="main-content">
        <div class="top-bar d-flex justify-content-between align-items-center">
            <h4 class="mb-0"><i class="fas fa-clock me-2 text-primary"></i>Manage Doctor Schedules</h4>
            <span>Welcome, {admin_info['full_name']}</span>
        </div>
        
        {message}
        
""")

if not doctors:
    print('<div class="alert alert-info">No doctors found. Please add doctors first.</div>')
else:
    for doctor in doctors:
        doc_id = doctor['doctor_id']
        schedules = doctor_schedules.get(doc_id, [])
        print(f"""
        <div class="doctor-card">
            <div class="d-flex justify-content-between align-items-center">
                <h5><i class="fas fa-user-md me-2 text-primary"></i>{doctor['full_name']} <small class="text-muted">({doctor['specialty']})</small></h5>
                <button class="btn btn-sm btn-primary" data-bs-toggle="modal" data-bs-target="#addModal{doc_id}">
                    <i class="fas fa-plus"></i> Add Schedule
                </button>
            </div>
            
            <div class="schedule-table">
                <table class="table table-sm table-hover">
                    <thead>
                        <tr>
                            <th>Day</th>
                            <th>Start</th>
                            <th>End</th>
                            <th>Max Patients</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
        """)
        if schedules:
            for s in schedules:
                print(f"""
                        <tr>
                            <td><span class="day-badge">{s['day_of_week']}</span></td>
                            <td>{s['start_time']}</td>
                            <td>{s['end_time']}</td>
                            <td>{s['max_patients']}</td>
                            <td>
                                <a href="?action=delete_schedule&schedule_id={s['schedule_id']}" 
                                   class="btn btn-sm btn-outline-danger btn-sm-custom"
                                   onclick="return confirm('Delete this schedule entry?')">
                                    <i class="fas fa-trash"></i>
                                </a>
                            </td>
                        </tr>
                """)
        else:
            print('<tr><td colspan="5" class="text-center text-muted">No schedule defined</td></tr>')
        print("""
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Modal for adding schedule to this doctor -->
        <div class="modal fade" id="addModal{}" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Add Schedule for {}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="post" action="admin_schedule.py">
                        <div class="modal-body">
                            <input type="hidden" name="action" value="add_schedule">
                            <input type="hidden" name="doctor_id" value="{}">
                            <div class="mb-3">
                                <label class="form-label">Day of Week</label>
                                <select class="form-select" name="day_of_week" required>
                                    <option value="">Select Day</option>
                                    <option value="Monday">Monday</option>
                                    <option value="Tuesday">Tuesday</option>
                                    <option value="Wednesday">Wednesday</option>
                                    <option value="Thursday">Thursday</option>
                                    <option value="Friday">Friday</option>
                                    <option value="Saturday">Saturday</option>
                                    <option value="Sunday">Sunday</option>
                                </select>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Start Time</label>
                                    <input type="time" class="form-control" name="start_time" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">End Time</label>
                                    <input type="time" class="form-control" name="end_time" required>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Max Patients per Slot</label>
                                <input type="number" class="form-control" name="max_patients" value="10" min="1">
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="submit" class="btn btn-primary">Add Schedule</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        """.format(doc_id, doctor['full_name'], doc_id))

print("""
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")