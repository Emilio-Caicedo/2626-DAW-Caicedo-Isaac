document.addEventListener("DOMContentLoaded", function () {

    const formulario = document.getElementById("formRegistro");

    const nombreProducto = document.getElementById("nombreProducto");
    const descripcionProducto = document.getElementById("descripcionProducto");
    const categoriaProducto = document.getElementById("categoriaProducto");

    const mensajeNombre = document.getElementById("mensajeNombre");
    const mensajeDescripcion = document.getElementById("mensajeDescripcion");
    const mensajeCategoria = document.getElementById("mensajeCategoria");
    const mensajeValidacion = document.getElementById("mensajeValidacion");

    const listaRegistros = document.getElementById("listaRegistros");
    const totalRegistros = document.getElementById("totalRegistros");

    nombreProducto.addEventListener("input", validarNombre);
    nombreProducto.addEventListener("blur", validarNombre);

    descripcionProducto.addEventListener("input", validarDescripcion);
    descripcionProducto.addEventListener("blur", validarDescripcion);

    categoriaProducto.addEventListener("change", validarCategoria);
    categoriaProducto.addEventListener("blur", validarCategoria);

    formulario.addEventListener("submit", function (evento) {
        evento.preventDefault();

        const nombreValido = validarNombre();
        const descripcionValida = validarDescripcion();
        const categoriaValida = validarCategoria();

        if (!nombreValido || !descripcionValida || !categoriaValida) {
            mostrarMensajeGeneral(
                "Revise los campos marcados en rojo antes de registrar la solicitud.",
                "danger"
            );
            return;
        }

        const nombre = nombreProducto.value.trim();
        const descripcion = descripcionProducto.value.trim();
        const categoria = categoriaProducto.value.trim();

        crearRegistro(nombre, descripcion, categoria);

        formulario.reset();
        limpiarValidaciones();
        nombreProducto.focus();

        mostrarMensajeGeneral(
            "Solicitud registrada correctamente.",
            "success"
        );
    });

    function validarNombre() {
        const nombre = nombreProducto.value.trim();

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

    function validarDescripcion() {
        const descripcion = descripcionProducto.value.trim();

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

    function validarCategoria() {
        const categoria = categoriaProducto.value.trim();

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

    function mostrarEstadoCampo(campo, contenedorMensaje, texto, estado) {
        campo.classList.remove("is-valid", "is-invalid");

        if (estado === "valido") {
            campo.classList.add("is-valid");
            contenedorMensaje.className = "valid-feedback d-block campo-mensaje";
        } else {
            campo.classList.add("is-invalid");
            contenedorMensaje.className = "invalid-feedback d-block campo-mensaje";
        }

        contenedorMensaje.textContent = texto;
    }

    function crearRegistro(nombre, descripcion, categoria) {
        const mensajeInicial = document.getElementById("mensajeInicial");

        if (mensajeInicial) {
            mensajeInicial.remove();
        }

        const columna = document.createElement("div");
        columna.className = "col-lg-6 col-md-6 col-sm-12";

        const tarjeta = document.createElement("div");
        tarjeta.className = "card tarjeta-registro";

        const cuerpoTarjeta = document.createElement("div");
        cuerpoTarjeta.className = "card-body";

        const etiquetaCategoria = document.createElement("span");
        etiquetaCategoria.className = "categoria-registro";
        etiquetaCategoria.textContent = categoria;

        const titulo = document.createElement("h4");
        titulo.className = "card-title h5 text-primary";
        titulo.textContent = nombre;

        const textoDescripcion = document.createElement("p");
        textoDescripcion.className = "card-text";
        textoDescripcion.textContent = descripcion;

        const botonEliminar = document.createElement("button");
        botonEliminar.className = "btn btn-outline-danger btn-sm";
        botonEliminar.textContent = "Eliminar";

        botonEliminar.addEventListener("click", function () {
            columna.remove();
            actualizarTotal();

            mostrarMensajeGeneral(
                "Solicitud eliminada correctamente.",
                "success"
            );

            if (listaRegistros.querySelectorAll(".tarjeta-registro").length === 0) {
                mostrarMensajeInicial();
            }
        });

        cuerpoTarjeta.appendChild(etiquetaCategoria);
        cuerpoTarjeta.appendChild(titulo);
        cuerpoTarjeta.appendChild(textoDescripcion);
        cuerpoTarjeta.appendChild(botonEliminar);

        tarjeta.appendChild(cuerpoTarjeta);
        columna.appendChild(tarjeta);

        listaRegistros.appendChild(columna);

        actualizarTotal();
    }

    function actualizarTotal() {
        const cantidadRegistros = listaRegistros.querySelectorAll(".tarjeta-registro").length;
        totalRegistros.textContent = cantidadRegistros;
    }

    function mostrarMensajeGeneral(texto, tipo) {
        mensajeValidacion.textContent = texto;
        mensajeValidacion.className = "alert alert-" + tipo + " mt-3";

        setTimeout(function () {
            mensajeValidacion.textContent = "";
            mensajeValidacion.className = "mt-3";
        }, 3500);
    }

    function limpiarValidaciones() {
        nombreProducto.classList.remove("is-valid", "is-invalid");
        descripcionProducto.classList.remove("is-valid", "is-invalid");
        categoriaProducto.classList.remove("is-valid", "is-invalid");

        mensajeNombre.textContent = "";
        mensajeDescripcion.textContent = "";
        mensajeCategoria.textContent = "";

        mensajeNombre.className = "campo-mensaje";
        mensajeDescripcion.className = "campo-mensaje";
        mensajeCategoria.className = "campo-mensaje";
    }

    function mostrarMensajeInicial() {
        const columnaMensaje = document.createElement("div");
        columnaMensaje.className = "col-12";
        columnaMensaje.id = "mensajeInicial";

        const alerta = document.createElement("div");
        alerta.className = "alert alert-info text-center";
        alerta.textContent = "Aún no existen registros. Complete el formulario para agregar uno.";

        columnaMensaje.appendChild(alerta);
        listaRegistros.appendChild(columnaMensaje);
    }

});