"""Formularios Flask-WTF organizados por módulo."""

from .cliente_form import ClienteForm
from .facturacion_form import FacturacionForm
from .login_form import LoginForm
from .producto_form import EliminarProductoForm, EliminarRegistroForm, ProductoForm
from .proveedor_form import ProveedorForm
from .usuario_form import CerrarSesionForm, UsuarioForm

__all__ = [
    "ClienteForm",
    "CerrarSesionForm",
    "EliminarProductoForm",
    "EliminarRegistroForm",
    "FacturacionForm",
    "LoginForm",
    "ProductoForm",
    "ProveedorForm",
    "UsuarioForm",
]
