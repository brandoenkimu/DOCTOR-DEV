#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
"""
Configuration file for Clinic Management System
Contains database settings, session configuration, and validation rules
"""

import os
import sys
# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Harooh13317265@',
    'database': 'clinic_system',
    'charset': 'utf8mb4'
}

# Session Configuration
SESSION_CONFIG = {
    'name': 'clinic_session',
    'lifetime': 3600,  # 1 hour in seconds
    'path': '/',
    'domain': '',
    'secure': False,  # Set to True in production with HTTPS
    'httponly': True,
    'samesite': 'Lax'
}

# Clinic Hours Configuration
CLINIC_HOURS = {
    'start': '08:00',
    'end': '20:00',
    'slot_duration': 30,  # minutes
    'break_start': '13:00',
    'break_end': '14:00',
    'days_advance': 30  # How many days in advance to show slots
}

# Validation Rules
VALIDATION_RULES = {
    'patient': {
        'reg_number': {
            'pattern': r'^PAT\d{3}$',
            'min_length': 6,
            'max_length': 10,
            'required': True
        },
        'full_name': {
            'min_length': 3,
            'max_length': 100,
            'required': True
        },
        'email': {
            'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'required': True
        },
        'phone': {
            'pattern': r'^\+254\d{9}$',
            'required': True
        },
        'password': {
            'min_length': 8,
            'required': True,
            'complexity': 'At least one uppercase, one lowercase, one number'
        },
        'date_of_birth': {
            'min_age': 18,
            'max_age': 120,
            'required': True
        }
    },
    'appointment': {
        'appointment_date': {
            'min_date': 'today',
            'max_date': '+30 days',
            'required': True
        },
        'appointment_time': {
            'min_time': '08:00',
            'max_time': '20:00',
            'required': True
        }
    }
}

# File Upload Settings
UPLOAD_CONFIG = {
    'max_size': 5 * 1024 * 1024,  # 5MB
    'allowed_types': ['image/jpeg', 'image/png', 'application/pdf'],
    'upload_dir': '../htdocs/uploads/'
}

# Security Settings
SECURITY_CONFIG = {
    'password_hash_algo': 'bcrypt',
    'csrf_token_length': 32,
    'session_regenerate_id': True,
    'login_attempts': {
        'max_attempts': 5,
        'lockout_time': 900  # 15 minutes in seconds
    }
}

# Email Configuration (for notifications)
EMAIL_CONFIG = {
    'smtp_host': 'smtp.gmail.com',
    'smtp_port': 587,
    'smtp_user': 'noreply@clinic.com',
    'smtp_password': 'your_password',
    'from_email': 'appointments@clinic.com',
    'from_name': 'Clinic Management System'
}

# Logging Configuration
LOGGING_CONFIG = {
    'log_file': '../logs/clinic.log',
    'log_level': 'INFO',
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}