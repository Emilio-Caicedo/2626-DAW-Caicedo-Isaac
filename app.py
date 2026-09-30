"""EmiTech Store - Proyecto Integrador, Semana 14.

La aplicación conserva el CRUD MySQL e incorpora registro, hash de contraseñas,
inicio de sesión, rutas protegidas y cierre de sesión mediante Flask-Login.
"""

import os
from datetime import date
from decimal import Decimal

from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_wtf.csrf import CSRFProtect
from mysql.connector import Error, IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from conexion import conectar_bd
from forms import (
    ClienteForm,
    CerrarSesionForm,
    EliminarProductoForm,
    FacturacionForm,
    LoginForm,
    ProductoForm,
    ProveedorForm,
    UsuarioForm,
)
from models import Usuario


load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "cambie-esta-clave-local-en-el-archivo-env"
)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Inicie sesión para acceder a esta página."
login_manager.login_message_category = "warning"
login_manager.session_protection = "strong"

NOMBRE_TIENDA = "EmiTech Store"
TASA_IMPUESTO_DEMO = Decimal("0.15")

# Referencia del catálogo de la Semana 12. En la Semana 13 los registros se
# cargan con sql/esquema.sql y se consultan directamente desde MySQL.
PRODUCTOS_INICIALES = [
    {"codigo": "PRO-001", "nombre": "Laptop para estudio", "categoria": "Laptops y computadoras", "descripcion": "Pantalla de 15,6 pulgadas, 8 GB de RAM y SSD de 512 GB.", "precio": "550.00", "stock": 8, "imagen": "laptop-estudio.jpg", "id_proveedor": 1},
    {"codigo": "PRO-002", "nombre": "Computadora de escritorio", "categoria": "Laptops y computadoras", "descripcion": "Equipo para oficina con 16 GB de RAM y SSD de 512 GB.", "precio": "680.00", "stock": 5, "imagen": "computadora-escritorio.jpg", "id_proveedor": 1},
    {"codigo": "PRO-003", "nombre": "Teclado y mouse", "categoria": "Accesorios tecnológicos", "descripcion": "Kit USB para las actividades diarias de estudio y trabajo.", "precio": "25.00", "stock": 20, "imagen": "teclado-mouse.jpg", "id_proveedor": 2},
    {"codigo": "PRO-004", "nombre": "Audífonos con micrófono", "categoria": "Accesorios tecnológicos", "descripcion": "Accesorio para clases virtuales, reuniones y llamadas.", "precio": "30.00", "stock": 12, "imagen": "audifonos.jpg", "id_proveedor": 2},
    {"codigo": "PRO-005", "nombre": "Memoria RAM de 8 GB", "categoria": "Componentes informáticos", "descripcion": "Módulo DDR4 para equipos compatibles.", "precio": "28.00", "stock": 15, "imagen": "memoria-ram.jpg", "id_proveedor": 3},
    {"codigo": "PRO-006", "nombre": "Disco SSD de 480 GB", "categoria": "Componentes informáticos", "descripcion": "Unidad SATA para mejorar el almacenamiento del equipo.", "precio": "45.00", "stock": 0, "imagen": "disco-ssd.jpg", "id_proveedor": 3},
]

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


def _cerrar_recursos(cursor, conexion):
    """Cierra de forma segura el cursor y la conexión utilizados."""
    if cursor is not None:
        cursor.close()
    if conexion is not None and conexion.is_connected():
        conexion.close()


def buscar_usuario_por_id(id_usuario):
    """Recupera una cuenta activa por su clave primaria para load_user()."""
    conexion = None
    cursor = None
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id_usuario, usuario, nombre_completo, password_hash, activo
            FROM usuarios
            WHERE id_usuario = %s AND activo = TRUE
            """,
            (id_usuario,),
        )
        return cursor.fetchone()
    finally:
        _cerrar_recursos(cursor, conexion)


def buscar_usuario_por_nombre(nombre_usuario):
    """Obtiene la cuenta que será verificada durante el inicio de sesión."""
    conexion = None
    cursor = None
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id_usuario, usuario, nombre_completo, password_hash, activo
            FROM usuarios
            WHERE usuario = %s AND activo = TRUE
            """,
            (nombre_usuario.strip().lower(),),
        )
        return cursor.fetchone()
    finally:
        _cerrar_recursos(cursor, conexion)


