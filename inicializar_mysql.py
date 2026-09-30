"""Inicializa las tablas y los datos de EmiTech Store en MySQL."""

from pathlib import Path

import mysql.connector
from dotenv import load_dotenv
import os


load_dotenv()


def inicializar():
    """Ejecuta el esquema completo, incluida la creación de la base."""
    script = (Path(__file__).parent / "sql" / "esquema_mysql_semana15.sql").read_text(
        encoding="utf-8"
    )
    conexion = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
    )
    cursor = conexion.cursor()
    try:
        # El esquema no contiene procedimientos almacenados; por ello puede
        # ejecutarse de forma portable dividiendo las sentencias por punto y coma.
        for sentencia in script.split(";"):
            sentencia = sentencia.strip()
            if not sentencia:
                continue
            cursor.execute(sentencia)
            if cursor.with_rows:
                cursor.fetchall()
        conexion.commit()
    finally:
        cursor.close()
        conexion.close()
    print("MySQL inicializado correctamente.")


if __name__ == "__main__":
    inicializar()
