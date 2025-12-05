#!/usr/bin/env python3
"""
Servicio de Autenticación - Versión corregida
"""
import os
import sys
import time
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Función principal del servicio de autenticación."""
    service_name = "authsv"
    logger.info(f"🚀🚀🚀 INICIANDO AUTH SERVICE CON BUS CLIENT CORREGIDO")
    
    # Obtener configuración
    bus_host = os.getenv('BUS_HOST', 'bus_server')
    bus_port = int(os.getenv('BUS_PORT', 5000))
    logger.info(f"📡 Conectando al bus en {bus_host}:{bus_port}")
    
    try:
        # Importar el cliente del bus CORRECTO
        sys.path.insert(0, '/app')
        from bus.bus_client import BusClient  # ¡IMPORTANTE!
        
        # Crear cliente del bus
        bus_client = BusClient(
            service_name=service_name,
            host=bus_host,
            port=bus_port
        )
        
        # Intentar conectar
        logger.info("🔄 Intentando conectar...")
        
        if bus_client.connect():
            logger.info("✅✅✅ CONEXIÓN Y REGISTRO EXITOSOS")
            logger.info("🏥 Servicio de autenticación LISTO")
            
            # Mantener el servicio corriendo
            try:
                while True:
                    time.sleep(10)
                    logger.debug("❤️  Servicio activo...")
            except KeyboardInterrupt:
                logger.info("👋 Deteniendo servicio...")
            finally:
                bus_client.disconnect()
        else:
            logger.error("❌❌❌ FALLÓ LA CONEXIÓN")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"💥💥💥 ERROR CRÍTICO: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()