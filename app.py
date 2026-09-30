"""EmiTech Store - Proyecto Integrador, Semana 15.

Aplicación Flask con PostgreSQL, autenticación y operaciones CRUD protegidas.
Productos, clientes y proveedores se almacenan en tablas relacionadas; el
módulo de facturación demuestra consultas JOIN y transacciones parametrizadas.
"""

import os
from datetime import date
from decimal import Decimal

from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_wtf.csrf import CSRFProtect
from psycopg import Error, IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from conexion import conectar_bd
from forms import (
    ClienteForm,
    CerrarSesionForm,
    EliminarProductoForm,
    EliminarRegistroForm,
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
    SESSION_COOKIE_SECURE=os.getenv("RENDER", "").lower() == "true",
)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Inicie sesión para acceder a esta página."
login_manager.login_message_category = "warning"
login_manager.session_protection = "strong"

NOMBRE_TIENDA = "EmiTech Store"
TASA_IMPUESTO = Decimal("0.15")
ERRORES_BD = (Error, RuntimeError)

# Se conservan como evidencia histórica para el frontend estático y las semanas
# anteriores. En la Semana 15 la aplicación no modifica estas colecciones.
PRODUCTOS_INICIALES = [
    {"codigo": "PRO-001", "nombre": "Laptop para estudio"},
    {"codigo": "PRO-002", "nombre": "Computadora de escritorio"},
    {"codigo": "PRO-003", "nombre": "Teclado y mouse"},
    {"codigo": "PRO-004", "nombre": "Audífonos con micrófono"},
    {"codigo": "PRO-005", "nombre": "Memoria RAM de 8 GB"},
    {"codigo": "PRO-006", "nombre": "Disco SSD de 480 GB"},
]
CLIENTES = []
PROVEEDORES = []
DETALLE_FACTURA = []
FACTURA = {}


def _cerrar_recursos(cursor, conexion):
    """Cierra cursor y conexión aunque una consulta haya fallado."""
    if cursor is not None:
        cursor.close()
    if conexion is not None:
        conexion.close()


def _consultar_todos(sql, parametros=()):
    conexion = cursor = None
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        cursor.execute(sql, parametros)
        return cursor.fetchall()
    finally:
        _cerrar_recursos(cursor, conexion)


def _consultar_uno(sql, parametros=()):
    conexion = cursor = None
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        cursor.execute(sql, parametros)
        return cursor.fetchone()
    finally:
        _cerrar_recursos(cursor, conexion)


def _ejecutar(sql, parametros=(), devolver_id=False):
    conexion = cursor = None
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        cursor.execute(sql, parametros)
        resultado = cursor.fetchone() if devolver_id else cursor.rowcount
        conexion.commit()
        return resultado["id"] if devolver_id else resultado
    except ERRORES_BD:
        if conexion is not None:
            conexion.rollback()
        raise
    finally:
        _cerrar_recursos(cursor, conexion)


# ---------------------------------------------------------------------------
# Usuarios y autenticación
# ---------------------------------------------------------------------------

def buscar_usuario_por_id(id_usuario):
    return _consultar_uno(
        """SELECT id_usuario, usuario, nombre_completo, password_hash, activo
           FROM usuarios WHERE id_usuario = %s AND activo = TRUE""",
        (id_usuario,),
    )


def buscar_usuario_por_nombre(nombre_usuario):
    return _consultar_uno(
        """SELECT id_usuario, usuario, nombre_completo, password_hash, activo
           FROM usuarios WHERE usuario = %s AND activo = TRUE""",
        (nombre_usuario.strip().lower(),),
    )


def insertar_usuario(usuario, nombre_completo, password_hash):
    return _ejecutar(
        """INSERT INTO usuarios (usuario, nombre_completo, password_hash)
           VALUES (%s, %s, %s) RETURNING id_usuario AS id""",
        (usuario.strip().lower(), nombre_completo.strip(), password_hash),
        devolver_id=True,
    )


@login_manager.user_loader
def cargar_usuario(id_usuario):
    try:
        fila = buscar_usuario_por_id(int(id_usuario))
    except (TypeError, ValueError):
        return None
    except ERRORES_BD:
        app.logger.exception("No fue posible recuperar la sesión desde PostgreSQL")
        return None
    return Usuario.desde_fila(fila)


@app.context_processor
def componentes_de_sesion():
    return {"cerrar_sesion_form": CerrarSesionForm()}


