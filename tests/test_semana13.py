
import re
import unittest
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from mysql.connector import IntegrityError

from app import (
    PRODUCTOS_INICIALES,
    actualizar_producto,
    app,
    buscar_producto_por_codigo,
    buscar_producto_por_id,
    eliminar_producto_bd,
    insertar_producto,
    obtener_productos,
)


RAIZ = Path(__file__).resolve().parents[1]

PROVEEDORES_PRUEBA = [
    {"id_proveedor": 1, "codigo": "PRV-001", "nombre": "LUSANCOMP"},
    {"id_proveedor": 2, "codigo": "PRV-002", "nombre": "MAXXICOMP"},
    {"id_proveedor": 3, "codigo": "PRV-003", "nombre": "PC MAX TECNOLOGIA"},
]


class BaseFalsa:
    def __init__(self):
        self.proveedores = deepcopy(PROVEEDORES_PRUEBA)
        self.productos = []
        for indice, producto in enumerate(PRODUCTOS_INICIALES, start=1):
            fila = deepcopy(producto)
            fila["id"] = indice
            fila["precio"] = Decimal(fila["precio"])
            self.productos.append(fila)
        self.siguiente_id = len(self.productos) + 1


class CursorFalso:
    def __init__(self, base, dictionary=False):
        self.base = base
        self.dictionary = dictionary
        self.resultados = []
        self.rowcount = 0
        self.lastrowid = None

    def execute(self, consulta, parametros=None):
        sql = " ".join(consulta.split()).upper()
        parametros = parametros or ()

        if sql.startswith("SELECT") and "FROM PROVEEDORES" in sql:
            self.resultados = sorted(deepcopy(self.base.proveedores), key=lambda p: p["nombre"])
            return

        if sql.startswith("SELECT") and "FROM PRODUCTOS AS P" in sql:
            filas = deepcopy(self.base.productos)
            if "WHERE P.ID_PRODUCTO = %S" in sql:
                filas = [p for p in filas if p["id"] == parametros[0]]
            for fila in filas:
                proveedor = next(p for p in self.base.proveedores if p["id_proveedor"] == fila["id_proveedor"])
                fila["proveedor_nombre"] = proveedor["nombre"]
            self.resultados = filas
            return

        if sql.startswith("SELECT") and "FROM PRODUCTOS" in sql and "WHERE CODIGO = %S" in sql:
            self.resultados = [deepcopy(p) for p in self.base.productos if p["codigo"] == parametros[0]]
            return

        if sql.startswith("INSERT INTO PRODUCTOS"):
            codigo = parametros[0]
            if any(p["codigo"] == codigo for p in self.base.productos):
                raise IntegrityError("Código duplicado")
            fila = {
                "id": self.base.siguiente_id,
                "codigo": parametros[0], "nombre": parametros[1],
                "categoria": parametros[2], "descripcion": parametros[3],
                "precio": Decimal(parametros[4]), "stock": parametros[5],
                "imagen": parametros[6], "id_proveedor": parametros[7],
            }
            self.base.productos.append(fila)
            self.lastrowid = self.base.siguiente_id
            self.base.siguiente_id += 1
            self.rowcount = 1
            return

        if sql.startswith("UPDATE PRODUCTOS"):
            id_producto = parametros[-1]
            codigo = parametros[0]
            if any(p["codigo"] == codigo and p["id"] != id_producto for p in self.base.productos):
                raise IntegrityError("Código duplicado")
            self.rowcount = 0
            for fila in self.base.productos:
                if fila["id"] == id_producto:
                    fila.update({
                        "codigo": parametros[0], "nombre": parametros[1],
                        "categoria": parametros[2], "descripcion": parametros[3],
                        "precio": Decimal(parametros[4]), "stock": parametros[5],
                        "imagen": parametros[6], "id_proveedor": parametros[7],
                    })
                    self.rowcount = 1
            return

        if sql.startswith("DELETE FROM PRODUCTOS"):
            cantidad = len(self.base.productos)
            self.base.productos[:] = [p for p in self.base.productos if p["id"] != parametros[0]]
            self.rowcount = cantidad - len(self.base.productos)
            return

        raise AssertionError(f"Consulta no simulada: {sql}")

    def fetchall(self):
        return deepcopy(self.resultados)

    def fetchone(self):
        return deepcopy(self.resultados[0]) if self.resultados else None

    def close(self):
        return None


