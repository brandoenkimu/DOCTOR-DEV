#!C:\Program Files\Python313\python.exe
# -*- coding: utf-8 -*-
"""
Database connection and operations module with MySQL connector
Uses parameterized queries to prevent SQL injection
"""

import mysql.connector
from mysql.connector import Error
import sys
import os
import logging

# Fix: Create logs directory if it doesn't exist
log_dir = 'C:/xampp/logs'
if not os.path.exists(log_dir):
    try:
        os.makedirs(log_dir)
    except:
        pass  # If we can't create logs, continue without logging

# Configure logging with error handling
try:
    logging.basicConfig(
        filename=os.path.join(log_dir, 'database.log'),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
except:
    # If logging fails, create a null handler
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
    logging.getLogger().addHandler(NullHandler())

# Add the current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config import DB_CONFIG
except ImportError:
    # Default config if config.py not found
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'Harooh13317265@',
        'database': 'clinic_system',
        'charset': 'utf8mb4'
    }

class DatabaseConnection:
    """Database connection manager with context manager support"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def __enter__(self):
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor(dictionary=True)
            return self.cursor
        except Error as e:
            logging.error(f"Database connection error: {e}")
            raise Exception(f"Database connection failed: {e}")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            if exc_type is None:
                self.connection.commit()
            else:
                self.connection.rollback()
            self.connection.close()

class DatabaseOperations:
    """Encapsulates all database operations"""
    
    @staticmethod
    def execute_query(query, params=None, fetch_one=False, fetch_all=False):
        """Execute a parameterized query safely"""
        try:
            with DatabaseConnection() as cursor:
                # If params is None, use an empty tuple
                params = params or ()
                logging.info(f"Executing query: {query} with params: {params}")
                cursor.execute(query, params)
                
                if fetch_one:
                    return cursor.fetchone()
                elif fetch_all:
                    return cursor.fetchall()
                else:
                    return cursor.lastrowid
        except Error as e:
            logging.error(f"Query execution error: {e}")
            logging.error(f"Query: {query}")
            logging.error(f"Params: {params}")
            raise Exception(f"Database error: {e} (Query: {query})")
    
    @staticmethod
    def get_patient_by_reg_number(reg_number):
        """Fetch patient by registration number"""
        query = "SELECT * FROM patients WHERE reg_number = %s"
        return DatabaseOperations.execute_query(query, (reg_number,), fetch_one=True)
    
    @staticmethod
    def get_patient_by_email(email):
        """Fetch patient by email"""
        query = "SELECT * FROM patients WHERE email = %s"
        return DatabaseOperations.execute_query(query, (email,), fetch_one=True)
    
    @staticmethod
    def create_patient(patient_data):
        """Insert a new patient record"""
        query = """
            INSERT INTO patients 
            (reg_number, full_name, email, phone, password_hash, date_of_birth, 
             address, emergency_contact, blood_group)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            patient_data['reg_number'],
            patient_data['full_name'],
            patient_data['email'],
            patient_data['phone'],
            patient_data['password_hash'],
            patient_data['date_of_birth'],
            patient_data.get('address', ''),
            patient_data.get('emergency_contact', ''),
            patient_data.get('blood_group', '')
        )
        return DatabaseOperations.execute_query(query, params)
    
    @staticmethod
    def get_doctors_by_specialty(specialty=None):
        """Fetch doctors, optionally filtered by specialty"""
        if specialty:
            query = """
                SELECT d.*, s.specialty_name, s.icon_class
                FROM doctors d
                LEFT JOIN specialties s ON d.specialty = s.specialty_name
                WHERE d.specialty = %s AND d.is_active = 1
                ORDER BY d.full_name
            """
            return DatabaseOperations.execute_query(query, (specialty,), fetch_all=True)
        else:
            query = """
                SELECT d.*, s.specialty_name, s.icon_class
                FROM doctors d
                LEFT JOIN specialties s ON d.specialty = s.specialty_name
                WHERE d.is_active = 1
                ORDER BY s.specialty_name, d.full_name
            """
            return DatabaseOperations.execute_query(query, fetch_all=True)
    
    @staticmethod
    def get_doctor_by_id(doctor_id):
        """Fetch doctor by ID"""
        query = """
            SELECT d.*, s.specialty_name, s.icon_class
            FROM doctors d
            LEFT JOIN specialties s ON d.specialty = s.specialty_name
            WHERE d.doctor_id = %s
        """
        return DatabaseOperations.execute_query(query, (doctor_id,), fetch_one=True)
    
    @staticmethod
    def get_all_specialties():
        """Get all medical specialties"""
        query = "SELECT * FROM specialties ORDER BY specialty_name"
        return DatabaseOperations.execute_query(query, fetch_all=True)
    
    @staticmethod
    def get_available_slots(doctor_id, date):
        """Get available time slots for a specific doctor and date"""
        query = """
            SELECT ts.*, 
                   CASE WHEN ts.is_booked THEN 'Booked' ELSE 'Available' END as status
            FROM time_slots ts
            WHERE ts.doctor_id = %s 
              AND ts.slot_date = %s
              AND ts.is_booked = FALSE
            ORDER BY ts.start_time
        """
        return DatabaseOperations.execute_query(query, (doctor_id, date), fetch_all=True)
    
    @staticmethod
    def generate_time_slots(doctor_id, date):
        """Generate time slots for a doctor on a specific date"""
        # First, check if slots already exist
        check_query = """
            SELECT COUNT(*) as count FROM time_slots 
            WHERE doctor_id = %s AND slot_date = %s
        """
        result = DatabaseOperations.execute_query(check_query, (doctor_id, date), fetch_one=True)
        
        if result and result['count'] == 0:
            # Get doctor's schedule for this day
            from datetime import datetime
            day_name = datetime.strptime(date, '%Y-%m-%d').strftime('%A')
            
            schedule_query = """
                SELECT * FROM schedules 
                WHERE doctor_id = %s AND day_of_week = %s
            """
            schedules = DatabaseOperations.execute_query(
                schedule_query, (doctor_id, day_name), fetch_all=True
            )
            
            if schedules:
                from datetime import datetime, timedelta
                
                slot_duration = 30  # minutes
                
                for schedule in schedules:
                    start_time = datetime.strptime(str(schedule['start_time']), '%H:%M:%S')
                    end_time = datetime.strptime(str(schedule['end_time']), '%H:%M:%S')
                    
                    current = start_time
                    while current < end_time:
                        slot_end = current + timedelta(minutes=slot_duration)
                        
                        # Skip break time (13:00-14:00)
                        break_start = datetime.strptime('13:00', '%H:%M').time()
                        break_end = datetime.strptime('14:00', '%H:%M').time()
                        
                        if not (break_start <= current.time() < break_end):
                            insert_query = """
                                INSERT INTO time_slots 
                                (doctor_id, slot_date, start_time, end_time)
                                VALUES (%s, %s, %s, %s)
                            """
                            try:
                                DatabaseOperations.execute_query(
                                    insert_query,
                                    (doctor_id, date, current.time().strftime('%H:%M:%S'), 
                                     slot_end.time().strftime('%H:%M:%S'))
                                )
                            except:
                                pass  # Skip if slot already exists
                        
                        current = slot_end
        
        return DatabaseOperations.get_available_slots(doctor_id, date)
    
    @staticmethod
    def book_appointment(patient_id, doctor_id, slot_id, symptoms):
        """Book an appointment"""
        try:
            with DatabaseConnection() as cursor:
                # Get slot details
                cursor.execute(
                    "SELECT * FROM time_slots WHERE slot_id = %s AND is_booked = FALSE",
                    (slot_id,)
                )
                slot = cursor.fetchone()
                
                if not slot:
                    raise Exception("Slot not available")
                
                # Create appointment
                appointment_query = """
                    INSERT INTO appointments 
                    (patient_id, doctor_id, appointment_date, appointment_time, 
                     end_time, symptoms, status)
                    VALUES (%s, %s, %s, %s, %s, %s, 'Scheduled')
                """
                cursor.execute(
                    appointment_query,
                    (patient_id, doctor_id, slot['slot_date'], 
                     slot['start_time'], slot['end_time'], symptoms)
                )
                appointment_id = cursor.lastrowid
                
                # Mark slot as booked
                cursor.execute(
                    "UPDATE time_slots SET is_booked = TRUE, booked_by = %s WHERE slot_id = %s",
                    (patient_id, slot_id)
                )
                
                return appointment_id
        except Error as e:
            logging.error(f"Booking error: {e}")
            raise
    
    @staticmethod
    def reschedule_appointment(old_appointment_id, patient_id, doctor_id, new_slot_id, new_symptoms):
        """Reschedule an existing appointment to a new time slot."""
        try:
            with DatabaseConnection() as cursor:
                # Start transaction
                # 1. Get the old appointment details
                cursor.execute(
                    "SELECT * FROM appointments WHERE appointment_id = %s AND patient_id = %s",
                    (old_appointment_id, patient_id)
                )
                old_appt = cursor.fetchone()
                if not old_appt:
                    raise Exception("Appointment not found or access denied")
                
                # 2. Get the new slot details and verify it's available
                cursor.execute(
                    "SELECT * FROM time_slots WHERE slot_id = %s AND is_booked = FALSE",
                    (new_slot_id,)
                )
                new_slot = cursor.fetchone()
                if not new_slot:
                    raise Exception("Selected time slot is no longer available")
                
                # 3. Free the old time slot (if it exists)
                cursor.execute(
                    "UPDATE time_slots SET is_booked = FALSE, booked_by = NULL WHERE doctor_id = %s AND slot_date = %s AND start_time = %s",
                    (old_appt['doctor_id'], old_appt['appointment_date'], old_appt['appointment_time'])
                )
                
                # 4. Update the appointment with new details
                cursor.execute(
                    """UPDATE appointments 
                    SET appointment_date = %s, appointment_time = %s, end_time = %s,
                        symptoms = %s, status = 'Scheduled', updated_at = NOW()
                    WHERE appointment_id = %s""",
                    (new_slot['slot_date'], new_slot['start_time'], new_slot['end_time'],
                    new_symptoms, old_appointment_id)
                )
                
                # 5. Mark the new slot as booked
                cursor.execute(
                    "UPDATE time_slots SET is_booked = TRUE, booked_by = %s WHERE slot_id = %s",
                    (patient_id, new_slot_id)
                )
                
                return old_appointment_id
        except Exception as e:
            logging.error(f"Reschedule error: {e}")
            raise
    
    @staticmethod
    def get_patient_appointments(patient_id):
        """Get all appointments for a patient"""
        query = """
            SELECT a.*, d.full_name as doctor_name, d.specialty,
                   TIME_FORMAT(a.appointment_time, '%h:%i %p') as time_formatted,
                   DATE_FORMAT(a.appointment_date, '%W, %M %d, %Y') as date_formatted
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.patient_id = %s
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """
        return DatabaseOperations.execute_query(query, (patient_id,), fetch_all=True)
    
    @staticmethod
    def get_doctor_appointments(doctor_id, date=None):
        """Get upcoming appointments for a doctor, optionally filtered by date"""
        if date:
            query = """
                SELECT a.*, p.full_name as patient_name, p.phone,
                       TIME_FORMAT(a.appointment_time, '%h:%i %p') as time_formatted
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                WHERE a.doctor_id = %s AND a.appointment_date = %s
                ORDER BY a.appointment_time
            """
            return DatabaseOperations.execute_query(
                query, (doctor_id, date), fetch_all=True
            )
        else:
            query = """
                SELECT a.*, p.full_name as patient_name, p.phone,
                       DATE_FORMAT(a.appointment_date, '%Y-%m-%d') as date_formatted,
                       TIME_FORMAT(a.appointment_time, '%h:%i %p') as time_formatted
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                WHERE a.doctor_id = %s AND a.appointment_date >= CURDATE()
                ORDER BY a.appointment_date, a.appointment_time
            """
            return DatabaseOperations.execute_query(query, (doctor_id,), fetch_all=True)

    # New method: Get ALL appointments for a doctor (past and future)
    @staticmethod
    def get_doctor_all_appointments(doctor_id):
        """
        Retrieve all appointments for a doctor, including past and future,
        with patient details. Returns a list of dictionaries.
        """
        query = """
            SELECT a.*, p.full_name as patient_name, p.phone
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            WHERE a.doctor_id = %s
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """
        return DatabaseOperations.execute_query(query, (doctor_id,), fetch_all=True)

    # New method: Update appointment status
    @staticmethod
    def update_appointment_status(appointment_id, new_status):
        """
        Update the status of an appointment.
        :param appointment_id: ID of the appointment
        :param new_status: one of 'Scheduled', 'Completed', 'Cancelled', 'Rescheduled', 'No-Show'
        """
        query = """
            UPDATE appointments
            SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE appointment_id = %s
        """
        DatabaseOperations.execute_query(query, (new_status, appointment_id))
        return True
    
    @staticmethod
    def cancel_appointment(appointment_id, patient_id):
        """Cancel an appointment"""
        try:
            with DatabaseConnection() as cursor:
                # Get appointment details
                cursor.execute(
                    "SELECT * FROM appointments WHERE appointment_id = %s AND patient_id = %s",
                    (appointment_id, patient_id)
                )
                appointment = cursor.fetchone()
                
                if not appointment:
                    raise Exception("Appointment not found")
                
                # Update appointment status
                cursor.execute(
                    "UPDATE appointments SET status = 'Cancelled' WHERE appointment_id = %s",
                    (appointment_id,)
                )
                
                # Free up the time slot
                cursor.execute(
                    """UPDATE time_slots SET is_booked = FALSE, booked_by = NULL 
                       WHERE doctor_id = %s AND slot_date = %s AND start_time = %s""",
                    (appointment['doctor_id'], appointment['appointment_date'], 
                     appointment['appointment_time'])
                )
                
                return True
        except Error as e:
            logging.error(f"Cancellation error: {e}")
            raise