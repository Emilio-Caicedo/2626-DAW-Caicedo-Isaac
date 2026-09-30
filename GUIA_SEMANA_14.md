# Guía de ejecución y evidencias — Semana 14

## 1. Archivos incorporados

La Semana 14 continúa el mismo proyecto y agrega:

- `models.py`: clase `Usuario(UserMixin)`.
- `forms/login_form.py`: credenciales y opción de recordar sesión.
- `forms/usuario_form.py`: registro y formulario CSRF para logout.
- `templates/login.html`, `registro.html` y `dashboard.html`.
- `sql/migracion_semana14.sql`: agrega `usuarios` sin borrar la Semana 13.
- `tests/test_semana14.py`: pruebas automatizadas de autenticación.

## 2. Actualizar el proyecto local

Copie los archivos de la Semana 14 dentro de:

```text
D:\DESARROLLO_APP_WEB
```

La carpeta debe conservar `.git` y el archivo privado `.env` de la Semana 13.
No copie `.venv` desde otra computadora.

## 3. Instalar las dependencias

Abra la terminal de Visual Studio Code:

```cmd
cd /d D:\DESARROLLO_APP_WEB
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

Flask-Login y Werkzeug deben quedar disponibles.

## 4. Agregar la tabla de usuarios

No elimine `emitech_store` ni vuelva a crear las tablas existentes.

1. Abra MySQL Workbench.
2. Ingrese a `Local instance MySQL80`.
3. Seleccione **File > Open SQL Script**.
4. Abra:

```text
D:\DESARROLLO_APP_WEB\sql\migracion_semana14.sql
```

5. Ejecute todo el archivo con el primer rayo amarillo.
6. Actualice **SCHEMAS > emitech_store > Tables**.
7. Compruebe que aparezca `usuarios`.

## 5. Ejecutar la aplicación

```cmd
python app.py
```

Abra:

```text
http://127.0.0.1:5000
```

## 6. Prueba obligatoria completa

### A. Comprobar una ruta protegida

Sin iniciar sesión, escriba:

```text
http://127.0.0.1:5000/productos
```

El sistema debe redirigir automáticamente a `/login`.

### B. Registrar una cuenta

Abra `/registro` y use datos académicos de prueba. Ejemplo:

```text
Nombre completo: Isaac Emilio Caicedo Uriña
Usuario: isaac_emitech
Contraseña: Emitech2026
Confirmación: Emitech2026
```

La cuenta se guarda en MySQL y el sistema redirige al login.

### C. Verificar el hash directamente en MySQL

Abra una pestaña SQL y ejecute:

```sql
USE emitech_store;

SELECT
    id_usuario,
    usuario,
    nombre_completo,
    password_hash,
    CHAR_LENGTH(password_hash) AS longitud_hash,
    activo
FROM usuarios;
```

`password_hash` debe mostrar una cadena extensa. No debe mostrar la contraseña
que se escribió en el formulario.

### D. Probar una contraseña incorrecta

Ingrese el usuario correcto y una contraseña diferente. Debe mostrarse:

```text
Usuario o contraseña incorrectos.
```

El sistema no debe abrir el panel.

### E. Probar el login correcto

Utilice las credenciales registradas. Debe abrirse `/dashboard`, mostrarse el
nombre completo y aparecer el usuario activo en el menú.

### F. Comprobar los módulos privados

Abra Productos, Clientes, Proveedores y Facturación. Todos deben funcionar
después de iniciar sesión. Pruebe además el CRUD de Productos de la Semana 13.

### G. Cerrar sesión

Pulse **Cerrar sesión**. Luego escriba directamente:

```text
http://127.0.0.1:5000/productos
```

El sistema debe volver a redirigir hacia el login.

## 7. Pruebas automatizadas

Detenga Flask con `Ctrl + C` y ejecute:

```cmd
python -m unittest discover -s tests -v
```

Resultado esperado:

```text
Ran 33 tests
OK (skipped=3)
```

Los tres módulos omitidos corresponden a suites históricas sustituidas; no son
errores.

## 8. Evidencias recomendadas

Tome capturas de:

1. La tabla `usuarios` visible en MySQL Workbench.
2. El registro realizado correctamente.
3. La consulta que demuestra el hash.
4. El mensaje de contraseña incorrecta.
5. El dashboard mostrando el usuario autenticado.
6. Productos funcionando después del login.
7. La redirección al login después del logout.
8. La terminal con las pruebas en estado `OK`.

No muestre el archivo `.env` ni su contraseña de MySQL en las capturas.

## 9. Actualizar GitHub Pages

```cmd
python generar_frontend.py
```

Debe indicar:

```text
Frontend actualizado: index.html
```

El login no funcionará en GitHub Pages; esa publicación muestra únicamente el
frontend. La autenticación se demuestra ejecutando Flask localmente.

## 10. Verificar y subir a GitHub

```cmd
git check-ignore .env
git status
git add .
git status
git commit -m "Semana 14: sistema de login y rutas protegidas"
git push origin main
```

`git check-ignore .env` debe responder `.env`. Antes del commit, confirme que
`.env` y `.venv` no estén entre los archivos preparados.
