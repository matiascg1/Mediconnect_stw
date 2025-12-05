# Usuarios de MediConnect - Guía de Base de Datos

## 🔐 Usuarios Pre-configurados

La base de datos incluye los siguientes usuarios de prueba (contraseña para todos: **admin123**):

### Administrador
- **Email:** admin@mediconnect.com
- **Contraseña:** admin123
- **Rol:** admin
- **Nombre:** Admin System

### Doctores
1. **Dr. John Smith**
   - **Email:** doctor1@mediconnect.com
   - **Contraseña:** admin123
   - **Especialidad:** Cardiology
   - **Licencia:** LIC12345
   - **Teléfono:** +1234567890

2. **Dra. Maria Garcia**
   - **Email:** doctor2@mediconnect.com
   - **Contraseña:** admin123
   - **Especialidad:** Pediatrics
   - **Licencia:** LIC67890
   - **Teléfono:** +1234567891

### Pacientes
1. **Alice Johnson**
   - **Email:** patient1@mediconnect.com
   - **Contraseña:** admin123
   - **Fecha de Nacimiento:** 1990-01-15
   - **Teléfono:** +1234567892
   - **Dirección:** 123 Main St, City

2. **Bob Williams**
   - **Email:** patient2@mediconnect.com
   - **Contraseña:** admin123
   - **Fecha de Nacimiento:** 1985-05-20
   - **Teléfono:** +1234567893
   - **Dirección:** 456 Oak Ave, Town

---

## 🗄️ Comandos SQL Útiles

