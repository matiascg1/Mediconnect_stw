from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

@dataclass
class User:
    id: Optional[int] = None
    email: str = ""
    password_hash: str = ""
    first_name: str = ""
    last_name: str = ""
    role: str = ""  # 'patient', 'doctor', 'admin'
    date_of_birth: Optional[datetime] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    specialty: Optional[str] = None  # For doctors
    license_number: Optional[str] = None  # For doctors
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True
    
    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "phone_number": self.phone_number,
            "address": self.address,
            "specialty": self.specialty,
            "license_number": self.license_number,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active
        }

@dataclass
class Appointment:
    id: Optional[int] = None
    patient_id: int = 0
    doctor_id: int = 0
    appointment_date: datetime = None
    duration_minutes: int = 30
    status: str = "scheduled"  # scheduled, confirmed, cancelled, completed
    appointment_type: str = "consultation"  # consultation, follow_up, emergency
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "appointment_date": self.appointment_date.isoformat() if self.appointment_date else None,
            "duration_minutes": self.duration_minutes,
            "status": self.status,
            "appointment_type": self.appointment_type,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

@dataclass
class EHR:
    id: Optional[int] = None
    patient_id: int = 0
    doctor_id: int = 0
    appointment_id: Optional[int] = None
    consultation_date: datetime = None
    symptoms: str = ""
    diagnosis: str = ""
    treatment_plan: str = ""
    prescription_id: Optional[int] = None
    notes: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "appointment_id": self.appointment_id,
            "consultation_date": self.consultation_date.isoformat() if self.consultation_date else None,
            "symptoms": self.symptoms,
            "diagnosis": self.diagnosis,
            "treatment_plan": self.treatment_plan,
            "prescription_id": self.prescription_id,
            "notes": self.notes,
            "follow_up_date": self.follow_up_date.isoformat() if self.follow_up_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

@dataclass
class Prescription:
    id: Optional[int] = None
    patient_id: int = 0
    doctor_id: int = 0
    ehr_id: Optional[int] = None
    medication_name: str = ""
    dosage: str = ""
    frequency: str = ""
    duration_days: int = 0
    instructions: Optional[str] = None
    prescribed_date: datetime = None
    status: str = "active"  # active, completed, cancelled
    refills_remaining: int = 0
    created_at: Optional[datetime] = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "ehr_id": self.ehr_id,
            "medication_name": self.medication_name,
            "dosage": self.dosage,
            "frequency": self.frequency,
            "duration_days": self.duration_days,
            "instructions": self.instructions,
            "prescribed_date": self.prescribed_date.isoformat() if self.prescribed_date else None,
            "status": self.status,
            "refills_remaining": self.refills_remaining,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
