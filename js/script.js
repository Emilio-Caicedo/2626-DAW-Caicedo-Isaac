document.addEventListener("DOMContentLoaded", function () {

    const formulario = document.getElementById("formRegistro");
    const nombreProducto = document.getElementById("nombreProducto");
    const descripcionProducto = document.getElementById("descripcionProducto");
    const categoriaProducto = document.getElementById("categoriaProducto");
    const mensajeValidacion = document.getElementById("mensajeValidacion");
    const listaRegistros = document.getElementById("listaRegistros");
    const totalRegistros = document.getElementById("totalRegistros");
    const mensajeInicial = document.getElementById("mensajeInicial");

    formulario.addEventListener("submit", function (evento) {
        evento.preventDefault();

        const nombre = nombreProducto.value.trim();
        const descripcion = descripcionProducto.value.trim();
        const categoria = categoriaProducto.value.trim();

        if (nombre === "" || descripcion === "" || categoria === "") {
            mostrarMensaje("Por favor, complete todos los campos antes de agregar el registro.", "danger");
            return;
        }

        crearRegistro(nombre, descripcion, categoria);

        formulario.reset();
        nombreProducto.focus();

        mostrarMensaje("Registro agregado correctamente.", "success");
    });

    function crearRegistro(nombre, descripcion, categoria) {

        const mensajeInicialActual = document.getElementById("mensajeInicial");

        if (mensajeInicialActual) {
            mensajeInicialActual.remove();
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
            mostrarMensaje("Registro eliminado correctamente.", "warning");

            if (listaRegistros.children.length === 0) {
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
        totalRegistros.textContent = listaRegistros.children.length;
    }

    function mostrarMensaje(texto, tipo) {
        mensajeValidacion.textContent = texto;
        mensajeValidacion.className = "alert alert-" + tipo + " mt-3";

        setTimeout(function () {
            mensajeValidacion.textContent = "";
            mensajeValidacion.className = "mt-3";
        }, 3000);
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