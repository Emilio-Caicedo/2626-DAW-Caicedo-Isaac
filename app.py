from decimal import Decimal

from flask import Flask, render_template, url_for

app = Flask(__name__)

# Variable simple compartida por la portada Flask y su exportación estática.
NOMBRE_TIENDA = "EmiTech Store"


def obtener_catalogo():
    """Conserva las tres categorías dinámicas de la página de la semana 8."""
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


@app.route("/")
def inicio():
    """Página informativa conservada de las semanas anteriores."""
    return render_template(
        "index.html", titulo=NOMBRE_TIENDA, catalogo=obtener_catalogo()
    )


@app.route("/productos")
def productos():
    """Catálogo del módulo Productos."""
    # Variable simple: se envía a Jinja2 y se muestra mediante {{ titulo }}.
    titulo = "Productos"
    # Lista de diccionarios. PRO-006 tiene stock cero para probar el else.
    lista_productos = [
        {"codigo": "PRO-001", "nombre": "Laptop para estudio", "categoria": "Laptops y computadoras", "descripcion": "Pantalla de 15,6 pulgadas, 8 GB de RAM y SSD de 512 GB.", "precio": "550.00", "stock": 8, "imagen": "laptop-estudio.jpg"},
        {"codigo": "PRO-002", "nombre": "Computadora de escritorio", "categoria": "Laptops y computadoras", "descripcion": "Equipo para oficina con 16 GB de RAM y SSD de 512 GB.", "precio": "680.00", "stock": 5, "imagen": "computadora-escritorio.jpg"},
        {"codigo": "PRO-003", "nombre": "Teclado y mouse", "categoria": "Accesorios tecnológicos", "descripcion": "Kit USB para las actividades diarias de estudio y trabajo.", "precio": "25.00", "stock": 20, "imagen": "teclado-mouse.jpg"},
        {"codigo": "PRO-004", "nombre": "Audífonos con micrófono", "categoria": "Accesorios tecnológicos", "descripcion": "Accesorio para clases virtuales, reuniones y llamadas.", "precio": "30.00", "stock": 12, "imagen": "audifonos.jpg"},
        {"codigo": "PRO-005", "nombre": "Memoria RAM de 8 GB", "categoria": "Componentes informáticos", "descripcion": "Módulo DDR4 para equipos compatibles.", "precio": "28.00", "stock": 15, "imagen": "memoria-ram.jpg"},
        {"codigo": "PRO-006", "nombre": "Disco SSD de 480 GB", "categoria": "Componentes informáticos", "descripcion": "Unidad SATA para mejorar el almacenamiento del equipo.", "precio": "45.00", "stock": 0, "imagen": "disco-ssd.jpg"},
    ]
    return render_template(
        "productos.html",
        titulo=titulo,
        productos=lista_productos,
        aviso="Catálogo de ejemplo: precios, existencias e imágenes ilustrativos.",
    )


@app.route("/clientes")
def clientes():
    """Directorio para representar el módulo Clientes."""
    lista_clientes = [
        {"codigo": "CLI-001", "nombre": "CARLOS SEGUNDO ARCE BATALLAS", "tipo": "Estudiante", "correo": "cs.arceb@uea.edu.ec", "ciudad": "Puyo"},
        {"codigo": "CLI-002", "nombre": "JORDAN ALEXANDER ARRIAGA LOGRONO", "tipo": "Profesional", "correo": "ja.arriagal@uea.edu.ec", "ciudad": "Tena"},
        {"codigo": "CLI-003", "nombre": "XAVIER ALEXANDER CASA LEMA", "tipo": "Emprendimiento", "correo": "xa.casal@uea.edu.ec", "ciudad": "El Reventador"},
        {"codigo": "CLI-004", "nombre": "CRISTIAN DAVID CHIQUIMBA MENA", "tipo": "Empresa", "correo": "cd.chiquimbam@uea.edu.ec", "ciudad": "Nueva Loja"},
    ]
    return render_template(
        "clientes.html",
        titulo="Clientes",
        clientes=lista_clientes,
        aviso="Directorio de ejemplo. Los nombres y correos son de compañeros de la UEA.",
    )


@app.route("/proveedores")
def proveedores():
    """Proveedores de las categorías de EmiTech Store."""
    lista_proveedores = [
        {"codigo": "PRV-001", "nombre": "LUSANCOMP", "categoria": "Laptops, PCs corporativas y componentes informáticos.", "correo": "ventas@lusancomp.com", "ciudad": "Quito", "entrega": "2 a 4 días"},
        {"codigo": "PRV-002", "nombre": "MAXXICOMP", "categoria": "Laptops, hardware, periféricos y accesorios.", "correo": "ventasenlinea@maxxicomp.com", "ciudad": "Guayaquil", "entrega": "3 a 6 días"},
        {"codigo": "PRV-003", "nombre": "PC MAX TECNOLOGIA", "categoria": "Componentes, PC computadoras y accesorios tecnológicos.", "correo": "contacto@pcmax.com.ec", "ciudad": "Quito", "entrega": "2 a 4 días"},
    ]
    return render_template(
        "proveedores.html",
        titulo="Proveedores",
        proveedores=lista_proveedores,
        aviso="Proveedores consultados en Internet. Los plazos de entrega se incluyen como referencia.",
    )


@app.route("/facturacion")
def facturacion():
    """Comprobante didáctico; no emite facturas ni realiza cobros."""
    detalle = [
        {"codigo": "PRO-001", "producto": "Laptop para estudio", "cantidad": 1, "precio": Decimal("550.00")},
        {"codigo": "PRO-003", "producto": "Teclado y mouse", "cantidad": 2, "precio": Decimal("25.00")},
    ]
    for item in detalle:
        item["subtotal"] = item["cantidad"] * item["precio"]

    subtotal = sum((item["subtotal"] for item in detalle), Decimal("0.00"))
    # Porcentaje exclusivamente ilustrativo para practicar el cálculo.
    tasa_impuesto_demo = Decimal("0.15")
    impuesto = (subtotal * tasa_impuesto_demo).quantize(Decimal("0.01"))
    factura = {
        "numero": "DEMO-0001",
        "fecha": "02/09/2026",
        "cliente": "CARLOS SEGUNDO ARCE BATALLAS",
        "codigo_cliente": "CLI-001",
        "correo": "cs.arceb@uea.edu.ec",
        "subtotal": subtotal,
        "impuesto": impuesto,
        "total": subtotal + impuesto,
    }
    return render_template(
        "facturacion.html",
        titulo="Facturación",
        factura=factura,
        detalle=detalle,
        aviso="Comprobante demostrativo, sin validez tributaria. No se emite una factura ni se realiza un cobro.",
    )


if __name__ == "__main__":
    # Servidor de desarrollo local. Detener con Ctrl+C.
    app.run(host="127.0.0.1", port=5000)