# ---------------------------------------------------------------------------
# Productos: CRUD y JOIN con proveedores
# ---------------------------------------------------------------------------

SQL_PRODUCTOS = """
    SELECT p.id_producto AS id, p.codigo, p.nombre, p.categoria,
           p.descripcion, p.precio, p.stock, p.imagen, p.id_proveedor,
           pr.nombre AS proveedor_nombre
    FROM productos AS p
    INNER JOIN proveedores AS pr ON pr.id_proveedor = p.id_proveedor
"""


def obtener_productos():
    return _consultar_todos(SQL_PRODUCTOS + " ORDER BY p.id_producto")


def obtener_proveedores_bd():
    return _consultar_todos(
        "SELECT id_proveedor, codigo, nombre FROM proveedores ORDER BY nombre"
    )


def buscar_producto_por_id(id_producto):
    return _consultar_uno(SQL_PRODUCTOS + " WHERE p.id_producto = %s", (id_producto,))


def buscar_producto_por_codigo(codigo):
    return _consultar_uno(
        """SELECT id_producto AS id, codigo, nombre, categoria, descripcion,
                  precio, stock, imagen, id_proveedor
           FROM productos WHERE codigo = %s""",
        (codigo.strip().upper(),),
    )


def insertar_producto(producto):
    return _ejecutar(
        """INSERT INTO productos
               (codigo, nombre, categoria, descripcion, precio, stock, imagen, id_proveedor)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
           RETURNING id_producto AS id""",
        tuple(producto[c] for c in (
            "codigo", "nombre", "categoria", "descripcion", "precio", "stock",
            "imagen", "id_proveedor",
        )),
        devolver_id=True,
    )


def actualizar_producto(id_producto, producto):
    return _ejecutar(
        """UPDATE productos
           SET codigo=%s, nombre=%s, categoria=%s, descripcion=%s, precio=%s,
               stock=%s, imagen=%s, id_proveedor=%s
           WHERE id_producto=%s""",
        tuple(producto[c] for c in (
            "codigo", "nombre", "categoria", "descripcion", "precio", "stock",
            "imagen", "id_proveedor",
        )) + (id_producto,),
    )


def eliminar_producto_bd(id_producto):
    return _ejecutar("DELETE FROM productos WHERE id_producto=%s", (id_producto,))


# ---------------------------------------------------------------------------
# Clientes: CRUD y relación con facturas
# ---------------------------------------------------------------------------

SQL_CLIENTES = """
    SELECT c.id_cliente AS id, c.codigo, c.nombre, c.tipo, c.correo, c.ciudad,
           COUNT(f.id_factura)::int AS total_facturas
    FROM clientes AS c
    LEFT JOIN facturas AS f ON f.id_cliente = c.id_cliente
"""


def obtener_clientes():
    return _consultar_todos(
        SQL_CLIENTES + " GROUP BY c.id_cliente ORDER BY c.id_cliente"
    )


def buscar_cliente_por_id(id_cliente):
    return _consultar_uno(
        """SELECT id_cliente AS id, codigo, nombre, tipo, correo, ciudad
           FROM clientes WHERE id_cliente=%s""",
        (id_cliente,),
    )


def buscar_cliente_por_codigo(codigo):
    return _consultar_uno(
        """SELECT id_cliente AS id, codigo, nombre, tipo, correo, ciudad
           FROM clientes WHERE codigo=%s""",
        (codigo.strip().upper(),),
    )


def insertar_cliente(cliente):
    return _ejecutar(
        """INSERT INTO clientes (codigo, nombre, tipo, correo, ciudad)
           VALUES (%s, %s, %s, %s, %s) RETURNING id_cliente AS id""",
        tuple(cliente[c] for c in ("codigo", "nombre", "tipo", "correo", "ciudad")),
        devolver_id=True,
    )


def actualizar_cliente(id_cliente, cliente):
    return _ejecutar(
        """UPDATE clientes SET codigo=%s, nombre=%s, tipo=%s, correo=%s, ciudad=%s
           WHERE id_cliente=%s""",
        tuple(cliente[c] for c in ("codigo", "nombre", "tipo", "correo", "ciudad"))
        + (id_cliente,),
    )


def eliminar_cliente_bd(id_cliente):
    return _ejecutar("DELETE FROM clientes WHERE id_cliente=%s", (id_cliente,))


# ---------------------------------------------------------------------------
# Proveedores: CRUD y relación con productos
# ---------------------------------------------------------------------------

