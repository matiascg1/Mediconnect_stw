from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import os
import sys
import threading
import time
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Agregar path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from bus.bus_client import BusClient
from config.settings import settings

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

SECRET_KEY = settings.JWT_SECRET
ALGORITHM = settings.JWT_ALGORITHM

# Cliente del bus
bus_client = None
response_store = {}
response_lock = threading.Lock()

def init_bus_client():
    """Inicializa el cliente del bus"""
    global bus_client
    
    service_name = "apigw"
    bus_host = os.getenv("BUS_HOST", "bus_server")
    bus_port = int(os.getenv("BUS_PORT", 5000))
    
    logger.info(f"🚀 Iniciando API Gateway...")
    logger.info(f"📡 Conectando al bus en {bus_host}:{bus_port}")
    
    max_retries = 10
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            bus_client = BusClient(service_name, bus_host, bus_port)
            
            # Registrar callback para respuestas
            def handle_response_callback(data):
                request_id = data.get('request_id')
                if request_id:
                    with response_lock:
                        response_store[request_id] = data
                return None
            
            bus_client.register_callback("response", handle_response_callback)
            bus_client.register_callback("error", handle_response_callback)
            
            if bus_client.connect():
                logger.info("✅ API Gateway conectado al bus exitosamente")
                return True
            else:
                logger.error(f"❌ Error conectando al bus (intento {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    
        except Exception as e:
            logger.error(f"❌ Error inicializando bus client: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    
    logger.error("❌ Máximo de reintentos alcanzado")
    return False

def send_to_service(service: str, action: str, data: dict, timeout: int = 10) -> dict:
    """Envía una solicitud a un servicio y espera respuesta"""
    global bus_client
    
    if not bus_client or not bus_client._is_connected():
        return {
            'status': 'error',
            'message': 'API Gateway no conectado al bus',
            'status_code': 503
        }
    
    # Generar ID único para la solicitud
    import uuid
    request_id = str(uuid.uuid4())
    
    logger.debug(f"📤 Enviando a {service}.{action}: {request_id}")
    
    # Enviar mensaje
    result = bus_client.send_message(service, action, data, request_id, True, timeout)
    
    if result:
        return result
    else:
        return {
            'status': 'error',
            'message': 'No se recibió respuesta del servicio',
            'status_code': 504
        }

def verify_token(token: str):
    """Verifica un token JWT"""
    if not token:
        return None
    
    try:
        # Verificar con auth service
        response = send_to_service('authsv', 'verify_token', {'token': token})
        if response.get('status') == 'success':
            return response.get('user')
    except:
        pass
    
    return None

def require_auth(roles=None):
    """Decorador para requerir autenticación"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({
                    'status': 'error',
                    'message': 'Token de autorización requerido'
                }), 401
            
            token = auth_header.split(' ')[1]
            user = verify_token(token)
            
            if not user:
                return jsonify({
                    'status': 'error',
                    'message': 'Token inválido o expirado'
                }), 401
            
            # Verificar roles si se especifican
            if roles and user.get('rol') not in roles:
                return jsonify({
                    'status': 'error',
                    'message': 'No autorizado para esta acción'
                }), 403
            
            # Agregar usuario al contexto de la request
            request.user = user
            return f(*args, **kwargs)
        
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

# Middleware para logging
@app.before_request
def log_request():
    logger.info(f"🌐 {request.method} {request.path}")

@app.after_request
def log_response(response):
    logger.info(f"📨 {request.method} {request.path} - {response.status_code}")
    return response

# Endpoints de Autenticación
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Registro de usuario"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Datos requeridos'
            }), 400
        
        response = send_to_service('authsv', 'register', data)
        return jsonify(response), response.get('status_code', 500)
        
    except Exception as e:
        logger.error(f"Error en registro: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login de usuario"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Datos requeridos'
            }), 400
        
        response = send_to_service('authsv', 'login', data)
        return jsonify(response), response.get('status_code', 500)
        
    except Exception as e:
        logger.error(f"Error en login: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500

@app.route('/api/auth/verify', methods=['GET'])
@require_auth()
def verify():
    """Verificar token"""
    return jsonify({
        'status': 'success',
        'message': 'Token válido',
        'user': request.user
    }), 200

# Endpoints de Usuarios
@app.route('/api/users/<int:user_id>', methods=['GET'])
@require_auth()
def get_user(user_id):
    """Obtener usuario por ID"""
    try:
        response = send_to_service('usersv', 'get_user_by_id', {'user_id': user_id})
        return jsonify(response), response.get('status_code', 500)
        
    except Exception as e:
        logger.error(f"Error obteniendo usuario: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500

@app.route('/api/users', methods=['GET'])
@require_auth(['administrativo'])
def get_all_users():
    """Obtener todos los usuarios (solo admin)"""
    try:
        response = send_to_service('usersv', 'get_all_users', {})
        return jsonify(response), response.get('status_code', 500)
        
    except Exception as e:
        logger.error(f"Error obteniendo usuarios: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500

# Endpoints de Citas
@app.route('/api/appointments', methods=['POST'])
@require_auth(['paciente', 'administrativo'])
def create_appointment():
    """Crear una nueva cita"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Datos requeridos'
            }), 400
        
        # Agregar pacienteId del usuario autenticado si es paciente
        if request.user.get('rol') == 'paciente':
            data['pacienteId'] = request.user.get('user_id')
        
        response = send_to_service('appointmentsv', 'create_appointment', data)
        return jsonify(response), response.get('status_code', 500)
        
    except Exception as e:
        logger.error(f"Error creando cita: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500

@app.route('/api/appointments/user/<int:user_id>', methods=['GET'])
@require_auth()
def get_user_appointments(user_id):
    """Obtener citas por usuario"""
    try:
        # Verificar que el usuario solo pueda ver sus propias citas
        if request.user.get('rol') != 'administrativo' and request.user.get('user_id') != user_id:
            return jsonify({
                'status': 'error',
                'message': 'No autorizado'
            }), 403
        
        user_type = 'paciente' if request.user.get('rol') == 'paciente' else 'medico'
        
        response = send_to_service('appointmentsv', 'get_appointments_by_user', {
            'user_id': user_id,
            'user_type': user_type
        })
        return jsonify(response), response.get('status_code', 500)
        
    except Exception as e:
        logger.error(f"Error obteniendo citas: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500

@app.route('/api/appointments/<int:appointment_id>/status', methods=['PUT'])
@require_auth(['medico', 'administrativo'])
def update_appointment_status(appointment_id):
    """Actualizar estado de una cita"""
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Nuevo estado requerido'
            }), 400
        
        data['appointment_id'] = appointment_id
        response = send_to_service('appointmentsv', 'update_appointment_status', data)
        return jsonify(response), response.get('status_code', 500)
        
    except Exception as e:
        logger.error(f"Error actualizando cita: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500

# Endpoint de Health Check
@app.route('/health', methods=['GET'])
def health_check():
    """Health check del sistema"""
    bus_status = 'connected' if bus_client and bus_client._is_connected() else 'disconnected'
    
    return jsonify({
        'status': 'healthy',
        'service': 'api_gateway',
        'bus_status': bus_status,
        'timestamp': datetime.now().isoformat()
    }), 200

# Endpoint de prueba
@app.route('/test', methods=['GET'])
def test():
    """Endpoint de prueba"""
    return jsonify({
        'message': 'MediConnect API Gateway funcionando',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    # Inicializar cliente del bus
    if init_bus_client():
        port = settings.API_GATEWAY_PORT
        logger.info(f"🌐 Iniciando servidor Flask en puerto {port}")
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
    else:
        logger.error("❌ No se pudo iniciar el API Gateway")
