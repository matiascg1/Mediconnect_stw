"""
Servicio de gestión de citas médicas para MediConnect.
Maneja agenda, disponibilidad, confirmación y cancelación de citas.
"""
import mysql.connector
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from database.connection import get_db_connection
from utils.logger import get_logger
from utils.formatters import format_datetime

logger = get_logger(__name__)

class AppointmentService:
    """Servicio de gestión de citas médicas."""
    
    def __init__(self):
        self.bus_client = None
    
    def set_bus_client(self, bus_client):
        """Configura el cliente del bus."""
        self.bus_client = bus_client
    
    def handle_create_appointment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una nueva cita médica."""
        try:
            # Validar campos requeridos
            required_fields = ['pacienteId', 'medicoId', 'fechaHora']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return {
                    'status': 'error',
                    'message': f'Campos requeridos faltantes: {", ".join(missing_fields)}',
                    'status_code': 400
                }
            
            # Validar IDs
            paciente_id = data['pacienteId']
            medico_id = data['medicoId']
            
            if not isinstance(paciente_id, int) or paciente_id <= 0:
                return {
                    'status': 'error',
                    'message': 'ID de paciente inválido',
                    'status_code': 400
                }
            
            if not isinstance(medico_id, int) or medico_id <= 0:
                return {
                    'status': 'error',
                    'message': 'ID de médico inválido',
                    'status_code': 400
                }
            
            # Parsear fecha y hora
            try:
                fecha_hora = datetime.fromisoformat(data['fechaHora'].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                return {
                    'status': 'error',
                    'message': 'Formato de fecha inválido. Use ISO 8601',
                    'status_code': 400
                }
            
            # Validar que la fecha no sea en el pasado
            if fecha_hora < datetime.now():
                return {
                    'status': 'error',
                    'message': 'No se pueden agendar citas en el pasado',
                    'status_code': 400
                }
            
            # Validar que la fecha no sea muy lejana (máximo 3 meses)
            max_future_date = datetime.now() + timedelta(days=90)
            if fecha_hora > max_future_date:
                return {
                    'status': 'error',
                    'message': 'No se pueden agendar citas con más de 3 meses de anticipación',
                    'status_code': 400
                }
            
            # Validar horario de trabajo (8:00 - 18:00)
            hora = fecha_hora.time()
            if hora < datetime.strptime('08:00', '%H:%M').time() or hora > datetime.strptime('18:00', '%H:%M').time():
                return {
                    'status': 'error',
                    'message': 'Horario fuera del horario de trabajo (8:00 - 18:00)',
                    'status_code': 400
                }
            
            # Validar que sea en intervalos de 30 minutos
            if hora.minute not in [0, 30]:
                return {
                    'status': 'error',
                    'message': 'Las citas deben ser en intervalos de 30 minutos (en punto o y media)',
                    'status_code': 400
                }
            
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            
            # Verificar que el paciente existe y está activo
            cursor.execute(
                """
                SELECT idUsuario, nombre, estado 
                FROM Usuarios 
                WHERE idUsuario = %s AND rol = 'paciente'
                """,
                (paciente_id,)
            )
            paciente = cursor.fetchone()
            
            if not paciente:
                cursor.close()
                db.close()
                return {
                    'status': 'error',
                    'message': 'Paciente no encontrado',
                    'status_code': 404
                }
            
            if paciente['estado'] != 'activo':
                cursor.close()
                db.close()
                return {
                    'status': 'error',
                    'message': 'Paciente no está activo',
                    'status_code': 400
                }
            
            # Verificar que el médico existe, está activo y es médico
            cursor.execute(
                """
                SELECT idUsuario, nombre, especialidad, estado 
                FROM Usuarios 
                WHERE idUsuario = %s AND rol = 'medico'
                """,
                (medico_id,)
            )
            medico = cursor.fetchone()
            
            if not medico:
                cursor.close()
                db.close()
                return {
                    'status': 'error',
                    'message': 'Médico no encontrado',
                    'status_code': 404
                }
            
            if medico['estado'] != 'activo':
                cursor.close()
                db.close()
                return {
                    'status': 'error',
                    'message': 'Médico no está activo',
                    'status_code': 400
                }
            
            # Verificar disponibilidad del médico
            cursor.execute(
                """
                SELECT idCita 
                FROM Citas 
                WHERE medicoId = %s 
                  AND fechaHora = %s 
                  AND estado IN ('agendada', 'confirmada')
                """,
                (medico_id, fecha_hora)
            )
            
            existing_appointment = cursor.fetchone()
            if existing_appointment:
                cursor.close()
                db.close()
                return {
                    'status': 'error',
                    'message': 'El médico no está disponible en ese horario',
                    'status_code': 409
                }
            
            # Verificar que el paciente no tenga otra cita a la misma hora
            cursor.execute(
                """
                SELECT idCita 
                FROM Citas 
                WHERE pacienteId = %s 
                  AND fechaHora = %s 
                  AND estado IN ('agendada', 'confirmada')
                """,
                (paciente_id, fecha_hora)
            )
            
            paciente_busy = cursor.fetchone()
            if paciente_busy:
                cursor.close()
                db.close()
                return {
                    'status': 'error',
                    'message': 'Ya tienes una cita agendada para ese horario',
                    'status_code': 409
                }
            
            # Crear la cita
            motivo = data.get('motivo', 'Consulta médica')
            
            cursor.execute(
                """
                INSERT INTO Citas (pacienteId, medicoId, fechaHora, motivo, estado)
                VALUES (%s, %s, %s, %s, 'agendada')
                """,
                (
                    paciente_id,
                    medico_id,
                    fecha_hora,
                    motivo[:200]  # Limitar a 200 caracteres
                )
            )
            
            appointment_id = cursor.lastrowid
            
            # Registrar actividad
            cursor.execute(
                """
                INSERT INTO ActividadCitas (citaId, accion, detalles)
                VALUES (%s, 'creacion', %s)
                """,
                (appointment_id, f"Cita creada para {fecha_hora}")
            )
            
            db.commit()
            cursor.close()
            db.close()
            
            logger.info(f"Cita creada: ID {appointment_id}, Paciente {paciente_id}, Médico {medico_id}, {fecha_hora}")
            
            # Notificar a otros servicios (si hubiera servicio de notificaciones)
            # self._notify_appointment_created(appointment_id, paciente_id, medico_id)
            
            return {
                'status': 'success',
                'message': 'Cita creada exitosamente',
                'cita_id': appointment_id,
                'fecha_hora': fecha_hora.isoformat(),
                'status_code': 201
            }
            
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos creando cita: {e}")
            return {
                'status': 'error',
                'message': 'Error en el servidor de base de datos',
                'status_code': 500
            }
        except Exception as e:
            logger.error(f"Error interno creando cita: {e}")
            return {
                'status': 'error',
                'message': 'Error interno del servidor',
                'status_code': 500
            }
    
    def handle_get_appointments_by_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene citas por usuario (paciente o médico)."""
        try:
            user_id = data.get('user_id')
            user_type = data.get('user_type', 'paciente')  # 'paciente' o 'medico'
            estado_filter = data.get('estado')
            fecha_desde = data.get('fecha_desde')
            fecha_hasta = data.get('fecha_hasta')
            
            if not user_id:
                return {
                    'status': 'error',
                    'message': 'ID de usuario requerido',
                    'status_code': 400
                }
            
            # Parsear fechas si se proporcionan
            fecha_desde_dt = None
            fecha_hasta_dt = None
            
            if fecha_desde:
                try:
                    fecha_desde_dt = datetime.fromisoformat(fecha_desde.replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    return {
                        'status': 'error',
                        'message': 'Formato de fecha_desde inválido',
                        'status_code': 400
                    }
            
            if fecha_hasta:
                try:
                    fecha_hasta_dt = datetime.fromisoformat(fecha_hasta.replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    return {
                        'status': 'error',
                        'message': 'Formato de fecha_hasta inválido',
                        'status_code': 400
                    }
            
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            
            if user_type == 'paciente':
                query = """
                    SELECT 
                        c.idCita, c.pacienteId, c.medicoId, c.fechaHora, 
                        c.motivo, c.estado, c.created_at,
                        u.nombre as medico_nombre, u.especialidad as medico_especialidad,
                        u.telefono as medico_telefono,
                        p.nombre as paciente_nombre, p.telefono as paciente_telefono
                    FROM Citas c
                    JOIN Usuarios u ON c.medicoId = u.idUsuario
                    JOIN Usuarios p ON c.pacienteId = p.idUsuario
                    WHERE c.pacienteId = %s
                """
                params = [user_id]
            else:  # medico
                query = """
                    SELECT 
                        c.idCita, c.pacienteId, c.medicoId, c.fechaHora, 
                        c.motivo, c.estado, c.created_at,
                        u.nombre as paciente_nombre, u.telefono as paciente_telefono,
                        u.rut as paciente_rut,
                        m.nombre as medico_nombre, m.especialidad as medico_especialidad
                    FROM Citas c
                    JOIN Usuarios u ON c.pacienteId = u.idUsuario
                    JOIN Usuarios m ON c.medicoId = m.idUsuario
                    WHERE c.medicoId = %s
                """
                params = [user_id]
            
            # Aplicar filtros adicionales
            if estado_filter:
                query += " AND c.estado = %s"
                params.append(estado_filter)
            
            if fecha_desde_dt:
                query += " AND c.fechaHora >= %s"
                params.append(fecha_desde_dt)
            
            if fecha_hasta_dt:
                query += " AND c.fechaHora <= %s"
                params.append(fecha_hasta_dt)
            
            query += " ORDER BY c.fechaHora DESC"
            
            cursor.execute(query, params)
            appointments = cursor.fetchall()
            
            cursor.close()
            db.close()
            
            # Formatear citas
            formatted_appointments = []
            for apt in appointments:
                formatted_apt = {
                    'id': apt['idCita'],
                    'pacienteId': apt['pacienteId'],
                    'medicoId': apt['medicoId'],
                    'fechaHora': apt['fechaHora'].isoformat() if apt['fechaHora'] else None,
                    'motivo': apt['motivo'],
                    'estado': apt['estado'],
                    'created_at': apt['created_at'].isoformat() if apt['created_at'] else None,
                    'paciente_nombre': apt['paciente_nombre'],
                    'paciente_telefono': apt['paciente_telefono'],
                    'medico_nombre': apt['medico_nombre'],
                    'medico_especialidad': apt.get('medico_especialidad')
                }
                
                if 'paciente_rut' in apt:
                    formatted_apt['paciente_rut'] = apt['paciente_rut']
                if 'medico_telefono' in apt:
                    formatted_apt['medico_telefono'] = apt['medico_telefono']
                
                formatted_appointments.append(formatted_apt)
            
            return {
                'status': 'success',
                'data': formatted_appointments,
                'count': len(formatted_appointments),
                'status_code': 200
            }
            
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos obteniendo citas: {e}")
            return {
                'status': 'error',
                'message': 'Error en el servidor de base de datos',
                'status_code': 500
            }
        except Exception as e:
            logger.error(f"Error interno obteniendo citas: {e}")
            return {
                'status': 'error',
                'message': 'Error interno del servidor',
                'status_code': 500
            }
    
    def handle_get_appointment_by_id(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene una cita por ID."""
        try:
            appointment_id = data.get('appointment_id')
            if not appointment_id:
                return {
                    'status': 'error',
                    'message': 'ID de cita requerido',
                    'status_code': 400
                }
            
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            
            cursor.execute(
                """
                SELECT 
                    c.idCita, c.pacienteId, c.medicoId, c.fechaHora, 
                    c.motivo, c.estado, c.created_at,
                    p.nombre as paciente_nombre, p.telefono as paciente_telefono, p.rut as paciente_rut,
                    m.nombre as medico_nombre, m.especialidad as medico_especialidad, m.telefono as medico_telefono
                FROM Citas c
                JOIN Usuarios p ON c.pacienteId = p.idUsuario
                JOIN Usuarios m ON c.medicoId = m.idUsuario
                WHERE c.idCita = %s
                """,
                (appointment_id,)
            )
            appointment = cursor.fetchone()
            
            cursor.close()
            db.close()
            
            if not appointment:
                return {
                    'status': 'error',
                    'message': 'Cita no encontrada',
                    'status_code': 404
                }
            
            # Formatear cita
            formatted_appointment = {
                'id': appointment['idCita'],
                'pacienteId': appointment['pacienteId'],
                'medicoId': appointment['medicoId'],
                'fechaHora': appointment['fechaHora'].isoformat() if appointment['fechaHora'] else None,
                'motivo': appointment['motivo'],
                'estado': appointment['estado'],
                'created_at': appointment['created_at'].isoformat() if appointment['created_at'] else None,
                'paciente': {
                    'nombre': appointment['paciente_nombre'],
                    'telefono': appointment['paciente_telefono'],
                    'rut': appointment['paciente_rut']
                },
                'medico': {
                    'nombre': appointment['medico_nombre'],
                    'especialidad': appointment['medico_especialidad'],
                    'telefono': appointment['medico_telefono']
                }
            }
            
            return {
                'status': 'success',
                'data': formatted_appointment,
                'status_code': 200
            }
            
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos obteniendo cita: {e}")
            return {
                'status': 'error',
                'message': 'Error en el servidor de base de datos',
                'status_code': 500
            }
        except Exception as e:
            logger.error(f"Error interno obteniendo cita: {e}")
            return {
                'status': 'error',
                'message': 'Error interno del servidor',
                'status_code': 500
            }
    
    def handle_update_appointment_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza el estado de una cita."""
        try:
            appointment_id = data.get('appointment_id')
            new_status = data.get('status')
            reason = data.get('reason', '')
            
            if not appointment_id or not new_status:
                return {
                    'status': 'error',
                    'message': 'ID de cita y nuevo estado requeridos',
                    'status_code': 400
                }
            
            # Validar estado
            valid_statuses = ['agendada', 'confirmada', 'completada', 'cancelada']
            if new_status not in valid_statuses:
                return {
                    'status': 'error',
                    'message': f'Estado inválido. Debe ser: {", ".join(valid_statuses)}',
                    'status_code': 400
                }
            
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            
            # Obtener cita actual
            cursor.execute(
                """
                SELECT estado, fechaHora, pacienteId, medicoId 
                FROM Citas 
                WHERE idCita = %s
                """,
                (appointment_id,)
            )
            appointment = cursor.fetchone()
            
            if not appointment:
                cursor.close()
                db.close()
                return {
                    'status': 'error',
                    'message': 'Cita no encontrada',
                    'status_code': 404
                }
            
            current_status = appointment['estado']
            fecha_hora = appointment['fechaHora']
            
            # Validar transiciones de estado
            valid_transitions = {
                'agendada': ['confirmada', 'cancelada'],
                'confirmada': ['completada', 'cancelada'],
                'completada': [],  # No se puede cambiar después de completada
                'cancelada': []    # No se puede cambiar después de cancelada
            }
            
            if new_status not in valid_transitions.get(current_status, []):
                cursor.close()
                db.close()
                return {
                    'status': 'error',
                    'message': f'No se puede cambiar de {current_status} a {new_status}',
                    'status_code': 400
                }
            
            # Validar cancelación con poca anticipación
            if new_status == 'cancelada' and fecha_hora:
                time_until_appointment = fecha_hora - datetime.now()
                if time_until_appointment < timedelta(hours=2):
                    cursor.close()
                    db.close()
                    return {
                        'status': 'error',
                        'message': 'No se puede cancelar con menos de 2 horas de anticipación',
                        'status_code': 400
                    }
            
            # Actualizar estado
            cursor.execute(
                """
                UPDATE Citas 
                SET estado = %s 
                WHERE idCita = %s
                """,
                (new_status, appointment_id)
            )
            
            # Registrar actividad
            actividad_detalles = f"Estado cambiado de {current_status} a {new_status}"
            if reason:
                actividad_detalles += f". Razón: {reason}"
            
            cursor.execute(
                """
                INSERT INTO ActividadCitas (citaId, accion, detalles)
                VALUES (%s, 'cambio_estado', %s)
                """,
                (appointment_id, actividad_detalles)
            )
            
            db.commit()
            affected_rows = cursor.rowcount
            
            cursor.close()
            db.close()
            
            if affected_rows == 0:
                return {
                    'status': 'error',
                    'message': 'Cita no encontrada',
                    'status_code': 404
                }
            
            logger.info(f"Estado de cita {appointment_id} actualizado a {new_status}")
            
            # Notificar cambio de estado
            # self._notify_appointment_status_changed(appointment_id, new_status, appointment['pacienteId'], appointment['medicoId'])
            
            return {
                'status': 'success',
                'message': f'Estado de cita actualizado a {new_status}',
                'status_code': 200
            }
            
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos actualizando cita: {e}")
            return {
                'status': 'error',
                'message': 'Error en el servidor de base de datos',
                'status_code': 500
            }
        except Exception as e:
            logger.error(f"Error interno actualizando cita: {e}")
            return {
                'status': 'error',
                'message': 'Error interno del servidor',
                'status_code': 500
            }
    
    def handle_get_doctor_availability(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene disponibilidad de un médico para una fecha específica."""
        try:
            medico_id = data.get('medico_id')
            fecha = data.get('fecha')  # Fecha en formato YYYY-MM-DD
            
            if not medico_id or not fecha:
                return {
                    'status': 'error',
                    'message': 'ID de médico y fecha requeridos',
                    'status_code': 400
                }
            
            try:
                fecha_dt = datetime.strptime(fecha, '%Y-%m-%d').date()
            except ValueError:
                return {
                    'status': 'error',
                    'message': 'Formato de fecha inválido. Use YYYY-MM-DD',
                    'status_code': 400
                }
            
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            
            # Verificar que el médico existe y está activo
            cursor.execute(
                """
                SELECT idUsuario, nombre, especialidad 
                FROM Usuarios 
                WHERE idUsuario = %s AND rol = 'medico' AND estado = 'activo'
                """,
                (medico_id,)
            )
            medico = cursor.fetchone()
            
            if not medico:
                cursor.close()
                db.close()
                return {
                    'status': 'error',
                    'message': 'Médico no encontrado o no activo',
                    'status_code': 404
                }
            
            # Obtener citas agendadas para ese día
            fecha_inicio = datetime.combine(fecha_dt, datetime.min.time())
            fecha_fin = datetime.combine(fecha_dt, datetime.max.time())
            
            cursor.execute(
                """
                SELECT fechaHora 
                FROM Citas 
                WHERE medicoId = %s 
                  AND fechaHora BETWEEN %s AND %s
                  AND estado IN ('agendada', 'confirmada')
                ORDER BY fechaHora
                """,
                (medico_id, fecha_inicio, fecha_fin)
            )
            booked_slots = cursor.fetchall()
            
            cursor.close()
            db.close()
            
            # Generar horarios disponibles (8:00 - 18:00, cada 30 minutos)
            available_slots = []
            start_time = datetime.combine(fecha_dt, datetime.strptime('08:00', '%H:%M').time())
            end_time = datetime.combine(fecha_dt, datetime.strptime('18:00', '%H:%M').time())
            
            current_time = start_time
            booked_times = {slot['fechaHora'] for slot in booked_slots}
            
            while current_time < end_time:
                if current_time not in booked_times:
                    # Solo mostrar horarios futuros o con al menos 1 hora de anticipación
                    if current_time > datetime.now() + timedelta(hours=1):
                        available_slots.append(current_time.isoformat())
                
                current_time += timedelta(minutes=30)
            
            return {
                'status': 'success',
                'data': {
                    'medico': {
                        'id': medico['idUsuario'],
                        'nombre': medico['nombre'],
                        'especialidad': medico['especialidad']
                    },
                    'fecha': fecha,
                    'available_slots': available_slots,
                    'total_slots': len(available_slots)
                },
                'status_code': 200
            }
            
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos obteniendo disponibilidad: {e}")
            return {
                'status': 'error',
                'message': 'Error en el servidor de base de datos',
                'status_code': 500
            }
        except Exception as e:
            logger.error(f"Error interno obteniendo disponibilidad: {e}")
            return {
                'status': 'error',
                'message': 'Error interno del servidor',
                'status_code': 500
            }
    
    def handle_get_appointment_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene estadísticas de citas."""
        try:
            medico_id = data.get('medico_id')
            fecha_desde = data.get('fecha_desde')
            fecha_hasta = data.get('fecha_hasta')
            
            # Parsear fechas si se proporcionan
            fecha_desde_dt = None
            fecha_hasta_dt = None
            
            if fecha_desde:
                try:
                    fecha_desde_dt = datetime.fromisoformat(fecha_desde.replace('Z', '+00:00'))
                except:
                    fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
            
            if fecha_hasta:
                try:
                    fecha_hasta_dt = datetime.fromisoformat(fecha_hasta.replace('Z', '+00:00'))
                except:
                    fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            
            # Construir query base
            query = """
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN estado = 'agendada' THEN 1 END) as agendadas,
                    COUNT(CASE WHEN estado = 'confirmada' THEN 1 END) as confirmadas,
                    COUNT(CASE WHEN estado = 'completada' THEN 1 END) as completadas,
                    COUNT(CASE WHEN estado = 'cancelada' THEN 1 END) as canceladas,
                    AVG(TIMESTAMPDIFF(MINUTE, created_at, fechaHora)) as tiempo_promedio_agendamiento
                FROM Citas 
                WHERE 1=1
            """
            params = []
            
            if medico_id:
                query += " AND medicoId = %s"
                params.append(medico_id)
            
            if fecha_desde_dt:
                query += " AND fechaHora >= %s"
                params.append(fecha_desde_dt)
            
            if fecha_hasta_dt:
                query += " AND fechaHora <= %s"
                params.append(fecha_hasta_dt)
            
            cursor.execute(query, params)
            stats = cursor.fetchone()
            
            # Citas por día de la semana
            cursor.execute(
                """
                SELECT 
                    DAYNAME(fechaHora) as dia_semana,
                    COUNT(*) as cantidad
                FROM Citas 
                WHERE 1=1
                GROUP BY DAYNAME(fechaHora), DAYOFWEEK(fechaHora)
                ORDER BY DAYOFWEEK(fechaHora)
                """
            )
            by_weekday = cursor.fetchall()
            
            # Citas por especialidad
            cursor.execute(
                """
                SELECT 
                    u.especialidad,
                    COUNT(*) as cantidad
                FROM Citas c
                JOIN Usuarios u ON c.medicoId = u.idUsuario
                WHERE u.especialidad IS NOT NULL
                GROUP BY u.especialidad
                ORDER BY cantidad DESC
                """
            )
            by_specialty = cursor.fetchall()
            
            cursor.close()
            db.close()
            
            # Formatear estadísticas
            formatted_stats = {
                'totales': {
                    'total': stats['total'] or 0,
                    'agendadas': stats['agendadas'] or 0,
                    'confirmadas': stats['confirmadas'] or 0,
                    'completadas': stats['completadas'] or 0,
                    'canceladas': stats['canceladas'] or 0,
                    'tiempo_promedio_agendamiento_minutos': float(stats['tiempo_promedio_agendamiento'] or 0)
                },
                'por_dia_semana': [
                    {
                        'dia': day['dia_semana'],
                        'cantidad': day['cantidad']
                    }
                    for day in by_weekday
                ],
                'por_especialidad': [
                    {
                        'especialidad': spec['especialidad'],
                        'cantidad': spec['cantidad']
                    }
                    for spec in by_specialty
                ]
            }
            
            return {
                'status': 'success',
                'data': formatted_stats,
                'status_code': 200
            }
            
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos obteniendo estadísticas: {e}")
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
    
    def handle_reschedule_appointment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Reprograma una cita existente."""
        try:
            appointment_id = data.get('appointment_id')
            new_fecha_hora = data.get('new_fecha_hora')
            reason = data.get('reason', '')
            
            if not appointment_id or not new_fecha_hora:
                return {
                    'status': 'error',
                    'message': 'ID de cita y nueva fecha/hora requeridos',
                    'status_code': 400
                }
            
            # Parsear nueva fecha y hora
            try:
                new_fecha_hora_dt = datetime.fromisoformat(new_fecha_hora.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                return {
                    'status': 'error',
                    'message': 'Formato de fecha inválido. Use ISO 8601',
                    'status_code': 400
                }
            
            # Validaciones similares a crear cita
            if new_fecha_hora_dt < datetime.now():
                return {
                    'status': 'error',
                    'message': 'No se pueden reprogramar citas al pasado',
                    'status_code': 400
                }
            
            hora = new_fecha_hora_dt.time()
            if hora.minute not in [0, 30]:
                return {
                    'status': 'error',
                    'message': 'Las citas deben ser en intervalos de 30 minutos',
                    'status_code': 400
                }
            
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            
            # Obtener cita actual
            cursor.execute(
                """
                SELECT c.*, p.nombre as paciente_nombre, m.nombre as medico_nombre
                FROM Citas c
                JOIN Usuarios p ON c.pacienteId = p.idUsuario
                JOIN Usuarios m ON c.medicoId = m.idUsuario
                WHERE c.idCita = %s
                """,
                (appointment_id,)
            )
            appointment = cursor.fetchone()
            
            if not appointment:
                cursor.close()
                db.close()
                return {
                    'status': 'error',
                    'message': 'Cita no encontrada',
                    'status_code': 404
                }
            
            # Validar que la cita no esté completada o cancelada
            if appointment['estado'] in ['completada', 'cancelada']:
                cursor.close()
                db.close()
                return {
                    'status': 'error',
                    'message': f'No se puede reprogramar una cita {appointment["estado"]}',
                    'status_code': 400
                }
            
            # Validar disponibilidad del médico en nuevo horario
            cursor.execute(
                """
                SELECT idCita 
                FROM Citas 
                WHERE medicoId = %s 
                  AND fechaHora = %s 
                  AND idCita != %s
                  AND estado IN ('agendada', 'confirmada')
                """,
                (appointment['medicoId'], new_fecha_hora_dt, appointment_id)
            )
            
            conflicting_appointment = cursor.fetchone()
            if conflicting_appointment:
                cursor.close()
                db.close()
                return {
                    'status': 'error',
                    'message': 'El médico no está disponible en el nuevo horario',
                    'status_code': 409
                }
            
            # Actualizar fecha/hora
            old_fecha_hora = appointment['fechaHora']
            
            cursor.execute(
                """
                UPDATE Citas 
                SET fechaHora = %s,
                    estado = 'agendada',
                    updated_at = NOW()
                WHERE idCita = %s
                """,
                (new_fecha_hora_dt, appointment_id)
            )
            
            # Registrar actividad
            actividad_detalles = f"Cita reprogramada de {old_fecha_hora} a {new_fecha_hora_dt}"
            if reason:
                actividad_detalles += f". Razón: {reason}"
            
            cursor.execute(
                """
                INSERT INTO ActividadCitas (citaId, accion, detalles)
                VALUES (%s, 'reprogramacion', %s)
                """,
                (appointment_id, actividad_detalles)
            )
            
            db.commit()
            affected_rows = cursor.rowcount
            
            cursor.close()
            db.close()
            
            if affected_rows == 0:
                return {
                    'status': 'error',
                    'message': 'Cita no encontrada',
                    'status_code': 404
                }
            
            logger.info(f"Cita {appointment_id} reprogramada de {old_fecha_hora} a {new_fecha_hora_dt}")
            
            return {
                'status': 'success',
                'message': 'Cita reprogramada exitosamente',
                'new_fecha_hora': new_fecha_hora_dt.isoformat(),
                'status_code': 200
            }
            
        except mysql.connector.Error as e:
            logger.error(f"Error de base de datos reprogramando cita: {e}")
            return {
                'status': 'error',
                'message': 'Error en el servidor de base de datos',
                'status_code': 500
            }
        except Exception as e:
            logger.error(f"Error interno reprogramando cita: {e}")
            return {
                'status': 'error',
                'message': 'Error interno del servidor',
                'status_code': 500
            }