SQL_PROVEEDORES = """
    SELECT pr.id_proveedor AS id, pr.codigo, pr.nombre, pr.categoria, pr.correo,
           pr.ciudad, pr.entrega_dias,
           COUNT(p.id_producto)::int AS total_productos
    FROM proveedores AS pr
    LEFT JOIN productos AS p ON p.id_proveedor = pr.id_proveedor
"""


def obtener_proveedores():
    return _consultar_todos(
        SQL_PROVEEDORES + " GROUP BY pr.id_proveedor ORDER BY pr.id_proveedor"
    )


def buscar_proveedor_por_id(id_proveedor):
    return _consultar_uno(
        """SELECT id_proveedor AS id, codigo, nombre, categoria, correo, ciudad,
                  entrega_dias
           FROM proveedores WHERE id_proveedor=%s""",
        (id_proveedor,),
    )


def insertar_proveedor(proveedor):
    return _ejecutar(
        """INSERT INTO proveedores
               (codigo, nombre, categoria, correo, ciudad, entrega_dias)
           VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_proveedor AS id""",
        tuple(proveedor[c] for c in (
            "codigo", "nombre", "categoria", "correo", "ciudad", "entrega_dias",
        )),
        devolver_id=True,
    )


def actualizar_proveedor(id_proveedor, proveedor):
    return _ejecutar(
        """UPDATE proveedores
           SET codigo=%s, nombre=%s, categoria=%s, correo=%s, ciudad=%s,
               entrega_dias=%s WHERE id_proveedor=%s""",
        tuple(proveedor[c] for c in (
            "codigo", "nombre", "categoria", "correo", "ciudad", "entrega_dias",
        )) + (id_proveedor,),
    )


def eliminar_proveedor_bd(id_proveedor):
    return _ejecutar("DELETE FROM proveedores WHERE id_proveedor=%s", (id_proveedor,))


# ---------------------------------------------------------------------------
# Facturación: lectura relacionada y transacción de creación
# ---------------------------------------------------------------------------

def obtener_ultima_factura():
    factura = _consultar_uno(
        """SELECT f.id_factura AS id, f.numero, TO_CHAR(f.fecha, 'DD/MM/YYYY') AS fecha,
                  f.subtotal, f.impuesto, f.total, c.codigo AS codigo_cliente,
                  c.nombre AS cliente, c.correo
           FROM facturas AS f
           INNER JOIN clientes AS c ON c.id_cliente = f.id_cliente
           ORDER BY f.id_factura DESC LIMIT 1"""
    )
    if factura is None:
        return None, []
    detalle = _consultar_todos(
        """SELECT p.codigo, p.nombre AS producto, d.cantidad,
                  d.precio_unitario AS precio, d.subtotal
           FROM detalle_factura AS d
           INNER JOIN productos AS p ON p.id_producto = d.id_producto
           WHERE d.id_factura=%s ORDER BY d.id_detalle""",
        (factura["id"],),
    )
    return factura, detalle


def crear_factura(numero, fecha_factura, codigo_cliente, codigo_producto, cantidad):
    """Crea cabecera/detalle y descuenta stock dentro de una transacción."""
    conexion = cursor = None
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id_cliente FROM clientes WHERE codigo=%s", (codigo_cliente,)
        )
        cliente = cursor.fetchone()
        cursor.execute(
            """SELECT id_producto, precio, stock FROM productos
               WHERE codigo=%s FOR UPDATE""",
            (codigo_producto,),
        )
        producto = cursor.fetchone()
        if cliente is None or producto is None:
            raise ValueError("Cliente o producto inexistente.")
        if producto["stock"] < cantidad:
            raise ValueError("La cantidad supera el stock disponible.")

        subtotal = (Decimal(str(producto["precio"])) * cantidad).quantize(Decimal("0.01"))
        impuesto = (subtotal * TASA_IMPUESTO).quantize(Decimal("0.01"))
        total = subtotal + impuesto
        cursor.execute(
            """INSERT INTO facturas (numero, id_cliente, fecha, subtotal, impuesto, total)
               VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_factura""",
            (numero, cliente["id_cliente"], fecha_factura, subtotal, impuesto, total),
        )
        id_factura = cursor.fetchone()["id_factura"]
        cursor.execute(
            """INSERT INTO detalle_factura
                   (id_factura, id_producto, cantidad, precio_unitario, subtotal)
               VALUES (%s, %s, %s, %s, %s)""",
            (id_factura, producto["id_producto"], cantidad, producto["precio"], subtotal),
        )
        cursor.execute(
            "UPDATE productos SET stock=stock-%s WHERE id_producto=%s",
            (cantidad, producto["id_producto"]),
        )
        conexion.commit()
        return id_factura
    except (Error, RuntimeError, ValueError):
        if conexion is not None:
            conexion.rollback()
        raise
    finally:
        _cerrar_recursos(cursor, conexion)


