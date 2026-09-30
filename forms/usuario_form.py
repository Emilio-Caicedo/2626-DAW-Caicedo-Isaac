"""Formularios para registrar usuarios y cerrar la sesión."""

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Regexp


class UsuarioForm(FlaskForm):
    """Valida una cuenta antes de generar el hash de su contraseña."""

    nombre_completo = StringField(
        "Nombre completo",
        validators=[
            DataRequired(message="El nombre completo es obligatorio."),
            Length(min=5, max=100, message="Ingrese entre 5 y 100 caracteres."),
        ],
        render_kw={"placeholder": "Nombres y apellidos", "autocomplete": "name"},
    )
    usuario = StringField(
        "Usuario",
        validators=[
            DataRequired(message="El usuario es obligatorio."),
            Length(min=4, max=50, message="Ingrese entre 4 y 50 caracteres."),
            Regexp(
                r"^[A-Za-z0-9_]+$",
                message="Utilice únicamente letras, números y guion bajo.",
            ),
        ],
        render_kw={"placeholder": "Ejemplo: isaac_emitech", "autocomplete": "username"},
    )
    password = PasswordField(
        "Contraseña",
        validators=[
            DataRequired(message="La contraseña es obligatoria."),
            Length(min=8, max=128, message="Utilice entre 8 y 128 caracteres."),
            Regexp(
                r"^(?=.*[A-Za-z])(?=.*\d).+$",
                message="Incluya al menos una letra y un número.",
            ),
        ],
        render_kw={"placeholder": "Mínimo 8 caracteres", "autocomplete": "new-password"},
    )
    confirmar_password = PasswordField(
        "Confirmar contraseña",
        validators=[
            DataRequired(message="Confirme la contraseña."),
            EqualTo("password", message="Las contraseñas no coinciden."),
        ],
        render_kw={"placeholder": "Repita la contraseña", "autocomplete": "new-password"},
    )
    submit = SubmitField("Crear cuenta")


class CerrarSesionForm(FlaskForm):
    """Aporta protección CSRF a la operación de cerrar sesión."""

    submit = SubmitField("Cerrar sesión")
