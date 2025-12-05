-- Create database if not exists
CREATE DATABASE IF NOT EXISTS mediconnect_db;
USE mediconnect_db;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role ENUM('patient', 'doctor', 'admin') NOT NULL DEFAULT 'patient',
    date_of_birth DATE,
    phone_number VARCHAR(20),
    address TEXT,
    specialty VARCHAR(100),
    license_number VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_email (email),
    INDEX idx_role (role)
);

-- Appointments table
CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATETIME NOT NULL,
    duration_minutes INT DEFAULT 30,
    status ENUM('scheduled', 'confirmed', 'cancelled', 'completed') DEFAULT 'scheduled',
    appointment_type ENUM('consultation', 'follow_up', 'emergency') DEFAULT 'consultation',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_patient_id (patient_id),
    INDEX idx_doctor_id (doctor_id),
    INDEX idx_appointment_date (appointment_date),
    INDEX idx_status (status)
);

-- Electronic Health Records (EHR) table
CREATE TABLE IF NOT EXISTS ehr (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_id INT,
    consultation_date DATETIME NOT NULL,
    symptoms TEXT NOT NULL,
    diagnosis TEXT NOT NULL,
    treatment_plan TEXT NOT NULL,
    prescription_id INT,
    notes TEXT,
    follow_up_date DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE SET NULL,
    INDEX idx_patient_id (patient_id),
    INDEX idx_doctor_id (doctor_id),
    INDEX idx_consultation_date (consultation_date)
);

-- Prescriptions table
CREATE TABLE IF NOT EXISTS prescriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    ehr_id INT,
    medication_name VARCHAR(255) NOT NULL,
    dosage VARCHAR(100) NOT NULL,
    frequency VARCHAR(100) NOT NULL,
    duration_days INT NOT NULL,
    instructions TEXT,
    prescribed_date DATETIME NOT NULL,
    status ENUM('active', 'completed', 'cancelled') DEFAULT 'active',
    refills_remaining INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (ehr_id) REFERENCES ehr(id) ON DELETE SET NULL,
    INDEX idx_patient_id (patient_id),
    INDEX idx_doctor_id (doctor_id),
    INDEX idx_status (status)
);

-- Insert sample admin user (password: admin123)
-- Password hash for 'admin123'
INSERT INTO users (email, password_hash, first_name, last_name, role, is_active)
VALUES ('admin@mediconnect.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Admin', 'System', 'admin', TRUE);

-- Insert sample doctors
INSERT INTO users (email, password_hash, first_name, last_name, role, specialty, license_number, phone_number, is_active)
VALUES 
('doctor1@mediconnect.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'John', 'Smith', 'doctor', 'Cardiology', 'LIC12345', '+1234567890', TRUE),
('doctor2@mediconnect.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Maria', 'Garcia', 'doctor', 'Pediatrics', 'LIC67890', '+1234567891', TRUE);

-- Insert sample patients
INSERT INTO users (email, password_hash, first_name, last_name, role, date_of_birth, phone_number, address, is_active)
VALUES 
('patient1@mediconnect.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Alice', 'Johnson', 'patient', '1990-01-15', '+1234567892', '123 Main St, City', TRUE),
('patient2@mediconnect.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Bob', 'Williams', 'patient', '1985-05-20', '+1234567893', '456 Oak Ave, Town', TRUE);

-- Insert sample appointments
INSERT INTO appointments (patient_id, doctor_id, appointment_date, duration_minutes, status, appointment_type)
VALUES 
(3, 2, DATE_ADD(NOW(), INTERVAL 2 DAY), 30, 'scheduled', 'consultation'),
(4, 2, DATE_ADD(NOW(), INTERVAL 3 DAY), 45, 'confirmed', 'follow_up');

-- Insert sample EHR records
INSERT INTO ehr (patient_id, doctor_id, appointment_id, consultation_date, symptoms, diagnosis, treatment_plan)
VALUES 
(3, 2, 1, DATE_SUB(NOW(), INTERVAL 7 DAY), 'Headache, fever', 'Common cold', 'Rest, hydration, over-the-counter medication'),
(4, 2, 2, DATE_SUB(NOW(), INTERVAL 14 DAY), 'Back pain', 'Muscle strain', 'Physical therapy, pain relief medication');

-- Insert sample prescriptions
INSERT INTO prescriptions (patient_id, doctor_id, ehr_id, medication_name, dosage, frequency, duration_days, prescribed_date, status)
VALUES 
(3, 2, 1, 'Paracetamol', '500mg', 'Every 6 hours', 5, DATE_SUB(NOW(), INTERVAL 7 DAY), 'active'),
(4, 2, 2, 'Ibuprofen', '400mg', 'Every 8 hours', 7, DATE_SUB(NOW(), INTERVAL 14 DAY), 'active');
