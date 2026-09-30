-- EmiTech Store - Semana 15
-- Ejecutar conectado a la base emitech_store. El script es idempotente.

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario BIGSERIAL PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    nombre_completo VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS proveedores (
    id_proveedor BIGSERIAL PRIMARY KEY,
    codigo VARCHAR(7) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(120) NOT NULL,
    ciudad VARCHAR(60) NOT NULL,
    categoria VARCHAR(180) NOT NULL,
    entrega_dias INTEGER NOT NULL CHECK (entrega_dias BETWEEN 1 AND 60)
);

CREATE TABLE IF NOT EXISTS productos (
    id_producto BIGSERIAL PRIMARY KEY,
    codigo VARCHAR(7) NOT NULL UNIQUE,
    nombre VARCHAR(80) NOT NULL,
    categoria VARCHAR(60) NOT NULL,
    descripcion VARCHAR(250) NOT NULL,
    precio NUMERIC(10,2) NOT NULL CHECK (precio > 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    imagen VARCHAR(120) NOT NULL,
    id_proveedor BIGINT NOT NULL REFERENCES proveedores(id_proveedor)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS clientes (
    id_cliente BIGSERIAL PRIMARY KEY,
    codigo VARCHAR(7) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(120) NOT NULL,
    ciudad VARCHAR(60) NOT NULL,
    tipo VARCHAR(30) NOT NULL
);

CREATE TABLE IF NOT EXISTS facturas (
    id_factura BIGSERIAL PRIMARY KEY,
    numero VARCHAR(8) NOT NULL UNIQUE,
    id_cliente BIGINT NOT NULL REFERENCES clientes(id_cliente)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    fecha DATE NOT NULL,
    subtotal NUMERIC(10,2) NOT NULL CHECK (subtotal >= 0),
    impuesto NUMERIC(10,2) NOT NULL CHECK (impuesto >= 0),
    total NUMERIC(10,2) NOT NULL CHECK (total >= 0)
);

CREATE TABLE IF NOT EXISTS detalle_factura (
    id_detalle BIGSERIAL PRIMARY KEY,
    id_factura BIGINT NOT NULL REFERENCES facturas(id_factura)
        ON UPDATE CASCADE ON DELETE CASCADE,
    id_producto BIGINT NOT NULL REFERENCES productos(id_producto)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(10,2) NOT NULL CHECK (precio_unitario > 0),
    subtotal NUMERIC(10,2) NOT NULL CHECK (subtotal >= 0)
);

INSERT INTO proveedores (codigo, nombre, correo, ciudad, categoria, entrega_dias)
VALUES
    ('PRV-001', 'LUSANCOMP', 'ventas@lusancomp.com', 'Quito',
     'Laptops, computadoras y componentes informáticos.', 3),
    ('PRV-002', 'MAXXICOMP', 'ventasenlinea@maxxicomp.com', 'Guayaquil',
     'Hardware, periféricos y accesorios tecnológicos.', 5),
    ('PRV-003', 'PC MAX TECNOLOGIA', 'contacto@pcmax.com.ec', 'Quito',
     'Componentes, computadoras y accesorios tecnológicos.', 3)
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO productos
    (codigo, nombre, categoria, descripcion, precio, stock, imagen, id_proveedor)
VALUES
    ('PRO-001', 'Laptop para estudio', 'Laptops y computadoras',
     'Pantalla de 15,6 pulgadas, 8 GB de RAM y SSD de 512 GB.', 550.00, 8,
     'laptop-estudio.jpg', (SELECT id_proveedor FROM proveedores WHERE codigo='PRV-001')),
    ('PRO-002', 'Computadora de escritorio', 'Laptops y computadoras',
     'Equipo para oficina con 16 GB de RAM y SSD de 512 GB.', 680.00, 5,
     'computadora-escritorio.jpg', (SELECT id_proveedor FROM proveedores WHERE codigo='PRV-001')),
    ('PRO-003', 'Teclado y mouse', 'Accesorios tecnológicos',
     'Kit USB para las actividades diarias de estudio y trabajo.', 25.00, 20,
     'teclado-mouse.jpg', (SELECT id_proveedor FROM proveedores WHERE codigo='PRV-002')),
    ('PRO-004', 'Audífonos con micrófono', 'Accesorios tecnológicos',
     'Accesorio para clases virtuales, reuniones y llamadas.', 30.00, 12,
     'audifonos.jpg', (SELECT id_proveedor FROM proveedores WHERE codigo='PRV-002')),
    ('PRO-005', 'Memoria RAM de 8 GB', 'Componentes informáticos',
     'Módulo DDR4 para equipos compatibles.', 28.00, 15,
     'memoria-ram.jpg', (SELECT id_proveedor FROM proveedores WHERE codigo='PRV-003')),
    ('PRO-006', 'Disco SSD de 480 GB', 'Componentes informáticos',
     'Unidad SATA para mejorar el almacenamiento del equipo.', 45.00, 10,
     'disco-ssd.jpg', (SELECT id_proveedor FROM proveedores WHERE codigo='PRV-003'))
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO clientes (codigo, nombre, correo, ciudad, tipo)
VALUES
    ('CLI-001', 'CARLOS SEGUNDO ARCE BATALLAS', 'cs.arceb@uea.edu.ec', 'Puyo', 'Estudiante'),
    ('CLI-002', 'JORDAN ALEXANDER ARRIAGA LOGRONO', 'ja.arriagal@uea.edu.ec', 'Tena', 'Profesional'),
    ('CLI-003', 'XAVIER ALEXANDER CASA LEMA', 'xa.casal@uea.edu.ec', 'El Reventador', 'Emprendimiento'),
    ('CLI-004', 'CRISTIAN DAVID CHIQUIMBA MENA', 'cd.chiquimbam@uea.edu.ec', 'Nueva Loja', 'Empresa')
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO facturas (numero, id_cliente, fecha, subtotal, impuesto, total)
SELECT 'FAC-0001', id_cliente, CURRENT_DATE, 600.00, 90.00, 690.00
FROM clientes WHERE codigo='CLI-001'
ON CONFLICT (numero) DO NOTHING;

INSERT INTO detalle_factura
    (id_factura, id_producto, cantidad, precio_unitario, subtotal)
SELECT f.id_factura, p.id_producto, 1, 550.00, 550.00
FROM facturas f CROSS JOIN productos p
WHERE f.numero='FAC-0001' AND p.codigo='PRO-001'
  AND NOT EXISTS (
      SELECT 1 FROM detalle_factura d
      WHERE d.id_factura=f.id_factura AND d.id_producto=p.id_producto
  );

INSERT INTO detalle_factura
    (id_factura, id_producto, cantidad, precio_unitario, subtotal)
SELECT f.id_factura, p.id_producto, 2, 25.00, 50.00
FROM facturas f CROSS JOIN productos p
WHERE f.numero='FAC-0001' AND p.codigo='PRO-003'
  AND NOT EXISTS (
      SELECT 1 FROM detalle_factura d
      WHERE d.id_factura=f.id_factura AND d.id_producto=p.id_producto
  );

-- JOIN obligatorio de comprobación: Producto -> Proveedor.
SELECT p.codigo, p.nombre AS producto, pr.nombre AS proveedor, p.stock
FROM productos p
INNER JOIN proveedores pr ON pr.id_proveedor=p.id_proveedor
ORDER BY p.id_producto;
