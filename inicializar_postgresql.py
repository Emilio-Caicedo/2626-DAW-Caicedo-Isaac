"""Crea tablas y datos iniciales en el PostgreSQL configurado."""

from pathlib import Path

from conexion import conectar_bd


TABLAS_REQUERIDAS = {
    "usuarios",
    "proveedores",
    "productos",
    "clientes",
    "facturas",
    "detalle_factura",
}


def inicializar():
    script = (Path(__file__).parent / "sql" / "esquema_postgresql.sql").read_text(
        encoding="utf-8"
    )
    with conectar_bd() as conexion:
        # prepare=False habilita el script SQL con varias sentencias.
        conexion.execute(script, prepare=False)
        filas = conexion.execute(
            """SELECT table_name
               FROM information_schema.tables
               WHERE table_schema = 'public'"""
        ).fetchall()
        encontradas = {fila["table_name"] for fila in filas}

    faltantes = sorted(TABLAS_REQUERIDAS - encontradas)
    if faltantes:
        raise RuntimeError(
            "No se crearon todas las tablas requeridas: " + ", ".join(faltantes)
        )

    print("PostgreSQL inicializado y verificado correctamente.")
    print("Tablas disponibles: " + ", ".join(sorted(TABLAS_REQUERIDAS)))


if __name__ == "__main__":
    inicializar()
