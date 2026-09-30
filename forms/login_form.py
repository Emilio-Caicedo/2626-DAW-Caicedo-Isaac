"""Formulario de inicio de sesión."""

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    """Valida las credenciales antes de consultarlas en MySQL."""

    usuario = StringField(
        "Usuario",
        validators=[
            DataRequired(message="El usuario es obligatorio."),
            Length(min=4, max=50, message="Ingrese entre 4 y 50 caracteres."),
        ],
        render_kw={"placeholder": "Ingrese su usuario", "autocomplete": "username"},
    )
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired(message="La contraseña es obligatoria.")],
        render_kw={"placeholder": "Ingrese su contraseña", "autocomplete": "current-password"},
    )
    recordar = BooleanField("Mantener la sesión iniciada")
    submit = SubmitField("Iniciar sesión")
