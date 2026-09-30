# Guía de entrega — Semana 15

## 1. Qué demuestra este avance

- PostgreSQL mediante `DATABASE_URL`.
- Seis tablas: `usuarios`, `proveedores`, `productos`, `clientes`, `facturas` y `detalle_factura`.
- Relaciones con `PRIMARY KEY` y `FOREIGN KEY`.
- CRUD completo en Productos, Clientes y Proveedores.
- Formularios Flask-WTF, CSRF y consultas SQL parametrizadas.
- `JOIN` en Productos–Proveedores, Clientes–Facturas y Facturas–Detalle–Productos.
- Registro, login, logout y rutas administrativas con `@login_required`.
- Configuración reproducible para Render en `render.yaml`.

## 2. Probar localmente con PostgreSQL

1. Copie `.env.example` como `.env`.
2. Elija una conexión:
   - PostgreSQL local: cree `emitech_store` y complete usuario y contraseña.
   - PostgreSQL de Render: pegue la **External Database URL** en
     `DATABASE_URL`. No debe crear manualmente otra base.
4. Active el entorno virtual e instale dependencias:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

5. Cree las tablas, verifíquelas y ejecute el diagnóstico:

```powershell
python inicializar_postgresql.py
python diagnosticar_postgresql.py
```

El diagnóstico debe finalizar con
`DIAGNÓSTICO COMPLETADO: la base está lista para EmiTech Store.` No guarda el
usuario temporal utilizado para la comprobación.

6. Ejecute las pruebas y la aplicación:

```powershell
python -m unittest discover -s tests -v
python app.py
```

7. Abra `http://127.0.0.1:5000/registro`, cree una cuenta e inicie sesión.

El script es idempotente: se puede ejecutar nuevamente sin duplicar los datos
iniciales. MySQL ya no es utilizado por la Semana 15.

## 3. Prueba CRUD obligatoria

Después del login:

1. Abra **Productos** y verifique la columna Proveedor (JOIN).
2. Registre `PRO-099`, edítelo y después elimínelo.
3. Repita crear, editar y eliminar en **Clientes** con `CLI-099`.
4. En **Proveedores**, cree `PRV-099`, edítelo y elimínelo antes de asignarle productos.
5. Abra **Facturación** y compruebe el cliente y los productos relacionados.
6. Genere una factura con un número nuevo, por ejemplo `FAC-0099`.
7. Cierre sesión y confirme que `/dashboard` vuelve a solicitar login.

No elimine los proveedores que tengan productos ni los clientes que tengan
facturas: las claves foráneas los protegen y la aplicación muestra un aviso.

## 4. Publicar en Render

### Opción recomendada: Blueprint

1. Primero suba esta versión a GitHub.
2. En Render elija **New + → Blueprint**.
3. Conecte el repositorio `2626-DAW-Caicedo-Isaac`.
4. Render leerá `render.yaml` y propondrá un Web Service y una base PostgreSQL.
5. Pulse **Apply** y espere a que ambos recursos terminen.
6. En el plan gratuito, el comando de inicio ejecutará
   `inicializar_postgresql.py` y luego iniciará `gunicorn app:app`.
7. Abra la URL pública terminada en `.onrender.com`.
8. Entre primero a `/registro` y cree su usuario; no existe una contraseña
   predeterminada dentro del repositorio.

### Si Render no ofrece el plan `free`

Seleccione el plan disponible permitido por su cuenta o cree manualmente:

- una base **Render Postgres** llamada `emitech-store-db`;
- un **Web Service** Python conectado al repositorio;
- Build Command: `pip install -r requirements.txt`;
- Start Command: `python inicializar_postgresql.py && gunicorn app:app`;
- variable `DATABASE_URL`: Internal Database URL de Render Postgres;
- variable `SECRET_KEY`: valor aleatorio largo;
- Health Check Path: `/salud`.

Use la URL **interna** de PostgreSQL cuando el Web Service y la base estén en
Render y en la misma región. No publique `DATABASE_URL` ni `SECRET_KEY`.

## 5. Evidencias recomendadas

Capture:

1. Login correcto.
2. Tabla de Productos con el nombre del proveedor.
3. Formulario para agregar.
4. Registro agregado.
5. Registro modificado.
6. Confirmación de eliminación.
7. Factura con Cliente y Productos relacionados.
8. Cierre de sesión.
9. Panel de Render con despliegue exitoso, ocultando secretos.

Entregue el enlace del repositorio de GitHub y la URL pública de Render.