def insertar_usuario(usuario, nombre_completo, password_hash):
    """Registra una cuenta con un hash mediante INSERT parametrizado."""
    conexion = None
    cursor = None
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO usuarios (usuario, nombre_completo, password_hash)
            VALUES (%s, %s, %s)
            """,
            (usuario.strip().lower(), nombre_completo.strip(), password_hash),
        )
        conexion.commit()
        return cursor.lastrowid
    except Error:
        if conexion is not None:
            conexion.rollback()
        raise
    finally:
        _cerrar_recursos(cursor, conexion)


@login_manager.user_loader
def cargar_usuario(id_usuario):
    """Restaura desde MySQL el usuario identificado en la sesión."""
    try:
        fila = buscar_usuario_por_id(int(id_usuario))
    except (TypeError, ValueError):
        return None
    except Error:
        app.logger.exception("No fue posible recuperar la sesión desde MySQL")
        return None
    return Usuario.desde_fila(fila)


@app.context_processor
def componentes_de_sesion():
    """Facilita el formulario CSRF de logout a todas las plantillas."""
    return {"cerrar_sesion_form": CerrarSesionForm()}


def obtener_productos():
    """Ejecuta SELECT + JOIN y devuelve todos los productos de MySQL."""
    conexion = None
    cursor = None
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                p.id_producto AS id,
                p.codigo,
                p.nombre,
                p.categoria,
                p.descripcion,
                p.precio,
                p.stock,
                p.imagen,
                p.id_proveedor,
                pr.nombre AS proveedor_nombre
            FROM productos AS p
            INNER JOIN proveedores AS pr
                ON pr.id_proveedor = p.id_proveedor
            ORDER BY p.id_producto
            """
        )
        return cursor.fetchall()
    finally:
        _cerrar_recursos(cursor, conexion)


def obtener_proveedores_bd():
    """Recupera proveedores para relacionarlos con el formulario de productos."""
    conexion = None
    cursor = None
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id_proveedor, codigo, nombre
            FROM proveedores
            ORDER BY nombre
            """
        )
        return cursor.fetchall()
    finally:
        _cerrar_recursos(cursor, conexion)


def buscar_producto_por_id(id_producto):
    """Ejecuta SELECT con WHERE para recuperar un producto por su PK."""
    conexion = None
    cursor = None
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                p.id_producto AS id,
                p.codigo,
                p.nombre,
                p.categoria,
                p.descripcion,
                p.precio,
                p.stock,
                p.imagen,
                p.id_proveedor,
                pr.nombre AS proveedor_nombre
            FROM productos AS p
            INNER JOIN proveedores AS pr
                ON pr.id_proveedor = p.id_proveedor
            WHERE p.id_producto = %s
            """,
            (id_producto,),
        )
        return cursor.fetchone()
    finally:
        _cerrar_recursos(cursor, conexion)


