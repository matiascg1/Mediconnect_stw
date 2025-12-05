"""
Punto de entrada del servicio de citas médicas.
"""
import sys
import os
import time
import signal
from utils.logger import get_logger

# Agregar directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from bus.bus_client import BusClient
from .handlers import (
    handle_create_appointment, handle_get_appointments_by_user,
    handle_get_appointment_by_id, handle_update_appointment_status,
    handle_get_doctor_availability, handle_get_appointment_stats,
    handle_reschedule_appointment, handle_health_check, set_bus_client
)

logger = get_logger(__name__)

class AppointmentServiceApp:
    """Aplicación del servicio de citas médicas."""
    
    def __init__(self):
        self.service_name = "appointmentsv"
        self.bus_host = os.getenv("BUS_HOST", "localhost")
        self.bus_port = int(os.getenv("BUS_PORT", 5000))
        self.bus_client = None
        self.running = False
        
    def setup_signal_handlers(self):
        """Configura manejadores de señales."""
        def signal_handler(signum, frame):
            logger.info(f"📛 Recibida señal {signum}, apagando servicio...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def register_handlers(self):
        """Registra todos los handlers en el bus client."""
        logger.info("🎯 Registrando handlers del servicio de citas")
        
        self.bus_client.register_callback("create_appointment", handle_create_appointment)
        self.bus_client.register_callback("get_appointments_by_user", handle_get_appointments_by_user)
        self.bus_client.register_callback("get_appointment_by_id", handle_get_appointment_by_id)
        self.bus_client.register_callback("update_appointment_status", handle_update_appointment_status)
        self.bus_client.register_callback("get_doctor_availability", handle_get_doctor_availability)
        self.bus_client.register_callback("get_appointment_stats", handle_get_appointment_stats)
        self.bus_client.register_callback("reschedule_appointment", handle_reschedule_appointment)
        self.bus_client.register_callback("health_check", handle_health_check)
        
        # Configurar el bus client en el servicio
        set_bus_client(self.bus_client)
        
        logger.info("✅ Todos los handlers registrados")
    
    def start(self):
        """Inicia el servicio de citas."""
        logger.info(f"🚀 Iniciando servicio de citas '{self.service_name}'...")
        logger.info(f"📡 Conectando al bus en {self.bus_host}:{self.bus_port}")
        
        self.setup_signal_handlers()
        
        # Configurar intentos de conexión
        max_retries = 30
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # Crear cliente del bus
                self.bus_client = BusClient(self.service_name, self.bus_host, self.bus_port)
                
                # Configurar callbacks de eventos
                self.bus_client.on_connect = self._on_connect
                self.bus_client.on_disconnect = self._on_disconnect
                self.bus_client.on_error = self._on_error
                
                # Conectar al bus
                if self.bus_client.connect():
                    self.running = True
                    logger.info(f"✅ Servicio de citas '{self.service_name}' conectado al bus")
                    
                    # Registrar handlers
                    self.register_handlers()
                    
                    # Iniciar loop principal
                    self._main_loop()
                    
                    break  # Salir del loop de reintentos si todo va bien
                    
                else:
                    logger.error(f"❌ No se pudo conectar al bus (intento {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                    else:
                        logger.error("❌ Máximo de reintentos alcanzado")
                        sys.exit(1)
                        
            except Exception as e:
                logger.error(f"❌ Error en servicio (intento {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logger.error("❌ Máximo de reintentos alcanzado")
                    sys.exit(1)
    
    def _on_connect(self):
        """Callback cuando se conecta al bus."""
        logger.info("🔗 Conectado exitosamente al bus")
    
    def _on_disconnect(self):
        """Callback cuando se desconecta del bus."""
        logger.warning("🔌 Desconectado del bus")
        self.running = False
    
    def _on_error(self, error_message: str):
        """Callback cuando hay error de conexión."""
        logger.error(f"💥 Error de conexión: {error_message}")
    
    def _main_loop(self):
        """Loop principal del servicio."""
        logger.info("⏳ Servicio de citas en ejecución...")
        
        last_stats_time = time.time()
        stats_interval = 60  # Mostrar stats cada 60 segundos
        
        try:
            while self.running:
                # Pequeña pausa para evitar uso excesivo de CPU
                time.sleep(0.1)
                
                # Mostrar estadísticas periódicamente
                current_time = time.time()
                if current_time - last_stats_time > stats_interval:
                    if self.bus_client:
                        stats = self.bus_client.get_stats()
                        logger.info(f"📊 Estadísticas del servicio: {stats}")
                    last_stats_time = current_time
                    
        except KeyboardInterrupt:
            logger.info("👋 Interrupción por teclado recibida")
        except Exception as e:
            logger.error(f"💥 Error en loop principal: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Detiene el servicio."""
        logger.info("🛑 Deteniendo servicio de citas...")
        self.running = False
        
        if self.bus_client:
            self.bus_client.disconnect()
        
        logger.info("✅ Servicio de citas detenido")

def main():
    """Función principal para ejecutar el servicio."""
    app = AppointmentServiceApp()
    app.start()

if __name__ == "__main__":
    main()
