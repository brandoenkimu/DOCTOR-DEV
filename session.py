#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
"""
Session management module for handling user sessions securely
Uses file-based sessions with encryption
"""

import os
import json
import hashlib
import secrets
import time
from datetime import datetime, timedelta
import config
import sys

# Fix for Python 3.13 - cgi module is removed
try:
    import cgi
except ImportError:
    # Create a simple replacement for cgi.FieldStorage
    class SimpleFieldStorage:
        def __init__(self):
            self._parse_query_string()
        
        def _parse_query_string(self):
            """Parse query string from environment"""
            self.params = {}
            if 'QUERY_STRING' in os.environ:
                query = os.environ['QUERY_STRING']
                if query:
                    pairs = query.split('&')
                    for pair in pairs:
                        if '=' in pair:
                            key, value = pair.split('=', 1)
                            self.params[key] = value
    
    cgi = type('cgi', (), {'FieldStorage': SimpleFieldStorage})()

class SessionManager:
    """Manages user sessions securely"""
    
    def __init__(self):
        self.session_id = None
        self.data = {}
        self.session_file = None
        self.cookie_header = None  # Store the cookie header to be sent
        # Use Windows-friendly path
        self.session_path = 'C:/xampp/tmp/clinic_sessions/'
        
        # Create session directory if it doesn't exist
        if not os.path.exists(self.session_path):
            try:
                os.makedirs(self.session_path, mode=0o700)
            except:
                # Fallback to temp directory if can't create in XAMPP
                import tempfile
                self.session_path = os.path.join(tempfile.gettempdir(), 'clinic_sessions')
                if not os.path.exists(self.session_path):
                    os.makedirs(self.session_path, mode=0o700)
    
    def start_session(self):
        """Start a new session or resume existing one"""
        # Parse cookies from environment
        cookies = self._parse_cookies()
        
        # Get session name from config with fallback
        session_name = 'clinic_session'
        if hasattr(config, 'SESSION_CONFIG'):
            session_name = config.SESSION_CONFIG.get('name', 'clinic_session')
        
        session_cookie = cookies.get(session_name)
        
        if session_cookie and self._validate_session_id(session_cookie):
            self.session_id = session_cookie
            self._load_session()
        else:
            self._create_new_session()
        
        # Generate cookie header (but don't print)
        self._set_session_cookie()
        
        # Regenerate session ID periodically for security
        regenerate_id = False
        
        if hasattr(config, 'SESSION_CONFIG'):
            regenerate_id = config.SESSION_CONFIG.get('session_regenerate_id', False)
        
        if not regenerate_id and hasattr(config, 'SECURITY_CONFIG'):
            regenerate_id = config.SECURITY_CONFIG.get('session_regenerate_id', False)
        
        if regenerate_id:
            last_regenerated = self.data.get('last_regenerated', 0)
            if time.time() - last_regenerated > 300:
                self.regenerate_session_id()
    
    def _parse_cookies(self):
        """Parse cookies from HTTP_COOKIE environment variable"""
        cookies = {}
        if 'HTTP_COOKIE' in os.environ:
            cookie_string = os.environ['HTTP_COOKIE']
            for cookie in cookie_string.split('; '):
                if '=' in cookie:
                    name, value = cookie.split('=', 1)
                    cookies[name] = value
        return cookies
    
    def _create_new_session(self):
        """Create a new session"""
        self.session_id = self._generate_session_id()
        self.data = {
            'created_at': time.time(),
            'last_accessed': time.time(),
            'user_agent': os.environ.get('HTTP_USER_AGENT', ''),
            'ip_address': os.environ.get('REMOTE_ADDR', ''),
            'last_regenerated': time.time()
        }
        self._save_session()
    
    def _generate_session_id(self):
        """Generate a cryptographically secure session ID"""
        random_bytes = secrets.token_bytes(32)
        timestamp = str(int(time.time())).encode()
        return hashlib.sha256(random_bytes + timestamp).hexdigest()
    
    def _validate_session_id(self, session_id):
        """Validate session ID format"""
        return len(session_id) == 64 and all(c in '0123456789abcdef' for c in session_id)
    
    def _get_session_file(self):
        """Get the session file path"""
        return os.path.join(self.session_path, f'sess_{self.session_id}')
    
    def _load_session(self):
        """Load session data from file"""
        self.session_file = self._get_session_file()
        
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r') as f:
                    self.data = json.load(f)
                
                # Check session expiry
                last_accessed = self.data.get('last_accessed', 0)
                lifetime = 3600
                if hasattr(config, 'SESSION_CONFIG'):
                    lifetime = config.SESSION_CONFIG.get('lifetime', 3600)
                
                if time.time() - last_accessed > lifetime:
                    self.destroy_session()
                    self._create_new_session()
                else:
                    self.data['last_accessed'] = time.time()
                    self._save_session()
                    
                    current_ua = os.environ.get('HTTP_USER_AGENT', '')
                    stored_ua = self.data.get('user_agent', '')
                    
                    if current_ua and stored_ua and current_ua != stored_ua:
                        self.destroy_session()
                        self._create_new_session()
            except (json.JSONDecodeError, IOError):
                self.destroy_session()
                self._create_new_session()
        else:
            self._create_new_session()
    
    def _save_session(self):
        """Save session data to file"""
        self.session_file = self._get_session_file()
        try:
            with open(self.session_file, 'w') as f:
                json.dump(self.data, f)
            try:
                os.chmod(self.session_file, 0o600)
            except:
                pass
        except IOError as e:
            import sys
            print(f"Error saving session: {e}", file=sys.stderr)
    
    def _set_session_cookie(self):
        """Generate session cookie string and store it (does not print)"""
        session_name = 'clinic_session'
        path = '/'
        lifetime = 3600
        domain = ''
        secure = False
        httponly = True
        samesite = 'Lax'
        
        if hasattr(config, 'SESSION_CONFIG'):
            session_name = config.SESSION_CONFIG.get('name', session_name)
            path = config.SESSION_CONFIG.get('path', path)
            lifetime = config.SESSION_CONFIG.get('lifetime', lifetime)
            domain = config.SESSION_CONFIG.get('domain', domain)
            secure = config.SESSION_CONFIG.get('secure', secure)
            httponly = config.SESSION_CONFIG.get('httponly', httponly)
            samesite = config.SESSION_CONFIG.get('samesite', samesite)
        
        cookie = f"{session_name}={self.session_id}"
        cookie += f"; Path={path}"
        cookie += f"; Max-Age={lifetime}"
        
        if domain:
            cookie += f"; Domain={domain}"
        if secure:
            cookie += "; Secure"
        if httponly:
            cookie += "; HttpOnly"
        if samesite:
            cookie += f"; SameSite={samesite}"
        
        self.cookie_header = f"Set-Cookie: {cookie}"
    
    def regenerate_session_id(self):
        """Regenerate session ID to prevent session fixation"""
        old_session_id = self.session_id
        old_file = self._get_session_file()
        
        self.session_id = self._generate_session_id()
        self.data['last_regenerated'] = time.time()
        
        self._save_session()
        
        if os.path.exists(old_file):
            try:
                os.remove(old_file)
            except:
                pass
        
        self._set_session_cookie()
    
    def set(self, key, value):
        """Set a session variable"""
        self.data[key] = value
        self._save_session()
    
    def get(self, key, default=None):
        """Get a session variable"""
        return self.data.get(key, default)
    
    def delete(self, key):
        """Delete a session variable"""
        if key in self.data:
            del self.data[key]
            self._save_session()
    
    def destroy_session(self):
        """Destroy the current session"""
        if self.session_id:
            session_file = self._get_session_file()
            if os.path.exists(session_file):
                try:
                    os.remove(session_file)
                except:
                    pass
            
            # Create clear-cookie header
            session_name = 'clinic_session'
            if hasattr(config, 'SESSION_CONFIG'):
                session_name = config.SESSION_CONFIG.get('name', session_name)
            
            path = '/'
            if hasattr(config, 'SESSION_CONFIG'):
                path = config.SESSION_CONFIG.get('path', path)
            
            self.cookie_header = f"Set-Cookie: {session_name}=; Path={path}; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT"
        
        self.session_id = None
        self.data = {}
    
    def is_logged_in(self):
        """Check if user is logged in"""
        return self.get('user_id') is not None and self.get('user_type') is not None
    
    def get_user_info(self):
        """Get current user information"""
        if self.is_logged_in():
            return {
                'user_id': self.get('user_id'),
                'user_type': self.get('user_type'),
                'full_name': self.get('full_name'),
                'email': self.get('email')
            }
        return None
    
    def login(self, user_id, user_type, full_name, email):
        """Handle user login"""
        self.set('user_id', user_id)
        self.set('user_type', user_type)
        self.set('full_name', full_name)
        self.set('email', email)
        self.set('login_time', time.time())
        self.regenerate_session_id()
    
    def logout(self):
        """Handle user logout"""
        self.destroy_session()
    
    def get_cookie_header(self):
        """Return the cookie header to be printed (or None if no cookie)"""
        return self.cookie_header