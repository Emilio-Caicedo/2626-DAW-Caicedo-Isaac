"""Pruebas de formularios, validación, CSRF y conservación de rutas."""

import re
import unittest
from copy import deepcopy
from decimal import Decimal
from pathlib import Path

from flask_wtf import FlaskForm

from app import (
    CLIENTES,
    DETALLE_FACTURA,
    FACTURA,
    PRODUCTOS,
    PROVEEDORES,
    app,
)
from forms import ClienteForm, FacturacionForm, ProductoForm, ProveedorForm

RAIZ = Path(__file__).resolve().parents[1]
PRODUCTOS_INICIALES = deepcopy(PRODUCTOS)
CLIENTES_INICIALES = deepcopy(CLIENTES)
PROVEEDORES_INICIALES = deepcopy(PROVEEDORES)
DETALLE_INICIAL = deepcopy(DETALLE_FACTURA)
FACTURA_INICIAL = deepcopy(FACTURA)


class Semana11Test(unittest.TestCase):
    """Comprueba los requisitos expresos del Avance 11/16."""

    @classmethod
    def setUpClass(cls):
        cls.config_testing = app.config["TESTING"]
        cls.config_csrf = app.config.get("WTF_CSRF_ENABLED", True)
        app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)

    @classmethod
    def tearDownClass(cls):
        app.config.update(
            TESTING=cls.config_testing, WTF_CSRF_ENABLED=cls.config_csrf
        )

    def setUp(self):
        PRODUCTOS[:] = deepcopy(PRODUCTOS_INICIALES)
        CLIENTES[:] = deepcopy(CLIENTES_INICIALES)
        PROVEEDORES[:] = deepcopy(PROVEEDORES_INICIALES)
        DETALLE_FACTURA[:] = deepcopy(DETALLE_INICIAL)
        FACTURA.clear()
        FACTURA.update(deepcopy(FACTURA_INICIAL))
        self.cliente = app.test_client()

    def test_01_clases_heredan_de_flaskform(self):
        for clase in [ProductoForm, ClienteForm, ProveedorForm, FacturacionForm]:
            with self.subTest(clase=clase.__name__):
                self.assertTrue(issubclass(clase, FlaskForm))

    def test_02_rutas_get_post_y_token_csrf(self):
        app.config["WTF_CSRF_ENABLED"] = True
        rutas = [
            "/productos/nuevo",
            "/clientes/nuevo",
            "/proveedores/nuevo",
            "/facturacion/nueva",
        ]
        reglas = {regla.rule: regla.methods for regla in app.url_map.iter_rules()}
        for ruta in rutas:
            with self.subTest(ruta=ruta):
                self.assertTrue({"GET", "POST"}.issubset(reglas[ruta]))
                respuesta = self.cliente.get(ruta)
                html = respuesta.get_data(as_text=True)
                self.assertEqual(respuesta.status_code, 200)
                self.assertIn('method="POST"', html)
                self.assertRegex(html, r'name="csrf_token"[^>]*type="hidden"')
        app.config["WTF_CSRF_ENABLED"] = False

    def test_03_csrf_impide_procesar_post_sin_token(self):
        app.config["WTF_CSRF_ENABLED"] = True
        cantidad = len(PRODUCTOS)
        respuesta = self.cliente.post(
            "/productos/nuevo",
            data={
                "codigo": "PRO-007",
                "nombre": "Monitor profesional",
                "categoria": "Accesorios tecnológicos",
                "descripcion": "Monitor de alta resolución para oficina.",
                "precio": "200.00",
                "stock": "4",
            },
        )
        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(len(PRODUCTOS), cantidad)
        app.config["WTF_CSRF_ENABLED"] = False

    def test_04_campos_vacios_muestran_errores(self):
        for ruta, mensaje in [
            ("/productos/nuevo", "El código es obligatorio."),
            ("/clientes/nuevo", "El nombre es obligatorio."),
            ("/proveedores/nuevo", "El correo es obligatorio."),
            ("/facturacion/nueva", "La cantidad es obligatoria."),
        ]:
            with self.subTest(ruta=ruta):
                respuesta = self.cliente.post(ruta, data={})
                self.assertEqual(respuesta.status_code, 200)
                self.assertIn(mensaje, respuesta.get_data(as_text=True))

    def test_05_validadores_de_correo_formato_y_rango(self):
        respuesta = self.cliente.post(
            "/clientes/nuevo",
            data={
                "codigo": "CODIGO-MAL",
                "nombre": "Cliente de prueba",
                "tipo": "Estudiante",
                "correo": "correo-invalido",
                "ciudad": "Puyo",
            },
        )
        html = respuesta.get_data(as_text=True)
        self.assertIn("Use el formato CLI-000.", html)
        self.assertIn("Ingrese un correo electrónico válido.", html)
        self.assertEqual(len(CLIENTES), len(CLIENTES_INICIALES))

        respuesta = self.cliente.post(
            "/productos/nuevo",
            data={
                "codigo": "PRO-007",
                "nombre": "Monitor profesional",
                "categoria": "Accesorios tecnológicos",
                "descripcion": "Monitor de alta resolución para oficina.",
                "precio": "-5",
                "stock": "-1",
            },
        )
        html = respuesta.get_data(as_text=True)
        self.assertIn("Ingrese un precio mayor que 0.", html)
        self.assertIn("Ingrese un valor entre 0 y 9999.", html)

    def test_06_registro_valido_de_producto(self):
        respuesta = self.cliente.post(
            "/productos/nuevo",
            data={
                "codigo": "PRO-007",
                "nombre": "Monitor de 24 pulgadas",
                "categoria": "Accesorios tecnológicos",
                "descripcion": "Pantalla Full HD para estudio y oficina.",
                "precio": "189.90",
                "stock": "6",
            },
            follow_redirects=True,
        )
        html = respuesta.get_data(as_text=True)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(PRODUCTOS), len(PRODUCTOS_INICIALES) + 1)
        self.assertIn("Producto registrado correctamente.", html)
        self.assertIn("Monitor de 24 pulgadas", html)
        self.assertEqual(PRODUCTOS[-1]["precio"], "189.90")

    def test_07_registro_valido_de_cliente(self):
        respuesta = self.cliente.post(
            "/clientes/nuevo",
            data={
                "codigo": "CLI-005",
                "nombre": "Cliente académico de prueba",
                "tipo": "Profesional",
                "correo": "cliente.prueba@example.com",
                "ciudad": "Puyo",
            },
            follow_redirects=True,
        )
        html = respuesta.get_data(as_text=True)
        self.assertEqual(len(CLIENTES), len(CLIENTES_INICIALES) + 1)
        self.assertIn("Cliente registrado correctamente.", html)
        self.assertIn("CLIENTE ACADÉMICO DE PRUEBA", html)

    def test_08_registro_valido_de_proveedor(self):
        respuesta = self.cliente.post(
            "/proveedores/nuevo",
            data={
                "codigo": "PRV-004",
                "nombre": "Proveedor académico",
                "categoria": "Monitores y accesorios para computadoras.",
                "correo": "ventas@example.com",
                "ciudad": "Ambato",
                "entrega_dias": "4",
            },
            follow_redirects=True,
        )
        html = respuesta.get_data(as_text=True)
        self.assertEqual(len(PROVEEDORES), len(PROVEEDORES_INICIALES) + 1)
        self.assertIn("Proveedor registrado correctamente.", html)
        self.assertIn("4 días", html)

    def test_09_codigos_duplicados_no_se_procesan(self):
        cantidad = len(PRODUCTOS)
        respuesta = self.cliente.post(
            "/productos/nuevo",
            data={
                "codigo": "PRO-001",
                "nombre": "Producto repetido",
                "categoria": "Componentes informáticos",
                "descripcion": "Este registro utiliza un código existente.",
                "precio": "10.00",
                "stock": "1",
            },
        )
        self.assertEqual(len(PRODUCTOS), cantidad)
        self.assertIn(
            "Ya existe un producto con este código.",
            respuesta.get_data(as_text=True),
        )

    def test_10_factura_valida_calcula_totales(self):
        respuesta = self.cliente.post(
            "/facturacion/nueva",
            data={
                "numero": "FAC-0002",
                "fecha": "2026-09-05",
                "cliente_codigo": "CLI-002",
                "producto_codigo": "PRO-003",
                "cantidad": "3",
            },
            follow_redirects=True,
        )
        html = respuesta.get_data(as_text=True)
        self.assertIn("Comprobante generado correctamente.", html)
        self.assertEqual(FACTURA["numero"], "FAC-0002")
        self.assertEqual(FACTURA["subtotal"], Decimal("75.00"))
        self.assertEqual(FACTURA["impuesto"], Decimal("11.25"))
        self.assertEqual(FACTURA["total"], Decimal("86.25"))
        self.assertIn("$86.25", html)

    def test_11_factura_rechaza_cantidad_superior_al_stock(self):
        numero_anterior = FACTURA["numero"]
        respuesta = self.cliente.post(
            "/facturacion/nueva",
            data={
                "numero": "FAC-0003",
                "fecha": "2026-09-05",
                "cliente_codigo": "CLI-001",
                "producto_codigo": "PRO-002",
                "cantidad": "9",
            },
        )
        self.assertEqual(FACTURA["numero"], numero_anterior)
        self.assertIn(
            "La cantidad supera el stock disponible (5).",
            respuesta.get_data(as_text=True),
        )

    def test_12_estructura_archivos_y_dependencias(self):
        for archivo in [
            "forms/__init__.py",
            "forms/producto_form.py",
            "forms/cliente_form.py",
            "forms/proveedor_form.py",
            "forms/facturacion_form.py",
            "templates/formulario_producto.html",
            "templates/formulario_cliente.html",
            "templates/formulario_proveedor.html",
            "templates/formulario_facturacion.html",
        ]:
            self.assertTrue((RAIZ / archivo).is_file(), archivo)

        requirements = (RAIZ / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("Flask-WTF==", requirements)
        self.assertIn("WTForms==", requirements)
        self.assertIn("email-validator==", requirements)
        app_py = (RAIZ / "app.py").read_text(encoding="utf-8")
        self.assertIn('app.config["SECRET_KEY"]', app_py)
        self.assertEqual(
            len(re.findall(r"validate_on_submit\(\)", app_py)), 4
        )


if __name__ == "__main__":
    unittest.main()