class ConexionFalsa:
    def __init__(self, base):
        self.base = base
        self.conectada = True
        self.commits = 0
        self.rollbacks = 0

    def cursor(self, dictionary=False):
        return CursorFalso(self.base, dictionary=dictionary)

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def is_connected(self):
        return self.conectada

    def close(self):
        self.conectada = False


class Semana13Test(unittest.TestCase):
    def setUp(self):
        self.base = BaseFalsa()
        self.parche = patch("app.conectar_bd", side_effect=lambda: ConexionFalsa(self.base))
        self.parche.start()
        self.login_disabled_anterior = app.config.get("LOGIN_DISABLED", False)
        app.config.update(TESTING=True, WTF_CSRF_ENABLED=False, LOGIN_DISABLED=True)
        self.cliente = app.test_client()

    def tearDown(self):
        self.parche.stop()
        app.config["LOGIN_DISABLED"] = self.login_disabled_anterior

    def producto_nuevo(self):
        return {
            "codigo": "PRO-007", "nombre": "Monitor de 24 pulgadas",
            "categoria": "Accesorios tecnológicos",
            "descripcion": "Pantalla Full HD para estudio y oficina.",
            "precio": Decimal("189.90"), "stock": 6,
            "imagen": "accesorios-tecnologicos.jpg", "id_proveedor": 2,
        }

    def test_01_select_join_y_fetchall(self):
        productos = obtener_productos()
        self.assertEqual(len(productos), 6)
        self.assertEqual(productos[0]["proveedor_nombre"], "LUSANCOMP")
        self.assertEqual(productos[-1]["proveedor_nombre"], "PC MAX TECNOLOGIA")

    def test_02_insert_parametrizado_persiste_entre_conexiones(self):
        nuevo_id = insertar_producto(self.producto_nuevo())
        self.assertEqual(nuevo_id, 7)
        producto = buscar_producto_por_codigo("pro-007")
        self.assertEqual(producto["nombre"], "Monitor de 24 pulgadas")

    def test_03_update_con_where_modifica_un_registro(self):
        insertar_producto(self.producto_nuevo())
        editado = self.producto_nuevo()
        editado.update({"nombre": "Monitor profesional", "precio": Decimal("199.99"), "stock": 4})
        self.assertEqual(actualizar_producto(7, editado), 1)
        producto = buscar_producto_por_id(7)
        self.assertEqual(producto["nombre"], "Monitor profesional")
        self.assertEqual(producto["precio"], Decimal("199.99"))

    def test_04_delete_con_where_elimina_un_registro(self):
        insertar_producto(self.producto_nuevo())
        self.assertEqual(eliminar_producto_bd(7), 1)
        self.assertIsNone(buscar_producto_por_id(7))
        self.assertEqual(len(obtener_productos()), 6)

    def test_05_listado_jinja_muestra_mysql_join_y_acciones(self):
        respuesta = self.cliente.get("/productos")
        html = respuesta.get_data(as_text=True)
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("base de datos relacional MySQL", html)
        self.assertIn("LUSANCOMP", html)
        self.assertIn("Editar", html)
        self.assertIn("Eliminar", html)
        self.assertIn("INNER JOIN", html)

    def test_06_formulario_insert_valido(self):
        respuesta = self.cliente.post("/productos/nuevo", data={
            "codigo": "PRO-007", "nombre": "Monitor de 24 pulgadas",
            "categoria": "Accesorios tecnológicos", "proveedor_id": "2",
            "descripcion": "Pantalla Full HD para estudio y oficina.",
            "precio": "189.90", "stock": "6",
        }, follow_redirects=True)
        html = respuesta.get_data(as_text=True)
        self.assertIn("Producto registrado correctamente en MySQL.", html)
        self.assertIn("Monitor de 24 pulgadas", html)
        self.assertEqual(len(self.base.productos), 7)

    def test_07_edicion_carga_y_actualiza_datos(self):
        insertar_producto(self.producto_nuevo())
        formulario = self.cliente.get("/productos/7/editar").get_data(as_text=True)
        self.assertIn('value="PRO-007"', formulario)
        self.assertIn("Monitor de 24 pulgadas", formulario)
        respuesta = self.cliente.post("/productos/7/editar", data={
            "codigo": "PRO-007", "nombre": "Monitor editado",
            "categoria": "Accesorios tecnológicos", "proveedor_id": "3",
            "descripcion": "Pantalla editada para oficina y estudio.",
            "precio": "210.00", "stock": "2",
        }, follow_redirects=True)
        self.assertIn("Producto actualizado correctamente en MySQL.", respuesta.get_data(as_text=True))
        self.assertEqual(buscar_producto_por_id(7)["nombre"], "Monitor editado")

    def test_08_eliminacion_post_y_confirmacion_visual(self):
        insertar_producto(self.producto_nuevo())
        html = self.cliente.get("/productos").get_data(as_text=True)
        self.assertIn("¿Está seguro de eliminar", html)
        respuesta = self.cliente.post("/productos/7/eliminar", follow_redirects=True)
        self.assertIn("PRO-007 eliminado correctamente", respuesta.get_data(as_text=True))
        self.assertIsNone(buscar_producto_por_id(7))

    def test_09_validacion_impide_insert_invalido(self):
        respuesta = self.cliente.post("/productos/nuevo", data={
            "codigo": "MAL", "nombre": "X", "categoria": "",
            "proveedor_id": "0", "descripcion": "Corta", "precio": "-1", "stock": "-2",
        })
        html = respuesta.get_data(as_text=True)
        self.assertIn("Use el formato PRO-000.", html)
        self.assertIn("Seleccione un proveedor.", html)
        self.assertEqual(len(self.base.productos), 6)

    def test_10_codigo_duplicado_no_se_inserta(self):
        respuesta = self.cliente.post("/productos/nuevo", data={
            "codigo": "PRO-001", "nombre": "Producto repetido",
            "categoria": "Componentes informáticos", "proveedor_id": "1",
            "descripcion": "Producto con un código ya registrado.",
            "precio": "20.00", "stock": "1",
        })
        self.assertIn("Ya existe un producto con este código.", respuesta.get_data(as_text=True))
        self.assertEqual(len(self.base.productos), 6)

    def test_11_rutas_anteriores_continuan_funcionando(self):
        for ruta in ["/", "/productos", "/productos/nuevo", "/clientes", "/clientes/nuevo", "/proveedores", "/proveedores/nuevo", "/facturacion", "/facturacion/nueva"]:
            with self.subTest(ruta=ruta):
                self.assertEqual(self.cliente.get(ruta).status_code, 200)

    def test_12_esquema_relacional_completo(self):
        sql = (RAIZ / "sql/esquema.sql").read_text(encoding="utf-8").upper()
        for tabla in ["PROVEEDORES", "PRODUCTOS", "CLIENTES", "FACTURAS", "DETALLE_FACTURA"]:
            self.assertIn(f"CREATE TABLE IF NOT EXISTS {tabla}", sql)
        self.assertGreaterEqual(sql.count("PRIMARY KEY"), 5)
        self.assertGreaterEqual(sql.count("FOREIGN KEY"), 4)
        self.assertIn("INNER JOIN", sql)

    def test_13_consultas_parametrizadas_where_commit_y_close(self):
        codigo = (RAIZ / "app.py").read_text(encoding="utf-8")
        for fragmento in ["VALUES (%s, %s", "WHERE p.id_producto = %s", "WHERE id_producto = %s", "conexion.commit()", "cursor.close()", "conexion.close()", "cursor.fetchall()"]:
            self.assertIn(fragmento, codigo)
        self.assertNotRegex(codigo, r'DELETE FROM productos(?! WHERE)')

    def test_14_conexion_centralizada_y_configuracion_segura(self):
        conexion = (RAIZ / "conexion/conexion.py").read_text(encoding="utf-8")
        self.assertIn("mysql.connector.connect", conexion)
        self.assertIn('os.getenv("MYSQL_PASSWORD"', conexion)
        self.assertTrue((RAIZ / ".env.example").is_file())
        gitignore = (RAIZ / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".env", gitignore)
        self.assertIn("!.env.example", gitignore)

    def test_15_dependencias_y_estructura_solicitada(self):
        for ruta in ["conexion/__init__.py", "conexion/conexion.py", "sql/esquema.sql", "templates/productos.html", "templates/formulario_producto.html"]:
            self.assertTrue((RAIZ / ruta).is_file(), ruta)
        requirements = (RAIZ / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("mysql-connector-python==", requirements)
        self.assertIn("python-dotenv==", requirements)


if __name__ == "__main__":
    unittest.main()
