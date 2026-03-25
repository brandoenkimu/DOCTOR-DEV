-- Drop database if exists and recreate
DROP DATABASE IF EXISTS clinic_system;
CREATE DATABASE clinic_system;
USE clinic_system;

-- Table: patients
CREATE TABLE patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    reg_number VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    date_of_birth DATE NOT NULL,
    address TEXT,
    emergency_contact VARCHAR(15),
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_reg_number (reg_number),
    INDEX idx_email (email)
);

-- Table: doctors (with admin tracking columns)
CREATE TABLE doctors (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    license_number VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    specialty VARCHAR(100) NOT NULL,
    qualification TEXT,
    experience_years INT,
    consultation_fee DECIMAL(10,2),
    created_by INT NULL,               -- ID of admin who created this doctor
    updated_at TIMESTAMP NULL,          -- Last update timestamp
    profile_image VARCHAR(255) NULL,    -- Profile image path
    available_from TIME DEFAULT '09:00:00',
    available_to TIME DEFAULT '17:00:00',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_specialty (specialty),
    INDEX idx_email (email)
    -- Foreign key to admins will be added after admins table is created
);

-- Table: specialties
CREATE TABLE specialties (
    specialty_id INT AUTO_INCREMENT PRIMARY KEY,
    specialty_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon_class VARCHAR(50)
);

-- Table: schedules
CREATE TABLE schedules (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_id INT NOT NULL,
    day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    max_patients INT DEFAULT 10,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE,
    INDEX idx_doctor_day (doctor_id, day_of_week)
);

-- Table: appointments
CREATE TABLE appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    end_time TIME NOT NULL,
    status ENUM('Scheduled', 'Completed', 'Cancelled', 'Rescheduled', 'No-Show') DEFAULT 'Scheduled',
    symptoms TEXT,
    diagnosis TEXT,
    prescription TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE,
    UNIQUE KEY unique_appointment (doctor_id, appointment_date, appointment_time),
    INDEX idx_patient_date (patient_id, appointment_date),
    INDEX idx_doctor_date (doctor_id, appointment_date),
    INDEX idx_status (status),
    INDEX idx_date (appointment_date)
);

-- Table: time_slots
CREATE TABLE time_slots (
    slot_id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_id INT NOT NULL,
    slot_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_booked BOOLEAN DEFAULT FALSE,
    booked_by INT NULL,
    booking_time TIMESTAMP NULL,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE,
    FOREIGN KEY (booked_by) REFERENCES patients(patient_id) ON DELETE SET NULL,
    UNIQUE KEY unique_slot (doctor_id, slot_date, start_time),
    INDEX idx_available (doctor_id, slot_date, is_booked)
);

-- Admin table for system administrators
CREATE TABLE admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('super_admin', 'admin') DEFAULT 'admin',
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add foreign key to doctors table (created_by references admins)
ALTER TABLE doctors ADD FOREIGN KEY (created_by) REFERENCES admins(admin_id) ON DELETE SET NULL;

-- Insert default admin (password: Admin@123)
INSERT INTO admins (username, full_name, email, password_hash) VALUES 
('admin', 'System Administrator', 'admin@clinic.com', '$2b$12$ykrEm5qonsSpcQGrfE0MSuv5Mv6uEdNzo.usVxlNoUicAP8NKk0iq');

-- Insert specialties
INSERT INTO specialties (specialty_name, description, icon_class) VALUES
('Cardiology', 'Heart and cardiovascular system specialists', 'fas fa-heart'),
('Dermatology', 'Skin, hair, and nail specialists', 'fas fa-allergies'),
('Pediatrics', 'Child healthcare specialists', 'fas fa-child'),
('Orthopedics', 'Bone and joint specialists', 'fas fa-bone'),
('Neurology', 'Brain and nervous system specialists', 'fas fa-brain'),
('Ophthalmology', 'Eye care specialists', 'fas fa-eye'),
('Gynecology', 'Women\'s health specialists', 'fas fa-female'),
('Dentistry', 'Dental and oral health specialists', 'fas fa-tooth');

