"""Diagnóstico seguro de PostgreSQL para EmiTech Store.

No imprime la contraseña ni guarda datos de prueba. Comprueba la conexión,
las tablas, las columnas del login y un INSERT equivalente al registro.
"""

import os
import sys
from urllib.parse import urlsplit
from uuid import uuid4

from dotenv import load_dotenv
from psycopg import Error

from conexion import conectar_bd


TABLAS_REQUERIDAS = {
    "usuarios",
    "proveedores",
    "productos",
    "clientes",
    "facturas",
    "detalle_factura",
}
COLUMNAS_USUARIOS = {
    "id_usuario",
    "usuario",
    "nombre_completo",
    "password_hash",
    "activo",
    "creado_en",
}


def _destino_sin_credenciales():
    url = os.getenv("DATABASE_URL", "").strip()
    partes = urlsplit(url)
    return partes.hostname or "no definido", partes.path.lstrip("/") or "no definida"


def main():
    load_dotenv()
    host, base = _destino_sin_credenciales()
    print(f"Servidor: {host}")
    print(f"Base de datos: {base}")

    conexion = None
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        cursor.execute("SELECT current_database() AS base, current_user AS usuario")
        destino = cursor.fetchone()
        print(f"[OK] Conexión a {destino['base']}")

        cursor.execute(
            """SELECT table_name
               FROM information_schema.tables
               WHERE table_schema = 'public'"""
        )
        tablas = {fila["table_name"] for fila in cursor.fetchall()}
        faltantes = sorted(TABLAS_REQUERIDAS - tablas)
        if faltantes:
            raise RuntimeError("Faltan tablas: " + ", ".join(faltantes))
        print("[OK] Se encontraron las seis tablas requeridas")

        cursor.execute(
            """SELECT column_name
               FROM information_schema.columns
               WHERE table_schema = 'public' AND table_name = 'usuarios'"""
        )
        columnas = {fila["column_name"] for fila in cursor.fetchall()}
        faltantes = sorted(COLUMNAS_USUARIOS - columnas)
        if faltantes:
            raise RuntimeError("Faltan columnas en usuarios: " + ", ".join(faltantes))
        print("[OK] La tabla usuarios tiene la estructura correcta")

        usuario_prueba = "diagnostico_" + uuid4().hex[:12]
        cursor.execute(
            """INSERT INTO usuarios (usuario, nombre_completo, password_hash)
               VALUES (%s, %s, %s) RETURNING id_usuario""",
            (usuario_prueba, "Diagnóstico temporal", "hash-temporal-no-utilizable"),
        )
        cursor.fetchone()
        conexion.rollback()
        print("[OK] PostgreSQL permite registrar usuarios (prueba revertida)")
        print("DIAGNÓSTICO COMPLETADO: la base está lista para EmiTech Store.")
        return 0
    except (Error, RuntimeError) as error:
        if conexion is not None:
            conexion.rollback()
        codigo = getattr(error, "sqlstate", None) or "sin código SQL"
        print(f"[ERROR] {type(error).__name__} ({codigo})")
        print(str(error))
        print("Ejecute nuevamente python inicializar_postgresql.py y repita el diagnóstico.")
        return 1
    finally:
        if conexion is not None:
            conexion.close()


if __name__ == "__main__":
    sys.exit(main())
