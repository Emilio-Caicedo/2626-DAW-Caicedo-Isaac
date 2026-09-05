import os
import sqlite3
from datetime import date
from decimal import Decimal
from pathlib import Path

from flask import Flask, flash, redirect, render_template, url_for
from flask_wtf.csrf import CSRFProtect

from forms import ClienteForm, FacturacionForm, ProductoForm, ProveedorForm

app = Flask(__name__)

# Flask-WTF utiliza esta clave para firmar el token CSRF. En producción debe
# definirse la variable de entorno SECRET_KEY con un valor privado.
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "emitech-clave-academica-semana-12"
)
app.config["DATABASE"] = Path(__file__).resolve().parent / "data" / "emitech_store.db"
csrf = CSRFProtect(app)

NOMBRE_TIENDA = "EmiTech Store"
TASA_IMPUESTO_DEMO = Decimal("0.15")

PRODUCTOS_INICIALES = [
    {"codigo": "PRO-001", "nombre": "Laptop para estudio", "categoria": "Laptops y computadoras", "descripcion": "Pantalla de 15,6 pulgadas, 8 GB de RAM y SSD de 512 GB.", "precio": "550.00", "stock": 8, "imagen": "laptop-estudio.jpg"},
    {"codigo": "PRO-002", "nombre": "Computadora de escritorio", "categoria": "Laptops y computadoras", "descripcion": "Equipo para oficina con 16 GB de RAM y SSD de 512 GB.", "precio": "680.00", "stock": 5, "imagen": "computadora-escritorio.jpg"},
    {"codigo": "PRO-003", "nombre": "Teclado y mouse", "categoria": "Accesorios tecnológicos", "descripcion": "Kit USB para las actividades diarias de estudio y trabajo.", "precio": "25.00", "stock": 20, "imagen": "teclado-mouse.jpg"},
    {"codigo": "PRO-004", "nombre": "Audífonos con micrófono", "categoria": "Accesorios tecnológicos", "descripcion": "Accesorio para clases virtuales, reuniones y llamadas.", "precio": "30.00", "stock": 12, "imagen": "audifonos.jpg"},
    {"codigo": "PRO-005", "nombre": "Memoria RAM de 8 GB", "categoria": "Componentes informáticos", "descripcion": "Módulo DDR4 para equipos compatibles.", "precio": "28.00", "stock": 15, "imagen": "memoria-ram.jpg"},
    {"codigo": "PRO-006", "nombre": "Disco SSD de 480 GB", "categoria": "Componentes informáticos", "descripcion": "Unidad SATA para mejorar el almacenamiento del equipo.", "precio": "45.00", "stock": 0, "imagen": "disco-ssd.jpg"},
]


def conectar_bd():
    """Abre una conexión a la base local y permite leer columnas por nombre."""
    ruta_bd = Path(app.config["DATABASE"])
    ruta_bd.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(ruta_bd)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_base_datos():
    """Crea la tabla Productos y carga el catálogo original si está vacía."""
    conn = conectar_bd()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT NOT NULL UNIQUE,
                nombre TEXT NOT NULL,
                categoria TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                precio REAL NOT NULL CHECK (precio > 0),
                stock INTEGER NOT NULL CHECK (stock >= 0),
                imagen TEXT NOT NULL
            )
            """
        )
        cursor.execute("SELECT COUNT(*) FROM productos")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                """
                INSERT INTO productos
                    (codigo, nombre, categoria, descripcion, precio, stock, imagen)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        producto["codigo"],
                        producto["nombre"],
                        producto["categoria"],
                        producto["descripcion"],
                        producto["precio"],
                        producto["stock"],
                        producto["imagen"],
                    )
                    for producto in PRODUCTOS_INICIALES
                ],
            )
        conn.commit()
    finally:
        conn.close()


