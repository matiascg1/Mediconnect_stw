import api from './api';

export interface Appointment {
  id: number;
  patient_id: number;
  doctor_id: number;
  appointment_date: string;
  duration_minutes: number;
  status: 'scheduled' | 'confirmed' | 'cancelled' | 'completed';
  appointment_type: 'consultation' | 'follow_up' | 'emergency';
  notes?: string;
  patient_first_name?: string;
  patient_last_name?: string;
  doctor_first_name?: string;
  doctor_last_name?: string;
  doctor_specialty?: string;
}

export interface CreateAppointmentRequest {
  patient_id: number;
  doctor_id: number;
  appointment_date: string;
  duration_minutes?: number;
  appointment_type?: string;
  notes?: string;
}

export interface UpdateAppointmentRequest {
  appointment_date?: string;
  duration_minutes?: number;
  status?: string;
  appointment_type?: string;
  notes?: string;
}

export const appointmentService = {
  async getAppointments(): Promise<{ appointments: Appointment[]; count: number }> {
    const response = await api.get('/appointments');
    return response.data;
  },

  async getAppointment(id: number): Promise<Appointment> {
    const response = await api.get(`/appointments/${id}`);
    return response.data;
  },

  async createAppointment(data: CreateAppointmentRequest): Promise<Appointment> {
    const response = await api.post('/appointments', data);
    return response.data.appointment;
  },

  async updateAppointment(id: number, data: UpdateAppointmentRequest): Promise<Appointment> {
    const response = await api.put(`/appointments/${id}`, data);
    return response.data.appointment;
  },

  async cancelAppointment(id: number): Promise<void> {
    await api.delete(`/appointments/${id}`);
  },

  async getDoctorAvailability(doctorId: number, date: string): Promise<any[]> {
    const response = await api.get(`/appointments/doctor/${doctorId}/availability`, {
      params: { date }
    });
    return response.data.slots;
  },

  async getAppointmentsByDateRange(
    startDate: string,
    endDate: string,
    doctorId?: number,
    patientId?: number
  ): Promise<{ appointments: Appointment[]; count: number }> {
    const params: any = { start_date: startDate, end_date: endDate };
    if (doctorId) params.doctor_id = doctorId;
    if (patientId) params.patient_id = patientId;
    
    const response = await api.get('/appointments/date-range/', { params });
    return response.data;
  },
};
