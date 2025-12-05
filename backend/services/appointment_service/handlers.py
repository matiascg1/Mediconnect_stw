"""
Handlers para el servicio de citas médicas.
"""
from typing import Dict, Any
from .service import AppointmentService
from utils.logger import get_logger

logger = get_logger(__name__)

# Instancia global del servicio
_appointment_service = None

def get_appointment_service() -> AppointmentService:
    """Obtiene la instancia del servicio de citas."""
    global _appointment_service
    if _appointment_service is None:
        _appointment_service = AppointmentService()
    return _appointment_service

def set_bus_client(bus_client):
    """Configura el bus client para el servicio."""
    service = get_appointment_service()
    service.set_bus_client(bus_client)

def handle_create_appointment(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para crear cita médica."""
    try:
        logger.info("📅 Procesando creación de cita")
        service = get_appointment_service()
        return service.handle_create_appointment(data)
    except Exception as e:
        logger.error(f"💥 Error en handler create_appointment: {e}")
        return {
            'status': 'error',
            'message': 'Error interno creando cita',
            'status_code': 500
        }

def handle_get_appointments_by_user(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para obtener citas por usuario."""
    try:
        logger.debug("📋 Procesando obtención de citas por usuario")
        service = get_appointment_service()
        return service.handle_get_appointments_by_user(data)
    except Exception as e:
        logger.error(f"💥 Error en handler get_appointments_by_user: {e}")
        return {
            'status': 'error',
            'message': 'Error interno obteniendo citas',
            'status_code': 500
        }

def handle_get_appointment_by_id(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para obtener cita por ID."""
    try:
        logger.debug("🔍 Procesando obtención de cita por ID")
        service = get_appointment_service()
        return service.handle_get_appointment_by_id(data)
    except Exception as e:
        logger.error(f"💥 Error en handler get_appointment_by_id: {e}")
        return {
            'status': 'error',
            'message': 'Error interno obteniendo cita',
            'status_code': 500
        }

def handle_update_appointment_status(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para actualizar estado de cita."""
    try:
        logger.info("🔄 Procesando actualización de estado de cita")
        service = get_appointment_service()
        return service.handle_update_appointment_status(data)
    except Exception as e:
        logger.error(f"💥 Error en handler update_appointment_status: {e}")
        return {
            'status': 'error',
            'message': 'Error interno actualizando estado',
            'status_code': 500
        }

def handle_get_doctor_availability(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para obtener disponibilidad de médico."""
    try:
        logger.debug("⏰ Procesando obtención de disponibilidad")
        service = get_appointment_service()
        return service.handle_get_doctor_availability(data)
    except Exception as e:
        logger.error(f"💥 Error en handler get_doctor_availability: {e}")
        return {
            'status': 'error',
            'message': 'Error interno obteniendo disponibilidad',
            'status_code': 500
        }

def handle_get_appointment_stats(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para obtener estadísticas de citas."""
    try:
        logger.debug("📊 Procesando obtención de estadísticas")
        service = get_appointment_service()
        return service.handle_get_appointment_stats(data)
    except Exception as e:
        logger.error(f"💥 Error en handler get_appointment_stats: {e}")
        return {
            'status': 'error',
            'message': 'Error interno obteniendo estadísticas',
            'status_code': 500
        }

def handle_reschedule_appointment(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para reprogramar cita."""
    try:
        logger.info("🕐 Procesando reprogramación de cita")
        service = get_appointment_service()
        return service.handle_reschedule_appointment(data)
    except Exception as e:
        logger.error(f"💥 Error en handler reschedule_appointment: {e}")
        return {
            'status': 'error',
            'message': 'Error interno reprogramando cita',
            'status_code': 500
        }

def handle_cancel_appointment(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para cancelar cita."""
    try:
        logger.info("❌ Procesando cancelación de cita")
        service = get_appointment_service()
        return service.handle_cancel_appointment(data)
    except Exception as e:
        logger.error(f"💥 Error en handler cancel_appointment: {e}")
        return {
            'status': 'error',
            'message': 'Error interno cancelando cita',
            'status_code': 500
        }

def handle_health_check(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para health check del servicio."""
    try:
        logger.debug("❤️  Health check del servicio de citas")
        return {
            'status': 'success',
            'message': 'Appointment service is healthy',
            'service': 'appointment_service',
            'timestamp': '2024-01-01T00:00:00Z',
            'status_code': 200
        }
    except Exception as e:
        logger.error(f"💥 Error en health check: {e}")
        return {
            'status': 'error',
            'message': f'Appointment service error: {str(e)}',
            'status_code': 500
        }
