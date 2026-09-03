# EmiTech Store — Semana 9

Proyecto Integrador U3 · Avance 9/16 · Desarrollo de Aplicaciones Web.

**Estudiante:** Isaac Emilio Caicedo Uriña  
**Universidad:** Universidad Estatal Amazónica  
**Carrera:** Tecnologías de la Información y Comunicación  
**Paralelo:** B

## Objetivo del avance

Adaptar la página informativa de EmiTech Store a Python y Flask, organizar sus recursos en `templates` y `static`, y crear los módulos Productos, Clientes, Proveedores y Facturación mediante rutas y herencia de plantillas Jinja2. Esta semana utiliza datos demostrativos, sin base de datos.

La portada conserva el contenido, las imágenes y el diseño azul y naranja de la semana 8, junto con el catálogo dinámico, los detalles en un modal, las solicitudes y el video. Se mantiene Bootstrap 5.3.3.

## Organización

| Ruta | Función |
|---|---|
| `app.py` | Aplicación Flask, cinco rutas y datos de ejemplo. |
| `templates/base.html` | Estructura común: encabezado, menú, bloques, pie, Bootstrap, CSS y JavaScript. |
| `templates/index.html` | Página principal informativa, heredada de `base.html`. |
| `templates/productos.html` | Catálogo de seis productos de ejemplo. |
| `templates/clientes.html` | Directorio de cuatro clientes ficticios. |
| `templates/proveedores.html` | Tres proveedores ficticios. |
| `templates/facturacion.html` | Comprobante de venta demostrativo. |
| `static/css/style.css` | Estilos anteriores y estilos de los módulos. |
| `static/js/script.js` | Interactividad de la portada, validaciones y solicitudes. |
| `static/img/` | Las siete imágenes originales del proyecto. |
| `index.html` | Portada estática generada para GitHub Pages. |
| `generar_frontend.py` | Actualiza la portada estática a partir de las plantillas. |
| `requirements.txt` | Dependencia Flask con versión definida. |
| `.gitignore` | Excluye entorno virtual, cachés y archivos locales. |
| `.nojekyll` | Permite servir directamente los archivos estáticos en GitHub Pages. |
| `GUIA_SEMANA_9.md` | Instalación, explicación del código, pruebas y publicación paso a paso. |

## Ejecución local en Windows

Abrir esta carpeta en Visual Studio Code. En **Terminal → Nueva terminal**, seleccionar **Command Prompt / Símbolo del sistema (cmd)**. Ejecutar los comandos uno por uno:

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python app.py
```

`requirements.txt` instala Flask 3.1.2. El comando `pip install flask` indicado en la consigna también instala Flask; el archivo de dependencias permite reproducir la versión utilizada en este avance. Se necesita Python 3.9 o posterior; se recomienda Python 3.12.

Abrir [http://127.0.0.1:5000](http://127.0.0.1:5000). Detener el servidor con **Ctrl+C**. No abrir las plantillas con Live Server: necesitan ser procesadas por Flask.

Para macOS/Linux, activar el entorno con `source .venv/bin/activate`, después de crearlo con `python3 -m venv .venv`.

## Rutas implementadas

| URL local | Función de Python | Plantilla |
|---|---|---|
| `/` | `inicio()` | `index.html` |
| `/productos` | `productos()` | `productos.html` |
| `/clientes` | `clientes()` | `clientes.html` |
| `/proveedores` | `proveedores()` | `proveedores.html` |
| `/facturacion` | `facturacion()` | `facturacion.html` |

Todas usan `@app.route()` y `render_template()`. Las cinco páginas heredan de `base.html` mediante `{% extends "base.html" %}` y definen `{% block content %}`.

El menú genera los enlaces con `url_for()`. Las plantillas cargan los recursos mediante `url_for('static', filename='...')`. Las rutas de imágenes del catálogo dinámico también se generan con `url_for()` en Python y se entregan a JavaScript como JSON.

## GitHub Pages

GitHub Pages sirve el `index.html` de la **raíz** y los archivos de `static/`. La navegación pública conserva las secciones de la portada. Los cuatro módulos de Flask se ejecutan localmente y no se publican como rutas de GitHub Pages.

El `index.html` de la raíz ya está generado. Después de modificar la portada o su plantilla base, actualizarlo con:

```bat
python generar_frontend.py
```

Editar las páginas en `templates/`, no el archivo generado de la raíz. Esta organización evita mantener dos portadas escritas a mano; la exportación utiliza las mismas plantillas y recursos.

En el repositorio, configurar **Settings → Pages → Deploy from a branch → main → /(root)**, si esa es la rama utilizada para entregar el proyecto.

- Repositorio: [2626-DAW-Caicedo-Isaac](https://github.com/Emilio-Caicedo/2626-DAW-Caicedo-Isaac)
- Frontend: [EmiTech Store en GitHub Pages](https://emilio-caicedo.github.io/2626-DAW-Caicedo-Isaac/)

## Alcance de la demostración

- Los módulos muestran datos de ejemplo definidos en `app.py`.
- No hay base de datos, autenticación ni operaciones de compra.
- Las solicitudes de la portada se agregan y eliminan en la página; desaparecen al recargar y no se envían a la tienda.
- El formulario de contacto valida los campos y explica que no realiza envíos.
- Facturación presenta un ejemplo con subtotal de $600.00, impuesto ilustrativo de $90.00 y total de $690.00. El porcentaje del 15 % es un supuesto didáctico; el comprobante no tiene validez tributaria.
- Bootstrap y el video de YouTube necesitan acceso a Internet.
- El entorno `.venv` se crea en cada computadora y no se incluye en el ZIP ni se sube a GitHub.

## Comprobaciones del avance

Se ejecutó `python app.py` dentro de un entorno virtual y las cinco rutas respondieron con HTTP 200. También se comprobaron la herencia de plantillas, los enlaces internos, las rutas de imágenes/CSS/JavaScript y las referencias relativas del frontend estático. La página principal conserva sus secciones originales.

Las pruebas de JavaScript en un DOM simulado verificaron el catálogo, los tres modales de Bootstrap, la validación, la creación y eliminación de solicitudes, el contador y el mensaje del contacto, tanto en la portada Flask como en su exportación estática. Los cuatro módulos cargaron el script compartido sin errores. Esto no sustituye la revisión visual en tu navegador.

El 2 de septiembre de 2026, el repositorio y la página pública existentes respondieron con HTTP 200. Esa comprobación corresponde a la versión que ya estaba publicada; los archivos de este avance todavía deben subirse. Antes de entregar, seguir las pruebas de `GUIA_SEMANA_9.md` y comprobar los dos enlaces públicos después de subir los cambios.
