"""
Servicio de autenticación y autorización para MediConnect.
Maneja registro, login, verificación de tokens y gestión de sesiones.
"""
import bcrypt
import jwt
import datetime
import re
from typing import Dict, Any, Optional, Tuple
import mysql.connector
from database.connection import get_db_connection
from utils.logger import get_logger
from utils.security import generate_token, validate_token, hash_password, verify_password

logger = get_logger(__name__)

class AuthService:
    """Servicio de autenticación."""
    
    def __init__(self):
        self.bus_client = None
        self.jwt_secret = "mediconnect-super-secret-jwt-key-2025"
        self.jwt_algorithm = "HS256"
        self.token_expiry_hours = 24
        self.refresh_token_expiry_days = 7
    
    def set_bus_client(self, bus_client):
        """Configura el cliente del bus."""
        self.bus_client = bus_client
    
    def handle_register(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Maneja el registro de nuevos usuarios."""
        try:
            logger.info("Procesando solicitud de registro")
            
            # Validar campos requeridos
            validation_result = self._validate_registration_data(data)
            if not validation_result['valid']:
                return {
                    'status': 'error',
                    'message': validation_result['message'],
                    'status_code': 400
                }
            
            # Conectar a la base de datos
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            
            # Verificar si el usuario ya existe
            cursor.execute(
                """
                SELECT idUsuario, estado FROM Usuarios 
                WHERE rut = %s OR correo = %s
                """,
                (data['rut'], data['correo'].lower())
            )
            existing_user = cursor.fetchone()
            
            if existing_user:
                cursor.close()
                db.close()
                
                if existing_user['estado'] == 'bloqueado':
                    return {
                        'status': 'error',
                        'message': 'Esta cuenta ha sido bloqueada. Contacte al administrador.',
                        'status_code': 403
                    }
                
                return {
                    'status': 'error',
                    'message': 'Ya existe un usuario con ese RUT o correo electrónico.',
                    'status_code': 409
                }
            
            # Hashear contraseña
            password_hash = hash_password(data['password'])
            
            # Determinar rol
            rol = self._determine_user_role(data)
            
            # Insertar usuario
            cursor.execute(
                """
                INSERT INTO Usuarios 
                (nombre, rut, correo, telefono, password_hash, rol, especialidad, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'activo')
                """,
                (
                    data['nombre'].strip(),
                    data['rut'].strip(),
                    data['correo'].lower().strip(),
                    data.get('telefono', '').strip(),
                    password_hash,
                    rol,
                    data.get('especialidad') if rol == 'medico' else None
                )
            )
            
            user_id = cursor.lastrowid
            
            # Registrar actividad
            cursor.execute(
                """
                INSERT INTO ActividadUsuarios (usuarioId, accion, detalles)
                VALUES (%s, 'registro', %s)
                """,
                (user_id, f"Usuario registrado como {rol}")
            )
            
            # Confirmar transacción
            db.commit()
            
            cursor.close()
            db.close()
            
            logger.info(f"Usuario registrado exitosamente: {data['correo']} (ID: {user_id}, Rol: {rol})")
            
            # Generar token de acceso
            access_token = self._generate_access_token(
                user_id=user_id,
                email=data['correo'],
                nombre=data['nombre'],
                rol=rol
            )
            
            # Generar refresh token
            refresh_token = self._generate_refresh_token(user_id)
            
            # Preparar respuesta
            user_data = {
                'id': user_id,
                'nombre': data['nombre'],
                'correo': data['correo'],
                'rol': rol,
                'especialidad': data.get('especialidad'),
                'telefono': data.get('telefono'),
                'rut': data['rut']
            }
            
            return {
                'status': 'success',
                'message': 'Usuario registrado exitosamente',
                'user': user_data,
                'tokens': {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'expires_in': self.token_expiry_hours * 3600  # En segundos
                },
                'status_code': 201
            }
            
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en registro: {e}")
            return {
                'status': 'error',
                'message': 'Error en el servidor de base de datos',
                'status_code': 500
            }
        except Exception as e:
            logger.error(f"Error interno en registro: {e}")
            return {
                'status': 'error',
                'message': 'Error interno del servidor',
                'status_code': 500
            }
    
    def handle_login(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Maneja el inicio de sesión de usuarios."""
        try:
            logger.info(f"Procesando login para: {data.get('correo', 'unknown')}")
            
            # Validar campos requeridos
            if 'correo' not in data or 'password' not in data:
                return {
                    'status': 'error',
                    'message': 'Correo y contraseña son requeridos',
                    'status_code': 400
                }
            
            # Conectar a la base de datos
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            
            # Buscar usuario
            cursor.execute(
                """
                SELECT 
                    idUsuario, nombre, correo, password_hash, rol, especialidad, 
                    estado, ultimo_login, intentos_fallidos, telefono, rut
                FROM Usuarios 
                WHERE correo = %s
                """,
                (data['correo'].lower(),)
            )
            user = cursor.fetchone()
            
            if not user:
                cursor.close()
                db.close()
                logger.warning(f"Intento de login fallido: usuario no encontrado - {data['correo']}")
                return {
                    'status': 'error',
                    'message': 'Credenciales inválidas',
                    'status_code': 401
                }
            
            # Verificar estado
            if user['estado'] == 'bloqueado':
                cursor.close()
                db.close()
                logger.warning(f"Intento de login fallido: usuario bloqueado - {user['correo']}")
                return {
                    'status': 'error',
                    'message': 'Usuario bloqueado. Contacte al administrador.',
                    'status_code': 403
                }
            
            # Verificar intentos fallidos
            if user['intentos_fallidos'] and user['intentos_fallidos'] >= 5:
                # Bloquear usuario temporalmente
                cursor.execute(
                    "UPDATE Usuarios SET estado = 'bloqueado' WHERE idUsuario = %s",
                    (user['idUsuario'],)
                )
                db.commit()
                cursor.close()
                db.close()
                
                logger.warning(f"Usuario bloqueado por múltiples intentos fallidos: {user['correo']}")
                return {
                    'status': 'error',
                    'message': 'Cuenta bloqueada por seguridad. Contacte al administrador.',
                    'status_code': 403
                }
            
            # Verificar contraseña
            if not verify_password(data['password'], user['password_hash']):
                # Incrementar intentos fallidos
                cursor.execute(
                    """
                    UPDATE Usuarios 
                    SET intentos_fallidos = COALESCE(intentos_fallidos, 0) + 1,
                        ultimo_intento_fallido = NOW()
                    WHERE idUsuario = %s
                    """,
                    (user['idUsuario'],)
                )
                db.commit()
                
                cursor.close()
                db.close()
                
                logger.warning(f"Intento de login fallido: contraseña incorrecta - {user['correo']}")
                return {
                    'status': 'error',
                    'message': 'Credenciales inválidas',
                    'status_code': 401
                }
            
            # Resetear intentos fallidos y actualizar último login
            cursor.execute(
                """
                UPDATE Usuarios 
                SET intentos_fallidos = 0,
                    ultimo_login = NOW(),
                    ultimo_intento_fallido = NULL
                WHERE idUsuario = %s
                """,
                (user['idUsuario'],)
            )
            
            # Registrar actividad de login
            cursor.execute(
                """
                INSERT INTO ActividadUsuarios (usuarioId, accion, detalles)
                VALUES (%s, 'login_exitoso', 'Inicio de sesión exitoso')
                """,
                (user['idUsuario'],)
            )
            
            db.commit()
            cursor.close()
            db.close()
            
            # Generar tokens
            access_token = self._generate_access_token(
                user_id=user['idUsuario'],
                email=user['correo'],
                nombre=user['nombre'],
                rol=user['rol']
            )
            
            refresh_token = self._generate_refresh_token(user['idUsuario'])
            
            # Preparar datos del usuario
            user_data = {
                'id': user['idUsuario'],
                'nombre': user['nombre'],
                'correo': user['correo'],
                'rol': user['rol'],
                'especialidad': user['especialidad'],
                'telefono': user['telefono'],
                'rut': user['rut'],
                'estado': user['estado'],
                'last_login': user['ultimo_login'].isoformat() if user['ultimo_login'] else None
            }
            
            logger.info(f"Login exitoso: {user['correo']} (Rol: {user['rol']})")
            
            return {
                'status': 'success',
                'message': 'Login exitoso',
                'user': user_data,
                'tokens': {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'expires_in': self.token_expiry_hours * 3600
                },
                'status_code': 200
            }
            
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos en login: {e}")
            return {
                'status': 'error',
                'message': 'Error en el servidor de base de datos',
                'status_code': 500
            }
        except Exception as e:
            logger.error(f"Error interno en login: {e}")
            return {
                'status': 'error',
                'message': 'Error interno del servidor',
                'status_code': 500
            }
    
    def handle_verify_token(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica un token JWT y obtiene información del usuario."""
        try:
            token = data.get('token')
            if not token:
                return {
                    'status': 'error',
                    'message': 'Token no proporcionado',
                    'status_code': 401
                }
            
            # Decodificar y verificar token
            payload = self._verify_access_token(token)
            if not payload:
                return {
                    'status': 'error',
                    'message': 'Token inválido o expirado',
                    'status_code': 401
                }
            
            # Obtener información actualizada del usuario
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            
            cursor.execute(
                """
                SELECT idUsuario, nombre, correo, rol, especialidad, estado, telefono, rut
                FROM Usuarios 
                WHERE idUsuario = %s AND estado = 'activo'
                """,
                (payload['user_id'],)
            )
            user = cursor.fetchone()
            
            cursor.close()
            db.close()
            
            if not user:
                return {
                    'status': 'error',
                    'message': 'Usuario no encontrado o inactivo',
                    'status_code': 401
                }
            
            # Verificar que el correo coincida
            if user['correo'] != payload['email']:
                return {
                    'status': 'error',
                    'message': 'Token inválido',
                    'status_code': 401
                }
            
            # Preparar respuesta
            user_data = {
                'id': user['idUsuario'],
                'nombre': user['nombre'],
                'correo': user['correo'],
                'rol': user['rol'],
                'especialidad': user['especialidad'],
                'telefono': user['telefono'],
                'rut': user['rut'],
                'estado': user['estado']
            }
            
            return {
                'status': 'success',
                'message': 'Token válido',
                'user': user_data,
                'token_expiry': payload['exp'],
                'status_code': 200
            }
            
        except Exception as e:
            logger.error(f"Error verificando token: {e}")
            return {
                'status': 'error',
                'message': 'Error verificando token',
                'status_code': 500
            }
    
    def handle_refresh_token(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera un nuevo access token usando un refresh token."""
        try:
            refresh_token = data.get('refresh_token')
            if not refresh_token:
                return {
                    'status': 'error',
                    'message': 'Refresh token no proporcionado',
                    'status_code': 400
                }
            
            # Verificar refresh token
            payload = self._verify_refresh_token(refresh_token)
            if not payload:
                return {
                    'status': 'error',
                    'message': 'Refresh token inválido o expirado',
                    'status_code': 401
                }
            
            user_id = payload['user_id']
            
            # Verificar que el usuario exista y esté activo
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            
            cursor.execute(
                """
                SELECT idUsuario, nombre, correo, rol, especialidad
                FROM Usuarios 
                WHERE idUsuario = %s AND estado = 'activo'
                """,
                (user_id,)
            )
            user = cursor.fetchone()
            
            cursor.close()
            db.close()
            
            if not user:
                return {
                    'status': 'error',
                    'message': 'Usuario no encontrado o inactivo',
                    'status_code': 401
                }
            
            # Generar nuevo access token
            access_token = self._generate_access_token(
                user_id=user['idUsuario'],
                email=user['correo'],
                nombre=user['nombre'],
                rol=user['rol']
            )
            
            # Opcionalmente, generar nuevo refresh token (rotación)
            new_refresh_token = self._generate_refresh_token(user['idUsuario'])
            
            return {
                'status': 'success',
                'message': 'Token refrescado exitosamente',
                'tokens': {
                    'access_token': access_token,
                    'refresh_token': new_refresh_token,
                    'expires_in': self.token_expiry_hours * 3600
                },
                'status_code': 200
            }
            
        except Exception as e:
            logger.error(f"Error refrescando token: {e}")
            return {
                'status': 'error',
                'message': 'Error refrescando token',
                'status_code': 500
            }
    
    def handle_change_password(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cambia la contraseña de un usuario."""
        try:
            # Validar campos requeridos
            required_fields = ['user_id', 'current_password', 'new_password']
            for field in required_fields:
                if field not in data:
                    return {
                        'status': 'error',
                        'message': f'Campo {field} es requerido',
                        'status_code': 400
                    }
            
            # Validar nueva contraseña
            password_error = self._validate_password(data['new_password'])
            if password_error:
                return {
                    'status': 'error',
                    'message': password_error,
                    'status_code': 400
                }
            
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            
            # Obtener usuario
            cursor.execute(
                "SELECT password_hash, estado FROM Usuarios WHERE idUsuario = %s",
                (data['user_id'],)
            )
            user = cursor.fetchone()
            
            if not user:
                cursor.close()
                db.close()
                return {
                    'status': 'error',
                    'message': 'Usuario no encontrado',
                    'status_code': 404
                }
            
            if user['estado'] == 'bloqueado':
                cursor.close()
                db.close()
                return {
                    'status': 'error',
                    'message': 'Usuario bloqueado',
                    'status_code': 403
                }
            
            # Verificar contraseña actual
            if not verify_password(data['current_password'], user['password_hash']):
                cursor.close()
                db.close()
                return {
                    'status': 'error',
                    'message': 'Contraseña actual incorrecta',
                    'status_code': 401
                }
            
            # Hashear nueva contraseña
            new_password_hash = hash_password(data['new_password'])
            
            # Actualizar contraseña
            cursor.execute(
                """
                UPDATE Usuarios 
                SET password_hash = %s, 
                    updated_at = NOW(),
                    intentos_fallidos = 0
                WHERE idUsuario = %s
                """,
                (new_password_hash, data['user_id'])
            )
            
            # Registrar actividad
            cursor.execute(
                """
                INSERT INTO ActividadUsuarios (usuarioId, accion, detalles)
                VALUES (%s, 'cambio_password', 'Contraseña cambiada exitosamente')
                """,
                (data['user_id'],)
            )
            
            db.commit()
            cursor.close()
            db.close()
            
            logger.info(f"Contraseña cambiada para usuario ID: {data['user_id']}")
            
            return {
                'status': 'success',
                'message': 'Contraseña cambiada exitosamente',
                'status_code': 200
            }
            
        except mysql.connector.Error as e:
            logger.error(f"Error cambiando contraseña: {e}")
            return {
                'status': 'error',
                'message': 'Error en el servidor de base de datos',
                'status_code': 500
            }
        except Exception as e:
            logger.error(f"Error interno cambiando contraseña: {e}")
            return {
                'status': 'error',
                'message': 'Error interno del servidor',
                'status_code': 500
            }
    
    def handle_logout(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Maneja logout de usuario (registra actividad)."""
        try:
            user_id = data.get('user_id')
            if not user_id:
                return {
                    'status': 'error',
                    'message': 'ID de usuario requerido',
                    'status_code': 400
                }
            
            # Verificar token si se proporciona
            token = data.get('token')
            if token:
                payload = self._verify_access_token(token)
                if not payload or payload['user_id'] != user_id:
                    return {
                        'status': 'error',
                        'message': 'Token inválido para este usuario',
                        'status_code': 401
                    }
            
            db = get_db_connection()
            cursor = db.cursor()
            
            # Registrar actividad de logout
            cursor.execute(
                """
                INSERT INTO ActividadUsuarios (usuarioId, accion, detalles)
                VALUES (%s, 'logout', 'Sesión cerrada')
                """,
                (user_id,)
            )
            
            db.commit()
            cursor.close()
            db.close()
            
            logger.info(f"Logout registrado para usuario ID: {user_id}")
            
            return {
                'status': 'success',
                'message': 'Sesión cerrada exitosamente',
                'status_code': 200
            }
            
        except Exception as e:
            logger.error(f"Error registrando logout: {e}")
            return {
                'status': 'error',
                'message': 'Error registrando logout',
                'status_code': 500
            }
    
    def handle_reset_password_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Solicita restablecimiento de contraseña."""
        try:
            email = data.get('email')
            if not email:
                return {
                    'status': 'error',
                    'message': 'Correo electrónico requerido',
                    'status_code': 400
                }
            
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            
            # Verificar si el usuario existe
            cursor.execute(
                """
                SELECT idUsuario, nombre, correo, estado
                FROM Usuarios 
                WHERE correo = %s AND estado = 'activo'
                """,
                (email.lower(),)
            )
            user = cursor.fetchone()
            
            if not user:
                cursor.close()
                db.close()
                # Por seguridad, no revelamos si el usuario existe
                logger.info(f"Solicitud de reset password para email no registrado: {email}")
                return {
                    'status': 'success',
                    'message': 'Si el email existe en nuestro sistema, recibirá instrucciones',
                    'status_code': 200
                }
            
            # Generar token de restablecimiento
            reset_token = self._generate_reset_token(user['idUsuario'])
            reset_token_expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            
            # Guardar token en base de datos
            cursor.execute(
                """
                INSERT INTO ResetTokens 
                (usuarioId, token, expira_en, utilizado)
                VALUES (%s, %s, %s, 0)
                ON DUPLICATE KEY UPDATE
                token = VALUES(token),
                expira_en = VALUES(expira_en),
                utilizado = 0,
                created_at = NOW()
                """,
                (user['idUsuario'], reset_token, reset_token_expiry)
            )
            
            # Registrar actividad
            cursor.execute(
                """
                INSERT INTO ActividadUsuarios (usuarioId, accion, detalles)
                VALUES (%s, 'solicitud_reset_password', 'Solicitud de restablecimiento de contraseña')
                """,
                (user['idUsuario'],)
            )
            
            db.commit()
            cursor.close()
            db.close()
            
            # En un sistema real, aquí enviaríamos un email
            # Por ahora, solo logueamos
            logger.info(f"Token de reset generado para {email}: {reset_token}")
            
            return {
                'status': 'success',
                'message': 'Si el email existe en nuestro sistema, recibirá instrucciones',
                'reset_token': reset_token,  # En producción, no enviarías esto
                'status_code': 200
            }
            
        except Exception as e:
            logger.error(f"Error solicitando reset password: {e}")
            return {
                'status': 'error',
                'message': 'Error procesando solicitud',
                'status_code': 500
            }
    
    def handle_reset_password(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Restablece la contraseña usando un token."""
        try:
            token = data.get('token')
            new_password = data.get('new_password')
            
            if not token or not new_password:
                return {
                    'status': 'error',
                    'message': 'Token y nueva contraseña requeridos',
                    'status_code': 400
                }
            
            # Validar nueva contraseña
            password_error = self._validate_password(new_password)
            if password_error:
                return {
                    'status': 'error',
                    'message': password_error,
                    'status_code': 400
                }
            
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            
            # Verificar token
            cursor.execute(
                """
                SELECT rt.id, rt.usuarioId, rt.expira_en, rt.utilizado, u.estado
                FROM ResetTokens rt
                JOIN Usuarios u ON rt.usuarioId = u.idUsuario
                WHERE rt.token = %s AND rt.utilizado = 0
                """,
                (token,)
            )
            token_record = cursor.fetchone()
            
            if not token_record:
                cursor.close()
                db.close()
                return {
                    'status': 'error',
                    'message': 'Token inválido o ya utilizado',
                    'status_code': 400
                }
            
            # Verificar expiración
            if token_record['expira_en'] < datetime.datetime.utcnow():
                cursor.close()
                db.close()
                return {
                    'status': 'error',
                    'message': 'Token expirado',
                    'status_code': 400
                }
            
            if token_record['estado'] == 'bloqueado':
                cursor.close()
                db.close()
                return {
                    'status': 'error',
                    'message': 'Usuario bloqueado',
                    'status_code': 403
                }
            
            # Hashear nueva contraseña
            new_password_hash = hash_password(new_password)
            
            # Actualizar contraseña
            cursor.execute(
                """
                UPDATE Usuarios 
                SET password_hash = %s, 
                    updated_at = NOW(),
                    intentos_fallidos = 0
                WHERE idUsuario = %s
                """,
                (new_password_hash, token_record['usuarioId'])
            )
            
            # Marcar token como utilizado
            cursor.execute(
                "UPDATE ResetTokens SET utilizado = 1 WHERE id = %s",
                (token_record['id'],)
            )
            
            # Registrar actividad
            cursor.execute(
                """
                INSERT INTO ActividadUsuarios (usuarioId, accion, detalles)
                VALUES (%s, 'reset_password', 'Contraseña restablecida exitosamente')
                """,
                (token_record['usuarioId'],)
            )
            
            db.commit()
            cursor.close()
            db.close()
            
            logger.info(f"Contraseña restablecida para usuario ID: {token_record['usuarioId']}")
            
            return {
                'status': 'success',
                'message': 'Contraseña restablecida exitosamente',
                'status_code': 200
            }
            
        except Exception as e:
            logger.error(f"Error restableciendo contraseña: {e}")
            return {
                'status': 'error',
                'message': 'Error restableciendo contraseña',
                'status_code': 500
            }
    
    # Métodos auxiliares
    
    def _validate_registration_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida los datos de registro."""
        required_fields = ['nombre', 'rut', 'correo', 'password']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return {
                'valid': False,
                'message': f'Campos requeridos faltantes: {", ".join(missing_fields)}'
            }
        
        # Validar email
        if not self._validate_email(data['correo']):
            return {
                'valid': False,
                'message': 'Formato de correo electrónico inválido'
            }
        
        # Validar RUT (formato simple)
        if not self._validate_rut(data['rut']):
            return {
                'valid': False,
                'message': 'Formato de RUT inválido. Use formato: 12345678-9'
            }
        
        # Validar contraseña
        password_error = self._validate_password(data['password'])
        if password_error:
            return {
                'valid': False,
                'message': password_error
            }
        
        return {'valid': True, 'message': 'Datos válidos'}
    
    def _validate_email(self, email: str) -> bool:
        """Valida formato de email."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _validate_rut(self, rut: str) -> bool:
        """Valida formato básico de RUT."""
        pattern = r'^\d{7,8}-[\dkK]$'
        return re.match(pattern, rut) is not None
    
    def _validate_password(self, password: str) -> Optional[str]:
        """Valida fortaleza de contraseña."""
        if len(password) < 8:
            return 'La contraseña debe tener al menos 8 caracteres'
        
        if not any(c.isupper() for c in password):
            return 'La contraseña debe tener al menos una letra mayúscula'
        
        if not any(c.islower() for c in password):
            return 'La contraseña debe tener al menos una letra minúscula'
        
        if not any(c.isdigit() for c in password):
            return 'La contraseña debe tener al menos un número'
        
        return None
    
    def _determine_user_role(self, data: Dict[str, Any]) -> str:
        """Determina el rol del usuario basado en los datos."""
        # Por defecto, los usuarios se registran como pacientes
        rol = 'paciente'
        
        # Si se especifica un rol válido y hay autorización
        if 'rol' in data and data['rol'] in ['medico', 'administrativo']:
            # En un sistema real, aquí verificaríamos autorización
            # Por ahora, solo permitimos registros directos como pacientes
            pass
        
        return rol
    
    def _generate_access_token(self, user_id: int, email: str, nombre: str, rol: str) -> str:
        """Genera un token JWT de acceso."""
        payload = {
            'user_id': user_id,
            'email': email,
            'nombre': nombre,
            'rol': rol,
            'type': 'access',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=self.token_expiry_hours),
            'iat': datetime.datetime.utcnow()
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def _generate_refresh_token(self, user_id: int) -> str:
        """Genera un token JWT de refresh."""
        payload = {
            'user_id': user_id,
            'type': 'refresh',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=self.refresh_token_expiry_days),
            'iat': datetime.datetime.utcnow()
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def _generate_reset_token(self, user_id: int) -> str:
        """Genera un token para restablecimiento de contraseña."""
        import secrets
        import hashlib
        
        # Generar token seguro
        random_bytes = secrets.token_bytes(32)
        timestamp = str(datetime.datetime.utcnow().timestamp()).encode()
        user_bytes = str(user_id).encode()
        
        # Combinar y hashear
        combined = random_bytes + timestamp + user_bytes
        token = hashlib.sha256(combined).hexdigest()
        
        return token
    
    def _verify_access_token(self, token: str) -> Optional[Dict]:
        """Verifica un token JWT de acceso."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            # Verificar tipo de token
            if payload.get('type') != 'access':
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token de acceso expirado")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Token de acceso inválido")
            return None
    
    def _verify_refresh_token(self, token: str) -> Optional[Dict]:
        """Verifica un token JWT de refresh."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            # Verificar tipo de token
            if payload.get('type') != 'refresh':
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token de refresh expirado")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Token de refresh inválido")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Obtiene un usuario por ID."""
        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            
            cursor.execute(
                """
                SELECT idUsuario, nombre, correo, rol, especialidad, estado, telefono, rut
                FROM Usuarios 
                WHERE idUsuario = %s
                """,
                (user_id,)
            )
            user = cursor.fetchone()
            
            cursor.close()
            db.close()
            
            return user
            
        except Exception as e:
            logger.error(f"Error obteniendo usuario {user_id}: {e}")
            return None
