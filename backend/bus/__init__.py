"""
Módulo del bus de mensajería para comunicación entre servicios.
PARCHE DE EMERGENCIA - Versión debug
"""
import logging
logging.basicConfig(level=logging.DEBUG)

from .bus_server import BusServer
from .bus_client import BusClient

__all__ = ['BusServer', 'BusClient']