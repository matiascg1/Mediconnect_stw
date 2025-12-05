@echo off
echo ========================================
echo    Mediconnect Setup Script
echo ========================================
echo.

REM Check if .env exists, if not create from .env.example
if not exist .env (
    if exist .env.example (
        echo [INFO] Creating .env file from .env.example
        copy .env.example .env
        echo [INFO] .env file created successfully
        echo.
        echo [IMPORTANT] Please review the .env file and modify if needed
        echo.
    ) else (
        echo [ERROR] .env.example file not found!
        echo Creating a new .env file with default values...
        
        echo # Database Configuration> .env
        echo DB_HOST=mysql>> .env
        echo DB_PORT=3306>> .env
        echo DB_USER=mediconnect_user>> .env
        echo DB_PASSWORD=mediconnect_password>> .env
        echo DB_NAME=mediconnect_db>> .env
        echo.>> .env
        echo # JWT Configuration>> .env
        echo JWT_SECRET=dev-jwt-secret-key-change-in-production>> .env
        echo JWT_ALGORITHM=HS256>> .env
        echo ACCESS_TOKEN_EXPIRE_MINUTES=30>> .env
        echo.>> .env
        echo # Service Ports>> .env
        echo AUTH_SERVICE_PORT=8001>> .env
        echo USER_SERVICE_PORT=8002>> .env
        echo APPOINTMENT_SERVICE_PORT=8003>> .env
        echo EHR_SERVICE_PORT=8004>> .env
        echo PRESCRIPTION_SERVICE_PORT=8005>> .env
        echo ADMIN_SERVICE_PORT=8006>> .env
        echo API_GATEWAY_PORT=8000>> .env
        echo.>> .env
        echo # Message Bus (Redis)>> .env
        echo MESSAGE_BUS_HOST=redis>> .env
        echo MESSAGE_BUS_PORT=6379>> .env
        echo.>> .env
        echo # Environment>> .env
        echo ENVIRONMENT=development>> .env
        
        echo [INFO] .env file created with default values
    )
)

REM Check if Docker is running
echo [INFO] Checking if Docker is running...
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)
echo [OK] Docker is running
echo.

REM Stop and remove existing containers
echo [INFO] Cleaning up existing containers...
docker-compose down -v >nul 2>&1
echo [OK] Old containers removed
echo.

REM Build Docker images
echo [INFO] Building Docker images (this may take a few minutes)...
docker-compose build
if errorlevel 1 (
    echo [ERROR] Failed to build Docker images
    pause
    exit /b 1
)
echo [OK] Docker images built successfully
echo.

REM Start containers
echo [INFO] Starting Docker containers...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] Failed to start containers
    pause
    exit /b 1
)
echo [OK] Containers started successfully
echo.

REM Wait for services to initialize
echo [INFO] Waiting for services to initialize (30 seconds)...
timeout /t 30 /nobreak >nul
echo.

REM Check service status
echo ========================================
echo    Service Status
echo ========================================
echo.

REM Check MySQL
echo Checking MySQL...
docker ps --filter "name=mediconnect_mysql" --format "table {{.Names}}\t{{.Status}}" | findstr "mysql" >nul
if errorlevel 1 (
    echo [ERROR] MySQL is not running
    echo To view logs: docker logs mediconnect_mysql
) else (
    echo [OK] MySQL is running
)

REM Check Redis
echo Checking Redis...
docker ps --filter "name=mediconnect_redis" --format "table {{.Names}}\t{{.Status}}" | findstr "redis" >nul
if errorlevel 1 (
    echo [ERROR] Redis is not running
) else (
    echo [OK] Redis is running
)

REM Check API Gateway
echo Checking API Gateway...
docker ps --filter "name=mediconnect_api_gateway" --format "table {{.Names}}\t{{.Status}}" | findstr "api_gateway" >nul
if errorlevel 1 (
    echo [ERROR] API Gateway is not running
) else (
    echo [OK] API Gateway is running
)

echo.
echo ========================================
echo    Setup Complete!
echo ========================================
echo.
echo [ACCESS INFORMATION]
echo API Gateway: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo MySQL Port: 3307
echo Redis Port: 6379
echo.
echo [DEFAULT CREDENTIALS]
echo Admin: admin@mediconnect.com / admin123
echo Doctor: doctor1@mediconnect.com / admin123
echo Patient: patient1@mediconnect.com / admin123
echo.
echo [USEFUL COMMANDS]
echo View all logs: docker-compose logs
echo View specific service logs: docker logs [service_name]
echo Stop all services: docker-compose down
echo Restart services: docker-compose restart
echo Rebuild and restart: docker-compose up --build -d
echo.
echo ========================================
echo.
pause
