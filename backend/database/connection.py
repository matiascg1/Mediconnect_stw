"""
Módulo de conexión a la base de datos MySQL.
"""
import mysql.connector
import os
import logging
from typing import Optional
from mysql.connector import pooling
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pool de conexiones global
_connection_pool: Optional[mysql.connector.pooling.MySQLConnectionPool] = None

def init_connection_pool():
    """Inicializa el pool de conexiones a la base de datos."""
    global _connection_pool
    
    try:
        # Configuración de la base de datos desde variables de entorno
        db_config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', 3306)),
            'user': os.getenv('MYSQL_USER', 'mediconnect'),
            'password': os.getenv('MYSQL_PASSWORD', 'mediconnect123'),
            'database': os.getenv('MYSQL_DATABASE', 'mediconnect_db'),
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci',
            'use_unicode': True,
            'autocommit': False,
            'pool_name': 'mediconnect_pool',
            'pool_size': 10,
            'pool_reset_session': True
        }
        
        _connection_pool = mysql.connector.pooling.MySQLConnectionPool(**db_config)
        
        logger.info(f"✅ Pool de conexiones MySQL inicializado: {db_config['host']}:{db_config['port']}/{db_config['database']}")
        
        # Probar conexión
        with get_db_connection() as test_conn:
            test_cursor = test_conn.cursor()
            test_cursor.execute("SELECT 1")
            test_cursor.fetchone()
            test_cursor.close()
        
        logger.info("✅ Conexión a MySQL probada exitosamente")
        
    except mysql.connector.Error as e:
        logger.error(f"❌ Error inicializando pool de conexiones: {e}")
        raise

@contextmanager
def get_db_connection():
    """
    Obtiene una conexión del pool.
    
    Uso:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            # ... operaciones con la base de datos ...
            connection.commit()
    """
    global _connection_pool
    
    if _connection_pool is None:
        init_connection_pool()
    
    connection = None
    try:
        connection = _connection_pool.get_connection()
        yield connection
    except mysql.connector.Error as e:
        logger.error(f"❌ Error obteniendo conexión del pool: {e}")
        raise
    finally:
        if connection:
            connection.close()

def execute_query(query: str, params: tuple = None, fetch_one: bool = False):
    """
    Ejecuta una consulta y retorna los resultados.
    
    Args:
        query: Consulta SQL
        params: Parámetros para la consulta
        fetch_one: Si True, retorna solo una fila
    
    Returns:
        Resultados de la consulta
    """
    with get_db_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith('SELECT'):
                if fetch_one:
                    result = cursor.fetchone()
                else:
                    result = cursor.fetchall()
            else:
                connection.commit()
                result = cursor.rowcount
            
            return result
        except mysql.connector.Error as e:
            connection.rollback()
            logger.error(f"❌ Error ejecutando query: {e}")
            raise
        finally:
            cursor.close()

def execute_many(query: str, params_list: list):
    """
    Ejecuta una consulta múltiples veces con diferentes parámetros.
    
    Args:
        query: Consulta SQL
        params_list: Lista de tuplas de parámetros
    """
    with get_db_connection() as connection:
        cursor = connection.cursor()
        try:
            cursor.executemany(query, params_list)
            connection.commit()
            return cursor.rowcount
        except mysql.connector.Error as e:
            connection.rollback()
            logger.error(f"❌ Error ejecutando many: {e}")
            raise
        finally:
            cursor.close()

def check_database_connection() -> bool:
    """Verifica si se puede establecer conexión con la base de datos."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
    except Exception as e:
        logger.error(f"❌ Error verificando conexión a base de datos: {e}")
        return False

def get_database_stats() -> dict:
    """Obtiene estadísticas de la base de datos."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Obtener tamaño de base de datos
            cursor.execute("""
                SELECT 
                    table_schema as database_name,
                    SUM(data_length + index_length) / 1024 / 1024 as size_mb,
                    COUNT(*) as table_count
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
                GROUP BY table_schema
            """)
            db_stats = cursor.fetchone()
            
            # Obtener conteo de tablas principales
            cursor.execute("SELECT COUNT(*) as total FROM Usuarios")
            users_count = cursor.fetchone()
            
            cursor.execute("SELECT COUNT(*) as total FROM Citas")
            appointments_count = cursor.fetchone()
            
            cursor.execute("SELECT COUNT(*) as total FROM Consultas")
            consultations_count = cursor.fetchone()
            
            cursor.execute("SELECT COUNT(*) as total FROM Recetas")
            prescriptions_count = cursor.fetchone()
            
            cursor.close()
            
            return {
                'database': {
                    'name': db_stats['database_name'] if db_stats else 'unknown',
                    'size_mb': round(db_stats['size_mb'], 2) if db_stats and db_stats['size_mb'] else 0,
                    'table_count': db_stats['table_count'] if db_stats else 0
                },
                'counts': {
                    'usuarios': users_count['total'] if users_count else 0,
                    'citas': appointments_count['total'] if appointments_count else 0,
                    'consultas': consultations_count['total'] if consultations_count else 0,
                    'recetas': prescriptions_count['total'] if prescriptions_count else 0
                },
                'pool': {
                    'pool_size': _connection_pool.pool_size if _connection_pool else 0,
                    'active_connections': len(_connection_pool._cnx_queue) if _connection_pool else 0
                } if _connection_pool else {}
            }
            
    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas de base de datos: {e}")
        return {}

def close_pool():
    """Cierra el pool de conexiones."""
    global _connection_pool
    
    if _connection_pool:
        _connection_pool._remove_connections()
        _connection_pool = None
        logger.info("✅ Pool de conexiones cerrado")

# Inicializar pool al importar el módulo
try:
    init_connection_pool()
except Exception as e:
    logger.warning(f"⚠️  No se pudo inicializar el pool de conexiones: {e}")
