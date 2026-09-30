"""Conexión centralizada con PostgreSQL para EmiTech Store."""

import os
from urllib.parse import urlsplit

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row


load_dotenv()


def conectar_bd():
    """Abre PostgreSQL usando la URL local o la suministrada por Render.

    La URL se limpia para evitar espacios copiados accidentalmente. Cuando el
    servidor pertenece a Render se exige SSL. El tiempo máximo evita que la
    aplicación quede esperando indefinidamente si la red no está disponible.
    """
    database_url = (os.getenv("DATABASE_URL") or "").strip()
    if not database_url:
        raise RuntimeError(
            "Falta DATABASE_URL. Copie .env.example como .env y complete la conexión."
        )

    if database_url.startswith("postgres://"):
        database_url = "postgresql://" + database_url[len("postgres://"):]

    opciones = {
        "row_factory": dict_row,
        "connect_timeout": 15,
        "application_name": "emitech_store",
    }
    host = urlsplit(database_url).hostname or ""
    if host.endswith("render.com"):
        opciones["sslmode"] = "require"

    return psycopg.connect(database_url, **opciones)
