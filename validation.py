#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
"""
Validation module for form data and appointment rules
"""
import sys
import re
from datetime import datetime, date, timedelta
import config

class Validator:
    """Handles all validation logic"""
    
    @staticmethod
    def validate_patient_registration(data):
        """Validate patient registration form data"""
        errors = []
        rules = config.VALIDATION_RULES['patient']
        
        # Validate registration number
        if not data.get('reg_number'):
            errors.append("Registration number is required")
        elif not re.match(rules['reg_number']['pattern'], data['reg_number']):
            errors.append("Registration number must be in format PAT001")
        
        # Validate full name
        if not data.get('full_name'):
            errors.append("Full name is required")
        elif len(data['full_name']) < rules['full_name']['min_length']:
            errors.append(f"Name must be at least {rules['full_name']['min_length']} characters")
        
        # Validate email
        if not data.get('email'):
            errors.append("Email is required")
        elif not re.match(rules['email']['pattern'], data['email']):
            errors.append("Invalid email format")
        
        # Validate phone
        if not data.get('phone'):
            errors.append("Phone number is required")
        elif not re.match(rules['phone']['pattern'], data['phone']):
            errors.append("Phone must be in format +254XXXXXXXXX")
        
        # Validate password
        if not data.get('password'):
            errors.append("Password is required")
        elif len(data['password']) < rules['password']['min_length']:
            errors.append(f"Password must be at least {rules['password']['min_length']} characters")
        
        # Confirm password
        if data.get('password') != data.get('confirm_password'):
            errors.append("Passwords do not match")
        
        # Validate date of birth
        if not data.get('date_of_birth'):
            errors.append("Date of birth is required")
        else:
            try:
                dob = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
                today = date.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                
                if age < rules['date_of_birth']['min_age']:
                    errors.append(f"You must be at least {rules['date_of_birth']['min_age']} years old")
                elif age > rules['date_of_birth']['max_age']:
                    errors.append(f"Age cannot exceed {rules['date_of_birth']['max_age']} years")
            except ValueError:
                errors.append("Invalid date format")
        
        return errors
    
    @staticmethod
    def validate_appointment_booking(data):
        """Validate appointment booking data"""
        errors = []
        rules = config.VALIDATION_RULES['appointment']
        
        # Validate doctor selection
        if not data.get('doctor_id'):
            errors.append("Please select a doctor")
        
        # Validate appointment date
        if not data.get('appointment_date'):
            errors.append("Please select an appointment date")
        else:
            try:
                app_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
                today = date.today()
                max_date = today + timedelta(days=30)
                
                if app_date < today:
                    errors.append("Appointment date cannot be in the past")
                elif app_date > max_date:
                    errors.append("Appointments can only be booked up to 30 days in advance")
                elif app_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                    errors.append("Appointments are only available on weekdays")
            except ValueError:
                errors.append("Invalid date format")
        
        # Validate time slot
        if not data.get('slot_id'):
            errors.append("Please select a time slot")
        
        # Validate symptoms
        if not data.get('symptoms'):
            errors.append("Please describe your symptoms")
        elif len(data['symptoms']) < 10:
            errors.append("Please provide more detail about your symptoms (min 10 characters)")
        elif len(data['symptoms']) > 500:
            errors.append("Symptoms description too long (max 500 characters)")
        
        return errors
    
    @staticmethod
    def validate_doctor_login(data):
        """Validate doctor login data"""
        errors = []
        
        if not data.get('license_number'):
            errors.append("License number is required")
        
        if not data.get('password'):
            errors.append("Password is required")
        
        return errors
    
    @staticmethod
    def validate_patient_login(data):
        """Validate patient login data"""
        errors = []
        
        if not data.get('reg_number'):
            errors.append("Registration number is required")
        
        if not data.get('password'):
            errors.append("Password is required")
        
        return errors
    
    @staticmethod
    def validate_appointment_time(time_str, doctor_id, date_str):
        """Validate if appointment time is within clinic hours and doctor's schedule"""
        try:
            from database import DatabaseOperations
            
            app_time = datetime.strptime(time_str, '%H:%M').time()
            app_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Check clinic hours
            clinic_start = datetime.strptime(config.CLINIC_HOURS['start'], '%H:%M').time()
            clinic_end = datetime.strptime(config.CLINIC_HOURS['end'], '%H:%M').time()
            
            if not (clinic_start <= app_time <= clinic_end):
                return False, "Appointment time is outside clinic hours (08:00 - 20:00)"
            
            # Check if during break time
            break_start = datetime.strptime(config.CLINIC_HOURS['break_start'], '%H:%M').time()
            break_end = datetime.strptime(config.CLINIC_HOURS['break_end'], '%H:%M').time()
            
            if break_start <= app_time < break_end:
                return False, "Appointment time falls during lunch break (13:00 - 14:00)"
            
            # Get doctor's schedule for this day
            day_name = app_date.strftime('%A')
            schedule_query = """
                SELECT * FROM schedules 
                WHERE doctor_id = %s AND day_of_week = %s
            """
            schedules = DatabaseOperations.execute_query(
                schedule_query, (doctor_id, day_name), fetch_all=True
            )
            
            if not schedules:
                return False, "Doctor is not available on this day"
            
            # Check if time is within any schedule slot
            time_ok = False
            for schedule in schedules:
                s_start = schedule['start_time']
                s_end = schedule['end_time']
                
                if s_start <= app_time < s_end:
                    time_ok = True
                    break
            
            if not time_ok:
                return False, "Selected time is not within doctor's working hours"
            
            return True, "Time is valid"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    def sanitize_input(data):
        """Sanitize input data to prevent XSS"""
        if isinstance(data, str):
            # Remove HTML tags and escape special characters
            import html
            return html.escape(data.strip())
        elif isinstance(data, dict):
            return {key: Validator.sanitize_input(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [Validator.sanitize_input(item) for item in data]
        else:
            return data
    
    @staticmethod
    def validate_file_upload(file_data, filename):
        """Validate uploaded file"""
        errors = []
        
        # Check file size
        if len(file_data) > config.UPLOAD_CONFIG['max_size']:
            errors.append(f"File size exceeds {config.UPLOAD_CONFIG['max_size'] / (1024*1024)}MB limit")
        
        # Check file type
        import magic
        mime = magic.from_buffer(file_data, mime=True)
        if mime not in config.UPLOAD_CONFIG['allowed_types']:
            errors.append("File type not allowed")
        
        # Check filename for security
        if '..' in filename or '/' in filename or '\\' in filename:
            errors.append("Invalid filename")
        
        return errors