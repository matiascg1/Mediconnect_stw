#!/bin/bash

# Esperar a que MySQL esté listo
echo "Esperando a que MySQL esté listo..."
while ! mysqladmin ping -h"localhost" --silent; do
    sleep 1
done

echo "MySQL está listo. Inicializando base de datos..."

# Ejecutar script SQL de inicialización
mysql -u root -prootpassword <<EOF
-- Crear base de datos
CREATE DATABASE IF NOT EXISTS mediconnect_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Crear usuario
CREATE USER IF NOT EXISTS 'mediconnect'@'%' IDENTIFIED BY 'mediconnect123';
GRANT ALL PRIVILEGES ON mediconnect_db.* TO 'mediconnect'@'%';
FLUSH PRIVILEGES;

-- Usar la base de datos
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
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
    FOREIGN KEY (pacienteId) REFERENCES Usuarios(idUsuario),
    FOREIGN KEY (medicoId) REFERENCES Usuarios(idUsuario),
    INDEX idx_paciente (pacienteId),
    INDEX idx_medico (medicoId),
    INDEX idx_fecha (fechaHora)
);

-- Tabla Consultas
CREATE TABLE IF NOT EXISTS Consultas (
    idConsulta INT AUTO_INCREMENT PRIMARY KEY,
    citaId INT NOT NULL UNIQUE,
    notas TEXT,
    diagnostico TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (citaId) REFERENCES Citas(idCita)
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
    FOREIGN KEY (consultaId) REFERENCES Consultas(idConsulta),
    FOREIGN KEY (pacienteId) REFERENCES Usuarios(idUsuario),
    FOREIGN KEY (medicoId) REFERENCES Usuarios(idUsuario)
);

-- Insertar datos iniciales
INSERT IGNORE INTO Usuarios (nombre, rut, correo, telefono, password_hash, rol, estado) VALUES
('Admin Sistema', '11111111-1', 'admin@mediconnect.cl', '+56912345678', '\$2b\$12\$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'administrativo', 'activo'),
('Dr. Ricardo', '22222222-2', 'dr.ricardo@mediconnect.cl', '+56987654321', '\$2b\$12\$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'medico', 'activo'),
('Paciente Demo', '33333333-3', 'paciente@mediconnect.cl', '+56955555555', '\$2b\$12\$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'paciente', 'activo');

-- Actualizar especialidad del médico
UPDATE Usuarios SET especialidad = 'Medicina General' WHERE rol = 'medico';

EOF

echo "Base de datos inicializada exitosamente!"