def obtener_productos():
    """Recupera con SELECT y fetchall todos los productos persistentes."""
    conn = conectar_bd()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, codigo, nombre, categoria, descripcion, precio, stock, imagen
            FROM productos
            ORDER BY id
            """
        )
        filas = cursor.fetchall()
        return [dict(fila) for fila in filas]
    finally:
        conn.close()


def buscar_producto_por_codigo(codigo):
    """Consulta un producto con un parámetro SQL seguro."""
    conn = conectar_bd()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, codigo, nombre, categoria, descripcion, precio, stock, imagen
            FROM productos
            WHERE codigo = ?
            """,
            (codigo.strip().upper(),),
        )
        fila = cursor.fetchone()
        return dict(fila) if fila else None
    finally:
        conn.close()


def insertar_producto(producto):
    """Inserta un producto validado, confirma el cambio y cierra la conexión."""
    conn = conectar_bd()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO productos
                (codigo, nombre, categoria, descripcion, precio, stock, imagen)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                producto["codigo"],
                producto["nombre"],
                producto["categoria"],
                producto["descripcion"],
                producto["precio"],
                producto["stock"],
                producto["imagen"],
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        raise
    finally:
        conn.close()

CLIENTES = [
    {"codigo": "CLI-001", "nombre": "CARLOS SEGUNDO ARCE BATALLAS", "tipo": "Estudiante", "correo": "cs.arceb@uea.edu.ec", "ciudad": "Puyo"},
    {"codigo": "CLI-002", "nombre": "JORDAN ALEXANDER ARRIAGA LOGRONO", "tipo": "Profesional", "correo": "ja.arriagal@uea.edu.ec", "ciudad": "Tena"},
    {"codigo": "CLI-003", "nombre": "XAVIER ALEXANDER CASA LEMA", "tipo": "Emprendimiento", "correo": "xa.casal@uea.edu.ec", "ciudad": "El Reventador"},
    {"codigo": "CLI-004", "nombre": "CRISTIAN DAVID CHIQUIMBA MENA", "tipo": "Empresa", "correo": "cd.chiquimbam@uea.edu.ec", "ciudad": "Nueva Loja"},
]

PROVEEDORES = [
    {"codigo": "PRV-001", "nombre": "LUSANCOMP", "categoria": "Laptops, PCs corporativas y componentes informáticos.", "correo": "ventas@lusancomp.com", "ciudad": "Quito", "entrega": "2 a 4 días"},
    {"codigo": "PRV-002", "nombre": "MAXXICOMP", "categoria": "Laptops, hardware, periféricos y accesorios.", "correo": "ventasenlinea@maxxicomp.com", "ciudad": "Guayaquil", "entrega": "3 a 6 días"},
    {"codigo": "PRV-003", "nombre": "PC MAX TECNOLOGIA", "categoria": "Componentes, PC computadoras y accesorios tecnológicos.", "correo": "contacto@pcmax.com.ec", "ciudad": "Quito", "entrega": "2 a 4 días"},
]

DETALLE_FACTURA = [
    {"codigo": "PRO-001", "producto": "Laptop para estudio", "cantidad": 1, "precio": Decimal("550.00")},
    {"codigo": "PRO-003", "producto": "Teclado y mouse", "cantidad": 2, "precio": Decimal("25.00")},
]

FACTURA = {
    "numero": "DEMO-0001",
    "fecha": "02/09/2026",
    "cliente": "CARLOS SEGUNDO ARCE BATALLAS",
    "codigo_cliente": "CLI-001",
    "correo": "cs.arceb@uea.edu.ec",
}


def obtener_catalogo():
    """Conserva las tres categorías dinámicas de la portada."""
    return [
        {
            "nombre": "Laptops y computadoras",
            "descripcion": "Equipos ideales para estudiar, trabajar, emprender y desarrollar diferentes actividades profesionales.",
            "imagen": url_for("static", filename="img/laptops-computadoras.jpg"),
        },
        {
            "nombre": "Accesorios tecnológicos",
            "descripcion": "Teclados, mouse, audífonos y diferentes accesorios para mejorar la experiencia de uso de tus equipos.",
            "imagen": url_for("static", filename="img/accesorios-tecnologicos.jpg"),
        },
        {
            "nombre": "Componentes informáticos",
            "descripcion": "Memorias RAM, discos SSD, tarjetas gráficas y componentes para actualizar o mejorar una computadora.",
            "imagen": url_for("static", filename="img/componentes-informaticos.jpg"),
        },
    ]


