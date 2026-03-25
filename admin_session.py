#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
import sys
import os
import json
import hashlib
import secrets
import time
from datetime import datetime

class AdminSession:
    def __init__(self):
        self.session_id = None
        self.data = {}
        self.session_path = 'C:/xampp/tmp/admin_sessions/'
        
        if not os.path.exists(self.session_path):
            os.makedirs(self.session_path, exist_ok=True)
    
    def start_session(self):
        cookies = self._parse_cookies()
        self.session_id = cookies.get('admin_session', self._generate_id())
        self._load()
        self._set_cookie()
    
    def _parse_cookies(self):
        cookies = {}
        if 'HTTP_COOKIE' in os.environ:
            for cookie in os.environ['HTTP_COOKIE'].split('; '):
                if '=' in cookie:
                    k, v = cookie.split('=', 1)
                    cookies[k] = v
        return cookies
    
    def _generate_id(self):
        return secrets.token_hex(32)
    
    def _load(self):
        file = os.path.join(self.session_path, f'admin_{self.session_id}')
        if os.path.exists(file):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except:
                self.data = {}
        else:
            self.data = {}
            self._save()
    
    def _save(self):
        file = os.path.join(self.session_path, f'admin_{self.session_id}')
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f)
    
    def _set_cookie(self):
        print(f'Set-Cookie: admin_session={self.session_id}; Path=/; Max-Age=7200; HttpOnly; SameSite=Strict')
    
    def login(self, admin_id, full_name, username, role):
        self.data = {
            'admin_id': admin_id,
            'full_name': full_name,
            'username': username,
            'role': role,
            'login_time': time.time(),
            'ip_address': os.environ.get('REMOTE_ADDR', ''),
            'user_agent': os.environ.get('HTTP_USER_AGENT', '')
        }
        self._save()
    
    def is_logged_in(self):
        return 'admin_id' in self.data
    
    def get_admin_info(self):
        if self.is_logged_in():
            return {
                'admin_id': self.data.get('admin_id'),
                'full_name': self.data.get('full_name'),
                'username': self.data.get('username'),
                'role': self.data.get('role')
            }
        return None
    
    def logout(self):
        file = os.path.join(self.session_path, f'admin_{self.session_id}')
        if os.path.exists(file):
            os.remove(file)
        self.data = {}
        print('Set-Cookie: admin_session=; Path=/; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT')
    
    def get(self, key, default=None):
        return self.data.get(key, default)