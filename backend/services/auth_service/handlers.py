"""
Handlers para el servicio de autenticación.
Estas funciones son llamadas por el bus client cuando llegan mensajes.
"""
from typing import Dict, Any
from .service import AuthService
from utils.logger import get_logger

logger = get_logger(__name__)

# Instancia global del servicio
_auth_service = None

def get_auth_service() -> AuthService:
    """Obtiene la instancia del servicio de autenticación."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service

def set_bus_client(bus_client):
    """Configura el bus client para el servicio."""
    service = get_auth_service()
    service.set_bus_client(bus_client)

def handle_register(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para registro de usuarios."""
    try:
        logger.info("📝 Procesando solicitud de registro")
        service = get_auth_service()
        return service.handle_register(data)
    except Exception as e:
        logger.error(f"💥 Error en handler de registro: {e}")
        return {
            'status': 'error',
            'message': 'Error interno procesando registro',
            'status_code': 500
        }

def handle_login(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para login de usuarios."""
    try:
        logger.info("🔐 Procesando solicitud de login")
        service = get_auth_service()
        return service.handle_login(data)
    except Exception as e:
        logger.error(f"💥 Error en handler de login: {e}")
        return {
            'status': 'error',
            'message': 'Error interno procesando login',
            'status_code': 500
        }

def handle_verify_token(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para verificación de token."""
    try:
        logger.debug("🔍 Procesando verificación de token")
        service = get_auth_service()
        return service.handle_verify_token(data)
    except Exception as e:
        logger.error(f"💥 Error en handler de verificación de token: {e}")
        return {
            'status': 'error',
            'message': 'Error interno verificando token',
            'status_code': 500
        }

def handle_refresh_token(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para refresh de token."""
    try:
        logger.debug("🔄 Procesando refresh de token")
        service = get_auth_service()
        return service.handle_refresh_token(data)
    except Exception as e:
        logger.error(f"💥 Error en handler de refresh token: {e}")
        return {
            'status': 'error',
            'message': 'Error interno refrescando token',
            'status_code': 500
        }

def handle_change_password(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para cambio de contraseña."""
    try:
        logger.info("🔑 Procesando cambio de contraseña")
        service = get_auth_service()
        return service.handle_change_password(data)
    except Exception as e:
        logger.error(f"💥 Error en handler de cambio de contraseña: {e}")
        return {
            'status': 'error',
            'message': 'Error interno cambiando contraseña',
            'status_code': 500
        }

def handle_logout(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para logout."""
    try:
        logger.info("🚪 Procesando logout")
        service = get_auth_service()
        return service.handle_logout(data)
    except Exception as e:
        logger.error(f"💥 Error en handler de logout: {e}")
        return {
            'status': 'error',
            'message': 'Error interno procesando logout',
            'status_code': 500
        }

def handle_reset_password_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para solicitud de restablecimiento de contraseña."""
    try:
        logger.info("📧 Procesando solicitud de reset password")
        service = get_auth_service()
        return service.handle_reset_password_request(data)
    except Exception as e:
        logger.error(f"💥 Error en handler de reset password request: {e}")
        return {
            'status': 'error',
            'message': 'Error interno procesando solicitud',
            'status_code': 500
        }

def handle_reset_password(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para restablecimiento de contraseña."""
    try:
        logger.info("🔄 Procesando reset de contraseña")
        service = get_auth_service()
        return service.handle_reset_password(data)
    except Exception as e:
        logger.error(f"💥 Error en handler de reset password: {e}")
        return {
            'status': 'error',
            'message': 'Error interno restableciendo contraseña',
            'status_code': 500
        }

def handle_get_user(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para obtener información de usuario."""
    try:
        logger.debug("👤 Procesando obtención de usuario")
        service = get_auth_service()
        user_id = data.get('user_id')
        
        if not user_id:
            return {
                'status': 'error',
                'message': 'ID de usuario requerido',
                'status_code': 400
            }
        
        user = service.get_user_by_id(user_id)
        if not user:
            return {
                'status': 'error',
                'message': 'Usuario no encontrado',
                'status_code': 404
            }
        
        return {
            'status': 'success',
            'data': user,
            'status_code': 200
        }
        
    except Exception as e:
        logger.error(f"💥 Error obteniendo usuario: {e}")
        return {
            'status': 'error',
            'message': 'Error interno obteniendo usuario',
            'status_code': 500
        }

def handle_health_check(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler para health check del servicio."""
    try:
        service = get_auth_service()
        logger.debug("❤️  Health check del servicio de autenticación")
        
        return {
            'status': 'success',
            'message': 'Auth service is healthy',
            'service': 'auth_service',
            'timestamp': '2024-01-01T00:00:00Z',  # En realidad usar datetime
            'status_code': 200
        }
    except Exception as e:
        logger.error(f"💥 Error en health check: {e}")
        return {
            'status': 'error',
            'message': f'Auth service error: {str(e)}',
            'status_code': 500
        }
