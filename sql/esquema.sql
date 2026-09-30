CREATE DATABASE IF NOT EXISTS emitech_store
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE emitech_store;

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    nombre_completo VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS proveedores (
    id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(7) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    correo VARCHAR(120) NOT NULL,
    ciudad VARCHAR(60) NOT NULL,
    categoria VARCHAR(180) NOT NULL,
    entrega_dias INT NOT NULL,
    CONSTRAINT chk_proveedor_entrega CHECK (entrega_dias BETWEEN 1 AND 60)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(7) NOT NULL UNIQUE,
    nombre VARCHAR(80) NOT NULL,
    categoria VARCHAR(60) NOT NULL,
    descripcion VARCHAR(250) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    imagen VARCHAR(120) NOT NULL,
    id_proveedor INT NOT NULL,
    CONSTRAINT chk_producto_precio CHECK (precio > 0),
    CONSTRAINT chk_producto_stock CHECK (stock >= 0),
    CONSTRAINT fk_producto_proveedor
        FOREIGN KEY (id_proveedor)
        REFERENCES proveedores (id_proveedor)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(7) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    cedula VARCHAR(10) UNIQUE,
    telefono VARCHAR(20),
    correo VARCHAR(120) NOT NULL,
    ciudad VARCHAR(60) NOT NULL,
    tipo VARCHAR(30) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS facturas (
    id_factura INT AUTO_INCREMENT PRIMARY KEY,
    numero VARCHAR(8) NOT NULL UNIQUE,
    id_cliente INT NOT NULL,
    fecha DATE NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    impuesto DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_factura_cliente
        FOREIGN KEY (id_cliente)
        REFERENCES clientes (id_cliente)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS detalle_factura (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_factura INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    CONSTRAINT chk_detalle_cantidad CHECK (cantidad > 0),
    CONSTRAINT fk_detalle_factura
        FOREIGN KEY (id_factura)
        REFERENCES facturas (id_factura)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_detalle_producto
        FOREIGN KEY (id_producto)
        REFERENCES productos (id_producto)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

INSERT IGNORE INTO proveedores
    (codigo, nombre, telefono, correo, ciudad, categoria, entrega_dias)
VALUES
    ('PRV-001', 'LUSANCOMP', '022345678', 'ventas@lusancomp.com', 'Quito',
     'Laptops, computadoras y componentes informáticos.', 3),
    ('PRV-002', 'MAXXICOMP', '042345678', 'ventasenlinea@maxxicomp.com', 'Guayaquil',
     'Hardware, periféricos y accesorios tecnológicos.', 5),
    ('PRV-003', 'PC MAX TECNOLOGIA', '023456789', 'contacto@pcmax.com.ec', 'Quito',
     'Componentes, computadoras y accesorios tecnológicos.', 3);

INSERT IGNORE INTO productos
    (codigo, nombre, categoria, descripcion, precio, stock, imagen, id_proveedor)
VALUES
    ('PRO-001', 'Laptop para estudio', 'Laptops y computadoras',
     'Pantalla de 15,6 pulgadas, 8 GB de RAM y SSD de 512 GB.', 550.00, 8,
     'laptop-estudio.jpg', (SELECT id_proveedor FROM proveedores WHERE codigo = 'PRV-001')),
    ('PRO-002', 'Computadora de escritorio', 'Laptops y computadoras',
     'Equipo para oficina con 16 GB de RAM y SSD de 512 GB.', 680.00, 5,
     'computadora-escritorio.jpg', (SELECT id_proveedor FROM proveedores WHERE codigo = 'PRV-001')),
    ('PRO-003', 'Teclado y mouse', 'Accesorios tecnológicos',
     'Kit USB para las actividades diarias de estudio y trabajo.', 25.00, 20,
     'teclado-mouse.jpg', (SELECT id_proveedor FROM proveedores WHERE codigo = 'PRV-002')),
    ('PRO-004', 'Audífonos con micrófono', 'Accesorios tecnológicos',
     'Accesorio para clases virtuales, reuniones y llamadas.', 30.00, 12,
     'audifonos.jpg', (SELECT id_proveedor FROM proveedores WHERE codigo = 'PRV-002')),
    ('PRO-005', 'Memoria RAM de 8 GB', 'Componentes informáticos',
     'Módulo DDR4 para equipos compatibles.', 28.00, 15,
     'memoria-ram.jpg', (SELECT id_proveedor FROM proveedores WHERE codigo = 'PRV-003')),
    ('PRO-006', 'Disco SSD de 480 GB', 'Componentes informáticos',
     'Unidad SATA para mejorar el almacenamiento del equipo.', 45.00, 0,
     'disco-ssd.jpg', (SELECT id_proveedor FROM proveedores WHERE codigo = 'PRV-003'));

INSERT IGNORE INTO clientes
    (codigo, nombre, cedula, telefono, correo, ciudad, tipo)
VALUES
    ('CLI-001', 'CARLOS SEGUNDO ARCE BATALLAS', NULL, NULL, 'cs.arceb@uea.edu.ec', 'Puyo', 'Estudiante'),
    ('CLI-002', 'JORDAN ALEXANDER ARRIAGA LOGRONO', NULL, NULL, 'ja.arriagal@uea.edu.ec', 'Tena', 'Profesional'),
    ('CLI-003', 'XAVIER ALEXANDER CASA LEMA', NULL, NULL, 'xa.casal@uea.edu.ec', 'El Reventador', 'Emprendimiento'),
    ('CLI-004', 'CRISTIAN DAVID CHIQUIMBA MENA', NULL, NULL, 'cd.chiquimbam@uea.edu.ec', 'Nueva Loja', 'Empresa');

-- Consultas de comprobación para MySQL Workbench.
SELECT id_usuario, usuario, nombre_completo, password_hash, activo, creado_en
FROM usuarios
ORDER BY id_usuario;
SELECT * FROM proveedores ORDER BY id_proveedor;
SELECT * FROM productos ORDER BY id_producto;
SELECT
    p.id_producto,
    p.codigo,
    p.nombre AS producto,
    p.precio,
    p.stock,
    pr.nombre AS proveedor
FROM productos AS p
INNER JOIN proveedores AS pr
    ON pr.id_proveedor = p.id_proveedor
ORDER BY p.id_producto;
