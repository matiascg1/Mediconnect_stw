from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.database.connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)

class EHRService:
    @staticmethod
    async def create_ehr_record(ehr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new EHR record"""
        try:
            with DatabaseConnection.get_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO ehr (
                        patient_id, doctor_id, appointment_id, consultation_date,
                        symptoms, diagnosis, treatment_plan, prescription_id,
                        notes, follow_up_date
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        ehr_data["patient_id"],
                        ehr_data["doctor_id"],
                        ehr_data.get("appointment_id"),
                        ehr_data["consultation_date"],
                        ehr_data["symptoms"],
                        ehr_data["diagnosis"],
                        ehr_data["treatment_plan"],
                        ehr_data.get("prescription_id"),
                        ehr_data.get("notes"),
                        ehr_data.get("follow_up_date")
                    )
                )
                
                ehr_id = cursor.lastrowid
                
                # Get created record
                cursor.execute(
                    """
                    SELECT e.*, 
                           p.first_name as patient_first_name, p.last_name as patient_last_name,
                           d.first_name as doctor_first_name, d.last_name as doctor_last_name,
                           d.specialty as doctor_specialty
                    FROM ehr e
                    JOIN users p ON e.patient_id = p.id
                    JOIN users d ON e.doctor_id = d.id
                    WHERE e.id = %s
                    """,
                    (ehr_id,)
                )
                ehr_record = cursor.fetchone()
                
                return {
                    "message": "EHR record created successfully",
                    "record": ehr_record
                }
                
        except Exception as e:
            logger.error(f"Error creating EHR record: {e}")
            return {"error": "Internal server error", "status_code": 500}
    
    @staticmethod
    async def get_ehr_by_id(ehr_id: int) -> Optional[Dict[str, Any]]:
        """Get EHR record by ID"""
        try:
            with DatabaseConnection.get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT e.*, 
                           p.first_name as patient_first_name, p.last_name as patient_last_name,
                           d.first_name as doctor_first_name, d.last_name as doctor_last_name,
                           d.specialty as doctor_specialty
                    FROM ehr e
                    JOIN users p ON e.patient_id = p.id
                    JOIN users d ON e.doctor_id = d.id
                    WHERE e.id = %s
                    """,
                    (ehr_id,)
                )
                ehr_record = cursor.fetchone()
                return ehr_record
        except Exception as e:
            logger.error(f"Error getting EHR record: {e}")
            return None
    
    @staticmethod
    async def get_patient_ehr_history(patient_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all EHR records for a patient"""
        try:
            with DatabaseConnection.get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT e.*, 
                           d.first_name as doctor_first_name, d.last_name as doctor_last_name,
                           d.specialty as doctor_specialty
                    FROM ehr e
                    JOIN users d ON e.doctor_id = d.id
                    WHERE e.patient_id = %s
                    ORDER BY e.consultation_date DESC
                    LIMIT %s
                    """,
                    (patient_id, limit)
                )
                ehr_records = cursor.fetchall()
                return ehr_records
        except Exception as e:
            logger.error(f"Error getting patient EHR history: {e}")
            return []
    
    @staticmethod
    async def get_doctor_ehr_records(doctor_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all EHR records created by a doctor"""
        try:
            with DatabaseConnection.get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT e.*, 
                           p.first_name as patient_first_name, p.last_name as patient_last_name
                    FROM ehr e
                    JOIN users p ON e.patient_id = p.id
                    WHERE e.doctor_id = %s
                    ORDER BY e.consultation_date DESC
                    LIMIT %s
                    """,
                    (doctor_id, limit)
                )
                ehr_records = cursor.fetchall()
                return ehr_records
        except Exception as e:
            logger.error(f"Error getting doctor EHR records: {e}")
            return []
    
    @staticmethod
    async def update_ehr_record(ehr_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update EHR record"""
        try:
            allowed_updates = [
                'symptoms', 'diagnosis', 'treatment_plan', 'prescription_id',
                'notes', 'follow_up_date'
            ]
            
            update_fields = []
            update_values = []
            
            for field in allowed_updates:
                if field in update_data and update_data[field] is not None:
                    update_fields.append(f"{field} = %s")
                    update_values.append(update_data[field])
            
            if not update_fields:
                return {"error": "No valid fields to update", "status_code": 400}
            
            # Add ehr_id for WHERE clause
            update_values.append(ehr_id)
            
            query = f"UPDATE ehr SET {', '.join(update_fields)} WHERE id = %s"
            
            with DatabaseConnection.get_cursor() as cursor:
                cursor.execute(query, update_values)
                
                if cursor.rowcount == 0:
                    return {"error": "EHR record not found", "status_code": 404}
                
                # Get updated record
                cursor.execute(
                    """
                    SELECT e.*, 
                           p.first_name as patient_first_name, p.last_name as patient_last_name,
                           d.first_name as doctor_first_name, d.last_name as doctor_last_name,
                           d.specialty as doctor_specialty
                    FROM ehr e
                    JOIN users p ON e.patient_id = p.id
                    JOIN users d ON e.doctor_id = d.id
                    WHERE e.id = %s
                    """,
                    (ehr_id,)
                )
                updated_record = cursor.fetchone()
                
                return {
                    "message": "EHR record updated successfully",
                    "record": updated_record
                }
                
        except Exception as e:
            logger.error(f"Error updating EHR record: {e}")
            return {"error": "Internal server error", "status_code": 500}
    
    @staticmethod
    async def search_ehr_records(
        patient_id: Optional[int] = None,
        doctor_id: Optional[int] = None,
        diagnosis_keyword: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Search EHR records with filters"""
        try:
            with DatabaseConnection.get_cursor() as cursor:
                query = """
                    SELECT e.*, 
                           p.first_name as patient_first_name, p.last_name as patient_last_name,
                           d.first_name as doctor_first_name, d.last_name as doctor_last_name,
                           d.specialty as doctor_specialty
                    FROM ehr e
                    JOIN users p ON e.patient_id = p.id
                    JOIN users d ON e.doctor_id = d.id
                    WHERE 1=1
                """
                params = []
                
                if patient_id:
                    query += " AND e.patient_id = %s"
                    params.append(patient_id)
                
                if doctor_id:
                    query += " AND e.doctor_id = %s"
                    params.append(doctor_id)
                
                if diagnosis_keyword:
                    query += " AND e.diagnosis LIKE %s"
                    params.append(f"%{diagnosis_keyword}%")
                
                if start_date:
                    query += " AND e.consultation_date >= %s"
                    params.append(start_date)
                
                if end_date:
                    query += " AND e.consultation_date <= %s"
                    params.append(end_date)
                
                query += " ORDER BY e.consultation_date DESC LIMIT 100"
                
                cursor.execute(query, params)
                ehr_records = cursor.fetchall()
                return ehr_records
        except Exception as e:
            logger.error(f"Error searching EHR records: {e}")
            return []
    
    @staticmethod
    async def get_patient_statistics(patient_id: int) -> Dict[str, Any]:
        """Get statistics for a patient"""
        try:
            with DatabaseConnection.get_cursor() as cursor:
                # Total consultations
                cursor.execute(
                    "SELECT COUNT(*) as total_consultations FROM ehr WHERE patient_id = %s",
                    (patient_id,)
                )
                total_consults = cursor.fetchone()["total_consultations"]
                
                # Most common diagnosis
                cursor.execute(
                    """
                    SELECT diagnosis, COUNT(*) as frequency 
                    FROM ehr 
                    WHERE patient_id = %s 
                    GROUP BY diagnosis 
                    ORDER BY frequency DESC 
                    LIMIT 5
                    """,
                    (patient_id,)
                )
                common_diagnoses = cursor.fetchall()
                
                # Last consultation date
                cursor.execute(
                    """
                    SELECT MAX(consultation_date) as last_consultation 
                    FROM ehr 
                    WHERE patient_id = %s
                    """,
                    (patient_id,)
                )
                last_consultation = cursor.fetchone()["last_consultation"]
                
                # Active prescriptions count
                cursor.execute(
                    """
                    SELECT COUNT(*) as active_prescriptions 
                    FROM prescriptions 
                    WHERE patient_id = %s AND status = 'active'
                    """,
                    (patient_id,)
                )
                active_prescriptions = cursor.fetchone()["active_prescriptions"]
                
                return {
                    "total_consultations": total_consults,
                    "common_diagnoses": common_diagnoses,
                    "last_consultation": last_consultation,
                    "active_prescriptions": active_prescriptions,
                    "patient_id": patient_id
                }
        except Exception as e:
            logger.error(f"Error getting patient statistics: {e}")
            return {}
