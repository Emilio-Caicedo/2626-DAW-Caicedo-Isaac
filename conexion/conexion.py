"""Conexión centralizada con la base de datos MySQL de EmiTech Store."""

import os

import mysql.connector
from dotenv import load_dotenv


load_dotenv()


def conectar_bd():
    """Crea y devuelve una conexión MySQL usando variables de entorno."""
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "emitech_store"),
        charset="utf8mb4",
        collation="utf8mb4_unicode_ci",
    )