def buscar_producto_por_codigo(codigo):
    """Ejecuta una consulta SELECT parametrizada por código."""
    conexion = None
    cursor = None
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id_producto AS id, codigo, nombre, categoria, descripcion,
                   precio, stock, imagen, id_proveedor
            FROM productos
            WHERE codigo = %s
            """,
            (codigo.strip().upper(),),
        )
        return cursor.fetchone()
    finally:
        _cerrar_recursos(cursor, conexion)


def insertar_producto(producto):
    """Registra un producto mediante INSERT parametrizado y commit()."""
    conexion = None
    cursor = None
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO productos
                (codigo, nombre, categoria, descripcion, precio, stock, imagen,
                 id_proveedor)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                producto["codigo"], producto["nombre"], producto["categoria"],
                producto["descripcion"], producto["precio"], producto["stock"],
                producto["imagen"], producto["id_proveedor"],
            ),
        )
        conexion.commit()
        return cursor.lastrowid
    except Error:
        if conexion is not None:
            conexion.rollback()
        raise
    finally:
        _cerrar_recursos(cursor, conexion)


def actualizar_producto(id_producto, producto):
    """Actualiza únicamente el producto indicado mediante UPDATE + WHERE."""
    conexion = None
    cursor = None
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        cursor.execute(
            """
            UPDATE productos
            SET codigo = %s, nombre = %s, categoria = %s, descripcion = %s,
                precio = %s, stock = %s, imagen = %s, id_proveedor = %s
            WHERE id_producto = %s
            """,
            (
                producto["codigo"], producto["nombre"], producto["categoria"],
                producto["descripcion"], producto["precio"], producto["stock"],
                producto["imagen"], producto["id_proveedor"], id_producto,
            ),
        )
        conexion.commit()
        return cursor.rowcount
    except Error:
        if conexion is not None:
            conexion.rollback()
        raise
    finally:
        _cerrar_recursos(cursor, conexion)


def eliminar_producto_bd(id_producto):
    """Elimina únicamente el producto seleccionado mediante DELETE + WHERE."""
    conexion = None
    cursor = None
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        cursor.execute(
            "DELETE FROM productos WHERE id_producto = %s", (id_producto,)
        )
        conexion.commit()
        return cursor.rowcount
    except Error:
        if conexion is not None:
            conexion.rollback()
        raise
    finally:
        _cerrar_recursos(cursor, conexion)


def obtener_catalogo():
    """Conserva las tres categorías dinámicas de la portada."""
    return [
        {"nombre": "Laptops y computadoras", "descripcion": "Equipos ideales para estudiar, trabajar, emprender y desarrollar diferentes actividades profesionales.", "imagen": url_for("static", filename="img/laptops-computadoras.jpg")},
        {"nombre": "Accesorios tecnológicos", "descripcion": "Teclados, mouse, audífonos y diferentes accesorios para mejorar la experiencia de uso de tus equipos.", "imagen": url_for("static", filename="img/accesorios-tecnologicos.jpg")},
        {"nombre": "Componentes informáticos", "descripcion": "Memorias RAM, discos SSD, tarjetas gráficas y componentes para actualizar o mejorar una computadora.", "imagen": url_for("static", filename="img/componentes-informaticos.jpg")},
    ]


def buscar_por_codigo(registros, codigo):
    """Busca un diccionario por código sin distinguir mayúsculas."""
    codigo_normalizado = codigo.strip().upper()
    return next(
        (item for item in registros if item["codigo"].upper() == codigo_normalizado),
        None,
    )


def completar_totales_factura():
    """Calcula subtotales y totales del comprobante demostrativo."""
    for item in DETALLE_FACTURA:
        item["subtotal"] = item["cantidad"] * item["precio"]
    subtotal = sum((item["subtotal"] for item in DETALLE_FACTURA), Decimal("0.00"))
    impuesto = (subtotal * TASA_IMPUESTO_DEMO).quantize(Decimal("0.01"))
    FACTURA.update({"subtotal": subtotal, "impuesto": impuesto, "total": subtotal + impuesto})


def imagen_por_categoria(categoria):
    """Selecciona una imagen existente para los productos registrados."""
    return {
        "Laptops y computadoras": "laptops-computadoras.jpg",
        "Accesorios tecnológicos": "accesorios-tecnologicos.jpg",
        "Componentes informáticos": "componentes-informaticos.jpg",
    }[categoria]


def producto_desde_formulario(form):
    """Normaliza los valores validados de ProductoForm."""
    return {
        "codigo": form.codigo.data.strip().upper(),
        "nombre": form.nombre.data.strip(),
        "categoria": form.categoria.data,
        "descripcion": form.descripcion.data.strip(),
        "precio": form.precio.data,
        "stock": form.stock.data,
        "imagen": imagen_por_categoria(form.categoria.data),
        "id_proveedor": form.proveedor_id.data,
    }


def cargar_proveedores_en_formulario(form):
    """Carga en el SelectField opciones recuperadas desde MySQL."""
    form.proveedor_id.choices = [(0, "Seleccione un proveedor")] + [
        (p["id_proveedor"], f'{p["codigo"]} · {p["nombre"]}')
        for p in obtener_proveedores_bd()
    ]


@app.route("/")
def inicio():
    return render_template("index.html", titulo=NOMBRE_TIENDA, catalogo=obtener_catalogo())


def _destino_interno_seguro(destino):
    """Acepta únicamente rutas locales para evitar redirecciones externas."""
    return bool(destino and destino.startswith("/") and not destino.startswith("//"))


@app.route("/registro", methods=["GET", "POST"])
def registro():
    """Crea una cuenta y almacena solamente el hash de la contraseña."""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = UsuarioForm()
    if form.validate_on_submit():
        nombre_usuario = form.usuario.data.strip().lower()
        password_hash = generate_password_hash(form.password.data)
        try:
            insertar_usuario(
                nombre_usuario,
                form.nombre_completo.data,
                password_hash,
            )
        except IntegrityError:
            form.usuario.errors.append("El nombre de usuario ya está registrado.")
        except Error:
            app.logger.exception("No fue posible registrar el usuario")
            flash(
                "No se pudo registrar la cuenta. Verifique MySQL y la migración de la Semana 14.",
                "danger",
            )
        else:
            flash("Cuenta creada correctamente. Ya puede iniciar sesión.", "success")
            return redirect(url_for("login"))

    return render_template("registro.html", titulo="Crear cuenta", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Comprueba el hash y crea la sesión con Flask-Login."""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = LoginForm()
    siguiente = request.args.get("next", "")
    if form.validate_on_submit():
        try:
            fila = buscar_usuario_por_nombre(form.usuario.data)
        except Error:
            app.logger.exception("No fue posible consultar el usuario")
            flash("No se pudo conectar con MySQL. Intente nuevamente.", "danger")
        else:
            credenciales_validas = fila and check_password_hash(
                fila["password_hash"], form.password.data
            )
            if credenciales_validas:
                login_user(Usuario.desde_fila(fila), remember=form.recordar.data)
                flash(f'Bienvenido, {fila["nombre_completo"]}.', "success")
                if _destino_interno_seguro(siguiente):
                    return redirect(siguiente)
                return redirect(url_for("dashboard"))
            flash("Usuario o contraseña incorrectos.", "danger")

    return render_template(
        "login.html", titulo="Iniciar sesión", form=form, siguiente=siguiente
    )


