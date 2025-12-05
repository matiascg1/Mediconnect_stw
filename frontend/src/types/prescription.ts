export interface Prescription {
  id: number;
  patient_id: number;
  doctor_id: number;
  ehr_id?: number;
  medication_name: string;
  dosage: string;
  frequency: string;
  duration_days: number;
  instructions?: string;
  prescribed_date: string;
  status: 'active' | 'completed' | 'cancelled';
  refills_remaining: number;
  created_at?: string;
  patient_first_name?: string;
  patient_last_name?: string;
  doctor_first_name?: string;
  doctor_last_name?: string;
  doctor_specialty?: string;
}