-- Insert sample doctors (created_by will be NULL initially)
INSERT INTO doctors (license_number, full_name, email, phone, password_hash, specialty, qualification, experience_years, consultation_fee, available_from, available_to) VALUES
('LIC001', 'Dr. Sarah Johnson', 'sarah.johnson@clinic.com', '+254712345678', '$2y$10$YourHashedPasswordHere', 'Cardiology', 'MD, FACC', 15, 2500.00, '09:00', '17:00'),
('LIC002', 'Dr. Michael Omondi', 'michael.omondi@clinic.com', '+254723456789', '$2y$10$YourHashedPasswordHere', 'Dermatology', 'MD, DVD', 8, 2000.00, '10:00', '18:00'),
('LIC003', 'Dr. Grace Wambui', 'grace.wambui@clinic.com', '+254734567890', '$2y$10$YourHashedPasswordHere', 'Pediatrics', 'MD, FAAP', 12, 2200.00, '08:00', '16:00'),
('LIC004', 'Dr. James Kariuki', 'james.kariuki@clinic.com', '+254745678901', '$2y$10$YourHashedPasswordHere', 'Orthopedics', 'MS Ortho', 10, 2300.00, '09:00', '17:00'),
('LIC005', 'Dr. Elizabeth Akinyi', 'elizabeth.akinyi@clinic.com', '+254756789012', '$2y$10$YourHashedPasswordHere', 'Neurology', 'MD, DM', 14, 2800.00, '09:00', '17:00');

-- Insert sample patients
INSERT INTO patients (reg_number, full_name, email, phone, password_hash, date_of_birth, address, emergency_contact, blood_group) VALUES
('PAT001', 'John Mwangi', 'john.mwangi@email.com', '+254701234567', '$2y$10$YourHashedPasswordHere', '1990-05-15', '123 Kenyatta Ave, Nairobi', '+254711223344', 'O+'),
('PAT002', 'Mary Akinyi', 'mary.akinyi@email.com', '+254712345678', '$2y$10$YourHashedPasswordHere', '1985-08-22', '456 Moi Road, Kisumu', '+254722334455', 'A+'),
('PAT003', 'Peter Kimani', 'peter.kimani@email.com', '+254723456789', '$2y$10$YourHashedPasswordHere', '1978-03-10', '789 Uhuru St, Mombasa', '+254733445566', 'B+'),
('PAT004', 'Jane Wanjiku', 'jane.wanjiku@email.com', '+254734567890', '$2y$10$YourHashedPasswordHere', '1995-11-30', '321 Kencom House, Nairobi', '+254744556677', 'AB+'),
('PAT005', 'David Otieno', 'david.otieno@email.com', '+254745678901', '$2y$10$YourHashedPasswordHere', '1982-07-18', '654 Oginga Rd, Kisumu', '+254755667788', 'O-');

-- Insert schedules
INSERT INTO schedules (doctor_id, day_of_week, start_time, end_time, max_patients) VALUES
(1, 'Monday', '09:00', '13:00', 8),
(1, 'Monday', '14:00', '17:00', 8),
(1, 'Wednesday', '09:00', '13:00', 8),
(1, 'Friday', '09:00', '13:00', 8),
(2, 'Tuesday', '10:00', '14:00', 6),
(2, 'Thursday', '14:00', '18:00', 6),
(3, 'Monday', '08:00', '12:00', 10),
(3, 'Wednesday', '08:00', '12:00', 10),
(3, 'Friday', '08:00', '12:00', 10),
(4, 'Tuesday', '09:00', '13:00', 8),
(4, 'Thursday', '09:00', '13:00', 8),
(5, 'Monday', '09:00', '13:00', 6),
(5, 'Wednesday', '14:00', '17:00', 6);

COMMIT;

-- Verify data
SELECT 'Doctors' as 'Table', COUNT(*) as 'Count' FROM doctors
UNION ALL
SELECT 'Patients', COUNT(*) FROM patients
UNION ALL
SELECT 'Schedules', COUNT(*) FROM schedules
UNION ALL
SELECT 'Specialties', COUNT(*) FROM specialties
UNION ALL
SELECT 'Admins', COUNT(*) FROM admins;