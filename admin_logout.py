#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from admin_session import AdminSession

session = AdminSession()
session.start_session()
session.logout()

print("Location: admin_login.py")
print()