#!/usr/bin/env python3
"""
Punto de entrada principal para el Bus Server.
"""
import sys
import os
import logging

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bus_server import BusServer

def main():
    """Función principal."""
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)
    
    # Obtener configuración de variables de entorno
    host = os.getenv('BUS_HOST', '0.0.0.0')
    port = int(os.getenv('BUS_PORT', 5000))
    
    logger.info(f"🚀 Iniciando Bus Server en {host}:{port}")
    
    try:
        server = BusServer(host=host, port=port)
        server.start()
    except KeyboardInterrupt:
        logger.info("👋 Apagando por interrupción del usuario")
    except Exception as e:
        logger.error(f"💥 Error fatal: {e}")
        raise

if __name__ == "__main__":
    main()