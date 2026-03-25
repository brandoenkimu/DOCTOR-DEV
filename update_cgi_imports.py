#!C:\Program Files\Python313\python.exe
import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import re
import sys

# List of files to update
files = [
    'index.py', 'patient_register.py', 'patient_login.py', 
    'doctor_login.py', 'doctor_dashboard.py', 'book_appointment.py',
    'my_appointments.py', 'logout.py', 'session.py'
]

for filename in files:
    if not os.path.exists(filename):
        continue
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add compatibility code after shebang line
    lines = content.split('\n')
    new_lines = []
    shebang_found = False
    compatibility_added = False
    
    for line in lines:
        new_lines.append(line)
        
        # After shebang line, add compatibility code
        if not shebang_found and line.startswith('#!'):
            shebang_found = True
            new_lines.append('')
            new_lines.append('# Python 3.13 compatibility for removed cgi module')
            new_lines.append('import sys')
            new_lines.append('try:')
            new_lines.append('    import cgi')
            new_lines.append('    import cgitb')
            new_lines.append('except ImportError:')
            new_lines.append('    import legacy_cgi as cgi')
            new_lines.append('    # Simple cgitb replacement')
            new_lines.append('    class SimpleCGITB:')
            new_lines.append('        @staticmethod')
            new_lines.append('        def enable():')
            new_lines.append('            import traceback')
            new_lines.append('            def excepthook(type, value, tb):')
            new_lines.append('                import html')
            new_lines.append('                trace = "".join(traceback.format_exception(type, value, tb))')
            new_lines.append('                print("Content-Type: text/html\\n")')
            new_lines.append('                print(f"<html><body><pre>{html.escape(trace)}</pre></body></html>")')
            new_lines.append('            sys.excepthook = excepthook')
            new_lines.append('    cgitb = SimpleCGITB()')
            new_lines.append('')
            new_lines.append('cgitb.enable()')
            new_lines.append('')
            compatibility_added = True
    
    # Write the updated content
    if compatibility_added:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        print(f"✅ Updated: {filename}")
    else:
        print(f"⚠️  No shebang found in: {filename}")

print("\n🎉 All files updated! Try accessing the page again.")