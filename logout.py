#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from session import SessionManager

headers = []
session = SessionManager()
session.start_session()
session.logout()

cookie_header = session.get_cookie_header()
if cookie_header:
    headers.append(cookie_header)

headers.append("Location: patient_login.py")

for h in headers:
    print(h)
print()