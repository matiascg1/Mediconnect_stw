# MediConnect - Healthcare Management System

Sistema de gestión médica con arquitectura de microservicios.

## Estructura del Proyecto

\`\`\`
proyectomc/
├── backend/                 # Microservicios backend (Python/Flask)
│   ├── api_gateway/        # API Gateway principal
│   ├── services/           # Microservicios
│   │   ├── auth_service/   # Autenticación y autorización
│   │   ├── user_service/   # Gestión de usuarios
│   │   ├── appointment_service/  # Gestión de citas
│   │   ├── ehr_service/    # Historias clínicas electrónicas
│   │   ├── prescription_service/  # Prescripciones médicas
│   │   └── admin_service/  # Administración del sistema
│   ├── bus/                # Sistema de mensajería (Redis)
│   ├── database/           # Modelos y conexiones a DB
│   ├── config/             # Configuración centralizada
│   └── utils/              # Utilidades compartidas
├── frontend/               # Frontend React/Vite
│   └── src/
│       ├── components/     # Componentes reutilizables
│       ├── pages/          # Páginas de la aplicación
│       ├── services/       # Servicios API
│       └── contexts/       # Contextos de React
└── docker-compose.yml      # Configuración de Docker
\`\`\`

## Tecnologías

- **Backend**: Python 3.11, Flask, MySQL, Redis
- **Frontend**: React 18, TypeScript, Vite, TailwindCSS
- **Infraestructura**: Docker, Docker Compose

## Variables de Entorno

Las variables de entorno están definidas en el archivo `.env` en la raíz del proyecto:

- **Base de datos**: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
- **JWT**: JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
- **Puertos de servicios**: API_GATEWAY_PORT (8000), AUTH_SERVICE_PORT (8001), etc.
- **Message Bus**: MESSAGE_BUS_HOST (redis), MESSAGE_BUS_PORT (6379)

## Instalación y Ejecución

### Con Docker (Recomendado)

\`\`\`bash
# Clonar el repositorio
git clone <repository-url>
cd proyectomc

# Construir y ejecutar todos los servicios
docker-compose up --build

# El frontend estará disponible en http://localhost:3000
# El API Gateway estará disponible en http://localhost:8000
\`\`\`

### Desarrollo Local

#### Backend

\`\`\`bash
cd backend
pip install -r requirements.txt
python -m api_gateway.main
\`\`\`

#### Frontend

\`\`\`bash
cd frontend
npm install
npm run dev
\`\`\`

## Endpoints Principales

### Autenticación
- `POST /api/auth/register` - Registro de usuarios
- `POST /api/auth/login` - Inicio de sesión
- `GET /api/auth/verify` - Verificar token

### Usuarios
- `GET /api/users/:id` - Obtener usuario por ID
- `GET /api/users` - Listar todos los usuarios (admin)

### Citas
- `POST /api/appointments` - Crear nueva cita
- `GET /api/appointments/user/:id` - Obtener citas de un usuario
- `PUT /api/appointments/:id/status` - Actualizar estado de cita

## Roles de Usuario

- **paciente**: Puede crear y ver sus propias citas
- **medico**: Puede ver citas asignadas y actualizar estados
- **administrativo**: Acceso completo al sistema

## Contribución

1. Fork el proyecto
2. Crea tu rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT.
