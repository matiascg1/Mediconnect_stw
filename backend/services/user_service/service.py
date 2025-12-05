"""
Servicio de gestión de usuarios para MediConnect.
Maneja operaciones CRUD de usuarios, perfiles y roles.
"""
import mysql.connector
from typing import Dict, Any, List, Optional
from database.connection import get_db_connection
from utils.logger import get_logger
from utils.validators import validate_rut, validate_phone, validate_email
from utils.formatters import format_rut, format_phone

logger = get_logger(__name__)

class UserService:
    """Servicio de gestión de usuarios."""
    
    def __init__(self):
        self.bus_client = None
    
    def set_bus_client(self, bus_client):
        """Configura el cliente del bus."""
        self.bus_client = bus_client
    
    def handle_get_user_by_id(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene un usuario por ID."""
        try:
            user_id = data.get('user_id')
            if not user_id:
                return {
                    'status': 'error',
                    'message': 'ID de usuario requerido',
                    'status_code': 400
                }
            
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            
            cursor.execute(
                """
                SELECT 
                    idUsuario, nombre, rut, correo, telefono, rol, especialidad, 
                    estado, created_at, updated_at, ultimo_login
                FROM Usuarios 
                WHERE idUsuario = %s
                """,
                (user_id,)
            )
            user = cursor.fetchone()
            
            cursor.close()
            db.close()
            
            if not user:
                return {
                    'status': 'error',
                    'message': 'Usuario no encontrado',
                    'status_code': 404
                }
            
            # Formatear datos para respuesta
            formatted_user = self._format_user_data(user)
            
            return {
                'status': 'success',
                'data': formatted_user,
                'status_code': 200
            }
            
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos obteniendo usuario: {e}")
            return {
                'status': 'error',
                'message': 'Error en el servidor de base de datos',
                'status_code': 500
            }
        except Exception as e:
            logger.error(f"Error interno obteniendo usuario: {e}")
            return {
                'status': 'error',
                'message': 'Error interno del servidor',
                'status_code': 500
            }
    
    def handle_get_all_users(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene todos los usuarios con paginación y filtros."""
        try:
            # Parámetros de paginación
            page = int(data.get('page', 1))
            limit = int(data.get('limit', 50))
            role_filter = data.get('role')
            status_filter = data.get('status')
            search = data.get('search', '').strip()
            
            # Validar parámetros
            if page < 1:
                page = 1
            if limit < 1 or limit > 100:
                limit = 50
            
            # Calcular offset
            offset = (page - 1) * limit
            
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            
            # Construir query base
            query = """
                SELECT 
                    idUsuario, nombre, rut, correo, telefono, rol, especialidad, 
                    estado, created_at, ultimo_login
                FROM Usuarios 
                WHERE 1=1
            """
            params = []
            
            # Aplicar filtros
            if role_filter:
                query += " AND rol = %s"
                params.append(role_filter)
            
            if status_filter:
                query += " AND estado = %s"
                params.append(status_filter)
            
            if search:
                search_term = f"%{search}%"
                query += " AND (nombre LIKE %s OR correo LIKE %s OR rut LIKE %s OR telefono LIKE %s)"
                params.extend([search_term, search_term, search_term, search_term])
            
            # Contar total
            count_query = query.replace(
                "SELECT idUsuario, nombre, rut, correo, telefono, rol, especialidad, estado, created_at, ultimo_login",
                "SELECT COUNT(*) as total"
            )
            
            cursor.execute(count_query, params)
            total_result = cursor.fetchone()
            total = total_result['total'] if total_result else 0
            
            # Aplicar ordenamiento y paginación
            query += " ORDER BY nombre, created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            users = cursor.fetchall()
            
            cursor.close()
            db.close()
            
            # Formatear usuarios
            formatted_users = [self._format_user_data(user) for user in users]
            
            return {
                'status': 'success',
                'data': formatted_users,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit if limit > 0 else 0
                },
                'status_code': 200
            }
            
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos obteniendo usuarios: {e}")
            return {
                'status': 'error',
                'message': 'Error en el servidor de base de datos',
                'status_code': 500
            }
        except Exception as e:
            logger.error(f"Error interno obteniendo usuarios: {e}")
            return {
                'status': 'error',
                'message': 'Error interno del servidor',
                'status_code': 500
            }
    
    def handle_update_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza un usuario."""
        try:
            user_id = data.get('user_id')
            if not user_id:
                return {
                    'status': 'error',
                    'message': 'ID de usuario requerido',
                    'status_code': 400
                }
            
            # Validar campos actualizables
            update_fields = []
            update_values = []
            
            # Campos básicos
            if 'nombre' in data:
                nombre = data['nombre'].strip()
                if not nombre:
                    return {
                        'status': 'error',
                        'message': 'Nombre no puede estar vacío',
                        'status_code': 400
                    }
                update_fields.append("nombre = %s")
                update_values.append(nombre)
            
            if 'telefono' in data:
                telefono = data['telefono'].strip()
                if telefono and not validate_phone(telefono):
                    return {
                        'status': 'error',
                        'message': 'Formato de teléfono inválido',
                        'status_code': 400
                    }
                update_fields.append("telefono = %s")
                update_values.append(format_phone(telefono) if telefono else '')
            
            # Campos específicos de rol
            if 'especialidad' in data:
                # Verificar que sea médico
                db_check = get_db_connection()
                cursor_check = db_check.cursor(dictionary=True)
                cursor_check.execute("SELECT rol FROM Usuarios WHERE idUsuario = %s", (user_id,))
                user_check = cursor_check.fetchone()
                cursor_check.close()
                db_check.close()
                
                if user_check and user_check['rol'] == 'medico':
                    especialidad = data['especialidad'].strip()
                    if not especialidad:
                        return {
                            'status': 'error',
                            'message': 'Especialidad no puede estar vacía para médicos',
                            'status_code': 400
                        }
                    update_fields.append("especialidad = %s")
                    update_values.append(especialidad)
                elif data['especialidad']:
                    # Si no es médico pero se intenta asignar especialidad
                    return {
                        'status': 'error',
                        'message': 'Solo los médicos pueden tener especialidad',
                        'status_code': 400
                    }
            
            # Campos administrativos
            if 'estado' in data:
                if data['estado'] not in ['activo', 'bloqueado']:
                    return {
                        'status': 'error',
                        'message': 'Estado inválido. Use: activo o bloqueado',
                        'status_code': 400
                    }
                update_fields.append("estado = %s")
                update_values.append(data['estado'])
            
            if 'rol' in data:
                if data['rol'] not in ['paciente', 'medico', 'administrativo']:
                    return {
                        'status': 'error',
                        'message': 'Rol inválido',
                        'status_code': 400
                    }
                update_fields.append("rol = %s")
                update_values.append(data['rol'])
                
                # Si cambia a médico y no tiene especialidad, usar default
                if data['rol'] == 'medico' and 'especialidad' not in data:
                    # Verificar si ya tiene especialidad
                    db_check = get_db_connection()
                    cursor_check = db_check.cursor(dictionary=True)
                    cursor_check.execute(
                        "SELECT especialidad FROM Usuarios WHERE idUsuario = %s",
                        (user_id,)
                    )
                    user_data = cursor_check.fetchone()
                    cursor_check.close()
                    db_check.close()
                    
                    if not user_data or not user_data['especialidad']:
                        update_fields.append("especialidad = %s")
                        update_values.append('Medicina General')
            
            if not update_fields:
                return {
                    'status': 'error',
                    'message': 'No hay campos para actualizar',
                    'status_code': 400
                }
            
            # Agregar user_id al final para WHERE
            update_values.append(user_id)
            
            db = get_db_connection()
            cursor = db.cursor()
            
            query = f"""
                UPDATE Usuarios 
                SET {', '.join(update_fields)}, updated_at = NOW()
                WHERE idUsuario = %s
            """
            
            cursor.execute(query, update_values)
            db.commit()
            
            affected_rows = cursor.rowcount
            
            if affected_rows > 0:
                # Registrar actividad
                cursor.execute(
                    """
                    INSERT INTO ActividadUsuarios (usuarioId, accion, detalles)
                    VALUES (%s, 'actualizacion_perfil', 'Perfil actualizado')
                    """,
                    (user_id,)
                )
                db.commit()
            
            cursor.close()
            db.close()
            
            if affected_rows == 0:
                return {
                    'status': 'error',
                    'message': 'Usuario no encontrado',
                    'status_code': 404
                }
            
            logger.info(f"Usuario actualizado: ID {user_id}")
            
            return {
                'status': 'success',
                'message': 'Usuario actualizado exitosamente',
                'status_code': 200
            }
            
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos actualizando usuario: {e}")
            return {
                'status': 'error',
                'message': 'Error en el servidor de base de datos',
                'status_code': 500
            }
        except Exception as e:
            logger.error(f"Error interno actualizando usuario: {e}")
            return {
                'status': 'error',
                'message': 'Error interno del servidor',
                'status_code': 500
            }
    
    def handle_delete_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina (desactiva) un usuario."""
        try:
            user_id = data.get('user_id')
            if not user_id:
                return {
                    'status': 'error',
                    'message': 'ID de usuario requerido',
                    'status_code': 400
                }
            
            db = get_db_connection()
            cursor = db.cursor()
            
            # En lugar de eliminar, cambiamos el estado a bloqueado
            cursor.execute(
                """
                UPDATE Usuarios 
                SET estado = 'bloqueado', updated_at = NOW()
                WHERE idUsuario = %s AND estado != 'bloqueado'
                """,
                (user_id,)
            )
            
            db.commit()
            affected_rows = cursor.rowcount
            
            if affected_rows > 0:
                # Registrar actividad
                cursor.execute(
                    """
                    INSERT INTO ActividadUsuarios (usuarioId, accion, detalles)
                    VALUES (%s, 'desactivacion_cuenta', 'Cuenta desactivada/bloqueada')
                    """,
                    (user_id,)
                )
                db.commit()
            
            cursor.close()
            db.close()
            
            if affected_rows == 0:
                # Verificar si el usuario existe
                db_check = get_db_connection()
                cursor_check = db_check.cursor(dictionary=True)
                cursor_check.execute(
                    "SELECT idUsuario FROM Usuarios WHERE idUsuario = %s",
                    (user_id,)
                )
                exists = cursor_check.fetchone()
                cursor_check.close()
                db_check.close()
                
                if not exists:
                    return {
                        'status': 'error',
                        'message': 'Usuario no encontrado',
                        'status_code': 404
                    }
                else:
                    return {
                        'status': 'error',
                        'message': 'El usuario ya está bloqueado',
                        'status_code': 400
                    }
            
            logger.info(f"Usuario bloqueado/desactivado: ID {user_id}")
            
            return {
                'status': 'success',
                'message': 'Usuario bloqueado/desactivado exitosamente',
                'status_code': 200
            }
            
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos eliminando usuario: {e}")
            return {
                'status': 'error',
                'message': 'Error en el servidor de base de datos',
                'status_code': 500
            }
        except Exception as e:
            logger.error(f"Error interno eliminando usuario: {e}")
            return {
                'status': 'error',
                'message': 'Error interno del servidor',
                'status_code': 500
            }
    
    def handle_activate_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Activa un usuario previamente bloqueado."""
        try:
            user_id = data.get('user_id')
            if not user_id:
                return {
                    'status': 'error',
                    'message': 'ID de usuario requerido',
                    'status_code': 400
                }
            
            db = get_db_connection()
            cursor = db.cursor()
            
            cursor.execute(
                """
                UPDATE Usuarios 
                SET estado = 'activo', 
                    intentos_fallidos = 0,
                    updated_at = NOW()
                WHERE idUsuario = %s AND estado = 'bloqueado'
                """,
                (user_id,)
            )
            
            db.commit()
            affected_rows = cursor.rowcount
            
            if affected_rows > 0:
                # Registrar actividad
                cursor.execute(
                    """
                    INSERT INTO ActividadUsuarios (usuarioId, accion, detalles)
                    VALUES (%s, 'activacion_cuenta', 'Cuenta activada')
                    """,
                    (user_id,)
                )
                db.commit()
            
            cursor.close()
            db.close()
            
            if affected_rows == 0:
                # Verificar si el usuario existe
                db_check = get_db_connection()
                cursor_check = db_check.cursor(dictionary=True)
                cursor_check.execute(
                    "SELECT idUsuario, estado FROM Usuarios WHERE idUsuario = %s",
                    (user_id,)
                )
                user = cursor_check.fetchone()
                cursor_check.close()
                db_check.close()
                
                if not user:
                    return {
                        'status': 'error',
                        'message': 'Usuario no encontrado',
                        'status_code': 404
                    }
                elif user['estado'] != 'bloqueado':
                    return {
                        'status': 'error',
                        'message': 'El usuario no está bloqueado',
                        'status_code': 400
                    }
            
            logger.info(f"Usuario activado: ID {user_id}")
            
            return {
                'status': 'success',
                'message': 'Usuario activado exitosamente',
                'status_code': 200
            }
            
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos activando usuario: {e}")
            return {
                'status': 'error',
                'message': 'Error en el servidor de base de datos',
                'status_code': 500
            }
        except Exception as e:
            logger.error(f"Error interno activando usuario: {e}")
            return {
                'status': 'error',
                'message': 'Error interno del servidor',
                'status_code': 500
            }
    
    def handle_get_doctors(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene todos los médicos activos."""
        try:
            # Parámetros opcionales
            especialidad = data.get('especialidad')
            search = data.get('search', '').strip()
            
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            
            # Construir query
            query = """
                SELECT 
                    idUsuario, nombre, rut, correo, telefono, especialidad, 
                    created_at, ultimo_login
                FROM Usuarios 
                WHERE rol = 'medico' AND estado = 'activo'
            """
            params = []
            
            # Aplicar filtros
            if especialidad:
                query += " AND especialidad = %s"
                params.append(especialidad)
            
            if search:
                search_term = f"%{search}%"
                query += " AND (nombre LIKE %s OR especialidad LIKE %s)"
                params.extend([search_term, search_term])
            
            query += " ORDER BY nombre"
            
            cursor.execute(query, params)
            doctors = cursor.fetchall()
            
            cursor.close()
            db.close()
            
            # Formatear médicos
            formatted_doctors = []
            for doctor in doctors:
                formatted_doctors.append({
                    'id': doctor['idUsuario'],
                    'nombre': doctor['nombre'],
                    'especialidad': doctor['especialidad'],
                    'correo': doctor['correo'],
                    'telefono': doctor['telefono'],
                    'rut': format_rut(doctor['rut']),
                    'last_login': doctor['ultimo_login'].isoformat() if doctor['ultimo_login'] else None
                })
            
            return {
                'status': 'success',
                'data': formatted_doctors,
                'count': len(formatted_doctors),
                'status_code': 200
            }
            
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo médicos: {e}")
            return {
                'status': 'error',
                'message': 'Error en el servidor de base de datos',
                'status_code': 500
            }
        except Exception as e:
            logger.error(f"Error interno obteniendo médicos: {e}")
            return {
                'status': 'error',
                'message': 'Error interno del servidor',
                'status_code': 500
            }
    
    def handle_get_user_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene estadísticas de usuarios."""
        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            
            # Total por rol
            cursor.execute(
                """
                SELECT rol, COUNT(*) as count 
                FROM Usuarios 
                WHERE estado = 'activo'
                GROUP BY rol
                """
            )
            role_stats = cursor.fetchall()
            
            # Usuarios nuevos últimos 7 días
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as new_users,
                    DATE(created_at) as date
                FROM Usuarios 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                GROUP BY DATE(created_at)
                ORDER BY date DESC
                """
            )
            new_users_by_day = cursor.fetchall()
            
            # Usuarios activos (login últimas 24h, 7d, 30d)
            cursor.execute(
                """
                SELECT 
                    COUNT(CASE WHEN ultimo_login >= DATE_SUB(NOW(), INTERVAL 24 HOUR) THEN 1 END) as active_24h,
                    COUNT(CASE WHEN ultimo_login >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 END) as active_7d,
                    COUNT(CASE WHEN ultimo_login >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 END) as active_30d
                FROM Usuarios 
                WHERE estado = 'activo'
                """
            )
            active_stats = cursor.fetchone()
            
            # Crecimiento mensual
            cursor.execute(
                """
                SELECT 
                    YEAR(created_at) as year,
                    MONTH(created_at) as month,
                    COUNT(*) as new_users
                FROM Usuarios 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
                GROUP BY YEAR(created_at), MONTH(created_at)
                ORDER BY year DESC, month DESC
                LIMIT 6
                """
            )
            monthly_growth = cursor.fetchall()
            
            cursor.close()
            db.close()
            
            # Preparar estadísticas
            stats = {
                'by_role': {stat['rol']: stat['count'] for stat in role_stats},
                'active_users': {
                    'last_24h': active_stats['active_24h'] if active_stats else 0,
                    'last_7d': active_stats['active_7d'] if active_stats else 0,
                    'last_30d': active_stats['active_30d'] if active_stats else 0
                },
                'new_users': {
                    'last_7d': new_users_by_day,
                    'total_7d': sum(day['new_users'] for day in new_users_by_day)
                },
                'monthly_growth': monthly_growth,
                'total': sum(stat['count'] for stat in role_stats)
            }
            
            return {
                'status': 'success',
                'data': stats,
                'status_code': 200
            }
            
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {
                'status': 'error',
                'message': 'Error en el servidor de base de datos',
                'status_code': 500
            }
        except Exception as e:
            logger.error(f"Error interno obteniendo estadísticas: {e}")
            return {
                'status': 'error',
                'message': 'Error interno del servidor',
                'status_code': 500
            }
    
    def handle_get_user_activity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene actividad reciente de un usuario."""
        try:
            user_id = data.get('user_id')
            limit = int(data.get('limit', 50))
            
            if not user_id:
                return {
                    'status': 'error',
                    'message': 'ID de usuario requerido',
                    'status_code': 400
                }
            
            if limit < 1 or limit > 100:
                limit = 50
            
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            
            # Verificar que el usuario existe
            cursor.execute(
                "SELECT idUsuario FROM Usuarios WHERE idUsuario = %s",
                (user_id,)
            )
            if not cursor.fetchone():
                cursor.close()
                db.close()
                return {
                    'status': 'error',
                    'message': 'Usuario no encontrado',
                    'status_code': 404
                }
            
            # Obtener actividad
            cursor.execute(
                """
                SELECT 
                    idActividad, accion, detalles, created_at
                FROM ActividadUsuarios 
                WHERE usuarioId = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (user_id, limit)
            )
            activities = cursor.fetchall()
            
            cursor.close()
            db.close()
            
            # Formatear actividades
            formatted_activities = []
            for activity in activities:
                formatted_activities.append({
                    'id': activity['idActividad'],
                    'action': activity['accion'],
                    'details': activity['detalles'],
                    'timestamp': activity['created_at'].isoformat() if activity['created_at'] else None
                })
            
            return {
                'status': 'success',
                'data': formatted_activities,
                'count': len(formatted_activities),
                'status_code': 200
            }
            
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo actividad: {e}")
            return {
                'status': 'error',
                'message': 'Error en el servidor de base de datos',
                'status_code': 500
            }
        except Exception as e:
            logger.error(f"Error interno obteniendo actividad: {e}")
            return {
                'status': 'error',
                'message': 'Error interno del servidor',
                'status_code': 500
            }
    
    def handle_search_users(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Busca usuarios por diferentes criterios."""
        try:
            search_term = data.get('search', '').strip()
            role = data.get('role')
            limit = int(data.get('limit', 20))
            
            if not search_term:
                return {
                    'status': 'error',
                    'message': 'Término de búsqueda requerido',
                    'status_code': 400
                }
            
            if limit < 1 or limit > 50:
                limit = 20
            
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            
            # Construir query
            query = """
                SELECT 
                    idUsuario, nombre, rut, correo, telefono, rol, especialidad, estado
                FROM Usuarios 
                WHERE (nombre LIKE %s OR correo LIKE %s OR rut LIKE %s OR telefono LIKE %s)
                    AND estado = 'activo'
            """
            search_pattern = f"%{search_term}%"
            params = [search_pattern, search_pattern, search_pattern, search_pattern]
            
            if role:
                query += " AND rol = %s"
                params.append(role)
            
            query += " ORDER BY nombre LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            users = cursor.fetchall()
            
            cursor.close()
            db.close()
            
            # Formatear resultados
            formatted_users = []
            for user in users:
                formatted_users.append({
                    'id': user['idUsuario'],
                    'nombre': user['nombre'],
                    'correo': user['correo'],
                    'telefono': user['telefono'],
                    'rol': user['rol'],
                    'especialidad': user['especialidad'],
                    'rut': format_rut(user['rut'])
                })
            
            return {
                'status': 'success',
                'data': formatted_users,
                'count': len(formatted_users),
                'status_code': 200
            }
            
        except mysql.connector.Error as e:
            logger.error(f"Error buscando usuarios: {e}")
            return {
                'status': 'error',
                'message': 'Error en el servidor de base de datos',
                'status_code': 500
            }
        except Exception as e:
            logger.error(f"Error interno buscando usuarios: {e}")
            return {
                'status': 'error',
                'message': 'Error interno del servidor',
                'status_code': 500
            }
    
    def _format_user_data(self, user: Dict) -> Dict:
        """Formatea los datos del usuario para la respuesta."""
        return {
            'id': user['idUsuario'],
            'nombre': user['nombre'],
            'rut': format_rut(user['rut']),
            'correo': user['correo'],
            'telefono': format_phone(user['telefono']) if user['telefono'] else None,
            'rol': user['rol'],
            'especialidad': user['especialidad'],
            'estado': user['estado'],
            'created_at': user['created_at'].isoformat() if user['created_at'] else None,
            'updated_at': user['updated_at'].isoformat() if 'updated_at' in user and user['updated_at'] else None,
            'last_login': user['ultimo_login'].isoformat() if user['ultimo_login'] else None
        }
