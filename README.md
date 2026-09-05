# EmiTech Store — Semana 11

Proyecto Integrador U3 · Avance 11/16 · Desarrollo de Aplicaciones Web.

**Estudiante:** Isaac Emilio Caicedo Uriña  
**Universidad:** Universidad Estatal Amazónica  
**Carrera:** Tecnologías de la Información y Comunicación  
**Paralelo:** B

## Objetivo del avance

Continuar el proyecto Flask de la Semana 10 e incorporar formularios web con
validación del servidor mediante **Flask-WTF y WTForms**. Se mantienen la
portada, las rutas, el contenido dinámico, Jinja2, Bootstrap, los componentes,
el diseño azul y naranja, las imágenes y la publicación estática de GitHub
Pages. En esta etapa no se utiliza una base de datos.

Los registros aceptados se agregan a listas y diccionarios de Python durante
la ejecución. Al detener y volver a iniciar Flask se recuperan los datos de
demostración originales.

## Evidencias de la Semana 11

| Requisito | Implementación |
|---|---|
| Carpeta `forms` | Contiene `__init__.py` y una clase independiente para cada módulo. |
| Flask-WTF | `ProductoForm`, `ClienteForm`, `ProveedorForm` y `FacturacionForm` heredan de `FlaskForm`. |
| Campos WTForms | Se utilizan `StringField`, `TextAreaField`, `SelectField`, `DecimalField`, `IntegerField` y `DateField`. |
| Validadores | Se aplican `DataRequired`, `InputRequired`, `Length`, `Email`, `NumberRange` y `Regexp`. |
| GET y POST | Las cuatro rutas de formularios aceptan ambos métodos. |
| Protección CSRF | La aplicación configura `SECRET_KEY` y cada plantilla ejecuta `form.hidden_tag()`. |
| Validación | Las rutas procesan los datos únicamente después de `form.validate_on_submit()`. |
| Errores | Cada mensaje de WTForms aparece debajo de su campo con estilos Bootstrap. |
| Respuesta válida | Se agrega el registro temporal, se muestra un mensaje y se redirige al módulo. |
| Reutilización | Una macro compartida presenta campos y errores; las páginas siguen heredando de `base.html`. |
| Sin base de datos | Los datos permanecen en memoria solo mientras Flask está encendido. |

## Estructura principal

```text
EmiTech_Store/
├── app.py
├── requirements.txt
├── forms/
│   ├── __init__.py
│   ├── producto_form.py
│   ├── cliente_form.py
│   ├── proveedor_form.py
│   └── facturacion_form.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── productos.html
│   ├── formulario_producto.html
│   ├── clientes.html
│   ├── formulario_cliente.html
│   ├── proveedores.html
│   ├── formulario_proveedor.html
│   ├── facturacion.html
│   ├── formulario_facturacion.html
│   └── components/
│       ├── navbar.html
│       ├── footer.html
│       ├── aviso.html
│       ├── campos_formulario.html
│       └── mensajes_flash.html
├── static/
│   ├── css/style.css
│   ├── js/script.js
│   └── img/
├── tests/
├── generar_frontend.py
└── index.html
```

## Instalación y ejecución en Windows

Abrir la carpeta en Visual Studio Code y usar **Terminal → New Terminal** con
**Command Prompt (cmd)**. Si el entorno `.venv` de las semanas anteriores ya
existe, no debe crearse nuevamente.

```bat
.venv\Scripts\activate
python -m pip install -r requirements.txt
python app.py
```

Abrir <http://127.0.0.1:5000>. Detener Flask con **Ctrl+C**. Las plantillas no
deben abrirse con Live Server porque requieren Flask y Jinja2.

## Rutas

| URL local | Métodos | Finalidad |
|---|---|---|
| `/` | GET | Portada informativa. |
| `/productos` | GET | Catálogo y existencias. |
| `/productos/nuevo` | GET, POST | Registrar un producto. |
| `/clientes` | GET | Directorio de clientes. |
| `/clientes/nuevo` | GET, POST | Registrar un cliente. |
| `/proveedores` | GET | Directorio de proveedores. |
| `/proveedores/nuevo` | GET, POST | Registrar un proveedor. |
| `/facturacion` | GET | Comprobante actual. |
| `/facturacion/nueva` | GET, POST | Generar un comprobante. |

## Pruebas

Con el entorno virtual activado:

```bat
python -m unittest discover -s tests -v
```

Las pruebas verifican la Semana 10 y la Semana 11: rutas, herencia, contenido
dinámico, componentes, archivos estáticos, formularios, validadores, mensajes,
CSRF, registros válidos e inválidos y cálculos del comprobante.

## GitHub Pages

GitHub Pages continúa mostrando exclusivamente el frontend estático. Después
de modificar la portada o `base.html`, se actualiza el archivo raíz con:

```bat
python generar_frontend.py
```

Los formularios Flask funcionan localmente y su código queda disponible en el
repositorio, tal como establece la consigna.

- Repositorio: <https://github.com/Emilio-Caicedo/2626-DAW-Caicedo-Isaac>
- Frontend: <https://emilio-caicedo.github.io/2626-DAW-Caicedo-Isaac/>

Para la demostración y las capturas recomendadas, consultar
`GUIA_SEMANA_11.md`.
