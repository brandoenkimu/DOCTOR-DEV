#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


import sys
import os
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

session = AdminSession()
session.start_session()

if not session.is_logged_in():
    print("Location: admin_login.py")
    print()
    sys.exit()

admin_info = session.get_admin_info()

# Handle CRUD actions
form = cgi.FieldStorage()
action = form.getvalue('action', '')
message = ''

if action == 'add':
    name = form.getvalue('name', '').strip()
    desc = form.getvalue('description', '').strip()
    icon = form.getvalue('icon', 'fas fa-stethoscope')
    if name:
        try:
            DatabaseOperations.execute_query(
                "INSERT INTO specialties (specialty_name, description, icon_class) VALUES (%s, %s, %s)",
                (name, desc, icon)
            )
            message = '<div class="alert alert-success">Specialty added successfully!</div>'
        except Exception as e:
            message = f'<div class="alert alert-danger">Error: {e}</div>'
    else:
        message = '<div class="alert alert-warning">Name is required.</div>'

elif action == 'delete':
    sid = form.getvalue('id', '')
    if sid:
        try:
            DatabaseOperations.execute_query("DELETE FROM specialties WHERE specialty_id = %s", (sid,))
            message = '<div class="alert alert-success">Specialty deleted.</div>'
        except Exception as e:
            message = f'<div class="alert alert-danger">Error: {e}</div>'

elif action == 'edit':
    sid = form.getvalue('id', '')
    name = form.getvalue('name', '').strip()
    desc = form.getvalue('description', '').strip()
    icon = form.getvalue('icon', 'fas fa-stethoscope')
    if sid and name:
        try:
            DatabaseOperations.execute_query(
                "UPDATE specialties SET specialty_name=%s, description=%s, icon_class=%s WHERE specialty_id=%s",
                (name, desc, icon, sid)
            )
            message = '<div class="alert alert-success">Specialty updated.</div>'
        except Exception as e:
            message = f'<div class="alert alert-danger">Error: {e}</div>'

# Get all specialties
specialties = DatabaseOperations.execute_query("SELECT * FROM specialties ORDER BY specialty_name", fetch_all=True) or []

print("Content-Type: text/html; charset=utf-8")
print()

print(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manage Specialties - Clinic Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary: #2A5C82;
            --secondary: #4A90E2;
            --dark: #2C3E50;
        }}
        body {{ font-family: 'Inter', sans-serif; background: #f4f6f9; }}
        .sidebar {{ position: fixed; width: 260px; height: 100vh; background: linear-gradient(135deg, var(--dark) 0%, var(--primary) 100%); color: white; padding: 20px; }}
        .main-content {{ margin-left: 260px; padding: 20px 30px; }}
        .top-bar {{ background: white; border-radius: 15px; padding: 15px 25px; margin-bottom: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .card-custom {{ background: white; border-radius: 15px; padding: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .icon-preview {{ font-size: 1.5rem; width: 40px; text-align: center; }}
    </style>
</head>
<body>
    <div class="sidebar">
        <!-- same sidebar as before -->
        <div class="sidebar-logo text-center mb-4">
            <i class="fas fa-clinic-medical fa-3x"></i>
            <h3>ClinicCare</h3>
        </div>
        <ul class="list-unstyled">
            <li><a href="admin_dashboard.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-tachometer-alt me-2"></i>Dashboard</a></li>
            <li><a href="admin_doctors.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-user-md me-2"></i>Doctors</a></li>
            <li><a href="admin_patients.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-users me-2"></i>Patients</a></li>
            <li><a href="admin_appointments.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-calendar-check me-2"></i>Appointments</a></li>
            <li><a href="admin_specialties.py" class="text-white text-decoration-none d-block p-2 active"><i class="fas fa-stethoscope me-2"></i>Specialties</a></li>
            <li><a href="admin_reports.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-chart-bar me-2"></i>Reports</a></li>
            <li><a href="admin_settings.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-cog me-2"></i>Settings</a></li>
            <li><hr class="bg-white opacity-25"></li>
            <li><a href="admin_logout.py" class="text-white text-decoration-none d-block p-2"><i class="fas fa-sign-out-alt me-2"></i>Logout</a></li>
        </ul>
    </div>
    
    <div class="main-content">
        <div class="top-bar">
            <h4 class="mb-0"><i class="fas fa-stethoscope me-2 text-primary"></i>Manage Specialties</h4>
        </div>
        
        {message}
        
        <div class="row">
            <div class="col-md-4">
                <div class="card-custom">
                    <h5 class="mb-3"><i class="fas fa-plus-circle me-2 text-primary"></i>Add New Specialty</h5>
                    <form method="post" action="admin_specialties.py">
                        <input type="hidden" name="action" value="add">
                        <div class="mb-3">
                            <label class="form-label">Name</label>
                            <input type="text" name="name" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Description</label>
                            <textarea name="description" class="form-control" rows="2"></textarea>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Icon Class (Font Awesome)</label>
                            <input type="text" name="icon" class="form-control" value="fas fa-stethoscope">
                        </div>
                        <button type="submit" class="btn btn-primary-custom"><i class="fas fa-save me-2"></i>Add Specialty</button>
                    </form>
                </div>
            </div>
            
            <div class="col-md-8">
                <div class="card-custom">
                    <h5 class="mb-3"><i class="fas fa-list me-2 text-primary"></i>Existing Specialties</h5>
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Icon</th>
                                <th>Name</th>
                                <th>Description</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
""")

for spec in specialties:
    print(f"""
                            <tr>
                                <td class="icon-preview"><i class="{spec['icon_class']}"></i></td>
                                <td>{spec['specialty_name']}</td>
                                <td>{spec['description'] or ''}</td>
                                <td>
                                    <a href="#" class="btn btn-sm btn-outline-primary edit-btn" 
                                       data-id="{spec['specialty_id']}"
                                       data-name="{spec['specialty_name']}"
                                       data-desc="{spec['description'] or ''}"
                                       data-icon="{spec['icon_class']}">
                                        <i class="fas fa-edit"></i>
                                    </a>
                                    <a href="?action=delete&id={spec['specialty_id']}" 
                                       class="btn btn-sm btn-outline-danger" 
                                       onclick="return confirm('Delete this specialty? It may affect doctors.')">
                                        <i class="fas fa-trash"></i>
                                    </a>
                                </td>
                            </tr>
    """)

print("""
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Edit Modal -->
    <div class="modal fade" id="editModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Edit Specialty</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <form method="post" action="admin_specialties.py">
                    <div class="modal-body">
                        <input type="hidden" name="action" value="edit">
                        <input type="hidden" name="id" id="edit-id">
                        <div class="mb-3">
                            <label class="form-label">Name</label>
                            <input type="text" name="name" id="edit-name" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Description</label>
                            <textarea name="description" id="edit-desc" class="form-control" rows="2"></textarea>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Icon Class</label>
                            <input type="text" name="icon" id="edit-icon" class="form-control">
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="submit" class="btn btn-primary">Save Changes</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.querySelectorAll('.edit-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                document.getElementById('edit-id').value = this.dataset.id;
                document.getElementById('edit-name').value = this.dataset.name;
                document.getElementById('edit-desc').value = this.dataset.desc;
                document.getElementById('edit-icon').value = this.dataset.icon;
                new bootstrap.Modal(document.getElementById('editModal')).show();
            });
        });
    </script>
</body>
</html>
""")