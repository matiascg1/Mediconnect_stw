-- Base de datos Mediconnect
CREATE DATABASE IF NOT EXISTS mediconnect_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE mediconnect_db;

-- Tabla Usuarios
CREATE TABLE IF NOT EXISTS Usuarios (
    idUsuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    rut VARCHAR(20) UNIQUE NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    rol ENUM('paciente', 'medico', 'administrativo') NOT NULL DEFAULT 'paciente',
    especialidad VARCHAR(100),
    estado ENUM('activo', 'bloqueado') DEFAULT 'activo',
    intentos_fallidos INT DEFAULT 0,
    ultimo_login TIMESTAMP NULL,
    ultimo_intento_fallido TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_rol (rol),
    INDEX idx_estado (estado),
    INDEX idx_correo (correo)
);

-- Tabla Actividad Usuarios
CREATE TABLE IF NOT EXISTS ActividadUsuarios (
    idActividad INT AUTO_INCREMENT PRIMARY KEY,
    usuarioId INT NOT NULL,
    accion VARCHAR(50) NOT NULL,
    detalles TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuarioId) REFERENCES Usuarios(idUsuario) ON DELETE CASCADE,
    INDEX idx_usuario (usuarioId),
    INDEX idx_created_at (created_at)
);

-- Tabla Citas
CREATE TABLE IF NOT EXISTS Citas (
    idCita INT AUTO_INCREMENT PRIMARY KEY,
    pacienteId INT NOT NULL,
    medicoId INT NOT NULL,
    fechaHora DATETIME NOT NULL,
    motivo VARCHAR(200),
    estado ENUM('agendada', 'confirmada', 'completada', 'cancelada') DEFAULT 'agendada',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pacienteId) REFERENCES Usuarios(idUsuario) ON DELETE CASCADE,
    FOREIGN KEY (medicoId) REFERENCES Usuarios(idUsuario) ON DELETE CASCADE,
    INDEX idx_paciente (pacienteId),
    INDEX idx_medico (medicoId),
    INDEX idx_fecha (fechaHora),
    INDEX idx_estado (estado),
    UNIQUE KEY idx_medico_fecha (medicoId, fechaHora)
);

-- Tabla Consultas
CREATE TABLE IF NOT EXISTS Consultas (
    idConsulta INT AUTO_INCREMENT PRIMARY KEY,
    citaId INT NOT NULL UNIQUE,
    notas TEXT,
    diagnostico TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (citaId) REFERENCES Citas(idCita) ON DELETE CASCADE,
    INDEX idx_cita (citaId)
);

-- Tabla Recetas
CREATE TABLE IF NOT EXISTS Recetas (
    idReceta INT AUTO_INCREMENT PRIMARY KEY,
    consultaId INT NOT NULL,
    pacienteId INT NOT NULL,
    medicoId INT NOT NULL,
    fechaEmision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    detalleMedicamentos JSON,
    firmaDigital VARCHAR(255),
    FOREIGN KEY (consultaId) REFERENCES Consultas(idConsulta) ON DELETE CASCADE,
    FOREIGN KEY (pacienteId) REFERENCES Usuarios(idUsuario) ON DELETE CASCADE,
    FOREIGN KEY (medicoId) REFERENCES Usuarios(idUsuario) ON DELETE CASCADE,
    INDEX idx_consulta (consultaId),
    INDEX idx_paciente (pacienteId),
    INDEX idx_medico (medicoId)
);

-- Usuarios iniciales
INSERT IGNORE INTO Usuarios (nombre, rut, correo, telefono, password_hash, rol, especialidad, estado) VALUES
('Administrador Sistema', '11111111-1', 'admin@mediconnect.cl', '+56912345678', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'administrativo', NULL, 'activo'),
('Dr. Juan Pérez', '22222222-2', 'dr.juan@mediconnect.cl', '+56923456789', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'medico', 'Medicina General', 'activo'),
('Dra. María González', '33333333-3', 'dra.maria@mediconnect.cl', '+56934567890', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'medico', 'Pediatría', 'activo'),
('Paciente Demo', '44444444-4', 'paciente@mediconnect.cl', '+56945678901', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'paciente', NULL, 'activo');

-- Citas de ejemplo
INSERT IGNORE INTO Citas (pacienteId, medicoId, fechaHora, motivo, estado) VALUES
(4, 2, DATE_ADD(NOW(), INTERVAL 1 DAY), 'Control rutinario', 'agendada'),
(4, 3, DATE_ADD(NOW(), INTERVAL 2 DAY), 'Consulta pediátrica', 'confirmada');

-- Permisos
GRANT ALL PRIVILEGES ON mediconnect_db.* TO 'mediconnect'@'%';
FLUSH PRIVILEGES;
