# Guía de defensa — Proyecto Final Semana 16

## 1. Presentación breve

> Buenos días. Mi proyecto se denomina EmiTech Store y corresponde a un
> sistema web para administrar una tienda de tecnología. Fue desarrollado con
> Python, Flask, Jinja2, PostgreSQL y Bootstrap. Incluye autenticación de
> usuarios, formularios validados, operaciones CRUD y tablas relacionadas.

## 2. Preparación antes de la tutoría

1. Compruebe que el repositorio de GitHub sea público y esté actualizado.
2. Abra previamente la aplicación publicada en Render para que el servicio
   termine de iniciar.
3. Tenga preparada una cuenta válida, pero no muestre ni diga su contraseña.
4. Ejecute `python diagnosticar_postgresql.py` y confirme que todas las
   comprobaciones indiquen `[OK]`.
5. Ejecute `python -m unittest discover -s tests -v` y confirme el resultado
   `OK`.
6. Prepare estos códigos para la demostración: `PRV-099`, `PRO-099` y
   `CLI-099`.

## 3. Demostración recomendada (4 a 5 minutos)

### 0:00–0:40 — Introducción y navegación

- Presente EmiTech Store y su objetivo.
- Muestre brevemente Inicio, Productos, Clientes, Proveedores y Facturación.
- Explique que las páginas administrativas están protegidas.

### 0:40–1:15 — Login y autenticación

- Intente abrir `/dashboard` sin sesión y muestre la redirección al login.
- Inicie sesión y enseñe el panel administrativo.
- Explique que Flask-Login administra la sesión y que las contraseñas se
  guardan mediante hash, nunca como texto original.

### 1:15–2:05 — CRUD de Proveedores

1. **Crear:** registre `PRV-099`.
2. **Leer:** muéstrelo en el listado.
3. **Actualizar:** modifique la ciudad o los días de entrega.
4. **Eliminar:** elimínelo después de mostrar la edición.

Explique que un proveedor relacionado con productos no puede eliminarse por la
clave foránea.

### 2:05–2:55 — CRUD de Productos

1. **Crear:** registre `PRO-099` y asígnele un proveedor existente.
2. **Leer:** muestre el producto y el nombre del proveedor obtenido con JOIN.
3. **Actualizar:** cambie precio o stock.
4. **Eliminar:** elimine el producto antes de incorporarlo a una factura.

### 2:55–3:40 — CRUD de Clientes

1. **Crear:** registre `CLI-099`.
2. **Leer:** muéstrelo en la tabla.
3. **Actualizar:** cambie ciudad o tipo.
4. **Eliminar:** elimínelo antes de relacionarlo con una factura.

### 3:40–4:25 — Relaciones y facturación

- Muestre la factura demostrativa existente.
- Explique las relaciones:
  - Proveedores → Productos.
  - Clientes → Facturas.
  - Facturas → Detalle de factura → Productos.
- Indique que el sistema utiliza claves primarias, claves foráneas y consultas
  JOIN para presentar la información relacionada.

### 4:25–5:00 — Cierre

- Cierre la sesión.
- Intente regresar al panel y muestre que vuelve a pedir autenticación.
- Enseñe brevemente el repositorio con `app.py`, `templates`, `static`,
  `forms`, `conexion`, `sql`, `tests` y `requirements.txt`.

## 4. Datos de demostración sugeridos

| Módulo | Código | Nombre sugerido | Cambio para UPDATE |
|---|---|---|---|
| Proveedores | PRV-099 | Proveedor Demostración | Ciudad: Quito → Puyo |
| Productos | PRO-099 | Mouse inalámbrico | Stock: 10 → 15 |
| Clientes | CLI-099 | Cliente Demostración | Tipo: Estudiante → Profesional |

No utilice información personal real durante la demostración.

## 5. Respuestas breves para posibles preguntas

**¿Dónde se almacenan los datos?**  
En PostgreSQL. La aplicación recibe la conexión mediante `DATABASE_URL`.

**¿Cómo se protegen las contraseñas?**  
Se procesan con `generate_password_hash()` de Werkzeug antes de almacenarse.

**¿Cómo se protegen las rutas?**  
Con Flask-Login y el decorador `@login_required`.

**¿Cómo se evita una inyección SQL?**  
Todas las consultas utilizan parámetros `%s`; los valores no se concatenan al
texto SQL.

**¿Cuáles son las tres tablas CRUD?**  
Productos, Clientes y Proveedores.

**¿Qué relaciones utiliza el sistema?**  
Productos referencia a Proveedores; Facturas referencia a Clientes; y
Detalle de factura referencia a Facturas y Productos.

**¿Por qué algunos registros no se pueden eliminar?**  
Las claves foráneas mantienen la integridad referencial y evitan borrar datos
que todavía se encuentran relacionados.

## 6. Lista final de entrega

- [ ] Registro e inicio de sesión funcionan.
- [ ] Logout protege nuevamente las rutas internas.
- [ ] CRUD de Productos funciona.
- [ ] CRUD de Clientes funciona.
- [ ] CRUD de Proveedores funciona.
- [ ] Se visualizan relaciones mediante JOIN.
- [ ] PostgreSQL conserva los datos.
- [ ] Las pruebas automáticas finalizan con `OK`.
- [ ] `.env` no está publicado en GitHub.
- [ ] El repositorio contiene instrucciones de ejecución.
- [ ] La aplicación de Render abre correctamente.
- [ ] El enlace de GitHub está listo para Moodle.

La defensa en vivo permite optar por la calificación máxima indicada por el
docente. El video alternativo debe utilizarse únicamente si no es posible
participar en Tutoría o Encuentro.
