import sqlite3
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from app import (
    PRODUCTOS_INICIALES,
    app,
    buscar_producto_por_codigo,
    inicializar_base_datos,
    insertar_producto,
    obtener_productos,
)

RAIZ = Path(__file__).resolve().parents[1]


class Semana12Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.database_original = app.config["DATABASE"]
        cls.testing_original = app.config["TESTING"]
        cls.csrf_original = app.config.get("WTF_CSRF_ENABLED", True)
        cls.directorio_temporal = TemporaryDirectory()
        app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
        app.config["DATABASE"] = (
            Path(cls.directorio_temporal.name) / "data" / "emitech_store.db"
        )

    @classmethod
    def tearDownClass(cls):
        app.config.update(
            TESTING=cls.testing_original, WTF_CSRF_ENABLED=cls.csrf_original
        )
        app.config["DATABASE"] = cls.database_original
        cls.directorio_temporal.cleanup()

    def setUp(self):
        ruta_bd = Path(app.config["DATABASE"])
        if ruta_bd.exists():
            ruta_bd.unlink()
        inicializar_base_datos()
        self.cliente = app.test_client()

    def test_01_nombre_archivo_tabla_y_clave_primaria(self):
        ruta_bd = Path(app.config["DATABASE"])
        self.assertEqual(ruta_bd.name, "emitech_store.db")
        self.assertTrue(ruta_bd.is_file())

        conn = sqlite3.connect(ruta_bd)
        try:
            tabla = conn.execute(
                "SELECT name FROM sqlite_schema WHERE type = ? AND name = ?",
                ("table", "productos"),
            ).fetchone()
            columnas = conn.execute("PRAGMA table_info(productos)").fetchall()
        finally:
            conn.close()

        self.assertEqual(tabla[0], "productos")
        por_nombre = {columna[1]: columna for columna in columnas}
        self.assertEqual(por_nombre["id"][5], 1)
        for nombre in [
            "codigo",
            "nombre",
            "categoria",
            "descripcion",
            "precio",
            "stock",
            "imagen",
        ]:
            self.assertIn(nombre, por_nombre)

    def test_02_create_if_not_exists_y_catalogo_inicial(self):
        inicializar_base_datos()
        inicializar_base_datos()
        productos = obtener_productos()
        self.assertEqual(len(productos), len(PRODUCTOS_INICIALES))
        self.assertTrue(all(isinstance(producto, dict) for producto in productos))
        self.assertEqual(productos[0]["codigo"], "PRO-001")

    def test_03_insert_parametrizado_y_select(self):
        insertar_producto(
            {
                "codigo": "PRO-007",
                "nombre": "Monitor Isaac's de 24 pulgadas",
                "categoria": "Accesorios tecnológicos",
                "descripcion": "Pantalla Full HD para estudio y oficina.",
                "precio": 189.90,
                "stock": 6,
                "imagen": "accesorios-tecnologicos.jpg",
            }
        )
        producto = buscar_producto_por_codigo("PRO-007")
        self.assertIsNotNone(producto)
        self.assertEqual(producto["nombre"], "Monitor Isaac's de 24 pulgadas")
        self.assertAlmostEqual(producto["precio"], 189.90)

        # Una conexión nueva recupera el mismo registro persistente.
        conn = sqlite3.connect(app.config["DATABASE"])
        try:
            fila = conn.execute(
                "SELECT codigo, nombre FROM productos WHERE codigo = ?",
                ("PRO-007",),
            ).fetchone()
        finally:
            conn.close()
        self.assertEqual(fila, ("PRO-007", "Monitor Isaac's de 24 pulgadas"))

    def test_04_formulario_valido_realiza_insert(self):
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
        self.assertIn("Producto guardado correctamente en emitech_store.db.", html)
        self.assertIn("Monitor de 24 pulgadas", html)
        self.assertEqual(len(obtener_productos()), len(PRODUCTOS_INICIALES) + 1)

    def test_05_formulario_invalido_no_realiza_insert(self):
        cantidad = len(obtener_productos())
        respuesta = self.cliente.post(
            "/productos/nuevo",
            data={
                "codigo": "CODIGO-MAL",
                "nombre": "X",
                "categoria": "Accesorios tecnológicos",
                "descripcion": "Corta",
                "precio": "-20",
                "stock": "-1",
            },
        )
        html = respuesta.get_data(as_text=True)
        self.assertIn("Use el formato PRO-000.", html)
        self.assertIn("Ingrese un precio mayor que 0.", html)
        self.assertEqual(len(obtener_productos()), cantidad)

    def test_06_codigo_duplicado_no_se_almacena(self):
        cantidad = len(obtener_productos())
        respuesta = self.cliente.post(
            "/productos/nuevo",
            data={
                "codigo": "PRO-001",
                "nombre": "Producto repetido",
                "categoria": "Componentes informáticos",
                "descripcion": "Registro con un código ya almacenado.",
                "precio": "25.00",
                "stock": "2",
            },
        )
        self.assertIn(
            "Ya existe un producto con este código.",
            respuesta.get_data(as_text=True),
        )
        self.assertEqual(len(obtener_productos()), cantidad)

    def test_07_select_se_muestra_en_tabla_jinja2(self):
        respuesta = self.cliente.get("/productos")
        html = respuesta.get_data(as_text=True)
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("Productos almacenados", html)
        self.assertIn("data/emitech_store.db", html)
        self.assertEqual(html.count("data-product-id="), len(PRODUCTOS_INICIALES))
        self.assertIn("PRO-001", html)
        self.assertIn("$550.00", html)

        plantilla = (RAIZ / "templates/productos.html").read_text(encoding="utf-8")
        self.assertIn("{% for producto in productos %}", plantilla)
        self.assertIn("<table", plantilla)

    def test_08_facturacion_consulta_productos_de_sqlite(self):
        insertar_producto(
            {
                "codigo": "PRO-007",
                "nombre": "Monitor persistente",
                "categoria": "Accesorios tecnológicos",
                "descripcion": "Producto disponible para el comprobante.",
                "precio": 100.00,
                "stock": 4,
                "imagen": "accesorios-tecnologicos.jpg",
            }
        )
        html = self.cliente.get("/facturacion/nueva").get_data(as_text=True)
        self.assertIn("PRO-007 · Monitor persistente", html)

    def test_09_rutas_anteriores_continuan_funcionando(self):
        for ruta in [
            "/",
            "/productos",
            "/productos/nuevo",
            "/clientes",
            "/clientes/nuevo",
            "/proveedores",
            "/proveedores/nuevo",
            "/facturacion",
            "/facturacion/nueva",
        ]:
            with self.subTest(ruta=ruta):
                self.assertEqual(self.cliente.get(ruta).status_code, 200)

    def test_10_evidencia_sqlite_en_codigo(self):
        codigo = (RAIZ / "app.py").read_text(encoding="utf-8")
        for evidencia in [
            "import sqlite3",
            "sqlite3.connect",
            "CREATE TABLE IF NOT EXISTS productos",
            "INSERT INTO productos",
            "SELECT id, codigo, nombre",
            "cursor.fetchall()",
            "conn.commit()",
            "conn.close()",
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            '"emitech_store.db"',
            "form.validate_on_submit()",
        ]:
            self.assertIn(evidencia, codigo)


if __name__ == "__main__":
    unittest.main()
