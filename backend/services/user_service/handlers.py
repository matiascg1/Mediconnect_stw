"""
Handlers para el servicio de gestión de usuarios.
"""
from typing import Dict, Any
from .service import UserService
from utils.logger import get_logger

logger = get_logger(__name__)

# Instancia global del servicio
_user_service = None

def get_user_service() -> UserService:
    """Obtiene la instancia del servicio de usuarios."""
    global _user_service
    if _user_service is None:
        _user_service = UserService()
    return _user_service

def set_bus_client(bus_client):
    """Configura el bus client para el servicio."""
    service = get_user_service()
    service.set_bus_client(bus_client)

def handle_get_user_by_id(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para obtener usuario por ID."""
    try:
        logger.debug("👤 Procesando obtención de usuario por ID")
        service = get_user_service()
        return service.handle_get_user_by_id(data)
    except Exception as e:
        logger.error(f"💥 Error en handler get_user_by_id: {e}")
        return {
            'status': 'error',
            'message': 'Error interno obteniendo usuario',
            'status_code': 500
        }

def handle_get_all_users(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para obtener todos los usuarios."""
    try:
        logger.debug("👥 Procesando obtención de todos los usuarios")
        service = get_user_service()
        return service.handle_get_all_users(data)
    except Exception as e:
        logger.error(f"💥 Error en handler get_all_users: {e}")
        return {
            'status': 'error',
            'message': 'Error interno obteniendo usuarios',
            'status_code': 500
        }

def handle_update_user(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para actualizar usuario."""
    try:
        logger.info("✏️  Procesando actualización de usuario")
        service = get_user_service()
        return service.handle_update_user(data)
    except Exception as e:
        logger.error(f"💥 Error en handler update_user: {e}")
        return {
            'status': 'error',
            'message': 'Error interno actualizando usuario',
            'status_code': 500
        }

def handle_delete_user(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para eliminar (desactivar) usuario."""
    try:
        logger.info("🗑️  Procesando eliminación de usuario")
        service = get_user_service()
        return service.handle_delete_user(data)
    except Exception as e:
        logger.error(f"💥 Error en handler delete_user: {e}")
        return {
            'status': 'error',
            'message': 'Error interno eliminando usuario',
            'status_code': 500
        }

def handle_activate_user(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para activar usuario."""
    try:
        logger.info("✅ Procesando activación de usuario")
        service = get_user_service()
        return service.handle_activate_user(data)
    except Exception as e:
        logger.error(f"💥 Error en handler activate_user: {e}")
        return {
            'status': 'error',
            'message': 'Error interno activando usuario',
            'status_code': 500
        }

def handle_get_doctors(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para obtener médicos."""
    try:
        logger.debug("🩺 Procesando obtención de médicos")
        service = get_user_service()
        return service.handle_get_doctors(data)
    except Exception as e:
        logger.error(f"💥 Error en handler get_doctors: {e}")
        return {
            'status': 'error',
            'message': 'Error interno obteniendo médicos',
            'status_code': 500
        }

def handle_get_user_stats(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para obtener estadísticas de usuarios."""
    try:
        logger.debug("📊 Procesando obtención de estadísticas")
        service = get_user_service()
        return service.handle_get_user_stats(data)
    except Exception as e:
        logger.error(f"💥 Error en handler get_user_stats: {e}")
        return {
            'status': 'error',
            'message': 'Error interno obteniendo estadísticas',
            'status_code': 500
        }

def handle_get_user_activity(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para obtener actividad de usuario."""
    try:
        logger.debug("📈 Procesando obtención de actividad")
        service = get_user_service()
        return service.handle_get_user_activity(data)
    except Exception as e:
        logger.error(f"💥 Error en handler get_user_activity: {e}")
        return {
            'status': 'error',
            'message': 'Error interno obteniendo actividad',
            'status_code': 500
        }

def handle_search_users(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para buscar usuarios."""
    try:
        logger.debug("🔍 Procesando búsqueda de usuarios")
        service = get_user_service()
        return service.handle_search_users(data)
    except Exception as e:
        logger.error(f"💥 Error en handler search_users: {e}")
        return {
            'status': 'error',
            'message': 'Error interno buscando usuarios',
            'status_code': 500
        }

def handle_health_check(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para health check del servicio."""
    try:
        logger.debug("❤️  Health check del servicio de usuarios")
        return {
            'status': 'success',
            'message': 'User service is healthy',
            'service': 'user_service',
            'timestamp': '2024-01-01T00:00:00Z',
            'status_code': 200
        }
    except Exception as e:
        logger.error(f"💥 Error en health check: {e}")
        return {
            'status': 'error',
            'message': f'User service error: {str(e)}',
            'status_code': 500
        }

def handle_create_user(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para crear nuevo usuario."""
    try:
        logger.info("✏️  Procesando creación de nuevo usuario")
        service = get_user_service()
        return service.handle_create_user(data)
    except Exception as e:
        logger.error(f"💥 Error en handler create_user: {e}")
        return {
            'status': 'error',
            'message': 'Error interno creando usuario',
            'status_code': 500
        }
