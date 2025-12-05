"""
Módulo de logging configurado para MediConnect.
"""
import logging
import sys
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

class CustomFormatter(logging.Formatter):
    """Formateador personalizado para logs."""
    
    # Colores para terminal
    grey = "\x1b[38;20m"
    green = "\x1b[32;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    blue = "\x1b[34;20m"
    reset = "\x1b[0m"
    
    # Formatos
    format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    FORMATS = {
        logging.DEBUG: f"{grey}{format_string}{reset}",
        logging.INFO: f"{green}{format_string}{reset}",
        logging.WARNING: f"{yellow}{format_string}{reset}",
        logging.ERROR: f"{red}{format_string}{reset}",
        logging.CRITICAL: f"{bold_red}{format_string}{reset}",
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

def setup_logger(name: str = None, level: str = None) -> logging.Logger:
    """
    Configura y retorna un logger.
    
    Args:
        name: Nombre del logger
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configurado
    """
    # Obtener nivel de logging
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    log_level = getattr(logging, level, logging.INFO)
    
    # Crear logger
    logger_name = name or "mediconnect"
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    
    # Evitar handlers duplicados
    if logger.handlers:
        return logger
    
    # Handler para consola (con colores)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)
    
    # Handler para archivo
    log_dir = os.getenv("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"mediconnect_{timestamp}.log")
    
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)  # Archivo tiene nivel DEBUG
    logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str = None) -> logging.Logger:
    """
    Obtiene un logger configurado.
    
    Args:
        name: Nombre del logger
    
    Returns:
        Logger configurado
    """
    return setup_logger(name)

# Logger root por defecto
logger = get_logger()

if __name__ == "__main__":
    # Ejemplo de uso
    logger.debug("Este es un mensaje de debug")
    logger.info("Este es un mensaje de info")
    logger.warning("Este es un mensaje de warning")
    logger.error("Este es un mensaje de error")
    logger.critical("Este es un mensaje crítico")
