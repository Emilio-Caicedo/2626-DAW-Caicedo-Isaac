"""Pruebas de Semana 10, sin base de datos ni dependencias adicionales.

Desde la raíz: python -m unittest discover -s tests -v
Las pruebas no modifican los datos del proyecto ni el archivo index.html.
"""

from copy import deepcopy
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re
import unittest

from flask import render_template, template_rendered
from jinja2 import StrictUndefined

from app import NOMBRE_TIENDA, app, obtener_catalogo
from generar_frontend import url_estatica


RAIZ = Path(__file__).resolve().parents[1]
RUTAS = {
    "/": "EmiTech Store",
    "/productos": "Productos",
    "/clientes": "Clientes",
    "/proveedores": "Proveedores",
    "/facturacion": "Facturación",
}


class AnalizadorHTML(HTMLParser):
    def __init__(self, texto):
        super().__init__()
        self.elementos = []
        self.feed(texto)

    def handle_starttag(self, etiqueta, atributos):
        self.elementos.append((etiqueta, dict(atributos)))

    def ids(self):
        return [a["id"] for _, a in self.elementos if "id" in a]


class PruebasSemana10(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_anterior = app.config["TESTING"]
        cls.undefined_anterior = app.jinja_env.undefined
        app.config["TESTING"] = True
        # Una variable olvidada produce un error, en lugar de quedar en blanco.
        app.jinja_env.undefined = StrictUndefined

    @classmethod
    def tearDownClass(cls):
        app.config["TESTING"] = cls.config_anterior
        app.jinja_env.undefined = cls.undefined_anterior

    def setUp(self):
        self.cliente = app.test_client()

    def obtener_contexto(self, ruta):
        capturados = []

        def capturar(sender, template, context, **extra):
            capturados.append((template.name, context))

        with template_rendered.connected_to(capturar, app):
            respuesta = self.cliente.get(ruta)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(capturados), 1)
        return respuesta.get_data(as_text=True), capturados[0][1]

    def test_01_cinco_rutas_y_variables_simples(self):
        for ruta, titulo in RUTAS.items():
            with self.subTest(ruta=ruta):
                html, contexto = self.obtener_contexto(ruta)
                self.assertIsInstance(contexto["titulo"], str)
                self.assertEqual(contexto["titulo"], titulo)
                self.assertIn(f"<h1>{titulo}</h1>", html)
                self.assertNotIn("{%", html)
                self.assertNotIn("{{", html)

    def test_02_listas_diccionarios_y_numero_de_registros(self):
        for ruta, clave, cantidad in [
            ("/productos", "productos", 6),
            ("/clientes", "clientes", 4),
            ("/proveedores", "proveedores", 3),
            ("/facturacion", "detalle", 2),
        ]:
            with self.subTest(ruta=ruta):
                html, contexto = self.obtener_contexto(ruta)
                self.assertIsInstance(contexto[clave], list)
                self.assertEqual(len(contexto[clave]), cantidad)
                self.assertTrue(all(isinstance(item, dict) for item in contexto[clave]))
                for item in contexto[clave]:
                    self.assertIn(item["codigo"], html)
        _, contexto = self.obtener_contexto("/facturacion")
        self.assertIsInstance(contexto["factura"], dict)

    def test_03_stock_disponible_y_agotado(self):
        html, contexto = self.obtener_contexto("/productos")
        self.assertEqual(html.count('class="badge bg-success"'), 5)
        self.assertEqual(html.count('class="badge bg-danger"'), 1)
        self.assertIn("Disponible", html)
        self.assertIn("Agotado", html)
        self.assertIn("Consultar reposición", html)
        self.assertEqual(contexto["productos"][-1]["codigo"], "PRO-006")
        self.assertEqual(contexto["productos"][-1]["stock"], 0)

    def test_04_mismo_producto_cambia_segun_stock(self):
        _, contexto = self.obtener_contexto("/productos")
        producto = deepcopy(contexto["productos"][0])
        for stock, esperado, ausente in [(0, "Agotado", "Disponible"), (1, "Disponible", "Agotado")]:
            with self.subTest(stock=stock), app.test_request_context("/productos"):
                producto["stock"] = stock
                html = render_template("productos.html", titulo="Prueba", productos=[producto], aviso="")
                self.assertIn(esperado, html)
                self.assertNotIn(ausente, html)

    def test_05_listas_vacias_en_cuatro_modulos(self):
        casos = [
            ("/productos", "productos.html", "productos", "No hay productos registrados"),
            ("/clientes", "clientes.html", "clientes", "No hay clientes registrados"),
            ("/proveedores", "proveedores.html", "proveedores", "No hay proveedores registrados"),
            ("/facturacion", "facturacion.html", "detalle", "El comprobante no tiene productos"),
        ]
        for ruta, plantilla, clave, mensaje in casos:
            _, contexto = self.obtener_contexto(ruta)
            datos = {"titulo": contexto["titulo"], "aviso": contexto["aviso"], clave: []}
            if clave == "detalle":
                datos["factura"] = contexto["factura"]
            with self.subTest(ruta=ruta), app.test_request_context(ruta):
                html = render_template(plantilla, **datos)
                self.assertIn(mensaje, html)

    def test_06_titulo_realmente_dinamico(self):
        with app.test_request_context("/productos"):
            html = render_template("productos.html", titulo="Catálogo de prueba", productos=[], aviso="")
        self.assertIn("<h1>Catálogo de prueba</h1>", html)
        self.assertIn("<title>Catálogo de prueba | EmiTech Store</title>", html)

    def test_07_componentes_y_estructura_unica(self):
        base = (RAIZ / "templates/base.html").read_text(encoding="utf-8")
        for nombre in ["navbar", "footer"]:
            self.assertIn('{% include "components/' + nombre + '.html" %}', base)
        self.assertNotIn("<header", base)
        self.assertNotIn("<footer", base)
        for ruta in RUTAS:
            html = self.cliente.get(ruta).get_data(as_text=True)
            analizador = AnalizadorHTML(html)
            etiquetas = [e for e, _ in analizador.elementos]
            for etiqueta in ["html", "head", "body", "header", "main", "footer"]:
                self.assertEqual(etiquetas.count(etiqueta), 1, (ruta, etiqueta))
            self.assertEqual(len(analizador.ids()), len(set(analizador.ids())), ruta)

    def test_08_aviso_reutilizable_con_y_sin_texto(self):
        with app.test_request_context("/"):
            con_texto = render_template("components/aviso.html", aviso="Mensaje de prueba")
            sin_texto = render_template("components/aviso.html", aviso="")
        self.assertIn("Mensaje de prueba", con_texto)
        self.assertNotIn("aviso-demo", sin_texto)
        for ruta in list(RUTAS)[1:]:
            html = self.cliente.get(ruta).get_data(as_text=True)
            self.assertEqual(html.count('class="aviso-demo"'), 1)

    def test_09_enlaces_y_anclas_sin_404(self):
        for ruta in RUTAS:
            html = self.cliente.get(ruta).get_data(as_text=True)
            for etiqueta, atributos in AnalizadorHTML(html).elementos:
                url = atributos.get("href", "")
                if etiqueta != "a" or not url.startswith(("/", "#")):
                    continue
                partes = urlsplit(url)
                destino = partes.path or ruta
                respuesta = self.cliente.get(destino)
                self.assertEqual(respuesta.status_code, 200, (ruta, url))
                if partes.fragment:
                    ids = AnalizadorHTML(respuesta.get_data(as_text=True)).ids()
                    self.assertIn(unquote(partes.fragment), ids, (ruta, url))

    def test_10_recursos_estaticos_y_catalogo_json(self):
        for ruta in RUTAS:
            html = self.cliente.get(ruta).get_data(as_text=True)
            for _, atributos in AnalizadorHTML(html).elementos:
                for clave in ["src", "href"]:
                    recurso = atributos.get(clave, "")
                    if recurso.startswith("/static/"):
                        with self.cliente.get(recurso) as respuesta:
                            self.assertEqual(respuesta.status_code, 200, recurso)
        inicio = self.cliente.get("/").get_data(as_text=True)
        json_catalogo = re.search(r'<script type="application/json" id="datosCatalogo">(.*?)</script>', inicio, re.S)
        self.assertIsNotNone(json_catalogo)
        catalogo = json.loads(json_catalogo.group(1))
        self.assertEqual(len(catalogo), 3)
        for categoria in catalogo:
            with self.cliente.get(categoria["imagen"]) as respuesta:
                self.assertEqual(respuesta.status_code, 200)
        css = (RAIZ / "static/css/style.css").read_text(encoding="utf-8")
        for url in re.findall(r'url\([\'"]?([^\)\'\"]+)[\'"]?\)', css):
            if not url.startswith(("http:", "https:", "data:")):
                self.assertTrue((RAIZ / "static/css" / url).is_file(), url)

    def test_11_filtros_y_totales_del_comprobante(self):
        html, contexto = self.obtener_contexto("/facturacion")
        factura = contexto["factura"]
        self.assertEqual(factura["subtotal"], Decimal("600.00"))
        self.assertEqual(factura["impuesto"], Decimal("90.00"))
        self.assertEqual(factura["total"], Decimal("690.00"))
        self.assertIn("$690.00", html)
        productos = self.cliente.get("/productos").get_data(as_text=True)
        self.assertIn("6 productos", productos)

    def test_12_herencia_y_bloques_en_cinco_paginas(self):
        for nombre in ["index", "productos", "clientes", "proveedores", "facturacion"]:
            texto = (RAIZ / f"templates/{nombre}.html").read_text(encoding="utf-8")
            self.assertIn('{% extends "base.html" %}', texto)
            self.assertIn("{% block title %}", texto)
            self.assertIn("{% block content %}", texto)

    def test_13_portada_estatica_sin_jinja_y_rutas_relativas(self):
        html = (RAIZ / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("{%", html)
        self.assertNotIn("{{", html)
        pagina = AnalizadorHTML(html)
        for etiqueta, atributos in pagina.elementos:
            for clave in ["href", "src"]:
                url = atributos.get(clave, "")
                self.assertFalse(url.startswith("/"), url)
                if url.startswith("static/"):
                    self.assertTrue((RAIZ / unquote(url)).is_file(), url)
                if etiqueta == "a" and url.startswith("#"):
                    self.assertIn(url[1:], pagina.ids(), url)
        for nombre in ["inicio", "quienes", "productos", "registro", "video", "contacto"]:
            self.assertIn(nombre, pagina.ids())
        self.assertNotIn('href="/clientes"', html)

    def test_14_exportacion_reproduce_la_portada_entregada(self):
        with app.test_request_context("/"):
            catalogo = obtener_catalogo()
            for categoria in catalogo:
                categoria["imagen"] = categoria["imagen"].lstrip("/")
            html = render_template("index.html", titulo=NOMBRE_TIENDA, catalogo=catalogo, modo_estatico=True, url_for=url_estatica)
        html = "\n".join(linea.rstrip() for linea in html.splitlines())
        aviso = "<!-- Generado con generar_frontend.py. Editar templates/index.html y regenerar. -->\n"
        self.assertEqual((RAIZ / "index.html").read_text(encoding="utf-8"), aviso + html + "\n")
        with self.assertRaises(ValueError):
            url_estatica("clientes")

    def test_15_escape_html_en_datos(self):
        _, contexto = self.obtener_contexto("/productos")
        producto = deepcopy(contexto["productos"][0])
        producto["nombre"] = "<script>alert('prueba')</script>"
        with app.test_request_context("/productos"):
            html = render_template("productos.html", titulo="Prueba", productos=[producto], aviso="")
        self.assertNotIn("<script>alert", html)
        self.assertIn("&lt;script&gt;", html)

    def test_16_imagenes_cuadradas_y_javascript_conservados(self):
        css = (RAIZ / "static/css/style.css").read_text(encoding="utf-8")
        self.assertIn(".modulo .tarjeta-producto .card-img-top", css)
        self.assertIn("aspect-ratio: 1 / 1", css)
        self.assertIn("object-fit: contain", css)
        html = self.cliente.get("/").get_data(as_text=True)
        for identificador in ["formRegistro", "listaRegistros", "totalRegistros", "modalDetalleProducto", "mensajeContacto"]:
            self.assertIn(identificador, AnalizadorHTML(html).ids())


if __name__ == "__main__":
    unittest.main()