@app.route("/dashboard")
@login_required
def dashboard():
    """Panel privado de acceso a los módulos administrativos."""
    return render_template("dashboard.html", titulo="Panel de administración")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    """Destruye la sesión activa mediante una operación POST protegida."""
    form = CerrarSesionForm()
    if not form.validate_on_submit():
        abort(400)
    logout_user()
    flash("La sesión se cerró correctamente.", "success")
    return redirect(url_for("login"))


@app.route("/productos")
@login_required
def productos():
    """Lista el catálogo recuperado desde MySQL mediante SELECT + JOIN."""
    try:
        registros = obtener_productos()
    except Error:
        app.logger.exception("No fue posible consultar productos en MySQL")
        registros = []
        flash("No se pudo conectar con MySQL. Revise el archivo .env y ejecute sql/esquema.sql.", "danger")
    return render_template(
        "productos.html", titulo="Productos", productos=registros,
        aviso="Productos recuperados desde la base de datos relacional MySQL emitech_store.",
        eliminar_form=EliminarProductoForm(),
    )


@app.route("/productos/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_producto():
    """Valida el formulario y ejecuta INSERT sobre MySQL."""
    form = ProductoForm()
    try:
        cargar_proveedores_en_formulario(form)
    except Error:
        app.logger.exception("No fue posible consultar proveedores en MySQL")
        form.proveedor_id.choices = [(0, "MySQL no disponible")]
        flash("No se pudo conectar con MySQL. Revise la configuración antes de registrar.", "danger")

    if form.validate_on_submit():
        try:
            insertar_producto(producto_desde_formulario(form))
        except IntegrityError:
            form.codigo.errors.append("Ya existe un producto con este código.")
        except Error:
            app.logger.exception("No fue posible insertar el producto")
            flash("MySQL no pudo guardar el producto. Intente nuevamente.", "danger")
        else:
            flash("Producto registrado correctamente en MySQL.", "success")
            return redirect(url_for("productos"))

    return render_template(
        "formulario_producto.html", titulo="Registrar producto",
        subtitulo="Complete los campos para incorporar un producto a MySQL.",
        form=form, accion=url_for("nuevo_producto"), modo_edicion=False,
    )


@app.route("/productos/<int:id_producto>/editar", methods=["GET", "POST"])
@login_required
def editar_producto(id_producto):
    """Carga el registro y guarda sus cambios mediante UPDATE + WHERE."""
    try:
        producto = buscar_producto_por_id(id_producto)
    except Error:
        app.logger.exception("No fue posible consultar el producto")
        flash("No se pudo consultar el producto en MySQL.", "danger")
        return redirect(url_for("productos"))
    if producto is None:
        abort(404)

    form = ProductoForm()
    try:
        cargar_proveedores_en_formulario(form)
    except Error:
        app.logger.exception("No fue posible consultar proveedores en MySQL")
        form.proveedor_id.choices = [(0, "MySQL no disponible")]

    if form.validate_on_submit():
        try:
            actualizar_producto(id_producto, producto_desde_formulario(form))
        except IntegrityError:
            form.codigo.errors.append("Ya existe otro producto con este código.")
        except Error:
            app.logger.exception("No fue posible actualizar el producto")
            flash("MySQL no pudo actualizar el producto.", "danger")
        else:
            flash("Producto actualizado correctamente en MySQL.", "success")
            return redirect(url_for("productos"))
    elif request.method == "GET":
        form.codigo.data = producto["codigo"]
        form.nombre.data = producto["nombre"]
        form.categoria.data = producto["categoria"]
        form.proveedor_id.data = producto["id_proveedor"]
        form.descripcion.data = producto["descripcion"]
        form.precio.data = producto["precio"]
        form.stock.data = producto["stock"]

    return render_template(
        "formulario_producto.html", titulo="Modificar producto",
        subtitulo="Actualice los datos seleccionados y guarde los cambios en MySQL.",
        form=form, accion=url_for("editar_producto", id_producto=id_producto),
        modo_edicion=True,
    )


@app.route("/productos/<int:id_producto>/eliminar", methods=["POST"])
@login_required
def eliminar_producto(id_producto):
    """Procesa una eliminación protegida con CSRF y DELETE + WHERE."""
    form = EliminarProductoForm()
    if not form.validate_on_submit():
        abort(400)
    try:
        producto = buscar_producto_por_id(id_producto)
        if producto is None:
            abort(404)
        filas = eliminar_producto_bd(id_producto)
    except IntegrityError:
        flash("El producto no puede eliminarse porque está relacionado con una factura.", "warning")
    except Error:
        app.logger.exception("No fue posible eliminar el producto")
        flash("MySQL no pudo eliminar el producto.", "danger")
    else:
        if filas:
            flash(f'Producto {producto["codigo"]} eliminado correctamente de MySQL.', "success")
        else:
            flash("El producto seleccionado ya no existe.", "warning")
    return redirect(url_for("productos"))


@app.route("/clientes")
@login_required
def clientes():
    return render_template(
        "clientes.html", titulo="Clientes", clientes=CLIENTES,
        aviso="Módulo preparado para su integración relacional en los siguientes avances.",
    )


@app.route("/clientes/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_cliente():
    form = ClienteForm()
    if form.validate_on_submit():
        codigo = form.codigo.data.strip().upper()
        if buscar_por_codigo(CLIENTES, codigo):
            form.codigo.errors.append("Ya existe un cliente con este código.")
        else:
            CLIENTES.append({
                "codigo": codigo, "nombre": form.nombre.data.strip().upper(),
                "tipo": form.tipo.data, "correo": form.correo.data.strip().lower(),
                "ciudad": form.ciudad.data.strip(),
            })
            flash("Cliente registrado correctamente.", "success")
            return redirect(url_for("clientes"))
    return render_template("formulario_cliente.html", titulo="Registrar cliente", form=form)


@app.route("/proveedores")
@login_required
def proveedores():
    return render_template(
        "proveedores.html", titulo="Proveedores", proveedores=PROVEEDORES,
        aviso="Los proveedores también están modelados en sql/esquema.sql y relacionados con Productos.",
    )


@app.route("/proveedores/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_proveedor():
    form = ProveedorForm()
    if form.validate_on_submit():
        codigo = form.codigo.data.strip().upper()
        if buscar_por_codigo(PROVEEDORES, codigo):
            form.codigo.errors.append("Ya existe un proveedor con este código.")
        else:
            dias = form.entrega_dias.data
            PROVEEDORES.append({
                "codigo": codigo, "nombre": form.nombre.data.strip().upper(),
                "categoria": form.categoria.data.strip(),
                "correo": form.correo.data.strip().lower(), "ciudad": form.ciudad.data.strip(),
                "entrega": f"{dias} día" if dias == 1 else f"{dias} días",
            })
            flash("Proveedor registrado correctamente.", "success")
            return redirect(url_for("proveedores"))
    return render_template("formulario_proveedor.html", titulo="Registrar proveedor", form=form)


@app.route("/facturacion")
@login_required
def facturacion():
    completar_totales_factura()
    return render_template(
        "facturacion.html", titulo="Facturación", factura=FACTURA,
        detalle=DETALLE_FACTURA,
        aviso="Comprobante demostrativo; sus tablas relacionales se encuentran preparadas en sql/esquema.sql.",
    )


@app.route("/facturacion/nueva", methods=["GET", "POST"])
@login_required
def nueva_factura():
    form = FacturacionForm()
    try:
        productos_disponibles = [p for p in obtener_productos() if p["stock"] > 0]
    except Error:
        app.logger.exception("No fue posible consultar productos para facturación")
        productos_disponibles = []
        flash("No se pudo consultar el catálogo de MySQL.", "danger")

    form.cliente_codigo.choices = [
        (c["codigo"], f'{c["codigo"]} · {c["nombre"]}') for c in CLIENTES
    ]
    form.producto_codigo.choices = [
        (p["codigo"], f'{p["codigo"]} · {p["nombre"]}') for p in productos_disponibles
    ]

    if form.validate_on_submit():
        cliente = buscar_por_codigo(CLIENTES, form.cliente_codigo.data)
        try:
            producto = buscar_producto_por_codigo(form.producto_codigo.data)
        except Error:
            producto = None
            flash("No se pudo consultar el producto en MySQL.", "danger")
        codigo_factura = form.numero.data.strip().upper()
        if codigo_factura == FACTURA["numero"]:
            form.numero.errors.append("Ingrese un número diferente al comprobante actual.")
        elif producto is None or producto["stock"] <= 0:
            form.producto_codigo.errors.append("Seleccione un producto disponible.")
        elif form.cantidad.data > producto["stock"]:
            form.cantidad.errors.append(f'La cantidad supera el stock disponible ({producto["stock"]}).')
        else:
            precio = Decimal(str(producto["precio"]))
            DETALLE_FACTURA.clear()
            DETALLE_FACTURA.append({
                "codigo": producto["codigo"], "producto": producto["nombre"],
                "cantidad": form.cantidad.data, "precio": precio,
            })
            FACTURA.clear()
            FACTURA.update({
                "numero": codigo_factura, "fecha": form.fecha.data.strftime("%d/%m/%Y"),
                "cliente": cliente["nombre"], "codigo_cliente": cliente["codigo"],
                "correo": cliente["correo"],
            })
            completar_totales_factura()
            flash("Comprobante generado correctamente.", "success")
            return redirect(url_for("facturacion"))

    if not form.is_submitted():
        form.fecha.data = date.today()
    return render_template("formulario_facturacion.html", titulo="Generar comprobante", form=form)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
