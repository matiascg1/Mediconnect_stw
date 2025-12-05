"""
Cliente del bus de mensajería para servicios MediConnect.
VERSIÓN CORREGIDA - Soluciona problemas de registro
"""
import socket
import json
import threading
import time
import logging
import uuid
from typing import Dict, List, Optional, Callable, Any, Union
from queue import Queue, Empty
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class ConnectionState(Enum):
    """Estados de conexión del cliente."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    REGISTERED = "registered"
    ERROR = "error"

@dataclass
class Message:
    """Representa un mensaje del bus."""
    action: str
    sender: str
    destination: Optional[str] = None
    data: Optional[Dict] = None
    request_id: Optional[str] = None
    timestamp: Optional[str] = None
    _metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Convierte el mensaje a diccionario."""
        result = {
            'action': self.action,
            'sender': self.sender,
            'timestamp': self.timestamp or datetime.now().isoformat()
        }
        
        if self.destination:
            result['destination'] = self.destination
        
        if self.data is not None:
            result['data'] = self.data
        
        if self.request_id:
            result['request_id'] = self.request_id
        
        if self._metadata:
            result['_metadata'] = self._metadata
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        """Crea un mensaje desde un diccionario."""
        return cls(
            action=data.get('action', ''),
            sender=data.get('sender', ''),
            destination=data.get('destination'),
            data=data.get('data'),
            request_id=data.get('request_id'),
            timestamp=data.get('timestamp'),
            _metadata=data.get('_metadata')
        )

