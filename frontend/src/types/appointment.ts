export interface Appointment {
  id: number;
  patient_id: number;
  doctor_id: number;
  appointment_date: string;
  duration_minutes: number;
  status: 'scheduled' | 'confirmed' | 'cancelled' | 'completed';
  appointment_type: 'consultation' | 'follow_up' | 'emergency';
  notes?: string;
  created_at?: string;
  updated_at?: string;
  patient_first_name?: string;
  patient_last_name?: string;
  doctor_first_name?: string;
  doctor_last_name?: string;
  doctor_specialty?: string;
}

export interface TimeSlot {
  start_time: string;
  end_time: string;
  is_available: boolean;
}
