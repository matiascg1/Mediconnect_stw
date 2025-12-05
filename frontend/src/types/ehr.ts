export interface EHR {
  id: number;
  patient_id: number;
  doctor_id: number;
  appointment_id?: number;
  consultation_date: string;
  symptoms: string;
  diagnosis: string;
  treatment_plan: string;
  prescription_id?: number;
  notes?: string;
  follow_up_date?: string;
  created_at?: string;
  patient_first_name?: string;
  patient_last_name?: string;
  doctor_first_name?: string;
  doctor_last_name?: string;
  doctor_specialty?: string;
}

export interface EHRStatistics {
  total_consultations: number;
  common_diagnoses: Array<{
    diagnosis: string;
    frequency: number;
  }>;
  last_consultation: string;
  active_prescriptions: number;
  patient_id: number;
}
