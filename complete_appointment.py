#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Complete Appointment Module – sets appointment status to Completed
"""

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
            def excepthook(typ, val, tb):
                import html
                trace = ''.join(traceback.format_exception(typ, val, tb))
                trace = trace.encode('ascii', 'replace').decode('ascii')
                print("Status: 500 Internal Server Error")
                print("Content-Type: text/html\n")
                print(f"<html><body><pre>{html.escape(trace)}</pre></body></html>")
            sys.excepthook = excepthook
    cgitb = SimpleCGITB()

cgitb.enable()

from session import SessionManager
from database import DatabaseOperations

headers = []
session = SessionManager()
session.start_session()
cookie = session.get_cookie_header()
if cookie: headers.append(cookie)

if not session.is_logged_in() or session.get('user_type') != 'doctor':
    headers.append("Location: doctor_login.py")
    for h in headers: print(h); print()
    sys.exit()

doctor_info = session.get_user_info()
doctor_id = doctor_info['user_id']

form = cgi.FieldStorage()
apt_id = form.getvalue('id', '')
if not apt_id:
    headers.append("Location: doctor_dashboard.py")
    for h in headers: print(h); print()
    sys.exit()

# Verify appointment belongs to this doctor
apt = DatabaseOperations.execute_query(
    "SELECT appointment_id FROM appointments WHERE appointment_id = %s AND doctor_id = %s",
    (apt_id, doctor_id),
    fetch_one=True
)
if apt:
    DatabaseOperations.execute_query(
        "UPDATE appointments SET status = 'Completed' WHERE appointment_id = %s",
        (apt_id,)
    )

# Redirect back to referring page (or dashboard)
referer = os.environ.get('HTTP_REFERER', 'doctor_dashboard.py')
headers.append(f"Location: {referer}")
for h in headers:
    print(h)
print()