def buscar_por_codigo(registros, codigo):
    """Busca un diccionario por código sin distinguir mayúsculas."""
    codigo_normalizado = codigo.strip().upper()
    return next(
        (item for item in registros if item["codigo"].upper() == codigo_normalizado),
        None,
    )


def completar_totales_factura():
    """Calcula subtotales y totales del comprobante actual."""
    for item in DETALLE_FACTURA:
        item["subtotal"] = item["cantidad"] * item["precio"]
    subtotal = sum(
        (item["subtotal"] for item in DETALLE_FACTURA), Decimal("0.00")
    )
    impuesto = (subtotal * TASA_IMPUESTO_DEMO).quantize(Decimal("0.01"))
    FACTURA.update(
        {"subtotal": subtotal, "impuesto": impuesto, "total": subtotal + impuesto}
    )


inicializar_base_datos()


@app.route("/")
def inicio():
    """Página informativa conservada de las semanas anteriores."""
    return render_template(
        "index.html", titulo=NOMBRE_TIENDA, catalogo=obtener_catalogo()
    )


@app.route("/productos")
def productos():
    """Consulta con SELECT el catálogo persistente del módulo Productos."""
    return render_template(
        "productos.html",
        titulo="Productos",
        productos=obtener_productos(),
        aviso="Productos recuperados desde la base de datos local emitech_store.db.",
    )


@app.route("/productos/nuevo", methods=["GET", "POST"])
def nuevo_producto():
    """Valida el formulario y realiza un INSERT parametrizado en SQLite."""
    form = ProductoForm()
    if form.validate_on_submit():
        codigo = form.codigo.data.strip().upper()
        imagenes = {
            "Laptops y computadoras": "laptops-computadoras.jpg",
            "Accesorios tecnológicos": "accesorios-tecnologicos.jpg",
            "Componentes informáticos": "componentes-informaticos.jpg",
        }
        producto = {
            "codigo": codigo,
            "nombre": form.nombre.data.strip(),
            "categoria": form.categoria.data,
            "descripcion": form.descripcion.data.strip(),
            "precio": float(form.precio.data),
            "stock": form.stock.data,
            "imagen": imagenes[form.categoria.data],
        }
        try:
            insertar_producto(producto)
        except sqlite3.IntegrityError:
            form.codigo.errors.append("Ya existe un producto con este código.")
        else:
            flash(
                "Producto guardado correctamente en emitech_store.db.", "success"
            )
            return redirect(url_for("productos"))
    return render_template(
        "formulario_producto.html", titulo="Registrar producto", form=form
    )


@app.route("/clientes")
def clientes():
    """Directorio dinámico del módulo Clientes."""
    return render_template(
        "clientes.html",
        titulo="Clientes",
        clientes=CLIENTES,
        aviso="Los datos son demostrativos y se conservan solo durante la ejecución.",
    )


@app.route("/clientes/nuevo", methods=["GET", "POST"])
def nuevo_cliente():
    """Presenta y procesa el formulario validado de clientes."""
    form = ClienteForm()
    if form.validate_on_submit():
        codigo = form.codigo.data.strip().upper()
        if buscar_por_codigo(CLIENTES, codigo):
            form.codigo.errors.append("Ya existe un cliente con este código.")
        else:
            CLIENTES.append(
                {
                    "codigo": codigo,
                    "nombre": form.nombre.data.strip().upper(),
                    "tipo": form.tipo.data,
                    "correo": form.correo.data.strip().lower(),
                    "ciudad": form.ciudad.data.strip(),
                }
            )
            flash("Cliente registrado correctamente.", "success")
            return redirect(url_for("clientes"))
    return render_template(
        "formulario_cliente.html", titulo="Registrar cliente", form=form
    )


