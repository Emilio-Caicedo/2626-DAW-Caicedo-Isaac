"""Comprobaciones finales exigidas en la evaluación de la Semana 16."""

import unittest
from pathlib import Path

from app import app


RAIZ = Path(__file__).resolve().parents[1]


class ProyectoFinalSemana16Test(unittest.TestCase):
    def test_login_registro_y_logout_existen(self):
        reglas = {regla.rule: regla.methods for regla in app.url_map.iter_rules()}
        self.assertIn("/registro", reglas)
        self.assertIn("/login", reglas)
        self.assertIn("/logout", reglas)
        self.assertIn("POST", reglas["/logout"])

    def test_tres_modulos_tienen_crud_completo(self):
        reglas = {regla.rule: regla.methods for regla in app.url_map.iter_rules()}
        for modulo, identificador in (
            ("productos", "id_producto"),
            ("clientes", "id_cliente"),
            ("proveedores", "id_proveedor"),
        ):
            with self.subTest(modulo=modulo):
                self.assertIn(f"/{modulo}", reglas)
                self.assertIn(f"/{modulo}/nuevo", reglas)
                self.assertIn(f"/{modulo}/<int:{identificador}>/editar", reglas)
                ruta_eliminar = f"/{modulo}/<int:{identificador}>/eliminar"
                self.assertIn(ruta_eliminar, reglas)
                self.assertIn("POST", reglas[ruta_eliminar])

    def test_esquema_tiene_relaciones_requeridas(self):
        sql = (RAIZ / "sql/esquema_postgresql.sql").read_text(encoding="utf-8").upper()
        for tabla in ("PROVEEDORES", "PRODUCTOS", "CLIENTES", "FACTURAS"):
            self.assertIn(f"CREATE TABLE IF NOT EXISTS {tabla}", sql)
        self.assertGreaterEqual(sql.count("REFERENCES"), 4)
        self.assertGreaterEqual(sql.count("PRIMARY KEY"), 3)

    def test_documentacion_final_y_seguridad(self):
        self.assertTrue((RAIZ / "GUIA_DEFENSA_SEMANA_16.md").is_file())
        gitignore = (RAIZ / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".env", gitignore)


if __name__ == "__main__":
    unittest.main()
