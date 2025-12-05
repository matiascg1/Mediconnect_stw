export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const ROLES = {
  PATIENT: 'patient',
  DOCTOR: 'doctor',
  ADMIN: 'admin'
} as const;

export const APPOINTMENT_STATUS = {
  SCHEDULED: 'scheduled',
  CONFIRMED: 'confirmed',
  CANCELLED: 'cancelled',
  COMPLETED: 'completed'
} as const;

export const APPOINTMENT_TYPES = {
  CONSULTATION: 'consultation',
  FOLLOW_UP: 'follow_up',
  EMERGENCY: 'emergency'
} as const;

export const PRESCRIPTION_STATUS = {
  ACTIVE: 'active',
  COMPLETED: 'completed',
  CANCELLED: 'cancelled'
} as const;

export const SPECIALTIES = [
  'Cardiology',
  'Pediatrics',
  'Orthopedics',
  'Neurology',
  'Dermatology',
  'Psychiatry',
  'Endocrinology',
  'Gastroenterology',
  'Ophthalmology',
  'Otolaryngology',
  'Urology',
  'Gynecology',
  'General Medicine'
];
