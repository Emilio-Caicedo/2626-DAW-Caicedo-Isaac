# EmiTech Store — Proyecto Integrador

- **Universidad:** Universidad Estatal Amazónica
- **Asignatura:** Desarrollo de Aplicaciones Web
- **Estudiante:** Isaac Emilio Caicedo Uriña
- **Avance:** Semana 15 de 16

Aplicación Flask con PostgreSQL, CRUD relacional, autenticación y despliegue
preparado para Render.

## Funcionalidades

- Registro, login, sesiones Flask-Login y contraseñas con hash de Werkzeug.
- Rutas administrativas protegidas mediante `@login_required`.
- CRUD completo para Productos, Clientes y Proveedores.
- Seis tablas PostgreSQL relacionadas mediante PK y FK.
- Consultas `JOIN`, SQL parametrizado y transacciones.
- Formularios Flask-WTF con validación y protección CSRF.
- Facturación relacionada con Cliente, Producto y control de stock.
- Portada estática compatible con GitHub Pages.
- `render.yaml`, `Procfile`, Gunicorn y ruta `/salud` para Render.

## Inicio rápido

```powershell
copy .env.example .env
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python inicializar_postgresql.py
python diagnosticar_postgresql.py
python -m unittest discover -s tests -v
python app.py
```

Si utilizará PostgreSQL local, cree primero la base `emitech_store`. Si
utilizará desde su computadora la base creada en Render, no cree otra base:
pegue la **External Database URL** de Render como `DATABASE_URL` en `.env`.

La explicación completa, prueba CRUD y pasos de Render están en
[GUIA_SEMANA_15.md](GUIA_SEMANA_15.md).

## Archivos relevantes

```text
app.py
conexion/conexion.py
forms/
templates/
sql/esquema_postgresql.sql
sql/esquema_mysql_semana14.sql
inicializar_postgresql.py
diagnosticar_postgresql.py
render.yaml
Procfile
requirements.txt
```

El archivo `.env` está ignorado por Git. El repositorio solo incluye
`.env.example`; no contiene contraseñas reales ni cuentas predeterminadas.
