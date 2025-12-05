from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.database.connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)

class PrescriptionService:
    @staticmethod
    async def create_prescription(prescription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new prescription"""
        try:
            with DatabaseConnection.get_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO prescriptions (
                        patient_id, doctor_id, ehr_id, medication_name,
                        dosage, frequency, duration_days, instructions,
                        prescribed_date, status, refills_remaining
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        prescription_data["patient_id"],
                        prescription_data["doctor_id"],
                        prescription_data.get("ehr_id"),
                        prescription_data["medication_name"],
                        prescription_data["dosage"],
                        prescription_data["frequency"],
                        prescription_data["duration_days"],
                        prescription_data.get("instructions"),
                        prescription_data.get("prescribed_date", datetime.now()),
                        prescription_data.get("status", "active"),
                        prescription_data.get("refills_remaining", 0)
                    )
                )
                
                prescription_id = cursor.lastrowid
                
                # Get created prescription
                cursor.execute(
                    """
                    SELECT p.*, 
                           pt.first_name as patient_first_name, pt.last_name as patient_last_name,
                           d.first_name as doctor_first_name, d.last_name as doctor_last_name,
                           d.specialty as doctor_specialty
                    FROM prescriptions p
                    JOIN users pt ON p.patient_id = pt.id
                    JOIN users d ON p.doctor_id = d.id
                    WHERE p.id = %s
                    """,
                    (prescription_id,)
                )
                prescription = cursor.fetchone()
                
                return {
                    "message": "Prescription created successfully",
                    "prescription": prescription
                }
                
        except Exception as e:
            logger.error(f"Error creating prescription: {e}")
            return {"error": "Internal server error", "status_code": 500}
    
    @staticmethod
    async def get_prescription_by_id(prescription_id: int) -> Optional[Dict[str, Any]]:
        """Get prescription by ID"""
        try:
            with DatabaseConnection.get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT p.*, 
                           pt.first_name as patient_first_name, pt.last_name as patient_last_name,
                           d.first_name as doctor_first_name, d.last_name as doctor_last_name,
                           d.specialty as doctor_specialty
                    FROM prescriptions p
                    JOIN users pt ON p.patient_id = pt.id
                    JOIN users d ON p.doctor_id = d.id
                    WHERE p.id = %s
                    """,
                    (prescription_id,)
                )
                prescription = cursor.fetchone()
                return prescription
        except Exception as e:
            logger.error(f"Error getting prescription: {e}")
            return None
    
    @staticmethod
    async def get_patient_prescriptions(patient_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all prescriptions for a patient"""
        try:
            with DatabaseConnection.get_cursor() as cursor:
                query = """
                    SELECT p.*, 
                           d.first_name as doctor_first_name, d.last_name as doctor_last_name,
                           d.specialty as doctor_specialty
                    FROM prescriptions p
                    JOIN users d ON p.doctor_id = d.id
                    WHERE p.patient_id = %s
                """
                params = [patient_id]
                
                if status:
                    query += " AND p.status = %s"
                    params.append(status)
                
                query += " ORDER BY p.prescribed_date DESC"
                
                cursor.execute(query, params)
                prescriptions = cursor.fetchall()
                return prescriptions
        except Exception as e:
            logger.error(f"Error getting patient prescriptions: {e}")
            return []
    
    @staticmethod
    async def get_doctor_prescriptions(doctor_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all prescriptions created by a doctor"""
        try:
            with DatabaseConnection.get_cursor() as cursor:
                query = """
                    SELECT p.*, 
                           pt.first_name as patient_first_name, pt.last_name as patient_last_name
                    FROM prescriptions p
                    JOIN users pt ON p.patient_id = pt.id
                    WHERE p.doctor_id = %s
                """
                params = [doctor_id]
                
                if status:
                    query += " AND p.status = %s"
                    params.append(status)
                
                query += " ORDER BY p.prescribed_date DESC"
                
                cursor.execute(query, params)
                prescriptions = cursor.fetchall()
                return prescriptions
        except Exception as e:
            logger.error(f"Error getting doctor prescriptions: {e}")
            return []
    
    @staticmethod
    async def update_prescription(prescription_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update prescription"""
        try:
            allowed_updates = [
                'medication_name', 'dosage', 'frequency', 'duration_days',
                'instructions', 'status', 'refills_remaining'
            ]
            
            update_fields = []
            update_values = []
            
            for field in allowed_updates:
                if field in update_data and update_data[field] is not None:
                    update_fields.append(f"{field} = %s")
                    update_values.append(update_data[field])
            
            if not update_fields:
                return {"error": "No valid fields to update", "status_code": 400}
            
            # Add prescription_id for WHERE clause
            update_values.append(prescription_id)
            
            query = f"UPDATE prescriptions SET {', '.join(update_fields)} WHERE id = %s"
            
            with DatabaseConnection.get_cursor() as cursor:
                cursor.execute(query, update_values)
                
                if cursor.rowcount == 0:
                    return {"error": "Prescription not found", "status_code": 404}
                
                # Get updated prescription
                cursor.execute(
                    """
                    SELECT p.*, 
                           pt.first_name as patient_first_name, pt.last_name as patient_last_name,
                           d.first_name as doctor_first_name, d.last_name as doctor_last_name,
                           d.specialty as doctor_specialty
                    FROM prescriptions p
                    JOIN users pt ON p.patient_id = pt.id
                    JOIN users d ON p.doctor_id = d.id
                    WHERE p.id = %s
                    """,
                    (prescription_id,)
                )
                updated_prescription = cursor.fetchone()
                
                return {
                    "message": "Prescription updated successfully",
                    "prescription": updated_prescription
                }
                
        except Exception as e:
            logger.error(f"Error updating prescription: {e}")
            return {"error": "Internal server error", "status_code": 500}
    
    @staticmethod
    async def refill_prescription(prescription_id: int) -> Dict[str, Any]:
        """Refill a prescription"""
        try:
            with DatabaseConnection.get_cursor() as cursor:
                # Check if refills are available
                cursor.execute(
                    "SELECT refills_remaining FROM prescriptions WHERE id = %s",
                    (prescription_id,)
                )
                prescription = cursor.fetchone()
                
                if not prescription:
                    return {"error": "Prescription not found", "status_code": 404}
                
                if prescription["refills_remaining"] <= 0:
                    return {"error": "No refills remaining", "status_code": 400}
                
                # Decrement refills
                cursor.execute(
                    """
                    UPDATE prescriptions 
                    SET refills_remaining = refills_remaining - 1
                    WHERE id = %s
                    """,
                    (prescription_id,)
                )
                
                return {"message": "Prescription refilled successfully"}
        except Exception as e:
            logger.error(f"Error refilling prescription: {e}")
            return {"error": "Internal server error", "status_code": 500}
    
    @staticmethod
    async def get_active_prescriptions(patient_id: int) -> List[Dict[str, Any]]:
        """Get active prescriptions for a patient"""
        try:
            with DatabaseConnection.get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT p.*, 
                           d.first_name as doctor_first_name, d.last_name as doctor_last_name,
                           d.specialty as doctor_specialty
                    FROM prescriptions p
                    JOIN users d ON p.doctor_id = d.id
                    WHERE p.patient_id = %s 
                    AND p.status = 'active'
                    AND (p.duration_days = 0 OR 
                         DATE_ADD(p.prescribed_date, INTERVAL p.duration_days DAY) >= CURDATE())
                    ORDER BY p.prescribed_date DESC
                    """,
                    (patient_id,)
                )
                prescriptions = cursor.fetchall()
                return prescriptions
        except Exception as e:
            logger.error(f"Error getting active prescriptions: {e}")
            return []
    
    @staticmethod
    async def search_prescriptions(
        patient_id: Optional[int] = None,
        doctor_id: Optional[int] = None,
        medication_name: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search prescriptions with filters"""
        try:
            with DatabaseConnection.get_cursor() as cursor:
                query = """
                    SELECT p.*, 
                           pt.first_name as patient_first_name, pt.last_name as patient_last_name,
                           d.first_name as doctor_first_name, d.last_name as doctor_last_name,
                           d.specialty as doctor_specialty
                    FROM prescriptions p
                    JOIN users pt ON p.patient_id = pt.id
                    JOIN users d ON p.doctor_id = d.id
                    WHERE 1=1
                """
                params = []
                
                if patient_id:
                    query += " AND p.patient_id = %s"
                    params.append(patient_id)
                
                if doctor_id:
                    query += " AND p.doctor_id = %s"
                    params.append(doctor_id)
                
                if medication_name:
                    query += " AND p.medication_name LIKE %s"
                    params.append(f"%{medication_name}%")
                
                if status:
                    query += " AND p.status = %s"
                    params.append(status)
                
                query += " ORDER BY p.prescribed_date DESC LIMIT 100"
                
                cursor.execute(query, params)
                prescriptions = cursor.fetchall()
                return prescriptions
        except Exception as e:
            logger.error(f"Error searching prescriptions: {e}")
            return []
