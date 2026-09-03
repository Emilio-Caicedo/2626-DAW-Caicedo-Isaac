document.addEventListener("DOMContentLoaded", function () {
    // Las imágenes llegan con rutas url_for desde Flask o con rutas relativas
    // al exportar el frontend. Un archivo .js no interpreta etiquetas Jinja2.
    const datosCatalogo = document.getElementById("datosCatalogo");
    const productos = datosCatalogo ? JSON.parse(datosCatalogo.textContent) : [];
    // El contacto sigue siendo demostrativo: no existe envío al servidor.
    const formularioContacto = document.querySelector(".formulario-contacto");
    if (formularioContacto) {
        formularioContacto.addEventListener("submit", function (evento) {
            evento.preventDefault();
            document.getElementById("mensajeContacto").textContent =
                "Validación completada. Esta demostración no envía mensajes; utiliza el correo o teléfono de contacto.";
        });
    }
    // Elementos relacionados con los productos
    const listaProductos = document.getElementById("listaProductos");
    const modalDetalleProducto = document.getElementById(
        "modalDetalleProducto"
    );
    const modalProductoImagen = document.getElementById(
        "modalProductoImagen"
    );
    const modalProductoNombre = document.getElementById(
        "modalProductoNombre"
    );
    const modalProductoDescripcion = document.getElementById(
        "modalProductoDescripcion"
    );
    // Función para mostrar los productos dinámicamente
    function mostrarProductos() {
        listaProductos.innerHTML = "";
        // Corrección: la condición se verifica antes del recorrido
        if (productos.length === 0) {
            listaProductos.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-warning text-center" role="alert">
                        No existen productos disponibles actualmente.
                    </div>
                </div>
            `;
            return;
        }
        productos.forEach(function (producto, indice) {
            listaProductos.innerHTML += `
                <div class="col-lg-4 col-md-6 col-sm-12">
                    <article class="card tarjeta-producto h-100">
                        <img
                            src="${producto.imagen}"
                            class="card-img-top"
                            alt="${producto.nombre}"
                            loading="lazy"
                        >
                        <div class="card-body">
                            <h3 class="card-title h4 text-primary">
                                ${producto.nombre}
                            </h3>
                            <p class="card-text">
                                ${producto.descripcion}
                            </p>
                            <button
                                type="button"
                                class="btn btn-outline-primary mt-auto btn-detalle-producto"
                                data-indice="${indice}"
                            >
                                Ver detalles
                            </button>
                        </div>
                    </article>
                </div>
            `;
        });
        activarBotonesDetalles();
    }
    // Asigna eventos a los botones creados dinámicamente
    function activarBotonesDetalles() {
        const botonesDetalles = document.querySelectorAll(
            ".btn-detalle-producto"
        );
        botonesDetalles.forEach(function (boton) {
            boton.addEventListener("click", function () {
                const indiceProducto = Number(
                    boton.dataset.indice
                );
                mostrarDetalleProducto(indiceProducto);
            });
        });
    }
    // Muestra la información del producto dentro del modal Bootstrap
    function mostrarDetalleProducto(indiceProducto) {
        const productoSeleccionado = productos[indiceProducto];
        if (!productoSeleccionado) {
            return;
        }
        modalProductoImagen.src = productoSeleccionado.imagen;
        modalProductoImagen.alt =
            "Imagen de " + productoSeleccionado.nombre;
        modalProductoNombre.textContent =
            productoSeleccionado.nombre;
        modalProductoDescripcion.textContent =
            productoSeleccionado.descripcion;
        const instanciaModal =
            bootstrap.Modal.getOrCreateInstance(
                modalDetalleProducto
            );
        instanciaModal.show();
    }
    // Renderizado inicial de productos
    if (listaProductos) {
        mostrarProductos();
    }
    // Elementos relacionados con el formulario de solicitudes
    const formulario = document.getElementById("formRegistro");
    // Los módulos internos comparten este script, pero no tienen este formulario.
    if (!formulario) {
        return;
    }
    const contactoDesdeModal = document.getElementById("contactoDesdeModal");
    if (contactoDesdeModal && modalDetalleProducto) {
        contactoDesdeModal.addEventListener("click", function () {
            modalDetalleProducto.addEventListener("hidden.bs.modal", function () {
                window.location.hash = "contacto";
            }, { once: true });
        });
    }
    let temporizadorMensaje;
    const nombreProducto =
        document.getElementById("nombreProducto");
    const descripcionProducto =
        document.getElementById("descripcionProducto");
    const categoriaProducto =
        document.getElementById("categoriaProducto");
    const mensajeNombre =
        document.getElementById("mensajeNombre");
    const mensajeDescripcion =
        document.getElementById("mensajeDescripcion");
    const mensajeCategoria =
        document.getElementById("mensajeCategoria");
    const mensajeValidacion =
        document.getElementById("mensajeValidacion");
    const listaRegistros =
        document.getElementById("listaRegistros");
    const totalRegistros =
        document.getElementById("totalRegistros");
    const botonAgregarSolicitud =
        document.getElementById("btnAgregarSolicitud");
    const textoBotonSolicitud =
        document.getElementById("textoBotonSolicitud");
    const spinnerRegistro =
        document.getElementById("spinnerRegistro");
    // Eventos dinámicos de validación
    nombreProducto.addEventListener(
        "input",
        validarNombre
    );
    nombreProducto.addEventListener(
        "blur",
        validarNombre
    );
    descripcionProducto.addEventListener(
        "input",
        validarDescripcion
    );
    descripcionProducto.addEventListener(
        "blur",
        validarDescripcion
    );
    categoriaProducto.addEventListener(
        "change",
        validarCategoria
    );
    categoriaProducto.addEventListener(
        "blur",
        validarCategoria
    );
    // Evento para registrar una solicitud
    formulario.addEventListener("submit", function (evento) {
        evento.preventDefault();
        const nombreValido = validarNombre();
        const descripcionValida = validarDescripcion();
        const categoriaValida = validarCategoria();
        if (
            !nombreValido ||
            !descripcionValida ||
            !categoriaValida
        ) {
            mostrarMensajeGeneral(
                "Revise los campos marcados en rojo antes de registrar la solicitud.",
                "danger"
            );
            return;
        }
        const nombre =
            nombreProducto.value.trim();
        const descripcion =
            descripcionProducto.value.trim();
        const categoria =
            categoriaProducto.value.trim();
        // Muestra el spinner Bootstrap
        cambiarEstadoCarga(true);
        // Simulación de un proceso de carga
        setTimeout(function () {
            try {
                crearRegistro(
                    nombre,
                    descripcion,
                    categoria
                );
                formulario.reset();
                limpiarValidaciones();
                mostrarMensajeGeneral(
                    "Solicitud registrada correctamente.",
                    "success"
                );
            } finally {
                cambiarEstadoCarga(false);
                nombreProducto.focus();
            }
        }, 900);
    });
    // Validación del nombre
    function validarNombre() {
        const nombre =
            nombreProducto.value.trim();
        if (nombre === "") {
            mostrarEstadoCampo(
                nombreProducto,
                mensajeNombre,
                "El nombre de la solicitud es obligatorio.",
                "invalido"
            );
            return false;
        }
        if (nombre.length < 3) {
            mostrarEstadoCampo(
                nombreProducto,
                mensajeNombre,
                "El nombre debe tener mínimo 3 caracteres.",
                "invalido"
            );
            return false;
        }
        mostrarEstadoCampo(
            nombreProducto,
            mensajeNombre,
            "Nombre válido.",
            "valido"
        );
        return true;
    }
    // Validación de la descripción
    function validarDescripcion() {
        const descripcion =
            descripcionProducto.value.trim();
        if (descripcion === "") {
            mostrarEstadoCampo(
                descripcionProducto,
                mensajeDescripcion,
                "La descripción es obligatoria.",
                "invalido"
            );
            return false;
        }
        if (descripcion.length < 15) {
            mostrarEstadoCampo(
                descripcionProducto,
                mensajeDescripcion,
                "La descripción debe tener mínimo 15 caracteres.",
                "invalido"
            );
            return false;
        }
        mostrarEstadoCampo(
            descripcionProducto,
            mensajeDescripcion,
            "Descripción válida.",
            "valido"
        );
        return true;
    }
    // Validación de categoría
    function validarCategoria() {
        const categoria =
            categoriaProducto.value.trim();
        if (categoria === "") {
            mostrarEstadoCampo(
                categoriaProducto,
                mensajeCategoria,
                "Debe seleccionar una categoría o tipo de solicitud.",
                "invalido"
            );
            return false;
        }
        mostrarEstadoCampo(
            categoriaProducto,
            mensajeCategoria,
            "Categoría seleccionada correctamente.",
            "valido"
        );
        return true;
    }
    // Modifica las clases Bootstrap según el resultado de validación
    function mostrarEstadoCampo(
        campo,
        contenedorMensaje,
        texto,
        estado
    ) {
        campo.classList.remove(
            "is-valid",
            "is-invalid"
        );
        if (estado === "valido") {
            campo.classList.add("is-valid");
            contenedorMensaje.className =
                "valid-feedback d-block campo-mensaje";
        } else {
            campo.classList.add("is-invalid");
            contenedorMensaje.className =
                "invalid-feedback d-block campo-mensaje";
        }
        campo.setAttribute("aria-invalid", estado === "valido" ? "false" : "true");
        contenedorMensaje.textContent = texto;
    }
    // Controla el spinner y el estado del botón
    function cambiarEstadoCarga(cargando) {
        botonAgregarSolicitud.disabled = cargando;
        spinnerRegistro.classList.toggle(
            "d-none",
            !cargando
        );
        if (cargando) {
            textoBotonSolicitud.textContent =
                "Procesando solicitud...";
        } else {
            textoBotonSolicitud.textContent =
                "Agregar solicitud";
        }
    }
    // Renderizado dinámico de una solicitud creada por el usuario
    function crearRegistro(
        nombre,
        descripcion,
        categoria
    ) {
        const mensajeInicial =
            document.getElementById("mensajeInicial");
        if (mensajeInicial) {
            mensajeInicial.remove();
        }
        const columna =
            document.createElement("div");
        columna.className =
            "col-lg-6 col-md-6 col-sm-12";
        const tarjeta =
            document.createElement("article");
        tarjeta.className =
            "card tarjeta-registro";
        const cuerpoTarjeta =
            document.createElement("div");
        cuerpoTarjeta.className =
            "card-body";
        const etiquetaCategoria =
            document.createElement("span");
        etiquetaCategoria.className =
            "categoria-registro";
        etiquetaCategoria.textContent =
            categoria;
        const titulo =
            document.createElement("h4");
        titulo.className =
            "card-title h5 text-primary";
        titulo.textContent =
            nombre;
        const textoDescripcion =
            document.createElement("p");
        textoDescripcion.className =
            "card-text";
        textoDescripcion.textContent =
            descripcion;
        const botonEliminar =
            document.createElement("button");
        botonEliminar.type =
            "button";
        botonEliminar.className =
            "btn btn-outline-danger btn-sm mt-auto";
        botonEliminar.textContent =
            "Eliminar solicitud";
        botonEliminar.setAttribute(
            "aria-label",
            "Eliminar la solicitud " + nombre
        );
        // Evento dinámico para eliminar el registro
        botonEliminar.addEventListener(
            "click",
            function () {
                columna.remove();
                actualizarTotal();
                mostrarMensajeGeneral(
                    "Solicitud eliminada correctamente.",
                    "success"
                );
                const cantidadRegistros =
                    listaRegistros.querySelectorAll(
                        ".tarjeta-registro"
                    ).length;
                if (cantidadRegistros === 0) {
                    mostrarMensajeInicial();
                }
            }
        );
        cuerpoTarjeta.appendChild(
            etiquetaCategoria
        );
        cuerpoTarjeta.appendChild(
            titulo
        );
        cuerpoTarjeta.appendChild(
            textoDescripcion
        );
        cuerpoTarjeta.appendChild(
            botonEliminar
        );
        tarjeta.appendChild(
            cuerpoTarjeta
        );
        columna.appendChild(
            tarjeta
        );
        listaRegistros.appendChild(
            columna
        );
        actualizarTotal();
    }
    // Actualiza el contador de registros
    function actualizarTotal() {
        const cantidadRegistros =
            listaRegistros.querySelectorAll(
                ".tarjeta-registro"
            ).length;
        totalRegistros.textContent =
            cantidadRegistros;
    }
    // Muestra alertas Bootstrap de éxito o error
    function mostrarMensajeGeneral(texto, tipo) {
        clearTimeout(temporizadorMensaje);
        mensajeValidacion.textContent =
            texto;
        mensajeValidacion.className =
            "alert alert-" +
            tipo +
            " mt-3";
        temporizadorMensaje = setTimeout(function () {
            mensajeValidacion.textContent =
                "";
            mensajeValidacion.className =
                "mt-3";
        }, 3500);
    }
    // Limpia los estados visuales después de registrar
    function limpiarValidaciones() {
        [nombreProducto, descripcionProducto, categoriaProducto].forEach(function (campo) {
            campo.removeAttribute("aria-invalid");
        });
        nombreProducto.classList.remove(
            "is-valid",
            "is-invalid"
        );
        descripcionProducto.classList.remove(
            "is-valid",
            "is-invalid"
        );
        categoriaProducto.classList.remove(
            "is-valid",
            "is-invalid"
        );
        mensajeNombre.textContent =
            "";
        mensajeDescripcion.textContent =
            "";
        mensajeCategoria.textContent =
            "";
        mensajeNombre.className =
            "campo-mensaje";
        mensajeDescripcion.className =
            "campo-mensaje";
        mensajeCategoria.className =
            "campo-mensaje";
    }
    // Recupera el mensaje cuando se eliminan todos los registros
    function mostrarMensajeInicial() {
        const mensajeExistente =
            document.getElementById("mensajeInicial");
        if (mensajeExistente) {
            return;
        }
        const columnaMensaje =
            document.createElement("div");
        columnaMensaje.className =
            "col-12";
        columnaMensaje.id =
            "mensajeInicial";
        const alerta =
            document.createElement("div");
        alerta.className =
            "alert alert-info text-center";
        alerta.textContent =
            "Aún no existen registros. Complete el formulario para agregar uno.";
        columnaMensaje.appendChild(
            alerta
        );
        listaRegistros.appendChild(
            columnaMensaje
        );
    }
    // Contador inicial
    actualizarTotal();
});
