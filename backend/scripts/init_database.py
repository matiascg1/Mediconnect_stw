import mysql.connector
import os
import sys
from backend.config.settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database with schema and sample data"""
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
        
        cursor = connection.cursor()
        
        # Create database if not exists
        logger.info("Creating database...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME}")
        cursor.execute(f"USE {settings.DB_NAME}")
        
        # Read and execute SQL file
        sql_file = os.path.join(os.path.dirname(__file__), '../../init-database.sql')
        
        with open(sql_file, 'r') as file:
            sql_commands = file.read().split(';')
            
            for command in sql_commands:
                if command.strip():
                    try:
                        cursor.execute(command)
                    except Exception as e:
                        logger.warning(f"Error executing command: {e}")
        
        connection.commit()
        logger.info("Database initialized successfully!")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()