@app.route("/proveedores")
def proveedores():
    """Directorio dinámico del módulo Proveedores."""
    return render_template(
        "proveedores.html",
        titulo="Proveedores",
        proveedores=PROVEEDORES,
        aviso="Los datos son demostrativos y se conservan solo durante la ejecución.",
    )


@app.route("/proveedores/nuevo", methods=["GET", "POST"])
def nuevo_proveedor():
    """Presenta y procesa el formulario validado de proveedores."""
    form = ProveedorForm()
    if form.validate_on_submit():
        codigo = form.codigo.data.strip().upper()
        if buscar_por_codigo(PROVEEDORES, codigo):
            form.codigo.errors.append("Ya existe un proveedor con este código.")
        else:
            dias = form.entrega_dias.data
            PROVEEDORES.append(
                {
                    "codigo": codigo,
                    "nombre": form.nombre.data.strip().upper(),
                    "categoria": form.categoria.data.strip(),
                    "correo": form.correo.data.strip().lower(),
                    "ciudad": form.ciudad.data.strip(),
                    "entrega": f"{dias} día" if dias == 1 else f"{dias} días",
                }
            )
            flash("Proveedor registrado correctamente.", "success")
            return redirect(url_for("proveedores"))
    return render_template(
        "formulario_proveedor.html", titulo="Registrar proveedor", form=form
    )


@app.route("/facturacion")
def facturacion():
    """Muestra el comprobante didáctico actual."""
    completar_totales_factura()
    return render_template(
        "facturacion.html",
        titulo="Facturación",
        factura=FACTURA,
        detalle=DETALLE_FACTURA,
        aviso="Comprobante demostrativo, sin validez tributaria y sin conexión a una base de datos.",
    )


@app.route("/facturacion/nueva", methods=["GET", "POST"])
def nueva_factura():
    """Presenta y procesa un comprobante de un producto."""
    form = FacturacionForm()
    productos_disponibles = [
        producto for producto in obtener_productos() if producto["stock"] > 0
    ]
    form.cliente_codigo.choices = [
        (cliente["codigo"], f'{cliente["codigo"]} · {cliente["nombre"]}')
        for cliente in CLIENTES
    ]
    form.producto_codigo.choices = [
        (producto["codigo"], f'{producto["codigo"]} · {producto["nombre"]}')
        for producto in productos_disponibles
    ]

    if form.validate_on_submit():
        cliente = buscar_por_codigo(CLIENTES, form.cliente_codigo.data)
        producto = buscar_producto_por_codigo(form.producto_codigo.data)
        codigo_factura = form.numero.data.strip().upper()

        if codigo_factura == FACTURA["numero"]:
            form.numero.errors.append("Ingrese un número diferente al comprobante actual.")
        elif producto is None or producto["stock"] <= 0:
            form.producto_codigo.errors.append("Seleccione un producto disponible.")
        elif form.cantidad.data > producto["stock"]:
            form.cantidad.errors.append(
                f'La cantidad supera el stock disponible ({producto["stock"]}).'
            )
        else:
            precio = Decimal(str(producto["precio"]))
            DETALLE_FACTURA.clear()
            DETALLE_FACTURA.append(
                {
                    "codigo": producto["codigo"],
                    "producto": producto["nombre"],
                    "cantidad": form.cantidad.data,
                    "precio": precio,
                }
            )
            FACTURA.clear()
            FACTURA.update(
                {
                    "numero": codigo_factura,
                    "fecha": form.fecha.data.strftime("%d/%m/%Y"),
                    "cliente": cliente["nombre"],
                    "codigo_cliente": cliente["codigo"],
                    "correo": cliente["correo"],
                }
            )
            completar_totales_factura()
            flash("Comprobante generado correctamente.", "success")
            return redirect(url_for("facturacion"))

    if not form.is_submitted():
        form.fecha.data = date.today()
    return render_template(
        "formulario_facturacion.html", titulo="Generar comprobante", form=form
    )


if __name__ == "__main__":
    # Servidor de desarrollo local. Detener con Ctrl+C.
    app.run(host="127.0.0.1", port=5000)
