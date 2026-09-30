"""Conexión centralizada con PostgreSQL para EmiTech Store."""

import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row


load_dotenv()


def conectar_bd():
    """Abre PostgreSQL usando la URL local o la suministrada por Render."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "Falta DATABASE_URL. Copie .env.example como .env y complete la conexión."
        )
    return psycopg.connect(database_url, row_factory=dict_row)