### Ver todos los usuarios
\`\`\`sql
USE mediconnect_db;
SELECT id, email, first_name, last_name, role, specialty, is_active FROM users;
\`\`\`

### Ver usuarios por rol
\`\`\`sql
-- Solo doctores
SELECT id, email, first_name, last_name, specialty, license_number 
FROM users WHERE role = 'doctor';

-- Solo pacientes
SELECT id, email, first_name, last_name, date_of_birth, phone_number 
FROM users WHERE role = 'patient';

-- Solo administradores
SELECT id, email, first_name, last_name FROM users WHERE role = 'admin';
\`\`\`

### Agregar un nuevo doctor
\`\`\`sql
INSERT INTO users (
    email, 
    password_hash, 
    first_name, 
    last_name, 
    role, 
    specialty, 
    license_number, 
    phone_number, 
    is_active
)
VALUES (
    'nuevo.doctor@mediconnect.com',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  -- admin123
    'Carlos',
    'Rodriguez',
    'doctor',
    'Neurología',
    'LIC99999',
    '+1234567899',
    TRUE
);
\`\`\`

### Agregar un nuevo paciente
\`\`\`sql
INSERT INTO users (
    email, 
    password_hash, 
    first_name, 
    last_name, 
    role, 
    date_of_birth, 
    phone_number, 
    address, 
    is_active
)
VALUES (
    'nuevo.paciente@mediconnect.com',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  -- admin123
    'Laura',
    'Martinez',
    'patient',
    '1995-03-10',
    '+1234567898',
    '789 Pine St, Village',
    TRUE
);
\`\`\`

### Agregar un nuevo administrador
\`\`\`sql
INSERT INTO users (
    email, 
    password_hash, 
    first_name, 
    last_name, 
    role, 
    is_active
)
VALUES (
    'nuevo.admin@mediconnect.com',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  -- admin123
    'Super',
    'Admin',
    'admin',
    TRUE
);
\`\`\`

### Actualizar información de un usuario
\`\`\`sql
-- Actualizar teléfono
UPDATE users SET phone_number = '+9876543210' WHERE email = 'patient1@mediconnect.com';

-- Actualizar contraseña (hash para 'newpassword123')
UPDATE users SET password_hash = '$2b$12$NewHashHereExample' WHERE email = 'doctor1@mediconnect.com';

-- Actualizar especialidad de un doctor
UPDATE users SET specialty = 'Cardiología Pediátrica' WHERE email = 'doctor1@mediconnect.com';

-- Desactivar un usuario
UPDATE users SET is_active = FALSE WHERE email = 'patient2@mediconnect.com';

-- Activar un usuario
UPDATE users SET is_active = TRUE WHERE email = 'patient2@mediconnect.com';
\`\`\`

### Eliminar un usuario (⚠️ Cuidado)
\`\`\`sql
-- Eliminar por email
DELETE FROM users WHERE email = 'usuario@eliminar.com';

-- Eliminar por ID
DELETE FROM users WHERE id = 5;
\`\`\`

### Ver estadísticas de usuarios
\`\`\`sql
-- Contar usuarios por rol
SELECT role, COUNT(*) as total FROM users GROUP BY role;

-- Usuarios activos vs inactivos
SELECT 
    is_active,
    COUNT(*) as total,
    CONCAT(ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM users), 2), '%') as porcentaje
FROM users 
GROUP BY is_active;

-- Doctores por especialidad
SELECT specialty, COUNT(*) as total 
FROM users 
WHERE role = 'doctor' 
GROUP BY specialty;
\`\`\`

---

## 🐳 Comandos Docker para acceder a MySQL

### Conectarse a la base de datos desde Docker
\`\`\`bash
# Ver contenedores corriendo
docker ps

# Conectarse al contenedor de MySQL
docker exec -it mysql_container mysql -u root -p

# Cuando pida la contraseña, ingresa: root_password
# (o la contraseña que configuraste en docker-compose.yml)
\`\`\`

### Desde dentro del contenedor MySQL
\`\`\`sql
-- Seleccionar la base de datos
USE mediconnect_db;

-- Ver todas las tablas
SHOW TABLES;

-- Ver estructura de la tabla users
DESCRIBE users;

-- Ejecutar cualquier query de arriba
SELECT * FROM users;
\`\`\`

### Exportar/Importar datos

#### Exportar usuarios a un archivo
\`\`\`bash
docker exec mysql_container mysqldump -u root -proot_password mediconnect_db users > usuarios_backup.sql
\`\`\`

#### Importar usuarios desde un archivo
\`\`\`bash
docker exec -i mysql_container mysql -u root -proot_password mediconnect_db < usuarios_backup.sql
\`\`\`

---

## 🔑 Nota sobre Contraseñas

El hash de contraseña usado en los ejemplos corresponde a: **admin123**

Hash: `$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW`

Para generar un nuevo hash de contraseña en Python (bcrypt):
\`\`\`python
import bcrypt
password = "mi_contraseña".encode('utf-8')
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
print(hashed.decode('utf-8'))
\`\`\`

---

## 📊 Comandos de Inicialización

### Reinicializar la base de datos desde Docker
\`\`\`bash
# Desde el directorio raíz del proyecto
docker-compose down -v  # Elimina volúmenes (⚠️ ELIMINA TODOS LOS DATOS)
docker-compose up -d mysql redis  # Levanta MySQL y Redis
docker-compose exec api_gateway python -m backend.scripts.init_database  # Inicializa DB
\`\`\`

### Ver logs de inicialización
\`\`\`bash
docker-compose logs api_gateway
docker-compose logs mysql
\`\`\`

---

## 🚀 Inicio Rápido

1. **Iniciar contenedores:**
   \`\`\`bash
   docker-compose up -d
   \`\`\`

2. **Acceder a MySQL:**
   \`\`\`bash
   docker exec -it mysql_container mysql -u root -proot_password mediconnect_db
   \`\`\`

3. **Ver usuarios:**
   \`\`\`sql
   SELECT id, email, first_name, last_name, role FROM users;
   \`\`\`

4. **Probar login en el frontend:**
   - Ve a http://localhost (o la URL de tu frontend)
   - Usa cualquier email de arriba con contraseña: `admin123`
