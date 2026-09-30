# EmiTech Store — Proyecto Integrador

- **Universidad:** Universidad Estatal Amazónica
- **Asignatura:** Desarrollo de Aplicaciones Web
- **Estudiante:** Isaac Emilio Caicedo Uriña
**Avance:** Semana 13 de 16

Aplicación web desarrollada con Flask, Jinja2, Flask-WTF, Bootstrap y MySQL.
La Semana 13 incorpora una base de datos relacional y el CRUD completo del
módulo Productos.

## Funcionalidades de la Semana 13

- Conexión MySQL centralizada en `conexion/conexion.py`.
- Variables de entorno para no publicar credenciales.
- Modelo relacional en `sql/esquema.sql`.
- Claves primarias y relaciones mediante claves foráneas.
- Listado de productos mediante `SELECT`, `INNER JOIN` y `fetchall()`.
- Registro validado mediante Flask-WTF e `INSERT`.
- Modificación mediante `UPDATE ... WHERE`.
- Eliminación mediante `DELETE ... WHERE`, confirmación visual y CSRF.
- Consultas SQL parametrizadas y cierre de cursores/conexiones.
- Persistencia de los cambios después de reiniciar Flask.
- Portada estática compatible con GitHub Pages.

## Estructura principal

```text
EmiTech Store/
├── app.py
├── requirements.txt
├── .env.example
├── conexion/
│   ├── __init__.py
│   └── conexion.py
├── sql/
│   └── esquema.sql
├── forms/
├── templates/
├── static/
├── data/
│   └── emitech_store.db  (evidencia de la Semana 12)
└── tests/
```

## Instalación rápida

1. Instale MySQL Server y MySQL Workbench.
2. Ejecute `sql/esquema.sql` desde MySQL Workbench.
3. Copie `.env.example` con el nombre `.env` y coloque su contraseña local.
4. Cree y active un entorno virtual.
5. Instale las dependencias con `pip install -r requirements.txt`.
6. Ejecute la aplicación con `python app.py`.
7. Abra `http://127.0.0.1:5000/productos`.

Las instrucciones detalladas y las evidencias recomendadas se encuentran en
`GUIA_SEMANA_13.md`.

## Seguridad

El archivo `.env` está excluido mediante `.gitignore`. No se deben escribir ni
subir contraseñas reales en `app.py`, `conexion/conexion.py` o GitHub.

## Publicación

- Flask y MySQL se ejecutan localmente.
- GitHub contiene el backend y el esquema SQL.
- GitHub Pages muestra únicamente la portada estática `index.html`.
