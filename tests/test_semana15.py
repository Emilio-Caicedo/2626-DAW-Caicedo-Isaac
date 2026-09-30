import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from app import app


RAIZ = Path(__file__).resolve().parents[1]


class Semana15Test(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True, WTF_CSRF_ENABLED=False, LOGIN_DISABLED=True)
        self.cliente = app.test_client()

    def test_01_dependencias_postgresql_y_render(self):
        requisitos = (RAIZ / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("psycopg[binary]", requisitos)
        self.assertIn("gunicorn==", requisitos)
        self.assertNotIn("mysql-connector", requisitos.lower())

    def test_02_conexion_utiliza_database_url_y_dict_row(self):
        codigo = (RAIZ / "conexion/conexion.py").read_text(encoding="utf-8")
        self.assertIn('os.getenv("DATABASE_URL")', codigo)
        self.assertIn("psycopg.connect", codigo)
        self.assertIn("dict_row", codigo)

    def test_03_esquema_contiene_tablas_relaciones_y_claves(self):
        sql = (RAIZ / "sql/esquema_postgresql.sql").read_text(encoding="utf-8").upper()
        for tabla in ["USUARIOS", "PROVEEDORES", "PRODUCTOS", "CLIENTES", "FACTURAS", "DETALLE_FACTURA"]:
            self.assertIn(f"CREATE TABLE IF NOT EXISTS {tabla}", sql)
        self.assertGreaterEqual(sql.count("PRIMARY KEY"), 6)
        self.assertGreaterEqual(sql.count("REFERENCES"), 4)

    def test_04_codigo_evidencia_crud_parametrizado_y_join(self):
        codigo = (RAIZ / "app.py").read_text(encoding="utf-8").upper()
        for operacion in ["INSERT INTO", "SELECT ", "UPDATE ", "DELETE FROM", "INNER JOIN", "LEFT JOIN"]:
            self.assertIn(operacion, codigo)
        self.assertIn("%S", codigo)
        self.assertNotIn("FORMAT(", codigo)

    def test_05_tres_modulos_tienen_rutas_crud(self):
        reglas = {regla.rule: regla.methods for regla in app.url_map.iter_rules()}
        for modulo, parametro in [
            ("productos", "id_producto"), ("clientes", "id_cliente"),
            ("proveedores", "id_proveedor"),
        ]:
            self.assertIn(f"/{modulo}", reglas)
            self.assertIn(f"/{modulo}/nuevo", reglas)
            self.assertIn(f"/{modulo}/<int:{parametro}>/editar", reglas)
            self.assertIn(f"/{modulo}/<int:{parametro}>/eliminar", reglas)
            self.assertIn("POST", reglas[f"/{modulo}/<int:{parametro}>/eliminar"])

    def test_06_rutas_administrativas_estan_protegidas(self):
        codigo = (RAIZ / "app.py").read_text(encoding="utf-8")
        self.assertGreaterEqual(codigo.count("@login_required"), 15)

    def test_07_render_esta_configurado(self):
        render = (RAIZ / "render.yaml").read_text(encoding="utf-8")
        self.assertIn("type: web", render)
        self.assertIn("fromDatabase:", render)
        self.assertIn("preDeployCommand: python inicializar_postgresql.py", render)
        self.assertIn("startCommand: gunicorn app:app", render)
        self.assertIn("/salud", render)
        respuesta = self.cliente.get("/salud")
        self.assertEqual(respuesta.status_code, 200)

    def test_08_listado_productos_muestra_join_y_acciones(self):
        registro = {
            "id": 1, "codigo": "PRO-001", "nombre": "Laptop",
            "categoria": "Laptops y computadoras", "descripcion": "Equipo de prueba",
            "precio": Decimal("550.00"), "stock": 8, "imagen": "laptop-estudio.jpg",
            "id_proveedor": 1, "proveedor_nombre": "LUSANCOMP",
        }
        with patch("app.obtener_productos", return_value=[registro]):
            html = self.cliente.get("/productos").get_data(as_text=True)
        self.assertIn("LUSANCOMP", html)
        self.assertIn("Editar", html)
        self.assertIn("Eliminar", html)

    def test_09_listado_clientes_muestra_relacion_y_acciones(self):
        registro = {
            "id": 1, "codigo": "CLI-001", "nombre": "CLIENTE PRUEBA",
            "tipo": "Estudiante", "correo": "cliente@example.com", "ciudad": "Puyo",
            "total_facturas": 2,
        }
        with patch("app.obtener_clientes", return_value=[registro]):
            html = self.cliente.get("/clientes").get_data(as_text=True)
        self.assertIn("CLIENTE PRUEBA", html)
        self.assertIn(">2<", html)
        self.assertIn("/clientes/1/editar", html)

    def test_10_listado_proveedores_muestra_productos_relacionados(self):
        registro = {
            "id": 1, "codigo": "PRV-001", "nombre": "PROVEEDOR PRUEBA",
            "categoria": "Equipos y componentes", "correo": "ventas@example.com",
            "ciudad": "Quito", "entrega_dias": 3, "total_productos": 4,
        }
        with patch("app.obtener_proveedores", return_value=[registro]):
            html = self.cliente.get("/proveedores").get_data(as_text=True)
        self.assertIn("PROVEEDOR PRUEBA", html)
        self.assertIn("Productos relacionados", html)
        self.assertIn("/proveedores/1/editar", html)

    def test_11_crear_cliente_invoca_insert(self):
        datos = {
            "codigo": "CLI-099", "nombre": "Cliente de Prueba",
            "tipo": "Profesional", "correo": "cliente99@example.com", "ciudad": "Puyo",
        }
        with patch("app.insertar_cliente", return_value=99) as insertar:
            respuesta = self.cliente.post("/clientes/nuevo", data=datos)
        self.assertEqual(respuesta.status_code, 302)
        insertar.assert_called_once()

    def test_12_editar_y_eliminar_cliente_invocan_update_delete(self):
        actual = {
            "id": 99, "codigo": "CLI-099", "nombre": "CLIENTE DE PRUEBA",
            "tipo": "Profesional", "correo": "cliente99@example.com", "ciudad": "Puyo",
        }
        datos = dict(actual)
        datos.pop("id")
        datos["nombre"] = "Cliente Actualizado"
        with patch("app.buscar_cliente_por_id", return_value=actual), \
             patch("app.actualizar_cliente", return_value=1) as actualizar:
            respuesta = self.cliente.post("/clientes/99/editar", data=datos)
        self.assertEqual(respuesta.status_code, 302)
        actualizar.assert_called_once()
        with patch("app.buscar_cliente_por_id", return_value=actual), \
             patch("app.eliminar_cliente_bd", return_value=1) as eliminar:
            respuesta = self.cliente.post("/clientes/99/eliminar")
        self.assertEqual(respuesta.status_code, 302)
        eliminar.assert_called_once_with(99)

    def test_13_plantillas_formulario_son_reutilizables(self):
        for archivo in ["formulario_producto.html", "formulario_cliente.html", "formulario_proveedor.html"]:
            html = (RAIZ / "templates" / archivo).read_text(encoding="utf-8")
            self.assertIn("{{ accion }}", html)
            self.assertIn("modo_edicion", html)

    def test_14_no_hay_secretos_publicados(self):
        ejemplo = (RAIZ / ".env.example").read_text(encoding="utf-8")
        gitignore = (RAIZ / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".env", gitignore)
        self.assertIn("SU_CONTRASENA", ejemplo)
        self.assertNotIn("MYSQL_PASSWORD", ejemplo)


if __name__ == "__main__":
    unittest.main()