# ---------------------------------------------------------------------------
# Transformaciones de formularios
# ---------------------------------------------------------------------------

def obtener_catalogo():
    return [
        {"nombre": "Laptops y computadoras", "descripcion": "Equipos ideales para estudiar, trabajar, emprender y desarrollar diferentes actividades profesionales.", "imagen": url_for("static", filename="img/laptops-computadoras.jpg")},
        {"nombre": "Accesorios tecnológicos", "descripcion": "Teclados, mouse, audífonos y diferentes accesorios para mejorar la experiencia de uso de tus equipos.", "imagen": url_for("static", filename="img/accesorios-tecnologicos.jpg")},
        {"nombre": "Componentes informáticos", "descripcion": "Memorias RAM, discos SSD y componentes para actualizar o mejorar una computadora.", "imagen": url_for("static", filename="img/componentes-informaticos.jpg")},
    ]


def imagen_por_categoria(categoria):
    return {
        "Laptops y computadoras": "laptops-computadoras.jpg",
        "Accesorios tecnológicos": "accesorios-tecnologicos.jpg",
        "Componentes informáticos": "componentes-informaticos.jpg",
    }[categoria]


def producto_desde_formulario(form):
    return {
        "codigo": form.codigo.data.strip().upper(), "nombre": form.nombre.data.strip(),
        "categoria": form.categoria.data, "descripcion": form.descripcion.data.strip(),
        "precio": form.precio.data, "stock": form.stock.data,
        "imagen": imagen_por_categoria(form.categoria.data),
        "id_proveedor": form.proveedor_id.data,
    }


def cliente_desde_formulario(form):
    return {
        "codigo": form.codigo.data.strip().upper(), "nombre": form.nombre.data.strip().upper(),
        "tipo": form.tipo.data, "correo": form.correo.data.strip().lower(),
        "ciudad": form.ciudad.data.strip(),
    }


def proveedor_desde_formulario(form):
    return {
        "codigo": form.codigo.data.strip().upper(), "nombre": form.nombre.data.strip().upper(),
        "categoria": form.categoria.data.strip(), "correo": form.correo.data.strip().lower(),
        "ciudad": form.ciudad.data.strip(), "entrega_dias": form.entrega_dias.data,
    }


def cargar_proveedores_en_formulario(form):
    form.proveedor_id.choices = [(0, "Seleccione un proveedor")] + [
        (p["id_proveedor"], f'{p["codigo"]} · {p["nombre"]}')
        for p in obtener_proveedores_bd()
    ]


def _destino_interno_seguro(destino):
    return bool(destino and destino.startswith("/") and not destino.startswith("//"))


# ---------------------------------------------------------------------------
# Rutas públicas y autenticación
# ---------------------------------------------------------------------------

@app.route("/")
def inicio():
    return render_template("index.html", titulo=NOMBRE_TIENDA, catalogo=obtener_catalogo())


