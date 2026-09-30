# EmiTech Store — Proyecto Integrador

- **Universidad:** Universidad Estatal Amazónica
- **Asignatura:** Desarrollo de Aplicaciones Web
- **Estudiante:** Isaac Emilio Caicedo Uriña
- **Avance:** Semana 14 de 16

Aplicación web desarrollada con Flask, Jinja2, Flask-WTF, Bootstrap,
Flask-Login, Werkzeug y MySQL. La Semana 14 conserva el CRUD de Productos e
incorpora un sistema de autenticación funcional conectado a la base relacional.

## Funcionalidades de la Semana 14

- Registro de usuarios en la tabla MySQL `usuarios`.
- Formularios validados mediante Flask-WTF.
- Contraseñas protegidas con `generate_password_hash()`.
- Validación de credenciales mediante `check_password_hash()`.
- Sesión administrada con `LoginManager`, `UserMixin` y `login_user()`.
- Recuperación de la sesión desde MySQL mediante `load_user()`.
- Rutas de Productos, Clientes, Proveedores y Facturación protegidas con
  `@login_required`.
- Visualización de `current_user` en el menú y panel privado.
- Cierre seguro de sesión mediante POST, CSRF y `logout_user()`.
- Mensajes claros para credenciales incorrectas y accesos no autorizados.
- Portada estática compatible con GitHub Pages.

## Estructura principal

```text
EmiTech Store/
├── app.py
├── models.py
├── requirements.txt
├── .env.example
├── conexion/
├── forms/
│   ├── login_form.py
│   └── usuario_form.py
├── sql/
│   ├── esquema.sql
│   └── migracion_semana14.sql
├── templates/
│   ├── login.html
│   ├── registro.html
│   ├── dashboard.html
│   └── components/
├── static/
└── tests/
```

## Instalación rápida

1. Mantenga MySQL Server en ejecución.
2. Si ya realizó la Semana 13, ejecute únicamente
   `sql/migracion_semana14.sql` desde MySQL Workbench.
3. Conserve su archivo local `.env`; nunca lo suba a GitHub.
4. Active el entorno virtual.
5. Instale las dependencias con `pip install -r requirements.txt`.
6. Ejecute `python app.py`.
7. Abra `http://127.0.0.1:5000/registro`, cree una cuenta y luego inicie sesión.

La guía completa de instalación, pruebas obligatorias y evidencias se encuentra
en [GUIA_SEMANA_14.md](GUIA_SEMANA_14.md).

## Seguridad

`.env` está excluido mediante `.gitignore`. El repositorio contiene solamente
`.env.example` con marcadores de ejemplo. No se incluyen contraseñas reales,
usuarios predeterminados ni claves privadas.

## Publicación

- Flask, MySQL, el login y las sesiones se ejecutan localmente.
- GitHub contiene el backend, formularios, plantillas y scripts SQL.
- GitHub Pages muestra únicamente la portada estática `index.html`.
