import unittest
from pathlib import Path
from unittest.mock import patch

from psycopg import IntegrityError
from werkzeug.security import check_password_hash

from app import app
from models import Usuario


RAIZ = Path(__file__).resolve().parents[1]


class Semana14Test(unittest.TestCase):
    def setUp(self):
        self.usuarios = {}
        self.siguiente_id = 1
        self.config_anterior = {
            "TESTING": app.config.get("TESTING"),
            "WTF_CSRF_ENABLED": app.config.get("WTF_CSRF_ENABLED", True),
            "LOGIN_DISABLED": app.config.get("LOGIN_DISABLED", False),
            "SECRET_KEY": app.config.get("SECRET_KEY"),
        }
        app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            LOGIN_DISABLED=False,
            SECRET_KEY="clave-pruebas-semana-14",
        )

        def insertar(usuario, nombre_completo, password_hash):
            if usuario in self.usuarios:
                raise IntegrityError("Usuario duplicado")
            fila = {
                "id_usuario": self.siguiente_id,
                "usuario": usuario,
                "nombre_completo": nombre_completo,
                "password_hash": password_hash,
                "activo": True,
            }
            self.usuarios[usuario] = fila
            self.siguiente_id += 1
            return fila["id_usuario"]

        def por_nombre(usuario):
            return self.usuarios.get(usuario.strip().lower())

        def por_id(id_usuario):
            return next(
                (
                    fila
                    for fila in self.usuarios.values()
                    if fila["id_usuario"] == int(id_usuario) and fila["activo"]
                ),
                None,
            )

        self.parches = [
            patch("app.insertar_usuario", side_effect=insertar),
            patch("app.buscar_usuario_por_nombre", side_effect=por_nombre),
            patch("app.buscar_usuario_por_id", side_effect=por_id),
            patch("app.obtener_productos", return_value=[]),
        ]
        for parche in self.parches:
            parche.start()
        self.cliente = app.test_client()

    def tearDown(self):
        for parche in reversed(self.parches):
            parche.stop()
        app.config.update(self.config_anterior)

    def registrar(self, usuario="isaac_emitech", password="Emitech2026"):
        return self.cliente.post(
            "/registro",
            data={
                "nombre_completo": "Isaac Emilio Caicedo Uriña",
                "usuario": usuario,
                "password": password,
                "confirmar_password": password,
            },
            follow_redirects=True,
        )

    def iniciar_sesion(self, usuario="isaac_emitech", password="Emitech2026", **kwargs):
        return self.cliente.post(
            "/login",
            data={"usuario": usuario, "password": password},
            **kwargs,
        )

    def test_01_registro_guarda_hash_no_texto_plano(self):
        respuesta = self.registrar()
        self.assertIn("Cuenta creada correctamente", respuesta.get_data(as_text=True))
        fila = self.usuarios["isaac_emitech"]
        self.assertNotEqual(fila["password_hash"], "Emitech2026")
        self.assertTrue(check_password_hash(fila["password_hash"], "Emitech2026"))

    def test_02_usuario_duplicado_es_rechazado(self):
        self.registrar()
        respuesta = self.registrar()
        self.assertIn("ya está registrado", respuesta.get_data(as_text=True))
        self.assertEqual(len(self.usuarios), 1)

    def test_03_formulario_valida_password_seguro_y_confirmacion(self):
        respuesta = self.cliente.post(
            "/registro",
            data={
                "nombre_completo": "Isaac Emilio Caicedo Uriña",
                "usuario": "isaac emitech",
                "password": "corta",
                "confirmar_password": "diferente",
            },
        )
        html = respuesta.get_data(as_text=True)
        self.assertIn("únicamente letras, números y guion bajo", html)
        self.assertIn("entre 8 y 128 caracteres", html)
        self.assertIn("no coinciden", html)
        self.assertFalse(self.usuarios)

    def test_04_login_incorrecto_no_crea_sesion(self):
        self.registrar()
        respuesta = self.iniciar_sesion(password="Incorrecta2026", follow_redirects=True)
        self.assertIn("Usuario o contraseña incorrectos", respuesta.get_data(as_text=True))
        privada = self.cliente.get("/dashboard")
        self.assertEqual(privada.status_code, 302)

    def test_05_login_correcto_muestra_usuario_actual(self):
        self.registrar()
        respuesta = self.iniciar_sesion(follow_redirects=True)
        html = respuesta.get_data(as_text=True)
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("Hola, Isaac Emilio Caicedo Uriña", html)
        self.assertIn("isaac_emitech", html)
        self.assertIn("Cerrar sesión", html)

    def test_06_rutas_internas_requieren_login(self):
        for ruta in ["/dashboard", "/productos", "/clientes", "/proveedores", "/facturacion"]:
            with self.subTest(ruta=ruta):
                respuesta = self.cliente.get(ruta)
                self.assertEqual(respuesta.status_code, 302)
                self.assertIn("/login?next=", respuesta.headers["Location"])

    def test_07_usuario_autenticado_accede_a_productos(self):
        self.registrar()
        self.iniciar_sesion()
        respuesta = self.cliente.get("/productos")
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("Productos", respuesta.get_data(as_text=True))

    def test_08_next_regresa_a_la_ruta_solicitada(self):
        self.registrar()
        respuesta = self.cliente.post(
            "/login?next=/productos",
            data={"usuario": "isaac_emitech", "password": "Emitech2026"},
            follow_redirects=True,
        )
        self.assertEqual(respuesta.request.path, "/productos")

    def test_09_logout_destruye_sesion_y_vuelve_a_proteger(self):
        self.registrar()
        self.iniciar_sesion()
        respuesta = self.cliente.post("/logout", follow_redirects=True)
        self.assertIn("La sesión se cerró correctamente", respuesta.get_data(as_text=True))
        privada = self.cliente.get("/productos")
        self.assertEqual(privada.status_code, 302)
        self.assertIn("/login?next=", privada.headers["Location"])

    def test_10_modelo_usuario_es_compatible_con_flask_login(self):
        usuario = Usuario(7, "admin", "Administrador EmiTech")
        self.assertEqual(usuario.get_id(), "7")
        self.assertTrue(usuario.is_authenticated)

    def test_11_esquema_y_migracion_incluyen_usuarios(self):
        for archivo in ["sql/esquema.sql", "sql/migracion_semana14.sql"]:
            sql = (RAIZ / archivo).read_text(encoding="utf-8").upper()
            self.assertIn("CREATE TABLE IF NOT EXISTS USUARIOS", sql)
            self.assertIn("USUARIO VARCHAR(50) NOT NULL UNIQUE", sql)
            self.assertIn("PASSWORD_HASH VARCHAR(255) NOT NULL", sql)

    def test_12_codigo_evidencia_hash_flask_login_y_consultas_seguras(self):
        codigo = (RAIZ / "app.py").read_text(encoding="utf-8")
        for fragmento in [
            "generate_password_hash(",
            "check_password_hash(",
            "LoginManager(app)",
            "@login_manager.user_loader",
            "login_user(",
            "logout_user()",
            "current_user",
            "@login_required",
            "WHERE usuario = %s",
            "WHERE id_usuario = %s",
        ]:
            self.assertIn(fragmento, codigo)

    def test_13_estructura_formularios_y_plantillas(self):
        for ruta in [
            "models.py",
            "forms/login_form.py",
            "forms/usuario_form.py",
            "templates/login.html",
            "templates/registro.html",
            "templates/dashboard.html",
        ]:
            self.assertTrue((RAIZ / ruta).is_file(), ruta)
        for plantilla in ["login.html", "registro.html", "dashboard.html"]:
            html = (RAIZ / "templates" / plantilla).read_text(encoding="utf-8")
            self.assertIn('{% extends "base.html" %}', html)

    def test_14_dependencias_actualizadas(self):
        requisitos = (RAIZ / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("Flask-Login==", requisitos)
        self.assertIn("Werkzeug==", requisitos)

    def test_15_no_se_publican_credenciales(self):
        gitignore = (RAIZ / ".gitignore").read_text(encoding="utf-8")
        ejemplo = (RAIZ / ".env.example").read_text(encoding="utf-8")
        self.assertIn(".env", gitignore)
        self.assertIn("DATABASE_URL=postgresql://", ejemplo)
        self.assertIn("SU_CONTRASENA", ejemplo)
        self.assertNotIn("Emitech2026", ejemplo)


if __name__ == "__main__":
    unittest.main()