@app.route("/salud")
def salud():
    return {"servicio": "EmiTech Store", "estado": "ok"}, 200


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    form = UsuarioForm()
    if form.validate_on_submit():
        try:
            insertar_usuario(
                form.usuario.data, form.nombre_completo.data,
                generate_password_hash(form.password.data),
            )
        except IntegrityError:
            form.usuario.errors.append("El nombre de usuario ya está registrado.")
        except ERRORES_BD as error:
            codigo = getattr(error, "sqlstate", None) or "CONEXION"
            app.logger.exception(
                "No fue posible registrar el usuario [código %s]", codigo
            )
            flash(
                f"No se pudo guardar la cuenta en PostgreSQL. Código: {codigo}.",
                "danger",
            )
        else:
            flash("Cuenta creada correctamente. Ya puede iniciar sesión.", "success")
            return redirect(url_for("login"))
    return render_template("registro.html", titulo="Crear cuenta", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    form = LoginForm()
    siguiente = request.args.get("next", "")
    if form.validate_on_submit():
        try:
            fila = buscar_usuario_por_nombre(form.usuario.data)
        except ERRORES_BD:
            app.logger.exception("No fue posible consultar el usuario")
            flash("No se pudo conectar con PostgreSQL.", "danger")
        else:
            if fila and check_password_hash(fila["password_hash"], form.password.data):
                login_user(Usuario.desde_fila(fila), remember=form.recordar.data)
                flash(f'Bienvenido, {fila["nombre_completo"]}.', "success")
                return redirect(siguiente if _destino_interno_seguro(siguiente) else url_for("dashboard"))
            flash("Usuario o contraseña incorrectos.", "danger")
    return render_template("login.html", titulo="Iniciar sesión", form=form, siguiente=siguiente)


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", titulo="Panel de administración")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    form = CerrarSesionForm()
    if not form.validate_on_submit():
        abort(400)
    logout_user()
    flash("La sesión se cerró correctamente.", "success")
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Rutas CRUD de Productos
# ---------------------------------------------------------------------------

@app.route("/productos")
@login_required
def productos():
    try:
        registros = obtener_productos()
    except ERRORES_BD:
        app.logger.exception("No fue posible consultar productos")
        registros = []
        flash("No se pudo consultar PostgreSQL. Revise DATABASE_URL.", "danger")
    return render_template(
        "productos.html", titulo="Productos", productos=registros,
        aviso="Productos recuperados desde PostgreSQL mediante JOIN con Proveedores.",
        eliminar_form=EliminarProductoForm(),
    )


@app.route("/productos/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_producto():
    form = ProductoForm()
    try:
        cargar_proveedores_en_formulario(form)
    except ERRORES_BD:
        form.proveedor_id.choices = [(0, "PostgreSQL no disponible")]
        flash("No se pudo consultar los proveedores.", "danger")
    if form.validate_on_submit():
        try:
            insertar_producto(producto_desde_formulario(form))
        except IntegrityError:
            form.codigo.errors.append("El código ya existe o el proveedor no es válido.")
        except ERRORES_BD:
            flash("PostgreSQL no pudo guardar el producto.", "danger")
        else:
            flash("Producto registrado correctamente.", "success")
            return redirect(url_for("productos"))
    return render_template(
        "formulario_producto.html", titulo="Registrar producto",
        subtitulo="Complete los campos para incorporar un producto a PostgreSQL.",
        form=form, accion=url_for("nuevo_producto"), modo_edicion=False,
    )


@app.route("/productos/<int:id_producto>/editar", methods=["GET", "POST"])
@login_required
def editar_producto(id_producto):
    try:
        producto = buscar_producto_por_id(id_producto)
    except ERRORES_BD:
        flash("No se pudo consultar el producto.", "danger")
        return redirect(url_for("productos"))
    if producto is None:
        abort(404)
    form = ProductoForm()
    try:
        cargar_proveedores_en_formulario(form)
    except ERRORES_BD:
        form.proveedor_id.choices = [(0, "PostgreSQL no disponible")]
    if form.validate_on_submit():
        try:
            actualizar_producto(id_producto, producto_desde_formulario(form))
        except IntegrityError:
            form.codigo.errors.append("El código ya pertenece a otro producto.")
        except ERRORES_BD:
            flash("No se pudo actualizar el producto.", "danger")
        else:
            flash("Producto actualizado correctamente.", "success")
            return redirect(url_for("productos"))
    elif request.method == "GET":
        for campo in ("codigo", "nombre", "categoria", "descripcion", "precio", "stock"):
            getattr(form, campo).data = producto[campo]
        form.proveedor_id.data = producto["id_proveedor"]
    return render_template(
        "formulario_producto.html", titulo="Modificar producto",
        subtitulo="Actualice los datos y guarde los cambios en PostgreSQL.",
        form=form, accion=url_for("editar_producto", id_producto=id_producto),
        modo_edicion=True,
    )


@app.route("/productos/<int:id_producto>/eliminar", methods=["POST"])
@login_required
def eliminar_producto(id_producto):
    form = EliminarProductoForm()
    if not form.validate_on_submit():
        abort(400)
    try:
        producto = buscar_producto_por_id(id_producto)
        if producto is None:
            abort(404)
        eliminar_producto_bd(id_producto)
    except IntegrityError:
        flash("No puede eliminarse: el producto aparece en una factura.", "warning")
    except ERRORES_BD:
        flash("No se pudo eliminar el producto.", "danger")
    else:
        flash(f'Producto {producto["codigo"]} eliminado correctamente.', "success")
    return redirect(url_for("productos"))


# ---------------------------------------------------------------------------
# Rutas CRUD de Clientes
# ---------------------------------------------------------------------------

@app.route("/clientes")
@login_required
def clientes():
    try:
        registros = obtener_clientes()
    except ERRORES_BD:
        registros = []
        flash("No se pudo consultar los clientes.", "danger")
    return render_template(
        "clientes.html", titulo="Clientes", clientes=registros,
        aviso="Clientes almacenados en PostgreSQL; el total usa LEFT JOIN con Facturas.",
        eliminar_form=EliminarRegistroForm(),
    )


@app.route("/clientes/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_cliente():
    form = ClienteForm()
    if form.validate_on_submit():
        try:
            insertar_cliente(cliente_desde_formulario(form))
        except IntegrityError:
            form.codigo.errors.append("Ya existe un cliente con este código.")
        except ERRORES_BD:
            flash("No se pudo guardar el cliente.", "danger")
        else:
            flash("Cliente registrado correctamente.", "success")
            return redirect(url_for("clientes"))
    return render_template(
        "formulario_cliente.html", titulo="Registrar cliente", form=form,
        accion=url_for("nuevo_cliente"), modo_edicion=False,
    )


@app.route("/clientes/<int:id_cliente>/editar", methods=["GET", "POST"])
@login_required
def editar_cliente(id_cliente):
    try:
        cliente = buscar_cliente_por_id(id_cliente)
    except ERRORES_BD:
        flash("No se pudo consultar el cliente.", "danger")
        return redirect(url_for("clientes"))
    if cliente is None:
        abort(404)
    form = ClienteForm()
    if form.validate_on_submit():
        try:
            actualizar_cliente(id_cliente, cliente_desde_formulario(form))
        except IntegrityError:
            form.codigo.errors.append("El código ya pertenece a otro cliente.")
        except ERRORES_BD:
            flash("No se pudo actualizar el cliente.", "danger")
        else:
            flash("Cliente actualizado correctamente.", "success")
            return redirect(url_for("clientes"))
    elif request.method == "GET":
        for campo in ("codigo", "nombre", "tipo", "correo", "ciudad"):
            getattr(form, campo).data = cliente[campo]
    return render_template(
        "formulario_cliente.html", titulo="Modificar cliente", form=form,
        accion=url_for("editar_cliente", id_cliente=id_cliente), modo_edicion=True,
    )


@app.route("/clientes/<int:id_cliente>/eliminar", methods=["POST"])
@login_required
def eliminar_cliente(id_cliente):
    if not EliminarRegistroForm().validate_on_submit():
        abort(400)
    try:
        cliente = buscar_cliente_por_id(id_cliente)
        if cliente is None:
            abort(404)
        eliminar_cliente_bd(id_cliente)
    except IntegrityError:
        flash("No puede eliminarse: el cliente tiene facturas relacionadas.", "warning")
    except ERRORES_BD:
        flash("No se pudo eliminar el cliente.", "danger")
    else:
        flash(f'Cliente {cliente["codigo"]} eliminado correctamente.', "success")
    return redirect(url_for("clientes"))


# ---------------------------------------------------------------------------
# Rutas CRUD de Proveedores
# ---------------------------------------------------------------------------

@app.route("/proveedores")
@login_required
def proveedores():
    try:
        registros = obtener_proveedores()
    except ERRORES_BD:
        registros = []
        flash("No se pudo consultar los proveedores.", "danger")
    return render_template(
        "proveedores.html", titulo="Proveedores", proveedores=registros,
        aviso="Proveedores almacenados en PostgreSQL; cada tarjeta cuenta sus productos mediante JOIN.",
        eliminar_form=EliminarRegistroForm(),
    )


@app.route("/proveedores/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_proveedor():
    form = ProveedorForm()
    if form.validate_on_submit():
        try:
            insertar_proveedor(proveedor_desde_formulario(form))
        except IntegrityError:
            form.codigo.errors.append("Ya existe un proveedor con este código.")
        except ERRORES_BD:
            flash("No se pudo guardar el proveedor.", "danger")
        else:
            flash("Proveedor registrado correctamente.", "success")
            return redirect(url_for("proveedores"))
    return render_template(
        "formulario_proveedor.html", titulo="Registrar proveedor", form=form,
        accion=url_for("nuevo_proveedor"), modo_edicion=False,
    )


@app.route("/proveedores/<int:id_proveedor>/editar", methods=["GET", "POST"])
@login_required
def editar_proveedor(id_proveedor):
    try:
        proveedor = buscar_proveedor_por_id(id_proveedor)
    except ERRORES_BD:
        flash("No se pudo consultar el proveedor.", "danger")
        return redirect(url_for("proveedores"))
    if proveedor is None:
        abort(404)
    form = ProveedorForm()
    if form.validate_on_submit():
        try:
            actualizar_proveedor(id_proveedor, proveedor_desde_formulario(form))
        except IntegrityError:
            form.codigo.errors.append("El código ya pertenece a otro proveedor.")
        except ERRORES_BD:
            flash("No se pudo actualizar el proveedor.", "danger")
        else:
            flash("Proveedor actualizado correctamente.", "success")
            return redirect(url_for("proveedores"))
    elif request.method == "GET":
        for campo in ("codigo", "nombre", "categoria", "correo", "ciudad", "entrega_dias"):
            getattr(form, campo).data = proveedor[campo]
    return render_template(
        "formulario_proveedor.html", titulo="Modificar proveedor", form=form,
        accion=url_for("editar_proveedor", id_proveedor=id_proveedor), modo_edicion=True,
    )


@app.route("/proveedores/<int:id_proveedor>/eliminar", methods=["POST"])
@login_required
def eliminar_proveedor(id_proveedor):
    if not EliminarRegistroForm().validate_on_submit():
        abort(400)
    try:
        proveedor = buscar_proveedor_por_id(id_proveedor)
        if proveedor is None:
            abort(404)
        eliminar_proveedor_bd(id_proveedor)
    except IntegrityError:
        flash("No puede eliminarse: el proveedor tiene productos relacionados.", "warning")
    except ERRORES_BD:
        flash("No se pudo eliminar el proveedor.", "danger")
    else:
        flash(f'Proveedor {proveedor["codigo"]} eliminado correctamente.', "success")
    return redirect(url_for("proveedores"))


# ---------------------------------------------------------------------------
# Rutas de Facturación relacionadas
# ---------------------------------------------------------------------------

@app.route("/facturacion")
@login_required
def facturacion():
    try:
        factura, detalle = obtener_ultima_factura()
    except ERRORES_BD:
        factura, detalle = None, []
        flash("No se pudo consultar la facturación.", "danger")
    return render_template(
        "facturacion.html", titulo="Facturación", factura=factura, detalle=detalle,
        aviso="Consulta relacionada: Facturas + Clientes + Detalle + Productos.",
    )


@app.route("/facturacion/nueva", methods=["GET", "POST"])
@login_required
def nueva_factura():
    form = FacturacionForm()
    try:
        clientes_bd = obtener_clientes()
        productos_disponibles = [p for p in obtener_productos() if p["stock"] > 0]
    except ERRORES_BD:
        clientes_bd, productos_disponibles = [], []
        flash("No se pudo cargar los datos de facturación.", "danger")
    form.cliente_codigo.choices = [
        (c["codigo"], f'{c["codigo"]} · {c["nombre"]}') for c in clientes_bd
    ]
    form.producto_codigo.choices = [
        (p["codigo"], f'{p["codigo"]} · {p["nombre"]}') for p in productos_disponibles
    ]
    if form.validate_on_submit():
        try:
            crear_factura(
                form.numero.data.strip().upper(), form.fecha.data,
                form.cliente_codigo.data, form.producto_codigo.data, form.cantidad.data,
            )
        except IntegrityError:
            form.numero.errors.append("Ya existe una factura con este número.")
        except ValueError as error:
            form.cantidad.errors.append(str(error))
        except ERRORES_BD:
            flash("No se pudo guardar la factura.", "danger")
        else:
            flash("Factura registrada y stock actualizado correctamente.", "success")
            return redirect(url_for("facturacion"))
    if not form.is_submitted():
        form.fecha.data = date.today()
    return render_template("formulario_facturacion.html", titulo="Generar factura", form=form)


if __name__ == "__main__":
    # Se usa un solo proceso para que todas las solicitudes y errores aparezcan
    # claramente en esta misma terminal durante las pruebas locales.
    app.run(host="127.0.0.1", port=5000, debug=False)
