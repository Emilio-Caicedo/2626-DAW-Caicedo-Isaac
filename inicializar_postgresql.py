"""Crea tablas y datos iniciales en el PostgreSQL configurado."""

from pathlib import Path

from conexion import conectar_bd


def inicializar():
    script = (Path(__file__).parent / "sql" / "esquema_postgresql.sql").read_text(
        encoding="utf-8"
    )
    with conectar_bd() as conexion:
        # prepare=False habilita el script SQL con varias sentencias.
        conexion.execute(script, prepare=False)
    print("PostgreSQL inicializado correctamente.")


if __name__ == "__main__":
    inicializar()
