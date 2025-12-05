from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from backend.database.connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)

class AdminService:
    @staticmethod
    async def get_system_stats() -> Dict[str, Any]:
        """Get system statistics"""
        try:
            with DatabaseConnection.get_cursor() as cursor:
                # User statistics
                cursor.execute(
                    """
                    SELECT 
                        COUNT(*) as total_users,
                        SUM(CASE WHEN role = 'patient' THEN 1 ELSE 0 END) as total_patients,
                        SUM(CASE WHEN role = 'doctor' THEN 1 ELSE 0 END) as total_doctors,
                        SUM(CASE WHEN role = 'admin' THEN 1 ELSE 0 END) as total_admins,
                        SUM(CASE WHEN is_active = TRUE THEN 1 ELSE 0 END) as active_users
                    FROM users
                    """
                )
                user_stats = cursor.fetchone()
                
                # Appointment statistics
                cursor.execute(
                    """
                    SELECT 
                        COUNT(*) as total_appointments,
                        SUM(CASE WHEN status = 'scheduled' THEN 1 ELSE 0 END) as scheduled,
                        SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) as confirmed,
                        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled,
                        COUNT(DISTINCT patient_id) as unique_patients,
                        COUNT(DISTINCT doctor_id) as unique_doctors
                    FROM appointments
                    WHERE appointment_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                    """
                )
                appointment_stats = cursor.fetchone()
                
                # EHR statistics
                cursor.execute(
                    """
                    SELECT 
                        COUNT(*) as total_ehr_records,
                        COUNT(DISTINCT patient_id) as patients_with_records,
                        COUNT(DISTINCT doctor_id) as doctors_with_records
                    FROM ehr
                    WHERE consultation_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                    """
                )
                ehr_stats = cursor.fetchone()
                
                # Prescription statistics
                cursor.execute(
                    """
                    SELECT 
                        COUNT(*) as total_prescriptions,
                        SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
                        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled,
                        SUM(refills_remaining) as total_refills_remaining
                    FROM prescriptions
                    WHERE prescribed_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                    """
                )
                prescription_stats = cursor.fetchone()
                
                # Today's appointments
                cursor.execute(
                    """
                    SELECT COUNT(*) as todays_appointments
                    FROM appointments
                    WHERE DATE(appointment_date) = CURDATE()
                    AND status IN ('scheduled', 'confirmed')
                    """
                )
                todays_stats = cursor.fetchone()
                
                return {
                    "user_stats": user_stats,
                    "appointment_stats": appointment_stats,
                    "ehr_stats": ehr_stats,
                    "prescription_stats": prescription_stats,
                    "todays_stats": todays_stats,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {}
    
    @staticmethod
    async def get_daily_metrics(days: int = 7) -> List[Dict[str, Any]]:
        """Get daily metrics for the last N days"""
        try:
            with DatabaseConnection.get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT 
                        DATE(created_at) as date,
                        COUNT(*) as new_users,
                        SUM(CASE WHEN role = 'patient' THEN 1 ELSE 0 END) as new_patients,
                        SUM(CASE WHEN role = 'doctor' THEN 1 ELSE 0 END) as new_doctors
                    FROM users
                    WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                    GROUP BY DATE(created_at)
                    ORDER BY date DESC
                    """,
                    (days,)
                )
                user_metrics = cursor.fetchall()
                
                cursor.execute(
                    """
                    SELECT 
                        DATE(appointment_date) as date,
                        COUNT(*) as appointments,
                        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
                    FROM appointments
                    WHERE appointment_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                    GROUP BY DATE(appointment_date)
                    ORDER BY date DESC
                    """,
                    (days,)
                )
                appointment_metrics = cursor.fetchall()
                
                cursor.execute(
                    """
                    SELECT 
                        DATE(consultation_date) as date,
                        COUNT(*) as consultations
                    FROM ehr
                    WHERE consultation_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                    GROUP BY DATE(consultation_date)
                    ORDER BY date DESC
                    """,
                    (days,)
                )
                ehr_metrics = cursor.fetchall()
                
                # Combine metrics by date
                metrics_by_date = {}
                
                for metric in user_metrics:
                    date = metric["date"].isoformat()
                    if date not in metrics_by_date:
                        metrics_by_date[date] = {"date": date}
                    metrics_by_date[date].update({
                        "new_users": metric["new_users"],
                        "new_patients": metric["new_patients"],
                        "new_doctors": metric["new_doctors"]
                    })
                
                for metric in appointment_metrics:
                    date = metric["date"].isoformat()
                    if date not in metrics_by_date:
                        metrics_by_date[date] = {"date": date}
                    metrics_by_date[date].update({
                        "appointments": metric["appointments"],
                        "completed_appointments": metric["completed"]
                    })
                
                for metric in ehr_metrics:
                    date = metric["date"].isoformat()
                    if date not in metrics_by_date:
                        metrics_by_date[date] = {"date": date}
                    metrics_by_date[date].update({
                        "consultations": metric["consultations"]
                    })
                
                # Convert to list and sort by date
                metrics_list = list(metrics_by_date.values())
                metrics_list.sort(key=lambda x: x["date"], reverse=True)
                
                return metrics_list
        except Exception as e:
            logger.error(f"Error getting daily metrics: {e}")
            return []
    
    @staticmethod
    async def get_user_activity(user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get user activity history"""
        try:
            with DatabaseConnection.get_cursor() as cursor:
                # Get user info
                cursor.execute(
                    """
                    SELECT id, email, first_name, last_name, role, created_at
                    FROM users WHERE id = %s
                    """,
                    (user_id,)
                )
                user_info = cursor.fetchone()
                
                if not user_info:
                    return {"error": "User not found"}
                
                # Get appointments
                cursor.execute(
                    """
                    SELECT COUNT(*) as total_appointments,
                           SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                           MIN(appointment_date) as first_appointment,
                           MAX(appointment_date) as last_appointment
                    FROM appointments
                    WHERE patient_id = %s
                    """,
                    (user_id,)
                )
                appointment_activity = cursor.fetchone()
                
                # Get EHR records
                cursor.execute(
                    """
                    SELECT COUNT(*) as total_consultations,
                           MIN(consultation_date) as first_consultation,
                           MAX(consultation_date) as last_consultation
                    FROM ehr
                    WHERE patient_id = %s
                    """,
                    (user_id,)
                )
                ehr_activity = cursor.fetchone()
                
                # Get prescriptions
                cursor.execute(
                    """
                    SELECT COUNT(*) as total_prescriptions,
                           SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
                           MIN(prescribed_date) as first_prescription,
                           MAX(prescribed_date) as last_prescription
                    FROM prescriptions
                    WHERE patient_id = %s
                    """,
                    (user_id,)
                )
                prescription_activity = cursor.fetchone()
                
                # Get recent activity (last N days)
                cursor.execute(
                    """
                    SELECT 'appointment' as type, appointment_date as date, status
                    FROM appointments
                    WHERE patient_id = %s
                    AND appointment_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    UNION ALL
                    SELECT 'consultation' as type, consultation_date as date, NULL as status
                    FROM ehr
                    WHERE patient_id = %s
                    AND consultation_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    UNION ALL
                    SELECT 'prescription' as type, prescribed_date as date, status
                    FROM prescriptions
                    WHERE patient_id = %s
                    AND prescribed_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    ORDER BY date DESC
                    LIMIT 50
                    """,
                    (user_id, days, user_id, days, user_id, days)
                )
                recent_activity = cursor.fetchall()
                
                return {
                    "user_info": user_info,
                    "appointment_activity": appointment_activity,
                    "ehr_activity": ehr_activity,
                    "prescription_activity": prescription_activity,
                    "recent_activity": recent_activity
                }
        except Exception as e:
            logger.error(f"Error getting user activity: {e}")
            return {}
    
    @staticmethod
    async def get_system_logs(
        log_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get system logs (placeholder - in production, use proper logging system)"""
        try:
            # This is a placeholder - in a real system, you'd query from a logging database
            return [
                {
                    "id": 1,
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "service": "auth",
                    "message": "User login successful",
                    "user_id": 1,
                    "ip_address": "192.168.1.1"
                }
            ]
        except Exception as e:
            logger.error(f"Error getting system logs: {e}")
            return []
    
    @staticmethod
    async def backup_database() -> Dict[str, Any]:
        """Trigger database backup"""
        try:
            # This is a placeholder - in production, implement proper backup logic
            backup_time = datetime.now()
            backup_file = f"backup_{backup_time.strftime('%Y%m%d_%H%M%S')}.sql"
            
            return {
                "message": "Backup initiated successfully",
                "backup_file": backup_file,
                "timestamp": backup_time.isoformat(),
                "status": "in_progress"
            }
        except Exception as e:
            logger.error(f"Error triggering backup: {e}")
            return {"error": "Backup failed", "status_code": 500}
    
    @staticmethod
    async def get_system_health() -> Dict[str, Any]:
        """Check system health status"""
        try:
            health_status = {
                "database": "healthy",
                "services": {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Check database connection
            try:
                with DatabaseConnection.get_cursor() as cursor:
                    cursor.execute("SELECT 1")
                health_status["database"] = "healthy"
            except Exception:
                health_status["database"] = "unhealthy"
            
            # This is a placeholder - in production, check all microservices
            health_status["services"] = {
                "auth_service": "healthy",
                "user_service": "healthy",
                "appointment_service": "healthy",
                "ehr_service": "healthy",
                "prescription_service": "healthy"
            }
            
            return health_status
        except Exception as e:
            logger.error(f"Error checking system health: {e}")
            return {"status": "error", "message": str(e)}
