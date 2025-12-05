"""
Servidor central del bus de mensajería para MediConnect.
Implementa comunicación TCP con protocolo JSON.
"""
import socket
import select
import json
import threading
import time
import logging
from typing import Dict, List, Optional, Set, Tuple
from queue import Queue, Empty
from dataclasses import dataclass, asdict
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

@dataclass
class ServiceInfo:
    """Información de un servicio registrado."""
    name: str
    socket: socket.socket
    address: Tuple[str, int]
    registered_at: datetime
    last_seen: datetime
    message_count: int = 0

class BusServer:
    """Servidor del bus de mensajería."""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 5000):
        self.host = host
        self.port = port
        self.server_socket: Optional[socket.socket] = None
        
        # Registro de servicios
        self.services: Dict[str, ServiceInfo] = {}
        self.socket_to_service: Dict[socket.socket, str] = {}
        
        # Colas de mensajes
        self.message_queues: Dict[socket.socket, Queue] = {}
        
        # Listas para select
        self.inputs: Set[socket.socket] = set()
        self.outputs: Set[socket.socket] = set()
        
        # Control
        self.running = False
        self.lock = threading.RLock()
        
        # Estadísticas
        self.stats = {
            'messages_received': 0,
            'messages_sent': 0,
            'errors': 0,
            'connections': 0,
            'start_time': None
        }
        
        # Configuración
        self.max_message_size = 10 * 1024 * 1024  # 10MB
        self.heartbeat_interval = 30  # segundos
        self.cleanup_interval = 60  # segundos
        
    def start(self):
        """Inicia el servidor del bus."""
        try:
            logger.info(f"🚀 Iniciando Bus Server en {self.host}:{self.port}")
            
            # Crear socket del servidor
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(100)  # Hasta 100 conexiones pendientes
            self.server_socket.setblocking(False)
            
            # Agregar a inputs
            self.inputs.add(self.server_socket)
            
            # Iniciar estadísticas
            self.stats['start_time'] = datetime.now()
            self.running = True
            
            # Iniciar hilos auxiliares
            self._start_auxiliary_threads()
            
            logger.info("✅ Bus Server iniciado correctamente")
            
            # Loop principal
            self._main_loop()
            
        except Exception as e:
            logger.error(f"❌ Error iniciando servidor: {e}")
            raise
        finally:
            self.stop()
    
    def _start_auxiliary_threads(self):
        """Inicia hilos auxiliares."""
        # Hilo de heartbeat
        self.heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            name="bus_heartbeat",
            daemon=True
        )
        self.heartbeat_thread.start()
        
        # Hilo de limpieza
        self.cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            name="bus_cleanup",
            daemon=True
        )
        self.cleanup_thread.start()
        
        logger.debug("Hilos auxiliares iniciados")
    
    def _main_loop(self):
        """Loop principal del servidor."""
        logger.info("⏳ Iniciando loop principal...")
        
        while self.running:
            try:
                # Usar select para manejar múltiples conexiones
                readable, writable, exceptional = select.select(
                    list(self.inputs),
                    list(self.outputs),
                    list(self.inputs),
                    1.0  # Timeout de 1 segundo
                )
                
                # Procesar sockets legibles
                for sock in readable:
                    if sock is self.server_socket:
                        self._accept_new_connection()
                    else:
                        self._handle_client_message(sock)
                
                # Procesar sockets escribibles
                for sock in writable:
                    self._send_pending_messages(sock)
                
                # Procesar sockets excepcionales
                for sock in exceptional:
                    self._handle_exceptional_socket(sock)
                    
            except KeyboardInterrupt:
                logger.info("📛 Recibida señal de interrupción")
                break
            except Exception as e:
                logger.error(f"💥 Error en loop principal: {e}")
                time.sleep(1)  # Prevenir CPU spin en caso de error
    
    def _accept_new_connection(self):
        """Acepta una nueva conexión."""
        try:
            client_socket, client_address = self.server_socket.accept()
            client_socket.setblocking(False)
            
            with self.lock:
                self.inputs.add(client_socket)
                self.message_queues[client_socket] = Queue()
                self.stats['connections'] += 1
            
            logger.info(f"🔗 Nueva conexión desde {client_address}")
            
            # Enviar mensaje de bienvenida
            welcome_msg = {
                'action': 'welcome',
                'message': 'Conectado al Bus de MediConnect',
                'timestamp': datetime.now().isoformat(),
                'server_version': '2.0.0'
            }
            self._send_to_socket(client_socket, welcome_msg)
            
        except Exception as e:
            logger.error(f"❌ Error aceptando conexión: {e}")
    
    def _handle_client_message(self, sock: socket.socket):
        """Maneja mensajes de un cliente."""
        try:
            message = self._receive_message(sock)
            if message:
                self._process_message(sock, message)
            else:
                # Conexión cerrada por el cliente
                self._cleanup_socket(sock)
                
        except ConnectionError:
            logger.debug(f"🔌 Conexión cerrada por cliente: {sock}")
            self._cleanup_socket(sock)
        except Exception as e:
            logger.error(f"💥 Error manejando mensaje del cliente: {e}")
            self._cleanup_socket(sock)
    
    def _receive_message(self, sock: socket.socket) -> Optional[Dict]:
        """Recibe un mensaje completo del socket."""
        try:
            # Recibir tamaño del mensaje (4 bytes, big-endian)
            header = sock.recv(4)
            if not header:
                return None  # Conexión cerrada
            
            message_size = int.from_bytes(header, 'big', signed=False)
            
            # Validar tamaño del mensaje
            if message_size > self.max_message_size:
                logger.warning(f"⚠️  Mensaje demasiado grande: {message_size} bytes")
                return None
            
            # Recibir mensaje completo
            received = 0
            chunks = []
            while received < message_size:
                chunk = sock.recv(min(4096, message_size - received))
                if not chunk:
                    return None  # Conexión cerrada antes de recibir todo
                chunks.append(chunk)
                received += len(chunk)
            
            # Decodificar JSON
            message_data = b''.join(chunks)
            message = json.loads(message_data.decode('utf-8'))
            
            return message
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Error decodificando JSON: {e}")
            return None
        except (ConnectionError, TimeoutError) as e:
            logger.debug(f"🔌 Error de conexión: {e}")
            return None
        except Exception as e:
            logger.error(f"💥 Error recibiendo mensaje: {e}")
            return None
    
    def _process_message(self, sock: socket.socket, message: Dict):
        """Procesa un mensaje recibido."""
        try:
            action = message.get('action')
            sender = message.get('sender', 'unknown')
            timestamp = message.get('timestamp', datetime.now().isoformat())
            
            logger.debug(f"📨 Mensaje de '{sender}': {action}")
            
            # Actualizar estadísticas
            with self.lock:
                self.stats['messages_received'] += 1
            
            # Procesar según acción
            if action == 'register':
                self._register_service(sock, message)
            elif action == 'ping':
                self._handle_ping(sock, message)
            elif action == 'discover':
                self._handle_discover(sock, message)
            elif action == 'broadcast':
                self._handle_broadcast(sock, message)
            elif 'destination' in message:
                self._route_message(sock, message)
            else:
                logger.warning(f"⚠️  Acción no reconocida: {action}")
                self._send_error(sock, f"Acción no reconocida: {action}")
                
        except Exception as e:
            logger.error(f"💥 Error procesando mensaje: {e}")
            self._send_error(sock, f"Error interno: {str(e)}")
    
    def _register_service(self, sock: socket.socket, message: Dict):
        """Registra un nuevo servicio."""
        try:
            service_name = message.get('service_name')
            if not service_name:
                self._send_error(sock, "Nombre de servicio requerido")
                return
            
            # Obtener dirección del cliente
            try:
                client_address = sock.getpeername()
            except:
                client_address = ('unknown', 0)
            
            with self.lock:
                # Verificar si el servicio ya está registrado
                if service_name in self.services:
                    old_sock = self.services[service_name].socket
                    if old_sock != sock:
                        # Servicio existente con nuevo socket (reconexión)
                        logger.info(f"🔄 Re-conexión del servicio: {service_name}")
                        self._cleanup_socket(old_sock)
                    else:
                        # Mismo socket, actualizar timestamp
                        self.services[service_name].last_seen = datetime.now()
                        self._send_success(sock, f"Servicio {service_name} ya registrado")
                        return
                
                # Registrar nuevo servicio
                service_info = ServiceInfo(
                    name=service_name,
                    socket=sock,
                    address=client_address,
                    registered_at=datetime.now(),
                    last_seen=datetime.now()
                )
                
                self.services[service_name] = service_info
                self.socket_to_service[sock] = service_name
                
                logger.info(f"✅ Servicio registrado: {service_name} desde {client_address}")
                
                # Enviar confirmación
                response = {
                    'action': 'registered',
                    'service_name': service_name,
                    'message': f'Servicio {service_name} registrado exitosamente',
                    'timestamp': datetime.now().isoformat(),
                    'registered_services': list(self.services.keys())
                }
                self._send_to_socket(sock, response)
                
                # Notificar a otros servicios sobre el nuevo servicio
                notification = {
                    'action': 'service_connected',
                    'service_name': service_name,
                    'timestamp': datetime.now().isoformat()
                }
                self._broadcast(notification, exclude_sockets=[sock])
                
        except Exception as e:
            logger.error(f"💥 Error registrando servicio: {e}")
            self._send_error(sock, f"Error registrando servicio: {str(e)}")
    
    def _route_message(self, sock: socket.socket, message: Dict):
        """Enruta un mensaje a su destino."""
        try:
            destination = message.get('destination')
            sender = message.get('sender', 'unknown')
            
            with self.lock:
                if destination not in self.services:
                    self._send_error(sock, f"Servicio destino '{destination}' no encontrado")
                    return
                
                # Obtener información del servicio destino
                dest_service = self.services[destination]
                dest_sock = dest_service.socket
                
                # Actualizar timestamp del servicio destino
                dest_service.last_seen = datetime.now()
                dest_service.message_count += 1
                
                # Actualizar estadísticas del sender si está registrado
                if sender in self.services:
                    self.services[sender].message_count += 1
                    self.services[sender].last_seen = datetime.now()
                
                # Agregar información de routing al mensaje
                routed_message = message.copy()
                routed_message['_routed'] = {
                    'sender_socket': str(sock.getpeername() if sock else 'unknown'),
                    'timestamp': datetime.now().isoformat(),
                    'hop_count': message.get('_routed', {}).get('hop_count', 0) + 1
                }
                
                # Encolar mensaje para envío
                self.message_queues[dest_sock].put(routed_message)
                if dest_sock not in self.outputs:
                    self.outputs.add(dest_sock)
                
                # Enviar confirmación al remitente
                confirmation = {
                    'action': 'routed',
                    'destination': destination,
                    'message': f'Mensaje enrutado a {destination}',
                    'timestamp': datetime.now().isoformat(),
                    'queue_size': self.message_queues[dest_sock].qsize()
                }
                self._send_to_socket(sock, confirmation)
                
                logger.debug(f"📤 Ruteado: {sender} -> {destination}")
                
        except Exception as e:
            logger.error(f"💥 Error enrutando mensaje: {e}")
            self._send_error(sock, f"Error enrutando mensaje: {str(e)}")
    
    def _handle_ping(self, sock: socket.socket, message: Dict):
        """Maneja mensajes de ping."""
        try:
            response = {
                'action': 'pong',
                'timestamp': datetime.now().isoformat(),
                'server_time': datetime.now().isoformat(),
                'services_count': len(self.services),
                'stats': self._get_server_stats()
            }
            self._send_to_socket(sock, response)
            
            # Actualizar last_seen si es un servicio registrado
            with self.lock:
                service_name = self.socket_to_service.get(sock)
                if service_name and service_name in self.services:
                    self.services[service_name].last_seen = datetime.now()
                    
        except Exception as e:
            logger.error(f"💥 Error manejando ping: {e}")
    
    def _handle_discover(self, sock: socket.socket, message: Dict):
        """Maneja solicitudes de descubrimiento de servicios."""
        try:
            with self.lock:
                services_list = []
                for service_name, service_info in self.services.items():
                    services_list.append({
                        'name': service_name,
                        'address': service_info.address,
                        'registered_at': service_info.registered_at.isoformat(),
                        'last_seen': service_info.last_seen.isoformat(),
                        'message_count': service_info.message_count
                    })
                
                response = {
                    'action': 'discover_response',
                    'timestamp': datetime.now().isoformat(),
                    'services': services_list,
                    'total_services': len(services_list)
                }
                self._send_to_socket(sock, response)
                
        except Exception as e:
            logger.error(f"💥 Error manejando discover: {e}")
    
    def _handle_broadcast(self, sock: socket.socket, message: Dict):
        """Maneja mensajes de broadcast."""
        try:
            sender = message.get('sender', 'unknown')
            data = message.get('data', {})
            
            # Crear mensaje de broadcast
            broadcast_msg = {
                'action': 'broadcast',
                'sender': sender,
                'data': data,
                'timestamp': datetime.now().isoformat(),
                'original_timestamp': message.get('timestamp')
            }
            
            # Broadcast a todos excepto al remitente
            exclude_sockets = [sock]
            recipients = self._broadcast(broadcast_msg, exclude_sockets)
            
            # Enviar confirmación al remitente
            confirmation = {
                'action': 'broadcast_sent',
                'timestamp': datetime.now().isoformat(),
                'recipients': recipients,
                'total_services': len(self.services)
            }
            self._send_to_socket(sock, confirmation)
            
            logger.info(f"📢 Broadcast de {sender} a {recipients} servicios")
            
        except Exception as e:
            logger.error(f"💥 Error en broadcast: {e}")
    
    def _broadcast(self, message: Dict, exclude_sockets: List[socket.socket] = None) -> int:
        """Envía un mensaje a todos los servicios excepto los excluidos."""
        exclude_sockets = exclude_sockets or []
        recipients = 0
        
        with self.lock:
            for service_name, service_info in self.services.items():
                if service_info.socket not in exclude_sockets:
                    try:
                        self.message_queues[service_info.socket].put(message)
                        if service_info.socket not in self.outputs:
                            self.outputs.add(service_info.socket)
                        recipients += 1
                    except Exception as e:
                        logger.error(f"💥 Error encolando broadcast para {service_name}: {e}")
        
        return recipients
    
    def _send_pending_messages(self, sock: socket.socket):
        """Envía mensajes pendientes de un socket."""
        try:
            queue = self.message_queues.get(sock)
            if not queue:
                return
            
            sent_count = 0
            max_messages_per_cycle = 100  # Limitar mensajes por ciclo
            
            while sent_count < max_messages_per_cycle and not queue.empty():
                try:
                    message = queue.get_nowait()
                    self._send_to_socket(sock, message)
                    sent_count += 1
                    
                    with self.lock:
                        self.stats['messages_sent'] += 1
                        
                except Empty:
                    break
                except Exception as e:
                    logger.error(f"💥 Error enviando mensaje pendiente: {e}")
                    break
            
            # Si la cola está vacía, remover de outputs
            if queue.empty() and sock in self.outputs:
                self.outputs.remove(sock)
                
        except Exception as e:
            logger.error(f"💥 Error enviando mensajes pendientes: {e}")
            self._cleanup_socket(sock)
    
    def _send_to_socket(self, sock: socket.socket, message: Dict):
        """Envía un mensaje a un socket."""
        try:
            # Convertir a JSON
            message_json = json.dumps(message, ensure_ascii=False)
            message_bytes = message_json.encode('utf-8')
            
            # Enviar tamaño (4 bytes, big-endian)
            size_bytes = len(message_bytes).to_bytes(4, 'big', signed=False)
            sock.send(size_bytes + message_bytes)
            
        except (BrokenPipeError, ConnectionError) as e:
            logger.debug(f"🔌 Error enviando a socket (conexión cerrada): {e}")
            self._cleanup_socket(sock)
        except Exception as e:
            logger.error(f"💥 Error enviando a socket: {e}")
            self._cleanup_socket(sock)
    
    def _send_success(self, sock: socket.socket, message: str):
        """Envía un mensaje de éxito."""
        response = {
            'action': 'success',
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self._send_to_socket(sock, response)
    
    def _send_error(self, sock: socket.socket, error_message: str):
        """Envía un mensaje de error."""
        response = {
            'action': 'error',
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        }
        self._send_to_socket(sock, response)
        
        with self.lock:
            self.stats['errors'] += 1
    
    def _handle_exceptional_socket(self, sock: socket.socket):
        """Maneja sockets con errores."""
        logger.warning(f"⚠️  Socket excepcional detectado: {sock}")
        self._cleanup_socket(sock)
    
    def _cleanup_socket(self, sock: socket.socket):
        """Limpia los recursos de un socket."""
        with self.lock:
            # Remover de registros
            service_name = self.socket_to_service.pop(sock, None)
            if service_name and service_name in self.services:
                service_info = self.services.pop(service_name)
                logger.info(f"🔌 Servicio desconectado: {service_name} ({service_info.address})")
                
                # Notificar a otros servicios
                notification = {
                    'action': 'service_disconnected',
                    'service_name': service_name,
                    'timestamp': datetime.now().isoformat(),
                    'reason': 'connection_closed'
                }
                self._broadcast(notification, exclude_sockets=[sock])
            
            # Remover de listas de selección
            if sock in self.inputs:
                self.inputs.remove(sock)
            if sock in self.outputs:
                self.outputs.remove(sock)
            
            # Limpiar cola de mensajes
            self.message_queues.pop(sock, None)
            
            # Cerrar socket
            try:
                sock.close()
            except:
                pass
    
    def _heartbeat_loop(self):
        """Loop para enviar heartbeats y verificar conexiones."""
        logger.debug("❤️  Iniciando heartbeat loop")
        
        while self.running:
            try:
                time.sleep(self.heartbeat_interval)
                
                # Verificar servicios inactivos
                now = datetime.now()
                inactive_services = []
                
                with self.lock:
                    for service_name, service_info in self.services.items():
                        time_since_last_seen = (now - service_info.last_seen).total_seconds()
                        if time_since_last_seen > self.heartbeat_interval * 3:  # 3 veces el intervalo
                            inactive_services.append(service_name)
                
                # Limpiar servicios inactivos
                for service_name in inactive_services:
                    logger.warning(f"⚠️  Servicio inactivo detectado: {service_name}")
                    service_info = self.services.get(service_name)
                    if service_info:
                        self._cleanup_socket(service_info.socket)
                
                # Enviar heartbeat a servicios activos
                heartbeat_msg = {
                    'action': 'heartbeat',
                    'timestamp': now.isoformat(),
                    'server_stats': self._get_server_stats()
                }
                
                with self.lock:
                    for service_info in self.services.values():
                        try:
                            self.message_queues[service_info.socket].put(heartbeat_msg)
                            if service_info.socket not in self.outputs:
                                self.outputs.add(service_info.socket)
                        except:
                            pass
                            
            except Exception as e:
                logger.error(f"💥 Error en heartbeat loop: {e}")
    
    def _cleanup_loop(self):
        """Loop para limpieza periódica."""
        logger.debug("🧹 Iniciando cleanup loop")
        
        while self.running:
            try:
                time.sleep(self.cleanup_interval)
                
                # Limpiar colas muy grandes
                with self.lock:
                    for sock, queue in list(self.message_queues.items()):
                        if queue.qsize() > 1000:
                            logger.warning(f"⚠️  Cola muy grande: {queue.qsize()} mensajes")
                            # Limpiar algunos mensajes antiguos
                            try:
                                for _ in range(500):  # Limpiar 500 mensajes
                                    queue.get_nowait()
                            except Empty:
                                pass
                
                # Log de estadísticas periódicas
                stats = self._get_server_stats()
                logger.info(f"📊 Estadísticas del servidor: {stats}")
                
            except Exception as e:
                logger.error(f"💥 Error en cleanup loop: {e}")
    
    def _get_server_stats(self) -> Dict:
        """Obtiene estadísticas del servidor."""
        with self.lock:
            uptime = None
            if self.stats['start_time']:
                uptime = str(datetime.now() - self.stats['start_time'])
            
            queue_sizes = {str(sock): q.qsize() for sock, q in self.message_queues.items()}
            
            return {
                'uptime': uptime,
                'connections': self.stats['connections'],
                'active_services': len(self.services),
                'messages_received': self.stats['messages_received'],
                'messages_sent': self.stats['messages_sent'],
                'errors': self.stats['errors'],
                'queue_sizes': queue_sizes,
                'timestamp': datetime.now().isoformat()
            }
    
    def stop(self):
        """Detiene el servidor."""
        logger.info("🛑 Deteniendo Bus Server...")
        self.running = False
        
        with self.lock:
            # Cerrar todos los sockets de clientes
            for sock in list(self.inputs):
                if sock != self.server_socket:
                    try:
                        sock.close()
                    except:
                        pass
            
            # Cerrar socket del servidor
            if self.server_socket:
                try:
                    self.server_socket.close()
                except:
                    pass
            
            # Limpiar todas las estructuras
            self.inputs.clear()
            self.outputs.clear()
            self.services.clear()
            self.socket_to_service.clear()
            self.message_queues.clear()
            self.server_socket = None
        
        logger.info("✅ Bus Server detenido correctamente")

def main():
    """Función principal para ejecutar el servidor."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Bus Server de MediConnect')
    parser.add_argument('--host', default='0.0.0.0', help='Host del servidor')
    parser.add_argument('--port', type=int, default=5000, help='Puerto del servidor')
    parser.add_argument('--verbose', '-v', action='store_true', help='Modo verbose')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    server = BusServer(host=args.host, port=args.port)
    
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("👋 Apagando por interrupción del usuario")
    except Exception as e:
        logger.error(f"💥 Error fatal: {e}")
        raise
    finally:
        server.stop()

if __name__ == "__main__":
    main()
