import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "mediconnect_user"
    DB_PASSWORD: str = "mediconnect123"
    DB_NAME: str = "mediconnect_db"
    
    # JWT
    JWT_SECRET: str = "mediconnect123"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Service Ports
    AUTH_SERVICE_PORT: int = 8001
    USER_SERVICE_PORT: int = 8002
    APPOINTMENT_SERVICE_PORT: int = 8003
    EHR_SERVICE_PORT: int = 8004
    PRESCRIPTION_SERVICE_PORT: int = 8005
    ADMIN_SERVICE_PORT: int = 8006
    API_GATEWAY_PORT: int = 8000
    
    # Message Bus
    MESSAGE_BUS_HOST: str = "redis"
    MESSAGE_BUS_PORT: int = 6379
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
