from pathlib import Path
from urllib.parse import quote

from flask import render_template

from app import NOMBRE_TIENDA, app, obtener_catalogo


def url_estatica(endpoint, **valores):
    """Solo se publican recursos y la portada; los módulos son locales."""
    if endpoint == "static":
        return "static/" + quote(valores["filename"], safe="/")
    if endpoint == "inicio":
        ancla = valores.get("_anchor")
        return "#" + quote(ancla) if ancla else "index.html"
    raise ValueError(f"La ruta {endpoint} no pertenece al frontend estático.")


def generar_frontend():
    with app.test_request_context("/"):
        catalogo = obtener_catalogo()
        for categoria in catalogo:
            categoria["imagen"] = categoria["imagen"].lstrip("/")
        html = render_template(
            "index.html",
            titulo=NOMBRE_TIENDA,
            catalogo=catalogo,
            modo_estatico=True,
            url_for=url_estatica,
        )
    destino = Path(__file__).resolve().parent / "index.html"
    # Limpia solo espacios finales; no cambia el contenido de la portada.
    html = "\n".join(linea.rstrip() for linea in html.splitlines())
    aviso = "<!-- Generado con generar_frontend.py. Editar templates/index.html y regenerar. -->\n"
    destino.write_text(aviso + html + "\n", encoding="utf-8")
    print("Frontend actualizado: index.html")


if __name__ == "__main__":
    generar_frontend()
