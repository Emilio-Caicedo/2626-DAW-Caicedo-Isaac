-- EmiTech Store - Migración de la Semana 14
-- Ejecute este archivo una sola vez sobre la base creada en la Semana 13.

USE emitech_store;

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    nombre_completo VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- La columna password_hash debe mostrar una cadena larga, nunca la clave real.
SELECT id_usuario, usuario, nombre_completo, password_hash, activo, creado_en
FROM usuarios
ORDER BY id_usuario;
