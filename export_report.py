#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Export Report Module – generates CSV of doctor's appointments
"""

import sys
import os
import csv
from io import StringIO
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

# Header collection
headers = []
session = SessionManager()
session.start_session()
cookie = session.get_cookie_header()
if cookie:
    headers.append(cookie)

# Check login
if not session.is_logged_in() or session.get('user_type') != 'doctor':
    headers.append("Location: doctor_login.py")
    for h in headers: print(h)
    print()
    sys.exit()

doctor_info = session.get_user_info()
doctor_id = doctor_info['user_id']

# Optional: get date range from query string
form = cgi.FieldStorage()
start_date = form.getvalue('start', '')
end_date = form.getvalue('end', '')

# Build query
query = """
    SELECT a.appointment_id, a.appointment_date, a.appointment_time, a.end_time,
           a.status, a.symptoms, a.diagnosis, a.prescription, a.notes,
           p.full_name AS patient_name, p.reg_number, p.phone, p.email
    FROM appointments a
    JOIN patients p ON a.patient_id = p.patient_id
    WHERE a.doctor_id = %s
"""
params = [doctor_id]
if start_date:
    query += " AND a.appointment_date >= %s"
    params.append(start_date)
if end_date:
    query += " AND a.appointment_date <= %s"
    params.append(end_date)
query += " ORDER BY a.appointment_date DESC, a.appointment_time DESC"

appointments = DatabaseOperations.execute_query(query, tuple(params), fetch_all=True) or []

# Generate CSV
output = StringIO()
writer = csv.writer(output)
writer.writerow(['ID', 'Date', 'Time', 'End Time', 'Patient', 'Reg No', 'Phone', 'Email',
                 'Status', 'Symptoms', 'Diagnosis', 'Prescription', 'Notes'])
for apt in appointments:
    writer.writerow([
        apt['appointment_id'],
        apt['appointment_date'],
        apt['appointment_time'],
        apt['end_time'],
        apt['patient_name'],
        apt['reg_number'],
        apt['phone'],
        apt['email'],
        apt['status'],
        apt['symptoms'] or '',
        apt['diagnosis'] or '',
        apt['prescription'] or '',
        apt['notes'] or ''
    ])

csv_data = output.getvalue()

# Set headers for CSV download
headers.append("Content-Type: text/csv")
headers.append("Content-Disposition: attachment; filename=appointments_report.csv")
headers.append(f"Content-Length: {len(csv_data)}")
for h in headers:
    print(h)
print()
print(csv_data, end='')