class BusClient:
    """Cliente para conectar servicios al bus de mensajería."""
    
    def __init__(self, service_name: str, host: str = 'localhost', port: int = 5000):
        self.service_name = service_name
        self.host = host
        self.port = port
        
        # Socket y conexión
        self.socket: Optional[socket.socket] = None
        self.connection_state = ConnectionState.DISCONNECTED
        
        # Callbacks registrados
        self.callbacks: Dict[str, Callable[[Dict], Optional[Dict]]] = {}
        
        # Colas de mensajes
        self.outgoing_queue = Queue()
        self.incoming_queue = Queue()
        self.response_queues: Dict[str, Queue] = {}
        
        # Hilos
        self.receiver_thread: Optional[threading.Thread] = None
        self.sender_thread: Optional[threading.Thread] = None
        self.processor_thread: Optional[threading.Thread] = None
        self.heartbeat_thread: Optional[threading.Thread] = None
        
        # 🔥 NUEVO: Evento para indicar que receiver está listo
        self.receiver_ready = threading.Event()
        
        # Control
        self.running = False
        self.lock = threading.RLock()
        
        # Configuración
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.reconnect_delay = 5
        self.heartbeat_interval = 30
        self.response_timeout = 30
        
        # Estadísticas
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'errors': 0,
            'connection_time': None,
            'last_heartbeat': None
        }
        
        # Eventos
        self.on_connect = None
        self.on_disconnect = None
        self.on_error = None
    
    def connect(self, timeout: int = 10) -> bool:
        """Conecta al bus y registra el servicio."""
        try:
            with self.lock:
                if self.connection_state == ConnectionState.CONNECTED:
                    logger.warning(f"⚠️  {self.service_name} ya está conectado")
                    return True
                
                self.connection_state = ConnectionState.CONNECTING
                logger.info(f"🔗 {self.service_name} conectando a {self.host}:{self.port}")
            
            # Crear socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(timeout)
            
            # Conectar
            self.socket.connect((self.host, self.port))
            self.socket.settimeout(None)
            
            with self.lock:
                self.connection_state = ConnectionState.CONNECTED
                self.stats['connection_time'] = datetime.now()
                self.reconnect_attempts = 0
            
            logger.info(f"✅ {self.service_name} conectado al bus")
            
            # Iniciar hilos
            self._start_threads()
            
            # 🔥 CRÍTICO: Esperar a que receiver esté listo
            logger.info(f"⏳ {self.service_name} esperando que receiver esté listo...")
            if not self.receiver_ready.wait(timeout=5):
                logger.error(f"❌ {self.service_name} receiver no se inició a tiempo")
                self.disconnect()
                return False
            logger.info(f"✅ {self.service_name} receiver está listo")
            
            # Registrar servicio
            if not self._register_service():
                logger.error(f"❌ {self.service_name} no pudo registrarse")
                self.disconnect()
                return False
            
            # Llamar callback de conexión
            if self.on_connect:
                try:
                    self.on_connect()
                except Exception as e:
                    logger.error(f"💥 Error en callback on_connect: {e}")
            
            return True
            
        except socket.timeout:
            logger.error(f"❌ {self.service_name} timeout conectando a {self.host}:{self.port}")
            self._handle_connection_error("Timeout de conexión")
            return False
        except ConnectionRefusedError:
            logger.error(f"❌ {self.service_name} conexión rechazada en {self.host}:{self.port}")
            self._handle_connection_error("Conexión rechazada")
            return False
        except Exception as e:
            logger.error(f"❌ {self.service_name} error conectando: {e}")
            self._handle_connection_error(str(e))
            return False
    
    def _register_service(self) -> bool:
        """Registra el servicio en el bus."""
        try:
            logger.info(f"📝 {self.service_name} iniciando registro...")
            
            register_msg = Message(
                action='register',
                sender=self.service_name,
                data={'service_name': self.service_name}
            )
            
            # Enviar mensaje de registro
            logger.info(f"📤 {self.service_name} enviando mensaje de registro...")
            self._send_message(register_msg)
            logger.info(f"📤 {self.service_name} mensaje de registro enviado")
            
            # Esperar respuesta
            logger.info(f"⏳ {self.service_name} esperando 'registered' (timeout: 15s)...")
            response = self._wait_for_response('registered', timeout=15)
            
            if response:
                logger.info(f"📥 {self.service_name} recibió respuesta: acción={response.get('action')}")
                if response.get('action') == 'registered':
                    with self.lock:
                        self.connection_state = ConnectionState.REGISTERED
                    
                    logger.info(f"✅✅✅ {self.service_name} REGISTRADO EXITOSAMENTE en el bus")
                    return True
                else:
                    logger.warning(f"⚠️  {self.service_name} recibió acción inesperada: {response}")
            else:
                logger.error(f"❌ {self.service_name} NO recibió NINGUNA respuesta")
            
            logger.error(f"❌ {self.service_name} no recibió confirmación de registro")
            return False
            
        except Exception as e:
            logger.error(f"❌ {self.service_name} error registrando: {e}", exc_info=True)
            return False
    
    def _start_threads(self):
        """Inicia los hilos del cliente."""
        with self.lock:
            self.running = True
            self.receiver_ready.clear()  # 🔥 Resetear evento
            
            # Hilo receptor
            self.receiver_thread = threading.Thread(
                target=self._receiver_loop,
                name=f"{self.service_name}_receiver",
                daemon=True
            )
            
            # Hilo enviador
            self.sender_thread = threading.Thread(
                target=self._sender_loop,
                name=f"{self.service_name}_sender",
                daemon=True
            )
            
            # Hilo procesador
            self.processor_thread = threading.Thread(
                target=self._processor_loop,
                name=f"{self.service_name}_processor",
                daemon=True
            )
            
            # Hilo heartbeat
            self.heartbeat_thread = threading.Thread(
                target=self._heartbeat_loop,
                name=f"{self.service_name}_heartbeat",
                daemon=True
            )
        
        # Iniciar hilos
        self.receiver_thread.start()
        self.sender_thread.start()
        self.processor_thread.start()
        self.heartbeat_thread.start()
        
        logger.debug(f"🔄 {self.service_name} hilos iniciados")
    
    def _receiver_loop(self):
        """Loop principal de recepción de mensajes."""
        logger.debug(f"👂 {self.service_name} iniciando receiver loop")
        
        # 🔥 CRÍTICO: Señalar que receiver está listo
        self.receiver_ready.set()
        logger.info(f"🎉 {self.service_name} receiver loop LISTO para recibir mensajes")
        
        while self.running:
            try:
                if not self._is_connected():
                    time.sleep(1)
                    continue
                
                # Recibir mensaje
                message_data = self._receive_raw_message(timeout=1)
                if message_data:
                    logger.info(f"📥 {self.service_name} RECIBIÓ: {message_data.get('action')}")
                    message = Message.from_dict(message_data)
                    
                    # Procesar mensajes especiales
                    if message.action == 'heartbeat':
                        self._handle_heartbeat(message)
                        continue
                    elif message.action == 'service_connected':
                        logger.info(f"🔗 Servicio conectado: {message.data.get('service_name')}")
                    elif message.action == 'service_disconnected':
                        logger.info(f"🔌 Servicio desconectado: {message.data.get('service_name')}")
                    
                    # Encolar para procesamiento - incluye 'registered'
                    self.incoming_queue.put(message)
                    logger.info(f"📥 {self.service_name} mensaje encolado: {message.action}")
                    
                    with self.lock:
                        self.stats['messages_received'] += 1
                else:
                    logger.debug(f"⏳ {self.service_name} no recibió datos (timeout)")
                    
            except socket.timeout:
                logger.debug(f"⏰ {self.service_name} timeout en receiver")
                continue
            except (ConnectionError, OSError) as e:
                logger.error(f"🔌 {self.service_name} error de conexión en receiver: {e}")
                self._handle_connection_error("Error de conexión en receiver")
                time.sleep(1)
            except Exception as e:
                logger.error(f"💥 {self.service_name} error en receiver loop: {e}")
                time.sleep(1)
    
    def _sender_loop(self):
        """Loop para enviar mensajes pendientes."""
        logger.debug(f"📨 {self.service_name} iniciando sender loop")
        
        while self.running:
            try:
                if not self._is_connected():
                    time.sleep(0.1)
                    continue
                
                # Obtener mensaje de la cola
                try:
                    message = self.outgoing_queue.get(timeout=0.1)
                except Empty:
                    continue
                
                # Enviar mensaje
                self._send_message(message)
                
                with self.lock:
                    self.stats['messages_sent'] += 1
                
                logger.debug(f"✅ {self.service_name} mensaje enviado: {message.action}")
                
            except (ConnectionError, OSError) as e:
                logger.error(f"🔌 {self.service_name} error de conexión en sender: {e}")
                if 'message' in locals():
                    self.outgoing_queue.put(message)
                self._handle_connection_error("Error de conexión en sender")
                time.sleep(1)
            except Exception as e:
                logger.error(f"💥 {self.service_name} error en sender loop: {e}")
                time.sleep(0.1)
    
    def _processor_loop(self):
        """Loop de procesamiento de mensajes recibidos."""
        logger.debug(f"⚙️  {self.service_name} iniciando processor loop")
        
        while self.running:
            try:
                # Obtener mensaje de la cola
                try:
                    message = self.incoming_queue.get(timeout=0.1)
                except Empty:
                    continue
                
                # Procesar mensaje
                self._process_message(message)
                
            except Exception as e:
                logger.error(f"💥 {self.service_name} error en processor loop: {e}")
                time.sleep(0.1)
    
    def _heartbeat_loop(self):
        """Loop para mantener la conexión activa."""
        logger.debug(f"❤️  {self.service_name} iniciando heartbeat loop")
        
        last_heartbeat = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                
                if current_time - last_heartbeat >= self.heartbeat_interval:
                    if self._is_connected():
                        self._send_heartbeat()
                        last_heartbeat = current_time
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"💥 {self.service_name} error en heartbeat loop: {e}")
                time.sleep(5)
    
    def _send_message(self, message: Message):
        """Envía un mensaje al socket."""
        try:
            if not self.socket:
                raise ConnectionError("Socket no disponible")
            
            # Convertir a JSON
            message_dict = message.to_dict()
            message_json = json.dumps(message_dict, ensure_ascii=False)
            message_bytes = message_json.encode('utf-8')
            
            # Enviar tamaño (4 bytes, big-endian)
            size_bytes = len(message_bytes).to_bytes(4, 'big', signed=False)
            
            # 🔥 CRÍTICO: Usar sendall() en lugar de send()
            self.socket.sendall(size_bytes + message_bytes)
            
        except (BrokenPipeError, ConnectionError, OSError) as e:
            logger.error(f"🔌 {self.service_name} error enviando mensaje: {e}")
            raise
        except Exception as e:
            logger.error(f"💥 {self.service_name} error inesperado enviando: {e}")
            raise
    
    def _receive_raw_message(self, timeout: Optional[float] = None) -> Optional[Dict]:
        """Recibe un mensaje completo del socket."""
        try:
            if not self.socket:
                return None
            
            if timeout:
                self.socket.settimeout(timeout)
            
            # Recibir tamaño del mensaje
            header = self.socket.recv(4)
            if not header:
                return None
            
            message_size = int.from_bytes(header, 'big', signed=False)
            
            # Recibir mensaje completo
            received = 0
            chunks = []
            while received < message_size:
                chunk = self.socket.recv(min(4096, message_size - received))
                if not chunk:
                    return None
                chunks.append(chunk)
                received += len(chunk)
            
            # Decodificar JSON
            message_data = b''.join(chunks)
            message = json.loads(message_data.decode('utf-8'))
            
            return message
            
        except socket.timeout:
            return None
        except (ConnectionError, OSError):
            raise
        except json.JSONDecodeError as e:
            logger.error(f"❌ {self.service_name} error decodificando JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"💥 {self.service_name} error recibiendo mensaje: {e}")
            return None
        finally:
            if timeout:
                self.socket.settimeout(None)
    
    def _process_message(self, message: Message):
        """Procesa un mensaje recibido."""
        try:
            request_id = message.request_id
            action = message.action
            sender = message.sender
            
            logger.debug(f"📥 {self.service_name} recibió {action} de {sender}")
            
            # Manejar respuestas específicas
            if request_id and request_id in self.response_queues:
                self.response_queues[request_id].put(message.to_dict())
                return
            
            # Ejecutar callback si existe
            callback = self.callbacks.get(action)
            if callback:
                try:
                    response_data = callback(message.data or {})
                    
                    # Enviar respuesta si hay request_id
                    if request_id and sender and response_data is not None:
                        response_msg = Message(
                            action='response',
                            sender=self.service_name,
                            destination=sender,
                            data=response_data,
                            request_id=request_id
                        )
                        self.outgoing_queue.put(response_msg)
                        
                except Exception as e:
                    logger.error(f"💥 {self.service_name} error en callback {action}: {e}")
                    
                    if request_id and sender:
                        error_msg = Message(
                            action='error',
                            sender=self.service_name,
                            destination=sender,
                            data={'error': str(e), 'original_action': action},
                            request_id=request_id
                        )
                        self.outgoing_queue.put(error_msg)
            
            # Si no hay callback pero es una respuesta, encolar
            elif action == 'response' and request_id:
                if request_id not in self.response_queues:
                    self.response_queues[request_id] = Queue()
                self.response_queues[request_id].put(message.to_dict())
            
            # Si es un error, encolar también
            elif action == 'error' and request_id:
                if request_id not in self.response_queues:
                    self.response_queues[request_id] = Queue()
                self.response_queues[request_id].put(message.to_dict())
                
        except Exception as e:
            logger.error(f"💥 {self.service_name} error procesando mensaje: {e}")
    
    def _wait_for_response(self, expected_action: str, timeout: float = 10) -> Optional[Dict]:
        """Espera un mensaje con una acción específica."""
        start_time = time.time()
        logger.info(f"⏳ {self.service_name} buscando '{expected_action}'...")
        
        while time.time() - start_time < timeout:
            # Verificar cola de mensajes entrantes
            try:
                if not self.incoming_queue.empty():
                    logger.info(f"📦 {self.service_name} cola tiene {self.incoming_queue.qsize()} mensajes")
                    
                    # Revisar todos los mensajes en la cola
                    messages_to_process = []
                    while not self.incoming_queue.empty():
                        try:
                            message = self.incoming_queue.get_nowait()
                            messages_to_process.append(message)
                        except Empty:
                            break
                    
                    for message in messages_to_process:
                        logger.info(f"🔍 {self.service_name} revisando mensaje: {message.action}")
                        if message.action == expected_action:
                            logger.info(f"🎯 {self.service_name} ENCONTRÓ '{expected_action}'!")
                            return message.to_dict()
                        else:
                            # Volver a encolar los mensajes que no son los que buscamos
                            logger.info(f"📭 {self.service_name} re-encolando '{message.action}'")
                            self.incoming_queue.put(message)
            except Exception as e:
                logger.error(f"💥 {self.service_name} error revisando cola: {e}")
            
            time.sleep(0.1)
        
        logger.warning(f"⏰ {self.service_name} timeout esperando '{expected_action}' después de {timeout}s")
        logger.warning(f"   Cola actual: {self.incoming_queue.qsize()} mensajes pendientes")
        return None
    
    def send_message(self, destination: str, action: str, data: Optional[Dict] = None, 
                    request_id: Optional[str] = None, wait_for_response: bool = False,
                    timeout: Optional[float] = None) -> Optional[Dict]:
        """Envía un mensaje a otro servicio."""
        try:
            if not self._is_connected():
                logger.error(f"❌ {self.service_name} no está conectado")
                return None
            
            if request_id is None:
                request_id = str(uuid.uuid4())
            
            message = Message(
                action=action,
                sender=self.service_name,
                destination=destination,
                data=data or {},
                request_id=request_id
            )
            
            logger.debug(f"📤 {self.service_name} -> {destination}.{action} (ID: {request_id})")
            
            self.outgoing_queue.put(message)
            
            if wait_for_response:
                return self._wait_for_specific_response(request_id, timeout or self.response_timeout)
            
            return None
            
        except Exception as e:
            logger.error(f"💥 {self.service_name} error enviando mensaje: {e}")
            self.stats['errors'] += 1
            return None
    
    def _wait_for_specific_response(self, request_id: str, timeout: float) -> Optional[Dict]:
        """Espera una respuesta específica por request_id."""
        response_queue = Queue()
        self.response_queues[request_id] = response_queue
        
        try:
            response = response_queue.get(timeout=timeout)
            return response
            
        except Empty:
            logger.warning(f"⏰ {self.service_name} timeout esperando respuesta {request_id}")
            return None
        finally:
            self.response_queues.pop(request_id, None)
    
    def register_callback(self, action: str, callback: Callable[[Dict], Optional[Dict]]):
        """Registra un callback para una acción específica."""
        with self.lock:
            self.callbacks[action] = callback
        
        logger.debug(f"🎯 {self.service_name} callback registrado para '{action}'")
    
    def _send_heartbeat(self):
        """Envía un mensaje de heartbeat."""
        try:
            heartbeat_msg = Message(
                action='ping',
                sender=self.service_name,
                data={'timestamp': datetime.now().isoformat()}
            )
            self.outgoing_queue.put(heartbeat_msg)
            
        except Exception as e:
            logger.error(f"💥 {self.service_name} error enviando heartbeat: {e}")
    
    def _handle_heartbeat(self, message: Message):
        """Maneja mensajes de heartbeat."""
        with self.lock:
            self.stats['last_heartbeat'] = datetime.now()
        
        pong_msg = Message(
            action='pong',
            sender=self.service_name,
            destination=message.sender,
            data={'timestamp': datetime.now().isoformat()}
        )
        self.outgoing_queue.put(pong_msg)
    
    def _handle_connection_error(self, error_message: str):
        """Maneja errores de conexión."""
        with self.lock:
            if self.connection_state != ConnectionState.ERROR:
                self.connection_state = ConnectionState.ERROR
                logger.error(f"❌ {self.service_name} error de conexión: {error_message}")
                
                if self.on_error:
                    try:
                        self.on_error(error_message)
                    except Exception as e:
                        logger.error(f"💥 Error en callback on_error: {e}")
        
        self._try_reconnect()
    
    def _try_reconnect(self):
        """Intenta reconectar al bus."""
        with self.lock:
            if self.reconnect_attempts >= self.max_reconnect_attempts:
                logger.error(f"❌ {self.service_name} máximo de intentos de reconexión alcanzado")
                
                if self.on_disconnect:
                    try:
                        self.on_disconnect()
                    except Exception as e:
                        logger.error(f"💥 Error en callback on_disconnect: {e}")
                
                return
            
            self.reconnect_attempts += 1
        
        logger.info(f"🔄 {self.service_name} intentando reconexión ({self.reconnect_attempts}/{self.max_reconnect_attempts})")
        
        time.sleep(self.reconnect_delay * min(self.reconnect_attempts, 3))
        
        try:
            self.disconnect()
            if self.connect():
                logger.info(f"✅ {self.service_name} reconectado exitosamente")
                return
        except Exception as e:
            logger.error(f"❌ {self.service_name} error en reconexión: {e}")
        
        self._try_reconnect()
    
    def _is_connected(self) -> bool:
        """Verifica si el cliente está conectado y registrado."""
        with self.lock:
            return self.connection_state == ConnectionState.REGISTERED and self.socket is not None
    
    @property
    def connected(self) -> bool:
        """Propiedad para verificar si está conectado."""
        return self._is_connected()
    
    def disconnect(self):
        """Desconecta del bus."""
        with self.lock:
            if not self.running:
                return
            
            self.running = False
            self.connection_state = ConnectionState.DISCONNECTED
            
            logger.info(f"🔌 {self.service_name} desconectando...")
        
        # Esperar a que los hilos terminen
        if self.receiver_thread:
            self.receiver_thread.join(timeout=2)
        if self.sender_thread:
            self.sender_thread.join(timeout=2)
        if self.processor_thread:
            self.processor_thread.join(timeout=2)
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=2)
        
        # Cerrar socket
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        # Limpiar colas
        while not self.outgoing_queue.empty():
            try:
                self.outgoing_queue.get_nowait()
            except Empty:
                break
        
        while not self.incoming_queue.empty():
            try:
                self.incoming_queue.get_nowait()
            except Empty:
                break
        
        self.response_queues.clear()
        
        logger.info(f"✅ {self.service_name} desconectado")
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del cliente."""
        with self.lock:
            stats = self.stats.copy()
            stats.update({
                'service_name': self.service_name,
                'connection_state': self.connection_state.value,
                'callbacks_registered': len(self.callbacks),
                'outgoing_queue_size': self.outgoing_queue.qsize(),
                'incoming_queue_size': self.incoming_queue.qsize(),
                'reconnect_attempts': self.reconnect_attempts
            })
            return stats
    
    def __enter__(self):
        """Context manager entry."""
        if not self.connect():
            raise ConnectionError(f"{self.service_name} no pudo conectarse al bus")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()