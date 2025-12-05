"""
Punto de entrada del servicio de autenticación.
"""
import sys
import os
import time
import signal
import threading
from utils.logger import get_logger

# Agregar directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from bus.bus_client import BusClient
from .handlers import (
    handle_register, handle_login, handle_verify_token, handle_refresh_token,
    handle_change_password, handle_logout, handle_reset_password_request,
    handle_reset_password, handle_get_user, handle_health_check, set_bus_client
)

logger = get_logger(__name__)

class AuthServiceApp:
    """Aplicación del servicio de autenticación."""
    
    def __init__(self):
        self.service_name = "authsv"
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
        logger.info("🎯 Registrando handlers del servicio de autenticación")
        
        self.bus_client.register_callback("register", handle_register)
        self.bus_client.register_callback("login", handle_login)
        self.bus_client.register_callback("verify_token", handle_verify_token)
        self.bus_client.register_callback("refresh_token", handle_refresh_token)
        self.bus_client.register_callback("change_password", handle_change_password)
        self.bus_client.register_callback("logout", handle_logout)
        self.bus_client.register_callback("reset_password_request", handle_reset_password_request)
        self.bus_client.register_callback("reset_password", handle_reset_password)
        self.bus_client.register_callback("get_user", handle_get_user)
        self.bus_client.register_callback("health_check", handle_health_check)
        
        # Configurar el bus client en el servicio
        set_bus_client(self.bus_client)
        
        logger.info("✅ Todos los handlers registrados")
    
    def start(self):
        """Inicia el servicio de autenticación."""
        logger.info(f"🚀 Iniciando servicio de autenticación '{self.service_name}'...")
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
                    logger.info(f"✅ Servicio de autenticación '{self.service_name}' conectado al bus")
                    
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
        logger.info("⏳ Servicio de autenticación en ejecución...")
        
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
        logger.info("🛑 Deteniendo servicio de autenticación...")
        self.running = False
        
        if self.bus_client:
            self.bus_client.disconnect()
        
        logger.info("✅ Servicio de autenticación detenido")

def main():
    """Función principal para ejecutar el servicio."""
    app = AuthServiceApp()
    app.start()

if __name__ == "__main__":
    main()
